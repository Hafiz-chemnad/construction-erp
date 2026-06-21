import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_KEY environment variables are missing.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Raje Construction ERP API")

origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://chic-vacherin-b8782a.netlify.app",
    "https://rococo-kulfi-69d6d2.netlify.app",
    "https://raysconstruction.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MODELS ────────────────────────────────────────────────────────────────────

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
    security_deposit_type: str = "Treasury FD"
    security_period: int
    security_closing_date: Optional[str] = None
    insurance_amount: float
    site_number: str
    site_handover_date: str

class AgreementUpdate(BaseModel):
    tender_amount: Optional[float] = None
    emd_amount: Optional[float] = None
    selection_notice_received: Optional[bool] = None
    selection_notice_date: Optional[str] = None
    supervision_amount: Optional[float] = None
    supervision_cert_received: Optional[bool] = None
    stamp_amount: Optional[float] = None
    security_amount: Optional[float] = None
    security_deposit_type: Optional[str] = None
    security_period: Optional[int] = None
    security_closing_date: Optional[str] = None
    insurance_amount: Optional[float] = None
    site_number: Optional[str] = None
    site_handover_date: Optional[str] = None

class Labourer(BaseModel):
    work_id: int
    name: str
    wage_type_1: float
    wage_type_2: float

class LabourerUpdate(BaseModel):
    name: Optional[str] = None
    wage_type_1: Optional[float] = None
    wage_type_2: Optional[float] = None

class AttendanceLog(BaseModel):
    work_id: int
    labourer_id: int
    date: str
    present: bool
    wage_used: float

class LabourCash(BaseModel):
    work_id: int
    labourer_id: int
    type: str
    amount: float
    date: str
    note: Optional[str] = None

class LabourCashUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[str] = None
    note: Optional[str] = None
    date: Optional[str] = None

class MaterialLog(BaseModel):
    work_id: int
    name: str
    amount: float
    date: str
    note: Optional[str] = None

class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[str] = None
    note: Optional[str] = None

class DieselLog(BaseModel):
    work_id: int
    vehicle_name: str
    amount: float
    # FIX: litres is optional — strip it before insert if the DB column doesn't exist
    litres: Optional[float] = None
    date: str
    note: Optional[str] = None

class DieselUpdate(BaseModel):
    vehicle_name: Optional[str] = None
    amount: Optional[float] = None
    litres: Optional[float] = None
    date: Optional[str] = None
    note: Optional[str] = None

class FinishWork(BaseModel):
    quoted_amount: float
    gst_amount: float
    final_bill_amount: float


# ═══════════════════════════════════════════════════════════════════
#  main.py — VEHICLE MODULE v2 (REPLACE previous vehicle additions)
#  Replace everything after the "── VEHICLE MODELS ──" comment
#  in your main.py with this entire block
# ═══════════════════════════════════════════════════════════════════

# ── VEHICLE MODELS ────────────────────────────────────────────────

class VehicleCreate(BaseModel):
    company:     str
    type:        str
    name:        str
    reg_number:  Optional[str]  = None
    driver_name: Optional[str]  = None

class VehicleUpdate(BaseModel):
    name:        Optional[str]  = None
    reg_number:  Optional[str]  = None
    driver_name: Optional[str]  = None
    is_active:   Optional[bool] = None

class VehicleLogBase(BaseModel):
    vehicle_id: int
    date: str
    site: Optional[str] = None
    driver_name: Optional[str] = None
    item: Optional[str] = None
    party_name: Optional[str] = None
    party_qty: float = 0
    base_price: float = 0
    total_price: float = 0
    vehicle_rent: float = 0
    total_amount: float = 0
    thoofan_giving_balance: float = 0
    final_balance: float = 0
    byhand_amount: float = 0
    load_qty: float = 0
    trip_rate: float = 0
    trip_amount: float = 0
    total_trip_amount: float = 0
    diesel_amount: float = 0
    km: float = 0
    rto_amount: float = 0
    parts_name: Optional[str] = None
    parts_amount: float = 0
    service_amount: float = 0
    byhand_balance: float = 0
    trip_balance: float = 0
    advance: float = 0  # 🌟 ADD THIS LINE
    note: Optional[str] = None

class ThoofanLogCreate(VehicleLogBase):
    pass  # Ready for future Thoofan-specific fields

class RaysLogCreate(VehicleLogBase):
    pass  # Ready for future Rays-specific fields

class OtherLogCreate(VehicleLogBase):
    pass  # Ready for future Other-specific fields

class VehicleLogUpdate(BaseModel):
    date: Optional[str] = None
    site: Optional[str] = None
    driver_name: Optional[str] = None
    item: Optional[str] = None
    party_name: Optional[str] = None
    party_qty: Optional[float] = None
    base_price: Optional[float] = None
    total_price: Optional[float] = None
    vehicle_rent: Optional[float] = None
    thoofan_giving_balance: Optional[float] = None
    final_balance: Optional[float] = None
    byhand_amount: Optional[float] = None
    load_qty: Optional[float] = None
    trip_rate: Optional[float] = None
    trip_amount: Optional[float] = None
    total_trip_amount: Optional[float] = None
    diesel_amount: Optional[float] = None
    km: Optional[float] = None
    rto_amount: Optional[float] = None
    parts_name: Optional[str] = None
    parts_amount: Optional[float] = None
    service_amount: Optional[float] = None
    byhand_balance: Optional[float] = None
    trip_balance: Optional[float] = None
    advance: float = 0  # 🌟 ADD THIS LINE
    note: Optional[str] = None
