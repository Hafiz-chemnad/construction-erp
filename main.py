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


# ── VEHICLE MODELS ────────────────────────────────────────────────
 
class VehicleCreate(BaseModel):
    company:     str             # 'thoofan' | 'rays' | 'other'
    type:        str             # 'vehicle' | 'machine'
    name:        str
    reg_number:  Optional[str]  = None
    driver_name: Optional[str]  = None
 
class VehicleUpdate(BaseModel):
    name:        Optional[str]  = None
    reg_number:  Optional[str]  = None
    driver_name: Optional[str]  = None
    is_active:   Optional[bool] = None
 
# Thoofan / Other log (hours-based rent)
class VehicleLogCreate(BaseModel):
    vehicle_id:     int
    date:           str
    hours:          Optional[float] = None
    rate:           Optional[float] = None
    site:           Optional[str]   = None
    parts_name:     Optional[str]   = None
    parts_amount:   float           = 0
    service_amount: float           = 0
    note:           Optional[str]   = None
 
# Rays vehicle trip log
class RaysVehicleLogCreate(BaseModel):
    vehicle_id:     int
    date:           str
    driver_name:    Optional[str]   = None
    trip_salary:    float           = 0
    load_quantity:  Optional[str]   = None
    site:           Optional[str]   = None
    diesel_source:  Optional[str]   = None
    diesel_amount:  float           = 0
    rto_amount:     float           = 0
    parts_name:     Optional[str]   = None
    parts_amount:   float           = 0
    service_amount: float           = 0
    note:           Optional[str]   = None
 
# Rays machine log (same as thoofan log)
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
 
class DriverSalaryCreate(BaseModel):
    vehicle_id:  int
    driver_name: str
    week_start:  str
    week_end:    str
    amount:      float
    paid:        bool           = False
    note:        Optional[str]  = None
 
class DriverSalaryUpdate(BaseModel):
    paid:   Optional[bool]  = None
    amount: Optional[float] = None
    note:   Optional[str]   = None
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

# ── VEHICLE REGISTRY ROUTES ───────────────────────────────────────
 
@app.get("/vehicles")
def get_vehicles(company: str):
    return supabase.table("vehicles") \
        .select("*") \
        .eq("company", company) \
        .eq("is_active", True) \
        .order("type") \
        .order("name") \
        .execute().data
 
@app.post("/vehicles")
def add_vehicle(item: VehicleCreate):
    data = {k: v for k, v in item.dict().items() if v is not None}
    data["is_active"] = True
    return supabase.table("vehicles").insert(data).execute().data
 
@app.patch("/vehicles/{vehicle_id}")
def update_vehicle(vehicle_id: int, data: VehicleUpdate):
    update = {k: v for k, v in data.dict().items() if v is not None}
    return supabase.table("vehicles").update(update).eq("id", vehicle_id).execute().data
 
