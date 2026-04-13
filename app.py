from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, date
import pandas as pd
import numpy as np
import io

ROOT_DIR: Path = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url: str = os.environ['MONGO_URL']
client: AsyncIOMotorClient = AsyncIOMotorClient(mongo_url)
db: AsyncIOMotorDatabase = client[os.environ['DB_NAME']]

app: FastAPI = FastAPI()
api_router: APIRouter = APIRouter(prefix="/api")

# ============ MODELS ============

class ClientModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    status: str = "Pending"
    due_date: Optional[str] = None
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ClientCreate(BaseModel):
    client_name: str
    status: str = "Pending"
    due_date: Optional[str] = None

class ClientUpdate(BaseModel):
    status: Optional[str] = None
    due_date: Optional[str] = None

class ReconciliationResult(BaseModel):
    matched_count: int = 0
    missing_count: int = 0
    mismatch_count: int = 0
    matched: list = []
    missing: list = []
    mismatched: list = []

# ============ HEALTH ============

@api_router.get("/")
async def root() -> dict:
    return {"message": "CA Toolkit API"}

# ============ CLIENTS ============

@api_router.get("/clients", response_model=List[ClientModel])
async def get_clients(search: str = "", status: str = "All") -> List[ClientModel]:
    query = {}
    if search:
        query["client_name"] = {"$regex": search, "$options": "i"}
    if status != "All":
        query["status"] = status
    clients = await db.clients.find(query, {"_id": 0}).to_list(500)
    return clients

@api_router.post("/clients", response_model=ClientModel)
async def create_client(data: ClientCreate) -> ClientModel:
    client_obj = ClientModel(
        client_name=data.client_name,
        status=data.status,
        due_date=data.due_date,
        last_updated=datetime.now(timezone.utc).isoformat()
    )
    doc = client_obj.model_dump()
    await db.clients.insert_one(doc)
    return client_obj

@api_router.put("/clients/{client_id}", response_model=ClientModel)
async def update_client(client_id: str, data: ClientUpdate) -> ClientModel:
    update_fields = {"last_updated": datetime.now(timezone.utc).isoformat()}
    if data.status is not None:
        update_fields["status"] = data.status
    if data.due_date is not None:
        update_fields["due_date"] = data.due_date
    await db.clients.update_one({"id": client_id}, {"$set": update_fields})
    updated = await db.clients.find_one({"id": client_id}, {"_id": 0})
    if not updated:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientModel(**updated)