class RaysMachineLogCreate(BaseModel):
    vehicle_id:     int
    date:           str
    hours:          Optional[float] = None
    rate:           Optional[float] = None
    site:           Optional[str]   = None
    parts_name:     Optional[str]   = None
    parts_amount:   float           = 0
    service_amount: float           = 0
    note:           Optional[str]   = None

class ThoofanMachineLogCreate(BaseModel):
    vehicle_id:     int
    date:           str
    hours:          Optional[float] = None
    rate:           Optional[float] = None
    site:           Optional[str]   = None
    parts_name:     Optional[str]   = None
    parts_amount:   float           = 0
    service_amount: float           = 0
    note:           Optional[str]   = None    

class ThoofanMachineLogUpdate(BaseModel):
    date:           Optional[str]   = None
    hours:          Optional[float] = None
    rate:           Optional[float] = None
    site:           Optional[str]   = None
    parts_name:     Optional[str]   = None
    parts_amount:   Optional[float] = None
    service_amount: Optional[float] = None
    note:           Optional[str]   = None
# Driver salary — UPDATED with new fields
class DriverSalaryCreate(BaseModel):
    vehicle_id:      Optional[int]  = None
    driver_name:     str
    week_start:      str
    week_end:        str
    advance:         float          = 0     # advance already given
    byhand_balance:  float          = 0     # total cash by hand this week
    trip_balance:    float          = 0     # total trip earnings this week
    salary_balance:  float          = 0     # trip_balance − byhand − advance
    note:            Optional[str]  = None

class DriverSalaryUpdate(BaseModel):
    advance:        Optional[float] = None
    byhand_balance: Optional[float] = None
    trip_balance:   Optional[float] = None
    salary_balance: Optional[float] = None
    note:           Optional[str]   = None

# Vehicle parts ledger
class VehiclePartCreate(BaseModel):
    vehicle_id:   int
    name:         str
    qty:          Optional[float] = None
    base_price:   Optional[float] = None
    total_price:  Optional[float] = None
    vehicle_cost: Optional[float] = None
    date:         Optional[str]   = None
    note:         Optional[str]   = None



# ── HELPERS ───────────────────────────────────────────────────────────────────

def recalculate_balance(work_id: int):
    """
    Recompute current_amount from scratch.
    current_amount = deal_amount - SUM(materials) - SUM(diesel) - SUM(labour_cash)
    """
    work = supabase.table("works").select("deal_amount").eq("id", work_id).single().execute()
    deal = float(work.data["deal_amount"])

    mat_res = supabase.table("materials").select("amount").eq("work_id", work_id).execute()
    dsl_res = supabase.table("diesel").select("amount").eq("work_id", work_id).execute()
    csh_res = supabase.table("labour_cash").select("amount").eq("work_id", work_id).execute()

    mat_total = sum(float(r["amount"]) for r in (mat_res.data or []))
    dsl_total = sum(float(r["amount"]) for r in (dsl_res.data or []))
    csh_total = sum(float(r["amount"]) for r in (csh_res.data or []))

    new_balance = deal - mat_total - dsl_total - csh_total

    supabase.table("works").update({
        "current_amount": new_balance,
    }).eq("id", work_id).execute()

    return new_balance

# ── ROOT ──────────────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"message": "Raje Construction API Online"}

# ── PANCHAYATHS ───────────────────────────────────────────────────────────────

@app.get("/panchayaths")
def get_all_panchayaths():
    return supabase.table("panchayaths").select("*").order("created_at").execute().data

@app.post("/panchayaths")
def add_panchayath(p: Panchayath):
    return supabase.table("panchayaths").insert({"name": p.name}).execute().data

# ── WORKS ─────────────────────────────────────────────────────────────────────
# NOTE: /works/detail/{id} MUST be declared before /works/by-panchayath/{id}