@app.delete("/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: int):
    # Soft delete — just mark inactive
    supabase.table("vehicles").update({"is_active": False}).eq("id", vehicle_id).execute()
    return {"deleted": True}
 
 
# ── THOOFAN LOGS ──────────────────────────────────────────────────
 
THOOFAN_LOG_COLUMNS = {
    "vehicle_id","date","hours","rate","site",
    "parts_name","parts_amount","service_amount","note"
}
 
@app.get("/vehicle-logs/thoofan/{vehicle_id}")
def get_thoofan_logs(vehicle_id: int):
    return supabase.table("thoofan_logs") \
        .select("*") \
        .eq("vehicle_id", vehicle_id) \
        .order("date", desc=True) \
        .execute().data
 
@app.post("/vehicle-logs/thoofan")
def add_thoofan_log(item: VehicleLogCreate):
    data = {k: v for k, v in item.dict().items()
            if k in THOOFAN_LOG_COLUMNS and v is not None}
    return supabase.table("thoofan_logs").insert(data).execute().data
 
@app.delete("/vehicle-logs/thoofan/{log_id}")
def delete_thoofan_log(log_id: int):
    supabase.table("thoofan_logs").delete().eq("id", log_id).execute()
    return {"deleted": True}
 
 
# ── OTHER COMPANY LOGS ────────────────────────────────────────────
 
OTHER_LOG_COLUMNS = {
    "vehicle_id","date","hours","rate","site",
    "parts_name","parts_amount","service_amount","note"
}
 
@app.get("/vehicle-logs/other/{vehicle_id}")
def get_other_logs(vehicle_id: int):
    return supabase.table("other_vehicle_logs") \
        .select("*") \
        .eq("vehicle_id", vehicle_id) \
        .order("date", desc=True) \
        .execute().data
 
@app.post("/vehicle-logs/other")
def add_other_log(item: VehicleLogCreate):
    data = {k: v for k, v in item.dict().items()
            if k in OTHER_LOG_COLUMNS and v is not None}
    return supabase.table("other_vehicle_logs").insert(data).execute().data
 
@app.delete("/vehicle-logs/other/{log_id}")
def delete_other_log(log_id: int):
    supabase.table("other_vehicle_logs").delete().eq("id", log_id).execute()
    return {"deleted": True}
 
 
# ── RAYS VEHICLE TRIP LOGS ────────────────────────────────────────
 
RAYS_VEHICLE_COLUMNS = {
    "vehicle_id","date","driver_name","trip_salary","load_quantity","site",
    "diesel_source","diesel_amount","rto_amount",
    "parts_name","parts_amount","service_amount","note"
}
 
@app.get("/rays/vehicle-logs/{vehicle_id}")
def get_rays_vehicle_logs(vehicle_id: int):
    return supabase.table("rays_vehicle_logs") \
        .select("*") \
        .eq("vehicle_id", vehicle_id) \
        .order("date", desc=True) \
        .execute().data
 
@app.post("/rays/vehicle-logs")
def add_rays_vehicle_log(item: RaysVehicleLogCreate):
    data = {k: v for k, v in item.dict().items()
            if k in RAYS_VEHICLE_COLUMNS and v is not None}
    return supabase.table("rays_vehicle_logs").insert(data).execute().data
 
@app.delete("/rays/vehicle-logs/{log_id}")
def delete_rays_vehicle_log(log_id: int):
    supabase.table("rays_vehicle_logs").delete().eq("id", log_id).execute()
    return {"deleted": True}
 
 
# ── RAYS MACHINE LOGS ─────────────────────────────────────────────
 
RAYS_MACHINE_COLUMNS = {
    "vehicle_id","date","hours","rate","site",
    "parts_name","parts_amount","service_amount","note"
}
 
@app.get("/rays/machine-logs/{vehicle_id}")
def get_rays_machine_logs(vehicle_id: int):
    return supabase.table("rays_machine_logs") \
        .select("*") \
        .eq("vehicle_id", vehicle_id) \
        .order("date", desc=True) \
        .execute().data
 
@app.post("/rays/machine-logs")
def add_rays_machine_log(item: RaysMachineLogCreate):
    data = {k: v for k, v in item.dict().items()
            if k in RAYS_MACHINE_COLUMNS and v is not None}
    return supabase.table("rays_machine_logs").insert(data).execute().data
 
@app.delete("/rays/machine-logs/{log_id}")
def delete_rays_machine_log(log_id: int):
    supabase.table("rays_machine_logs").delete().eq("id", log_id).execute()
    return {"deleted": True}
 
 
# ── DRIVER WEEKLY SALARY ──────────────────────────────────────────
 
@app.get("/driver-salary/{vehicle_id}")
def get_driver_salary(vehicle_id: int):
    return supabase.table("driver_salary") \
        .select("*") \
        .eq("vehicle_id", vehicle_id) \
        .order("week_start", desc=True) \
        .execute().data
 
@app.post("/driver-salary")
def add_driver_salary(item: DriverSalaryCreate):
    data = {k: v for k, v in item.dict().items() if v is not None}
    return supabase.table("driver_salary").insert(data).execute().data
 
@app.patch("/driver-salary/{salary_id}")
def update_driver_salary(salary_id: int, data: DriverSalaryUpdate):
    update = {k: v for k, v in data.dict().items() if v is not None}
    return supabase.table("driver_salary").update(update).eq("id", salary_id).execute().data
 
@app.delete("/driver-salary/{salary_id}")
def delete_driver_salary(salary_id: int):
    supabase.table("driver_salary").delete().eq("id", salary_id).execute()
    return {"deleted": True}
     