@api_router.delete("/clients/{client_id}")
async def delete_client(client_id: str) -> dict:
    result = await db.clients.delete_one({"id": client_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted"}

# ============ DASHBOARD ============

@api_router.get("/dashboard")
async def get_dashboard() -> dict:
    all_clients = await db.clients.find({}, {"_id": 0}).to_list(500)
    total = len(all_clients)
    pending = sum(1 for c in all_clients if c.get("status") == "Pending")
    completed = sum(1 for c in all_clients if c.get("status") == "Completed")

    today = date.today()
    urgent = []
    overdue = []

    for c in all_clients:
        if c.get("due_date"):
            try:
                due = date.fromisoformat(c["due_date"])
                days_left = (due - today).days
                entry = {
                    "client_name": c["client_name"],
                    "due_date": c["due_date"],
                    "days_left": days_left,
                    "status": c.get("status", "Pending")
                }
                if days_left < 0:
                    overdue.append(entry)
                elif days_left <= 2:
                    urgent.append(entry)
            except (ValueError, TypeError):
                pass

    return {
        "total": total,
        "pending": pending,
        "completed": completed,
        "urgent": urgent,
        "overdue": overdue,
        "clients": all_clients
    }

# ============ GST RECONCILIATION ============

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize a GST dataframe."""
    df.columns = df.columns.str.strip()

    # Normalize GSTIN
    df['GSTIN'] = df['GSTIN'].astype(str).str.replace('.0', '', regex=False).str.strip()

    # Normalize Invoice No
    df['Invoice No'] = df['Invoice No'].astype(str).str.strip().str.replace(" ", "")

    # Normalize Amount
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

    # ===== FIX: Remove blank/invalid rows =====
    df = df[
        (df['GSTIN'].notna()) &
        (df['GSTIN'] != 'None') &
        (df['GSTIN'] != 'nan') &
        (df['GSTIN'].str.strip() != '')
    ]
    df = df[
        (df['Invoice No'].notna()) &
        (df['Invoice No'] != 'None') &
        (df['Invoice No'] != 'nan') &
        (df['Invoice No'].str.strip() != '')
    ]
    df = df[df['Amount'].notna()]

    # Create matching key
    df['key'] = df['GSTIN'] + "_" + df['Invoice No']
    return df

@api_router.post("/gst/reconcile")
async def gst_reconcile(
    purchase_file: UploadFile = File(...),
    gstr2b_file: UploadFile = File(...)
) -> dict:
    try:
        purchase_bytes = await purchase_file.read()
        gstr2b_bytes = await gstr2b_file.read()

        df1 = pd.read_excel(io.BytesIO(purchase_bytes))
        df2 = pd.read_excel(io.BytesIO(gstr2b_bytes))

        # Check required columns
        required_cols = {'GSTIN', 'Invoice No', 'Amount'}
        for name, df in [("Purchase Register", df1), ("GSTR-2B", df2)]:
            missing_cols = required_cols - set(df.columns.str.strip())
            if missing_cols:
                raise HTTPException(
                    status_code=400,
                    detail=f"{name} is missing columns: {', '.join(missing_cols)}"
                )

        df1 = clean_dataframe(df1)
        df2 = clean_dataframe(df2)

        # Merge (inner join on key)
        merged = pd.merge(df1, df2, on='key', how='inner', suffixes=('_purchase', '_2B'))

        # Mismatch: amount difference > 1
        mismatch = merged[abs(merged['Amount_purchase'] - merged['Amount_2B']) > 1].copy()

        # Missing in 2B (purchase records not matched)
        matched_keys = merged['key']
        missing_in_2b = df1[~df1['key'].isin(matched_keys)].copy()

        # Missing in Purchase (2B records not matched)
        missing_in_purchase = df2[~df2['key'].isin(matched_keys)].copy()

        # Build response
        def safe_records(df, cols):
            records = df[cols].copy()
            records = records.replace({np.nan: None})
            return records.to_dict(orient='records')

        matched_list = safe_records(merged, ['GSTIN_purchase', 'Invoice No_purchase', 'Amount_purchase', 'Amount_2B'])
        missing_2b_list = safe_records(missing_in_2b, ['GSTIN', 'Invoice No', 'Amount'])
        missing_purchase_list = safe_records(missing_in_purchase, ['GSTIN', 'Invoice No', 'Amount'])

        mismatch_list = []
        if not mismatch.empty:
            mismatch['Difference'] = mismatch['Amount_purchase'] - mismatch['Amount_2B']
            mismatch_list = safe_records(mismatch, ['GSTIN_purchase', 'Invoice No_purchase', 'Amount_purchase', 'Amount_2B', 'Difference'])

        return {
            "matched_count": len(merged) - len(mismatch),
            "missing_in_2b_count": len(missing_in_2b),
            "missing_in_purchase_count": len(missing_in_purchase),
            "mismatch_count": len(mismatch),
            "matched": matched_list,
            "missing_in_2b": missing_2b_list,
            "missing_in_purchase": missing_purchase_list,
            "mismatched": mismatch_list,
            "purchase_total_rows": len(df1),
            "gstr2b_total_rows": len(df2)
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Reconciliation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/gst/export")
async def gst_export(
    purchase_file: UploadFile = File(...),
    gstr2b_file: UploadFile = File(...)
) -> StreamingResponse:
    """Export reconciliation results as Excel."""
    purchase_bytes = await purchase_file.read()
    gstr2b_bytes = await gstr2b_file.read()

    df1 = pd.read_excel(io.BytesIO(purchase_bytes))
    df2 = pd.read_excel(io.BytesIO(gstr2b_bytes))

    df1 = clean_dataframe(df1)
    df2 = clean_dataframe(df2)

    merged = pd.merge(df1, df2, on='key', how='inner', suffixes=('_purchase', '_2B'))
    mismatch = merged[abs(merged['Amount_purchase'] - merged['Amount_2B']) > 1].copy()
    matched_keys = merged['key']
    missing_in_2b = df1[~df1['key'].isin(matched_keys)].copy()
    missing_in_purchase = df2[~df2['key'].isin(matched_keys)].copy()

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if not merged.empty:
            merged[['GSTIN_purchase', 'Invoice No_purchase', 'Amount_purchase', 'Amount_2B']].to_excel(
                writer, sheet_name='Matched', index=False
            )
        if not missing_in_2b.empty:
            missing_in_2b[['GSTIN', 'Invoice No', 'Amount']].to_excel(
                writer, sheet_name='Missing in 2B', index=False
            )
        if not missing_in_purchase.empty:
            missing_in_purchase[['GSTIN', 'Invoice No', 'Amount']].to_excel(
                writer, sheet_name='Missing in Purchase', index=False
            )
        if not mismatch.empty:
            mismatch['Difference'] = mismatch['Amount_purchase'] - mismatch['Amount_2B']
            mismatch[['GSTIN_purchase', 'Invoice No_purchase', 'Amount_purchase', 'Amount_2B', 'Difference']].to_excel(
                writer, sheet_name='Mismatched', index=False
            )

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=reconciliation_report.xlsx"}
    )

# ============ SEED DATA ============

@api_router.post("/seed")
async def seed_data() -> dict:
    count = await db.clients.count_documents({})
    if count > 0:
        return {"message": "Data already seeded", "count": count}

    today = date.today()
    sample_clients = [
        {"id": str(uuid.uuid4()), "client_name": "Reliance Industries", "status": "Pending", "due_date": str(today.replace(day=min(today.day + 1, 28))), "last_updated": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "client_name": "Tata Motors", "status": "Completed", "due_date": str(today.replace(day=max(today.day - 5, 1))), "last_updated": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "client_name": "Infosys Ltd", "status": "Pending", "due_date": str(today), "last_updated": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "client_name": "Wipro Technologies", "status": "Pending", "due_date": str(today.replace(day=max(today.day - 2, 1))), "last_updated": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "client_name": "HCL Technologies", "status": "Completed", "due_date": str(today.replace(day=min(today.day + 5, 28))), "last_updated": datetime.now(timezone.utc).isoformat()},
    ]
    await db.clients.insert_many(sample_clients)
    return {"message": "Seeded 5 clients", "count": 5}

# ============ APP SETUP ============

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger: logging.Logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client() -> None:
    client.close()