@app.get("/works/detail/{work_id}")
def get_work_detail(work_id: int):
    res = supabase.table("works").select("*").eq("id", work_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Work not found")
    return res.data

@app.get("/works/by-panchayath/{panchayath_id}")
def get_works_by_panchayath(panchayath_id: int):
    return supabase.table("works").select("*").eq("panchayath_id", panchayath_id).order("created_at").execute().data

@app.post("/works")
def add_new_work(work: WorkCreate):
    if work.deal_amount <= 0:
        raise HTTPException(status_code=400, detail="Deal amount must be positive")
    data = {
        "panchayath_id": work.panchayath_id,
        "name": work.name,
        "deal_amount": work.deal_amount,
        "current_amount": work.deal_amount,
        "status": "PENDING",
    }
    return supabase.table("works").insert(data).execute().data

@app.patch("/works/{work_id}/status")
def update_status(work_id: int, data: StatusUpdate):
    return supabase.table("works").update({"status": data.status}).eq("id", work_id).execute().data

# ── AGREEMENTS ────────────────────────────────────────────────────────────────

@app.post("/agreements")
def create_agreement(agreement: AgreementCreate):
    res = supabase.table("agreements").insert(agreement.dict()).execute()
    supabase.table("works").update({"status": "INITIALIZED"}).eq("id", agreement.work_id).execute()
    return res.data

@app.get("/agreements/by-work/{work_id}")
def get_agreement_by_work(work_id: int):
    res = supabase.table("agreements").select("*").eq("work_id", work_id).execute()
    if not res.data:
        return None
    return res.data[0]

@app.patch("/agreements/{agreement_id}")
def update_agreement(agreement_id: int, data: AgreementUpdate):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    return supabase.table("agreements").update(update_data).eq("id", agreement_id).execute().data

# ── MATERIALS ─────────────────────────────────────────────────────────────────

@app.get("/materials/{work_id}")
def get_materials_by_work(work_id: int):
    return supabase.table("materials").select("*").eq("work_id", work_id).order("date", desc=True).execute().data

@app.post("/materials")
def add_material(item: MaterialLog):
    if item.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    # Strip None values — only send columns that actually exist in the table
    data = {k: v for k, v in item.dict().items() if v is not None}
    supabase.table("materials").insert(data).execute()
    new_bal = recalculate_balance(item.work_id)
    return {"message": "Material logged", "current_balance": new_bal}

@app.patch("/materials/{material_id}")
def update_material(material_id: int, data: MaterialUpdate):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    res = supabase.table("materials").update(update_data).eq("id", material_id).execute()
    mat = supabase.table("materials").select("work_id").eq("id", material_id).single().execute()
    if mat.data:
        recalculate_balance(mat.data["work_id"])
    return res.data

@app.delete("/materials/{material_id}")
def delete_material(material_id: int):
    mat = supabase.table("materials").select("work_id").eq("id", material_id).single().execute()
    work_id = mat.data["work_id"] if mat.data else None
    supabase.table("materials").delete().eq("id", material_id).execute()
    if work_id:
        recalculate_balance(work_id)
    return {"deleted": True}

# ── DIESEL ────────────────────────────────────────────────────────────────────

# Columns that actually exist in the 'diesel' table (from DB schema screenshot):
# id, work_id, vehicle_name, amount, date, note, created_at
# The 'litres' column does NOT exist — it only exists in 'diesel_expenses'.
# FIX: Always exclude 'litres' from inserts/updates to the 'diesel' table.
DIESEL_TABLE_COLUMNS = {"work_id", "vehicle_name", "amount", "date", "note"}

@app.get("/diesel/{work_id}")
def get_diesel_by_work(work_id: int):
    return supabase.table("diesel").select("*").eq("work_id", work_id).order("date", desc=True).execute().data

@app.post("/diesel")
def add_diesel(item: DieselLog):
    if item.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    # FIX: Only insert columns that exist in the diesel table.
    # item.dict() would include 'litres' which crashes with PGRST204.
    data = {k: v for k, v in item.dict().items() if k in DIESEL_TABLE_COLUMNS and v is not None}
    supabase.table("diesel").insert(data).execute()
    new_bal = recalculate_balance(item.work_id)
    return {"message": "Diesel logged", "current_balance": new_bal}

@app.patch("/diesel/{diesel_id}")
def update_diesel(diesel_id: int, data: DieselUpdate):
    # FIX: Same — strip litres and any None values before sending to DB
    update_data = {
        k: v for k, v in data.dict().items()
        if v is not None and k in DIESEL_TABLE_COLUMNS
    }
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    res = supabase.table("diesel").update(update_data).eq("id", diesel_id).execute()
    dsl = supabase.table("diesel").select("work_id").eq("id", diesel_id).single().execute()
    if dsl.data:
        recalculate_balance(dsl.data["work_id"])
    return res.data

@app.delete("/diesel/{diesel_id}")
def delete_diesel(diesel_id: int):
    dsl = supabase.table("diesel").select("work_id").eq("id", diesel_id).single().execute()
    work_id = dsl.data["work_id"] if dsl.data else None
    supabase.table("diesel").delete().eq("id", diesel_id).execute()
    if work_id:
        recalculate_balance(work_id)
    return {"deleted": True}

# ── LABOURERS ─────────────────────────────────────────────────────────────────

@app.get("/labourers/{work_id}")
def get_labourers(work_id: int):
    return supabase.table("labourers").select("*").eq("work_id", work_id).order("name").execute().data

@app.post("/labourers")
def add_labourer(item: Labourer):
    # labourers table has: work_id, name, daily_wage
    # Map wage_type_1 → daily_wage
    data = {
        "work_id": item.work_id,
        "name": item.name,
        "daily_wage": item.wage_type_1,
    }
    return supabase.table("labourers").insert(data).execute().data

@app.patch("/labourers/{labourer_id}")
def update_labourer(labourer_id: int, data: LabourerUpdate):
    update_data = {}
    if data.name is not None:
        update_data["name"] = data.name
    if data.wage_type_1 is not None:
        update_data["daily_wage"] = data.wage_type_1
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    return supabase.table("labourers").update(update_data).eq("id", labourer_id).execute().data

@app.delete("/labourers/{labourer_id}")
def delete_labourer(labourer_id: int):
    supabase.table("attendance").delete().eq("labourer_id", labourer_id).execute()
    supabase.table("labour_cash").delete().eq("labourer_id", labourer_id).execute()
    supabase.table("labourers").delete().eq("id", labourer_id).execute()
    return {"deleted": True}

# ── ATTENDANCE ────────────────────────────────────────────────────────────────

# Columns that exist in the 'attendance' table (from DB schema screenshot):
# id, labourer_id, work_id, date, present, created_at
# 'wage_used' does NOT exist in the table — it is stored in labourers.daily_wage
# FIX: Strip wage_used from attendance inserts. It is only used client-side for display.
ATTENDANCE_TABLE_COLUMNS = {"work_id", "labourer_id", "date", "present"}

@app.get("/attendance/{work_id}")
def get_attendance(work_id: int):
    try:
        return supabase.table("attendance").select("*").eq("work_id", work_id).execute().data or []
    except Exception as e:
        print(f"Error fetching attendance: {e}")
        return []

@app.post("/attendance")
def mark_attendance(item: AttendanceLog):
    # FIX: Only send columns that exist in the attendance table.
    # 'wage_used' caused the 500 → which browser showed as a CORS error.
    insert_data = {k: v for k, v in item.dict().items() if k in ATTENDANCE_TABLE_COLUMNS}

    existing = supabase.table("attendance") \
        .select("id") \
        .eq("labourer_id", item.labourer_id) \
        .eq("date", item.date) \
        .execute()

    if existing.data:
        return supabase.table("attendance") \
            .update({"present": item.present}) \
            .eq("id", existing.data[0]["id"]).execute().data

    return supabase.table("attendance").insert(insert_data).execute().data

@app.delete("/attendance/{attendance_id}")
def delete_attendance(attendance_id: int):
    supabase.table("attendance").delete().eq("id", attendance_id).execute()
    return {"deleted": True}

# ── LABOUR CASH ───────────────────────────────────────────────────────────────

@app.get("/labour-cash/{work_id}")
def get_labour_cash_history(work_id: int):
    try:
        return supabase.table("labour_cash").select("*").eq("work_id", work_id).order("date", desc=True).execute().data or []
    except Exception as e:
        print(f"Error fetching cash: {e}")
        return []

@app.post("/labour-cash")
def add_labour_cash(item: LabourCash):
    if item.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    # Strip None values before insert
    data = {k: v for k, v in item.dict().items() if v is not None}
    supabase.table("labour_cash").insert(data).execute()
    new_bal = recalculate_balance(item.work_id)
    return {"message": "Cash logged", "current_balance": new_bal}

@app.patch("/labour-cash/{cash_id}")
def update_labour_cash(cash_id: int, data: LabourCashUpdate):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    res = supabase.table("labour_cash").update(update_data).eq("id", cash_id).execute()
    csh = supabase.table("labour_cash").select("work_id").eq("id", cash_id).single().execute()
    if csh.data:
        recalculate_balance(csh.data["work_id"])
    return res.data

@app.delete("/labour-cash/{cash_id}")
def delete_labour_cash(cash_id: int):
    csh = supabase.table("labour_cash").select("work_id").eq("id", cash_id).single().execute()
    work_id = csh.data["work_id"] if csh.data else None
    supabase.table("labour_cash").delete().eq("id", cash_id).execute()
    if work_id:
        recalculate_balance(work_id)
    return {"deleted": True}

# ── FINISH WORK ───────────────────────────────────────────────────────────────

@app.post("/works/{work_id}/finish")
def finish_work(work_id: int, data: FinishWork):
    work = supabase.table("works").select("deal_amount, current_amount").eq("id", work_id).single().execute()
    if not work.data:
        raise HTTPException(status_code=404, detail="Work not found")

    deal_amount = float(work.data["deal_amount"])

    if data.final_bill_amount > deal_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Final bill ({data.final_bill_amount}) cannot exceed deal amount ({deal_amount})"
        )

    supabase.table("works").update({
        "quoted_amount":     data.quoted_amount,
        "gst_amount":        data.gst_amount,
        "final_bill_amount": data.final_bill_amount,
        "status":            "FINISHED",
    }).eq("id", work_id).execute()

    return {"status": "FINISHED", "final_bill_amount": data.final_bill_amount}

