import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 1. Connect to Supabase using Environment Variables
# These must be set in the Render Dashboard under 'Environment'
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_KEY environment variables are missing.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Raje Construction ERP API")
origins = [
    "http://127.0.0.1:5500",                   # Local development
    "http://localhost:5500",
    "https://chic-vacherin-b8782a.netlify.app" # Your live Netlify site
]
# 2. Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. DATA MODELS ---

class Panchayath(BaseModel):
    name: str

class WorkCreate(BaseModel):
    panchayath_id: int
    name: str
    deal_amount: float

class StatusUpdate(BaseModel):
    status: str

class AgreementCreate(BaseModel):
    work_id: int
    tender_amount: float
    emd_amount: float
    selection_notice_received: bool
    selection_notice_date: Optional[str] = None
    supervision_amount: float
    supervision_cert_received: bool
    stamp_amount: float
    security_amount: float
    security_period: int
    security_closing_date: Optional[str] = None
    insurance_amount: float
    site_number: str
    site_handover_date: str

class Labourer(BaseModel):
    work_id: int
    name: str
    daily_wage: float

class AttendanceLog(BaseModel):
    work_id: int
    labourer_id: int
    date: str
    present: bool    

class LabourCash(BaseModel):
    work_id: int
    labourer_id: int
    type: str # 'Advance' or 'Settlement'
    amount: float
    date: str
    note: Optional[str] = None

class MaterialLog(BaseModel):
    work_id: int
    name: str
    amount: float
    date: str
    note: Optional[str] = None

# --- ADD THIS MODEL AT THE TOP WITH YOUR OTHER MODELS ---
class DieselLog(BaseModel):
    work_id: int
    vehicle_name: str
    amount: float
    date: str
    note: Optional[str] = None

class FinishWork(BaseModel):
    quoted_amount: float
    gst_amount: float
    final_bill_amount: float

# --- 4. HELPER: THE LIVE SUBTRACTION ---
def subtract_from_balance(work_id: int, expense_amount: float):
    # Fetch current amount from database
    work = supabase.table("works").select("current_amount").eq("id", work_id).single().execute()
    # Subtract expense from balance
    new_balance = float(work.data['current_amount']) - expense_amount
    # Update work record with new balance
    supabase.table("works").update({"current_amount": new_balance}).eq("id", work_id).execute()
    return new_balance

# --- 5. ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "Raje Construction API Online"}

# PANCHAYATHS
@app.get("/panchayaths")
def get_all_panchayaths():
    response = supabase.table("panchayaths").select("*").execute()
    return response.data

@app.post("/panchayaths")
def add_panchayath(panchayath: Panchayath):
    response = supabase.table("panchayaths").insert({"name": panchayath.name}).execute()
    return response.data

# WORKS LIST (By Panchayath)
@app.get("/works/{panchayath_id}")
def get_works_by_panchayath(panchayath_id: int):
    response = supabase.table("works").select("*").eq("panchayath_id", panchayath_id).execute()
    return response.data

# WORK DETAIL (Single Project)
@app.get("/works/detail/{work_id}")
def get_work_detail(work_id: int):
    response = supabase.table("works").select("*").eq("id", work_id).single().execute()
    return response.data

@app.post("/works")
def add_new_work(work: WorkCreate):
    # Set current_amount equal to deal_amount initially
    new_work_data = {
        "panchayath_id": work.panchayath_id,
        "name": work.name,
        "deal_amount": work.deal_amount,
        "current_amount": work.deal_amount, 
        "status": "PENDING"
    }
    response = supabase.table("works").insert(new_work_data).execute()
    return response.data

@app.patch("/works/{work_id}/status")
def update_status(work_id: int, data: StatusUpdate):
    response = supabase.table("works").update({"status": data.status}).eq("id", work_id).execute()
    return response.data

# AGREEMENTS & INITIALIZATION
@app.post("/agreements")
def create_agreement(agreement: AgreementCreate):
    response = supabase.table("agreements").insert(agreement.dict()).execute()
    # Auto-initialize work
    supabase.table("works").update({"status": "INITIALIZED"}).eq("id", agreement.work_id).execute()
    return response.data

# MATERIALS (With Live Subtraction)
# --- ADD THIS NEW ENDPOINT ---
@app.get("/materials/{work_id}")
def get_materials_by_work(work_id: int):
    response = supabase.table("materials").select("*").eq("work_id", work_id).execute()
    return response.data

@app.post("/materials")
def add_material(item: MaterialLog):
    response = supabase.table("materials").insert(item.dict()).execute()
    new_bal = subtract_from_balance(item.work_id, item.amount) # Trigger subtraction
    return {"message": "Material logged", "current_balance": new_bal}

@app.get("/diesel/{work_id}")
def get_diesel_by_work(work_id: int):
    response = supabase.table("diesel").select("*").eq("work_id", work_id).execute()
    return response.data

@app.post("/diesel")
def add_diesel(item: DieselLog):
    response = supabase.table("diesel").insert(item.dict()).execute()
    new_bal = subtract_from_balance(item.work_id, item.amount) # Trigger subtraction
    return {"message": "Diesel logged", "current_balance": new_bal}


   
# LABOUR CASH (With Live Subtraction)

# --- ENDPOINTS ---

# 1. Get all labourers for a project
@app.get("/labourers/{work_id}")
def get_labourers(work_id: int):
    return supabase.table("labourers").select("*").eq("work_id", work_id).execute().data

# 2. Add a new labourer to the roster
@app.post("/labourers")
def add_labourer(item: Labourer):
    return supabase.table("labourers").insert(item.dict()).execute()

# 3. Log cash payment (and subtract from live balance)
@app.post("/labour-cash")
def add_labour_cash(item: LabourCash):
    response = supabase.table("labour_cash").insert(item.dict()).execute()
    # Subtract from the main work balance
    subtract_from_balance(item.work_id, item.amount)
    return response.data

@app.get("/labour-cash/{work_id}")
def get_labour_cash_history(work_id: int):
    try:
        response = supabase.table("labour_cash").select("*").eq("work_id", work_id).execute()
        return response.data if response.data else [] # Return empty list if no data
    except Exception as e:
        print(f"Error fetching cash: {e}")
        return []

@app.get("/attendance/{work_id}")
def get_attendance(work_id: int):
    try:
        response = supabase.table("attendance").select("*").eq("work_id", work_id).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching attendance: {e}")
        return []

# 2. Mark attendance
@app.post("/attendance")
def mark_attendance(item: AttendanceLog):
    return supabase.table("attendance").insert(item.dict()).execute()

# FINISH & PROFIT MATH
@app.post("/works/{work_id}/finish")
def finish_work(work_id: int, data: FinishWork):
    work = supabase.table("works").select("current_amount", "deal_amount").eq("id", work_id).single().execute()
    current_card_amount = float(work.data['current_amount'])
    deal_amount = float(work.data['deal_amount'])

    # Profit logic: Adjustment + remaining balance
    adjustment = data.final_bill_amount - deal_amount
    final_profit = current_card_amount + adjustment 

    update_data = {
        "quoted_amount": data.quoted_amount,
        "gst_amount": data.gst_amount,
        "final_bill_amount": data.final_bill_amount,
        "status": "FINISHED"
    }
    supabase.table("works").update(update_data).eq("id", work_id).execute()

    return {"status": "FINISHED", "final_profit": final_profit}