# ── VEHICLE REGISTRY ──────────────────────────────────────────────

@app.get("/vehicles")
def get_vehicles(company: str):
    return supabase.table("vehicles") \
        .select("*") \
        .eq("company", company) \
        .eq("is_active", True) \
        .order("type").order("name") \
        .execute().data

@app.post("/vehicles")
def add_vehicle(item: VehicleCreate):
    data = {k: v for k, v in item.dict().items() if v is not None}
    data["is_active"] = True
    return supabase.table("vehicles").insert(data).execute().data

@app.patch("/vehicles/{vehicle_id}")
def update_vehicle(vehicle_id: int, data: VehicleUpdate):
    upd = {k: v for k, v in data.dict().items() if v is not None}
    return supabase.table("vehicles").update(upd).eq("id", vehicle_id).execute().data

@app.delete("/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: int):
    supabase.table("vehicles").update({"is_active": False}).eq("id", vehicle_id).execute()
    return {"deleted": True}

UNIFIED_LOG_COLS = {
    "vehicle_id", "date", "site", "driver_name", "item", "party_name",
    "party_qty", "base_price", "total_price", "vehicle_rent", "total_amount",
    "thoofan_giving_balance", "final_balance", "byhand_amount", "load_qty",
    "trip_rate", "trip_amount", "total_trip_amount", "diesel_amount", "km",
    "rto_amount", "parts_name", "parts_amount", "service_amount",
    "byhand_balance", "trip_balance","advance","note"
}
# ── THOOFAN LOGS ──────────────────────────────────────────────────

THOOFAN_LOG_COLS = {
    "vehicle_id","date","hours","rate","site",
    "parts_name","parts_amount","service_amount","note"
}

@app.get("/vehicle-logs/thoofan/{vehicle_id}")
def get_thoofan_logs(vehicle_id: int):
    return supabase.table("thoofan_logs") \
        .select("*").eq("vehicle_id", vehicle_id) \
        .order("date", desc=True).execute().data

@app.post("/vehicle-logs/thoofan")
def add_thoofan_log(item: ThoofanLogCreate):
    data = {k: v for k, v in item.dict().items()
            if k in UNIFIED_LOG_COLS and v is not None}
    data.pop("total_amount", None)         
    return supabase.table("thoofan_logs").insert(data).execute().data

@app.delete("/vehicle-logs/thoofan/{log_id}")
def delete_thoofan_log(log_id: int):
    supabase.table("thoofan_logs").delete().eq("id", log_id).execute()
    return {"deleted": True}

THOOFAN_MACHINE_COLS = {
    "vehicle_id","date","hours","rate","site",
    "parts_name","parts_amount","service_amount","note"
}

@app.get("/thoofan/machine-logs/{vehicle_id}")
def get_thoofan_machine_logs(vehicle_id: int):
    return supabase.table("thoofan_machine_logs") \
        .select("*").eq("vehicle_id", vehicle_id) \
        .order("date", desc=True).execute().data

@app.post("/thoofan/machine-logs")
def add_thoofan_machine_log(item: ThoofanMachineLogCreate):
    data = {k: v for k, v in item.dict().items()
            if k in THOOFAN_MACHINE_COLS and v is not None}
    return supabase.table("thoofan_machine_logs").insert(data).execute().data

@app.delete("/thoofan/machine-logs/{log_id}")
def delete_thoofan_machine_log(log_id: int):
    supabase.table("thoofan_machine_logs").delete().eq("id", log_id).execute()
    return {"deleted": True}

@app.patch("/thoofan/machine-logs/{log_id}")
def update_thoofan_machine_log(log_id: int, data: ThoofanMachineLogUpdate):
    # Only update fields that were actually sent
    upd = {k: v for k, v in data.dict().items() if v is not None}
    if not upd:
        return {"message": "Nothing to update"}
    return supabase.table("thoofan_machine_logs").update(upd).eq("id", log_id).execute().data
# ── OTHER COMPANY LOGS ────────────────────────────────────────────

OTHER_LOG_COLS = {
    "vehicle_id","date","hours","rate","site",
    "parts_name","parts_amount","service_amount","note"
}
@app.patch("/vehicle-logs/thoofan/{log_id}")
def update_thoofan_log(log_id: int, data: VehicleLogUpdate):
    upd = {k: v for k, v in data.dict().items() if v is not None and k in UNIFIED_LOG_COLS}
    upd.pop("total_amount", None) # Prevent Supabase crash
    return supabase.table("thoofan_logs").update(upd).eq("id", log_id).execute().data

@app.patch("/vehicle-logs/other/{log_id}")
def update_other_log(log_id: int, data: VehicleLogUpdate):
    upd = {k: v for k, v in data.dict().items() if v is not None and k in UNIFIED_LOG_COLS}
    upd.pop("total_amount", None) # Prevent Supabase crash
    return supabase.table("other_vehicle_logs").update(upd).eq("id", log_id).execute().data

@app.patch("/rays/vehicle-logs/{log_id}")
def update_rays_vehicle_log(log_id: int, data: VehicleLogUpdate):
    upd = {k: v for k, v in data.dict().items() if v is not None and k in UNIFIED_LOG_COLS}
    upd.pop("total_amount", None) # Prevent Supabase crash
    return supabase.table("rays_vehicle_logs").update(upd).eq("id", log_id).execute().data

@app.get("/vehicle-logs/other/{vehicle_id}")
def get_other_logs(vehicle_id: int):
    return supabase.table("other_vehicle_logs") \
        .select("*").eq("vehicle_id", vehicle_id) \
        .order("date", desc=True).execute().data

@app.post("/vehicle-logs/other")
def add_other_log(item: OtherLogCreate):
    data = {k: v for k, v in item.dict().items()
            if k in UNIFIED_LOG_COLS and v is not None}
    data.pop("total_amount", None)        
    return supabase.table("other_vehicle_logs").insert(data).execute().data

@app.delete("/vehicle-logs/other/{log_id}")
def delete_other_log(log_id: int):
    supabase.table("other_vehicle_logs").delete().eq("id", log_id).execute()
    return {"deleted": True}


# ── RAYS VEHICLE TRIP LOGS ────────────────────────────────────────

RAYS_VEHICLE_COLS = {
    "vehicle_id","date","driver_name","items","site",
    "load_qty","trip_rate","trip_amount","total_trip_amount",
    "diesel_amount","km","rto_amount",
    "parts_name","parts_amount","service_amount",
    "byhand_balance","trip_balance","note"
}

@app.get("/rays/vehicle-logs/{vehicle_id}")
def get_rays_vehicle_logs(vehicle_id: int):
    return supabase.table("rays_vehicle_logs") \
        .select("*").eq("vehicle_id", vehicle_id) \
        .order("date", desc=True).execute().data

@app.post("/rays/vehicle-logs")
def add_rays_vehicle_log(item: RaysLogCreate):
    d = item.dict()
    # Auto-calculate trip_balance server-side as well (safety check)
    d["trip_balance"] = d.get("byhand_balance", 0) - d.get("vehicle_rent", 0)
    data = {k: v for k, v in d.items()
            if k in UNIFIED_LOG_COLS and v is not None}
    data.pop("total_amount", None)        
    return supabase.table("rays_vehicle_logs").insert(data).execute().data

@app.delete("/rays/vehicle-logs/{log_id}")
def delete_rays_vehicle_log(log_id: int):
    supabase.table("rays_vehicle_logs").delete().eq("id", log_id).execute()
    return {"deleted": True}


# ── RAYS MACHINE LOGS ─────────────────────────────────────────────

RAYS_MACHINE_COLS = {
    "vehicle_id","date","hours","rate","site",
    "parts_name","parts_amount","service_amount","note"
}

@app.get("/rays/machine-logs/{vehicle_id}")
def get_rays_machine_logs(vehicle_id: int):
    return supabase.table("rays_machine_logs") \
        .select("*").eq("vehicle_id", vehicle_id) \
        .order("date", desc=True).execute().data

@app.post("/rays/machine-logs")
def add_rays_machine_log(item: RaysMachineLogCreate):
    data = {k: v for k, v in item.dict().items()
            if k in RAYS_MACHINE_COLS and v is not None}
    return supabase.table("rays_machine_logs").insert(data).execute().data

@app.delete("/rays/machine-logs/{log_id}")
def delete_rays_machine_log(log_id: int):
    supabase.table("rays_machine_logs").delete().eq("id", log_id).execute()
    return {"deleted": True}


# ── DRIVER SALARY ─────────────────────────────────────────────────

SALARY_COLS = {
    "vehicle_id","driver_name","week_start","week_end",
    "advance","byhand_balance","trip_balance","salary_balance","note"
}
@app.get("/driver-salary-global")
def get_global_driver_salary():
    return supabase.table("driver_salary") \
        .select("*") \
        .order("week_start", desc=True).execute().data

@app.get("/driver-salary/{vehicle_id}")
def get_driver_salary(vehicle_id: int):
    return supabase.table("driver_salary") \
        .select("*").eq("vehicle_id", vehicle_id) \
        .order("week_start", desc=True).execute().data

@app.post("/driver-salary")
def add_driver_salary(item: DriverSalaryCreate):
    # Auto-calculate salary_balance server-side
    d = item.dict()
    d["salary_balance"] = d.get("trip_balance", 0) - d.get("advance", 0)
    data = {k: v for k, v in d.items()
            if k in SALARY_COLS and v is not None}
    return supabase.table("driver_salary").insert(data).execute().data

@app.patch("/driver-salary/{salary_id}")
def update_driver_salary(salary_id: int, data: DriverSalaryUpdate):
    upd = {k: v for k, v in data.dict().items() if v is not None}
    # Recalculate salary_balance if any component changed
    if upd:
        existing = supabase.table("driver_salary") \
            .select("trip_balance,byhand_balance,advance") \
            .eq("id", salary_id).single().execute()
        if existing.data:
            trip    = upd.get("trip_balance",   existing.data.get("trip_balance",   0))
            byhand  = upd.get("byhand_balance", existing.data.get("byhand_balance", 0))
            advance = upd.get("advance",        existing.data.get("advance",        0))
            upd["salary_balance"] = (trip or 0) - (byhand or 0) - (advance or 0)
    return supabase.table("driver_salary").update(upd).eq("id", salary_id).execute().data

@app.delete("/driver-salary/{salary_id}")
def delete_driver_salary(salary_id: int):
    supabase.table("driver_salary").delete().eq("id", salary_id).execute()
    return {"deleted": True}

@app.get("/drivers/active")
def get_active_drivers():
    # Fetch driver names from all 3 log tables
    rays = supabase.table("rays_vehicle_logs").select("driver_name").execute()
    thoofan = supabase.table("thoofan_logs").select("driver_name").execute()
    other = supabase.table("other_vehicle_logs").select("driver_name").execute()

    # Use a 'set' to automatically remove any duplicates!
    unique_drivers = set()
    for row in (rays.data or []) + (thoofan.data or []) + (other.data or []):
        name = row.get("driver_name")
        if name and str(name).strip():
            unique_drivers.add(str(name).strip())
            
    # Return a perfectly alphabetized list
    return sorted(list(unique_drivers))
# ── VEHICLE PARTS LEDGER ──────────────────────────────────────────

PARTS_COLS = {
    "vehicle_id","name","qty","base_price","total_price","vehicle_cost","date","note"
}

@app.get("/vehicle-parts/{vehicle_id}")
def get_vehicle_parts(vehicle_id: int):
    return supabase.table("vehicle_parts") \
        .select("*").eq("vehicle_id", vehicle_id) \
        .order("date", desc=True).execute().data

@app.post("/vehicle-parts")
def add_vehicle_part(item: VehiclePartCreate):
    d = item.dict()
    # Auto-calculate total_price = qty × base_price if not provided
    if not d.get("total_price") and d.get("qty") and d.get("base_price"):
        d["total_price"] = d["qty"] * d["base_price"]
    data = {k: v for k, v in d.items() if k in PARTS_COLS and v is not None}
    return supabase.table("vehicle_parts").insert(data).execute().data

@app.delete("/vehicle-parts/{part_id}")
def delete_vehicle_part(part_id: int):
    supabase.table("vehicle_parts").delete().eq("id", part_id).execute()
    return {"deleted": True}

# ── REPORTS & LEDGERS ─────────────────────────────────────────────

@app.get("/reports/check-logs")
def check_driver_logs(driver: str = "", start_date: str = "2000-01-01", end_date: str = "2100-01-01"):
    search_term = f"%{driver}%"

    rays = supabase.table("rays_vehicle_logs").select("thoofan_giving_balance, byhand_amount, final_balance, advance") \
        .ilike("driver_name", search_term).gte("date", start_date).lte("date", end_date).execute()

    # 🌟 FIXED: Added "final_balance" and "thoofan_giving_balance" to the Thoofan search query
    thoofan = supabase.table("thoofan_logs").select("thoofan_giving_balance, byhand_amount, final_balance, advance") \
        .ilike("driver_name", search_term).gte("date", start_date).lte("date", end_date).execute()

    other = supabase.table("other_vehicle_logs").select("thoofan_giving_balance, byhand_amount, final_balance, advance") \
        .ilike("driver_name", search_term).gte("date", start_date).lte("date", end_date).execute()

    # 1. ADVANCE (Includes ALL Three)
    total_advance = (
        sum(float(r.get("advance") or 0) for r in rays.data or []) +
        sum(float(r.get("advance") or 0) for r in thoofan.data or []) +
        sum(float(r.get("advance") or 0) for r in other.data or [])
    )

    # 2. THOOFAN GIVING AMOUNT (Only Rays + Other) - Excludes Thoofan's own logs
    total_thoofan_giving = (
        sum(float(r.get("thoofan_giving_balance") or 0) for r in rays.data or []) +
        sum(float(r.get("thoofan_giving_balance") or 0) for r in other.data or [])
    )

    # 3. BY HAND GIVEN (Includes ALL Three)
    total_byhand_given = (
        sum(float(r.get("byhand_amount") or 0) for r in rays.data or []) +
        sum(float(r.get("byhand_amount") or 0) for r in thoofan.data or []) +
        sum(float(r.get("byhand_amount") or 0) for r in other.data or [])
    )

    # 🌟 FIXED: 4. FINAL BALANCE (Includes ALL Three)
    total_final_balance = (
        sum(float(r.get("final_balance") or 0) for r in rays.data or []) +
        sum(float(r.get("final_balance") or 0) for r in thoofan.data or []) +
        sum(float(r.get("final_balance") or 0) for r in other.data or [])
    )

    return {
        "driver": driver,
        "total_advance": total_advance,
        "total_thoofan_giving": total_thoofan_giving,
        "total_byhand_given": total_byhand_given,
        "total_final_balance": total_final_balance
    }
     
@app.get("/reports/global-driver-trips")
def get_global_driver_trips(driver: str, start_date: str, end_date: str):
    search_term = f"%{driver}%"

    rays = supabase.table("rays_vehicle_logs").select("total_trip_amount, advance, byhand_balance") \
        .ilike("driver_name", search_term).gte("date", start_date).lte("date", end_date).execute()

    thoofan = supabase.table("thoofan_logs").select("total_trip_amount, advance, byhand_balance") \
        .ilike("driver_name", search_term).gte("date", start_date).lte("date", end_date).execute()

    other = supabase.table("other_vehicle_logs").select("total_trip_amount, advance, byhand_balance") \
        .ilike("driver_name", search_term).gte("date", start_date).lte("date", end_date).execute()

    all_trips = (rays.data or []) + (thoofan.data or []) + (other.data or [])

    total_earnings    = sum(float(t.get("total_trip_amount") or 0) for t in all_trips)
    total_advance     = sum(float(t.get("advance") or 0) for t in all_trips)
    total_byhand      = sum(float(t.get("byhand_balance") or 0) for t in all_trips)

    return {
        "driver": driver,
        "total_earnings": total_earnings,
        "total_advance": total_advance,
        "total_byhand": total_byhand
    }

    # ═══════════════════════════════════════════════════════════════════
#  BANKING & ACCOUNTING MODULE (FULL BACKEND)
# ═══════════════════════════════════════════════════════════════════

# ── 1. MODELS ──
class AccountCreate(BaseModel):
    name: str
    category: str  # 'BANK', 'TREASURY', 'TAX', 'LOAN'
    sub_type: str  # 'CURRENT', 'OD', 'GOLD_LOAN', 'FD', 'GST_CASH', 'GST_CREDIT', 'TDS'
    account_number: Optional[str] = None

class DailyBalanceCreate(BaseModel):
    account_name: str
    date: str
    balance: float
    note: Optional[str] = None

class DailyBalanceUpdate(BaseModel):
    balance: Optional[float] = None
    note: Optional[str] = None

class ODLogCreate(BaseModel):
    account_name: str
    date: str
    balance_amount: float = 0
    interest_amount: float = 0
    note: Optional[str] = None

class GoldLoanCreate(BaseModel):
    account_name: str
    opening_date: str
    closing_date: Optional[str] = None
    amount: float
    interest_amount: float = 0
    is_renewal: bool = False

class PurchaseBillCreate(BaseModel):
    work_id: int
    date: str
    purchase_amount: float = 0
    tax_amount: float = 0
    is_split_50_50: bool = False
    tds_deducted: float = 0
    sidko_charges: float = 0
    other_charges: float = 0
    note: Optional[str] = None

# ── 2. HELPER TO GET ACCOUNT ID BY NAME ──
def get_account_id(name: str):
    res = supabase.table("accounts").select("id").eq("name", name).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail=f"Account '{name}' not found")
    return res.data["id"]

# ── 3. ACCOUNTS ENDPOINTS (Dynamic Creation) ──
@app.post("/banking/accounts")
def create_account(data: AccountCreate):
    try:
        return supabase.table("accounts").insert(data.dict()).execute().data
    except Exception as e:
        # Catch duplicate name errors cleanly
        raise HTTPException(status_code=400, detail="An account with this name already exists or data is invalid.")

@app.get("/banking/accounts")
def get_accounts():
    return supabase.table("accounts").select("*").eq("is_active", True).order("created_at").execute().data

# ── 4. DAILY BALANCE ENDPOINTS (The Passbook) ──
@app.post("/banking/daily-balance")
def save_daily_balance(data: DailyBalanceCreate):
    acc_id = get_account_id(data.account_name)
    
    # Check if a balance for this exact day already exists
    existing = supabase.table("daily_balances").select("id").eq("account_id", acc_id).eq("date", data.date).execute()
    
    payload = {
        "account_id": acc_id,
        "date": data.date,
        "balance": data.balance,
        "note": data.note
    }

    if existing.data:
        # Update existing record
        return supabase.table("daily_balances").update(payload).eq("id", existing.data[0]["id"]).execute().data
    else:
        # Insert new record
        return supabase.table("daily_balances").insert(payload).execute().data

@app.get("/banking/opening-balance")
def get_opening_balance(account_name: str, target_date: str):
    """
    Magic Route: Finds the most recent closing balance BEFORE the selected date.
    """
    acc_id = get_account_id(account_name)
    
    # 1. Get the latest entry strictly BEFORE the target date (This is the Opening Balance)
    res = supabase.table("daily_balances") \
        .select("balance") \
        .eq("account_id", acc_id) \
        .lt("date", target_date) \
        .order("date", desc=True) \
        .limit(1) \
        .execute()
        
    opening_balance = float(res.data[0]["balance"]) if res.data else 0.0
    
    # 2. Check if they ALREADY typed a closing balance for the target_date itself
    today_res = supabase.table("daily_balances") \
        .select("balance") \
        .eq("account_id", acc_id) \
        .eq("date", target_date) \
        .execute()
        
    today_balance = float(today_res.data[0]["balance"]) if today_res.data else None
    
    return {
        "opening_balance": opening_balance,
        "saved_closing_balance": today_balance
    }

# ── 5. HISTORY, EDIT & DELETE (For Passbook) ──
@app.get("/banking/daily-balances/{account_name}")
def get_daily_balances_history(account_name: str):
    """Fetches the full passbook history for a specific account so the user can see past logs."""
    acc_id = get_account_id(account_name)
    return supabase.table("daily_balances") \
        .select("*") \
        .eq("account_id", acc_id) \
        .order("date", desc=True) \
        .execute().data

@app.patch("/banking/daily-balance/{log_id}")
def update_daily_balance(log_id: int, data: DailyBalanceUpdate):
    """Allows editing a specific log entry by its ID."""
    upd = {k: v for k, v in data.dict().items() if v is not None}
    if not upd:
        raise HTTPException(status_code=400, detail="Nothing to update")
    return supabase.table("daily_balances").update(upd).eq("id", log_id).execute().data

@app.delete("/banking/daily-balance/{log_id}")
def delete_daily_balance(log_id: int):
    """Deletes a specific passbook entry by its ID."""
    supabase.table("daily_balances").delete().eq("id", log_id).execute()
    return {"deleted": True}

# ── 6. LOAN ENDPOINTS (OD & Gold Loan) ──
@app.post("/banking/od-logs")
def add_od_log(data: ODLogCreate):
    acc_id = get_account_id(data.account_name)
    payload = data.dict()
    payload.pop("account_name")
    payload["account_id"] = acc_id
    return supabase.table("od_logs").insert(payload).execute().data

@app.post("/banking/gold-loans")
def add_gold_loan(data: GoldLoanCreate):
    acc_id = get_account_id(data.account_name)
    payload = data.dict()
    payload.pop("account_name")
    payload["account_id"] = acc_id
    return supabase.table("gold_loans").insert(payload).execute().data

# ── 7. TDS & PURCHASE BILLS ──
@app.post("/banking/purchase-bills")
def add_purchase_bill(data: PurchaseBillCreate):
    return supabase.table("purchase_bills").insert(data.dict()).execute().data

@app.get("/banking/purchase-bills")
def get_purchase_bills():
    # Joins with works table to get the project name
    return supabase.table("purchase_bills").select("*, works(name, panchayaths(name))").order("date", desc=True).execute().data

# ── 8. FD TOTALS (Linked to Agreements) ──
@app.get("/banking/fd-totals")
def get_fd_totals():
    """Calculates the total locked amount in Bank FDs vs Treasury FDs."""
    agreements = supabase.table("agreements").select("security_amount, security_deposit_type").execute()
    
    bank_fd = 0
    treasury_fd = 0
    
    for a in (agreements.data or []):
        amt = float(a.get("security_amount") or 0)
        dep_type = a.get("security_deposit_type")
        if dep_type == "Bank FD":
            bank_fd += amt
        elif dep_type == "Treasury FD":
            treasury_fd += amt
            
    return {"Bank FD": bank_fd, "Treasury FD": treasury_fd}