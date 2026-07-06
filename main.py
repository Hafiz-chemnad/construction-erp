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
    treasury_fd_amount: float = 0        # ADD
    bank_fd_amount: float = 0            # ADD
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
    treasury_fd_amount: float = 0      # ADD
    bank_fd_amount: float = 0
    security_period: Optional[int] = None
    security_closing_date: Optional[str] = None
    insurance_amount: Optional[float] = None
    site_number: Optional[str] = None
    site_handover_date: Optional[str] = None

class GlobalLabourerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    wage_tar: float = 0
    wage_concrete: float = 0
    wage_local: float = 0
    worker_type: str = "CORE"   # 'CORE' | 'TEMP'

class GlobalLabourerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    wage_tar: Optional[float] = None
    wage_concrete: Optional[float] = None
    wage_local: Optional[float] = None
    worker_type: Optional[str] = None
    is_active: Optional[bool] = None

class SiteRosterAdd(BaseModel):
    work_id: int
    global_labourer_id: int

class AttendanceLog(BaseModel):
    work_id: int
    global_labourer_id: int
    date: str
    work_type: str          # 'TAR' | 'CONCRETE' | 'LOCAL'
    shift_fraction: float = 1.0   # 0.25 / 0.5 / 0.75 / 1.0

class LabourCash(BaseModel):
    work_id: Optional[int] = None
    global_labourer_id: int
    type: str                # 'ADVANCE' | 'SETTLEMENT'
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

class OtherExpenseLog(BaseModel):
    work_id: int
    expense_type: str
    amount: float
    date: str
    note: Optional[str] = None

class OtherExpenseUpdate(BaseModel):
    expense_type: Optional[str] = None
    amount: Optional[float] = None
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

# FIX: Rays machine logs had no update/edit capability, unlike Thoofan's
# equivalent. Added to match ThoofanMachineLogUpdate.
class RaysMachineLogUpdate(BaseModel):
    date:           Optional[str]   = None
    hours:          Optional[float] = None
    rate:           Optional[float] = None
    site:           Optional[str]   = None
    parts_name:     Optional[str]   = None
    parts_amount:   Optional[float] = None
    service_amount: Optional[float] = None
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
    current_amount = deal_amount - SUM(materials) - SUM(diesel)
                      - SUM(attendance.wage_earned) - SUM(labour_cash where work_id set)
    NOTE: labour_cash.work_id is nullable now (advances not always tied to a site's
    petty cash), so only rows WITH a work_id are deducted from that site's balance.
    """
    work = supabase.table("works").select("deal_amount").eq("id", work_id).single().execute()
    deal = float(work.data["deal_amount"])

    mat_res = supabase.table("materials").select("amount").eq("work_id", work_id).execute()
    dsl_res = supabase.table("diesel").select("amount").eq("work_id", work_id).execute()
    csh_res = supabase.table("labour_cash").select("amount").eq("work_id", work_id).execute()
    att_res = supabase.table("attendance").select("wage_earned").eq("work_id", work_id).execute()
    oth_res = supabase.table("other_expenses").select("amount").eq("work_id", work_id).execute()

    mat_total = sum(float(r["amount"]) for r in (mat_res.data or []))
    dsl_total = sum(float(r["amount"]) for r in (dsl_res.data or []))
    csh_total = sum(float(r["amount"]) for r in (csh_res.data or []))
    wage_total = sum(float(r["wage_earned"] or 0) for r in (att_res.data or []))
    oth_total = sum(float(r["amount"]) for r in (oth_res.data or []))

    new_balance = deal - mat_total - dsl_total - csh_total - wage_total - oth_total

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

# Columns that exist in the 'diesel' table:
# id, work_id, vehicle_name, amount, litres, date, note, created_at
# FIX: 'litres' column was added via migration (see add_litres_to_diesel.sql) —
# it is now a real column, so it must be included here or every litres value
# typed in the UI gets silently dropped before insert/update.
DIESEL_TABLE_COLUMNS = {"work_id", "vehicle_name", "amount", "litres", "date", "note"}

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

# ── OTHER EXPENSES ────────────────────────────────────────────────────────────

OTHER_EXPENSE_TABLE_COLUMNS = {"work_id", "expense_type", "amount", "date", "note"}

@app.get("/other-expenses/{work_id}")
def get_other_expenses_by_work(work_id: int):
    return supabase.table("other_expenses").select("*").eq("work_id", work_id).order("date", desc=True).execute().data

@app.post("/other-expenses")
def add_other_expense(item: OtherExpenseLog):
    if item.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    data = {k: v for k, v in item.dict().items() if k in OTHER_EXPENSE_TABLE_COLUMNS and v is not None}
    supabase.table("other_expenses").insert(data).execute()
    new_bal = recalculate_balance(item.work_id)
    return {"message": "Other expense logged", "current_balance": new_bal}

@app.patch("/other-expenses/{expense_id}")
def update_other_expense(expense_id: int, data: OtherExpenseUpdate):
    update_data = {
        k: v for k, v in data.dict().items()
        if v is not None and k in OTHER_EXPENSE_TABLE_COLUMNS
    }
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    res = supabase.table("other_expenses").update(update_data).eq("id", expense_id).execute()
    oth = supabase.table("other_expenses").select("work_id").eq("id", expense_id).single().execute()
    if oth.data:
        recalculate_balance(oth.data["work_id"])
    return res.data

@app.delete("/other-expenses/{expense_id}")
def delete_other_expense(expense_id: int):
    oth = supabase.table("other_expenses").select("work_id").eq("id", expense_id).single().execute()
    work_id = oth.data["work_id"] if oth.data else None
    supabase.table("other_expenses").delete().eq("id", expense_id).execute()
    if work_id:
        recalculate_balance(work_id)
    return {"deleted": True}

# ── LABOURERS ─────────────────────────────────────────────────────────────────

WAGE_FIELD_BY_TYPE = {
    "TAR": "wage_tar",
    "CONCRETE": "wage_concrete",
    "LOCAL": "wage_local",
}
VALID_SHIFT_FRACTIONS = {0.25, 0.5, 0.75, 1.0}

# ── GLOBAL LABOURERS (Master Worker Pool) ───────────────────────────────────

@app.get("/global-labourers")
def get_global_labourers(active_only: bool = True):
    q = supabase.table("global_labourers").select("*").order("name")
    if active_only:
        q = q.eq("is_active", True)
    return q.execute().data

@app.post("/global-labourers")
def add_global_labourer(item: GlobalLabourerCreate):
    if item.worker_type not in ("CORE", "TEMP"):
        raise HTTPException(status_code=400, detail="worker_type must be CORE or TEMP")
    return supabase.table("global_labourers").insert(item.dict()).execute().data

@app.patch("/global-labourers/{labourer_id}")
def update_global_labourer(labourer_id: int, data: GlobalLabourerUpdate):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    return supabase.table("global_labourers").update(update_data).eq("id", labourer_id).execute().data

@app.delete("/global-labourers/{labourer_id}")
def deactivate_global_labourer(labourer_id: int):
    # Soft-delete only: a worker may have historical attendance/cash records
    # tied across many sites, so we never hard-delete them.
    supabase.table("global_labourers").update({"is_active": False}).eq("id", labourer_id).execute()
    return {"deactivated": True}

@app.get("/global-labourers/{labourer_id}/ledger")
def get_global_labourer_ledger(labourer_id: int):
    """Full passbook: every attendance entry + every cash entry, plus net balance."""
    att = supabase.table("attendance").select("*, works(name)").eq("global_labourer_id", labourer_id).order("date", desc=True).execute().data or []
    cash = supabase.table("labour_cash").select("*, works(name)").eq("global_labourer_id", labourer_id).order("date", desc=True).execute().data or []

    total_earned = sum(float(a["wage_earned"] or 0) for a in att)
    total_advance = sum(float(c["amount"]) for c in cash if c["type"] == "ADVANCE")
    total_settlement = sum(float(c["amount"]) for c in cash if c["type"] == "SETTLEMENT")
    net_pending = total_earned - total_advance - total_settlement

    return {
        "attendance": att,
        "cash": cash,
        "total_earned": total_earned,
        "total_advance": total_advance,
        "total_settlement": total_settlement,
        "net_pending": net_pending,
    }

# ── SITE ROSTER ──────────────────────────────────────────────────────────────

@app.get("/site-roster/{work_id}")
def get_site_roster(work_id: int):
    # Joins roster rows with the global labourer details for display
    return supabase.table("site_roster") \
        .select("*, global_labourers(*)") \
        .eq("work_id", work_id) \
        .execute().data or []

@app.post("/site-roster")
def add_to_roster(item: SiteRosterAdd):
    existing = supabase.table("site_roster") \
        .select("id") \
        .eq("work_id", item.work_id) \
        .eq("global_labourer_id", item.global_labourer_id) \
        .execute()
    if existing.data:
        return existing.data  # already on roster, no-op
    return supabase.table("site_roster").insert(item.dict()).execute().data

@app.delete("/site-roster/{roster_id}")
def remove_from_roster(roster_id: int):
    # Removing from roster does NOT delete attendance/cash history
    supabase.table("site_roster").delete().eq("id", roster_id).execute()
    return {"deleted": True}

# ── ATTENDANCE (Fractional Timesheet) ───────────────────────────────────────

@app.get("/attendance/{work_id}")
def get_attendance(work_id: int):
    try:
        return supabase.table("attendance") \
            .select("*, global_labourers(name)") \
            .eq("work_id", work_id) \
            .order("date", desc=True) \
            .execute().data or []
    except Exception as e:
        print(f"Error fetching attendance: {e}")
        return []

@app.post("/attendance")
def mark_attendance(item: AttendanceLog):
    work_type = item.work_type.upper()
    if work_type not in WAGE_FIELD_BY_TYPE:
        raise HTTPException(status_code=400, detail="work_type must be TAR, CONCRETE or LOCAL")
    if item.shift_fraction not in VALID_SHIFT_FRACTIONS:
        raise HTTPException(status_code=400, detail="shift_fraction must be 0.25, 0.5, 0.75 or 1.0")

    # Look up the worker's rate for this work_type and snapshot the earned wage
    worker = supabase.table("global_labourers").select("*").eq("id", item.global_labourer_id).single().execute()
    if not worker.data:
        raise HTTPException(status_code=404, detail="Worker not found")

    wage_field = WAGE_FIELD_BY_TYPE[work_type]
    day_rate = float(worker.data.get(wage_field) or 0)
    wage_earned = round(day_rate * item.shift_fraction, 2)

    insert_data = {
        "work_id": item.work_id,
        "global_labourer_id": item.global_labourer_id,
        "date": item.date,
        "work_type": work_type,
        "shift_fraction": item.shift_fraction,
        "wage_earned": wage_earned,
    }
    # NOTE: no unique(labourer, date) check — a worker can have multiple
    # shift entries across different sites (or work types) on the same day.
    res = supabase.table("attendance").insert(insert_data).execute()
    new_bal = recalculate_balance(item.work_id)
    return {"attendance": res.data, "current_balance": new_bal}

@app.delete("/attendance/{attendance_id}")
def delete_attendance(attendance_id: int):
    att = supabase.table("attendance").select("work_id").eq("id", attendance_id).single().execute()
    work_id = att.data["work_id"] if att.data else None
    supabase.table("attendance").delete().eq("id", attendance_id).execute()
    if work_id:
        recalculate_balance(work_id)
    return {"deleted": True}

# ── LABOUR CASH (Advances & Settlements) ────────────────────────────────────

@app.get("/labour-cash/{work_id}")
def get_labour_cash_history(work_id: int):
    try:
        return supabase.table("labour_cash") \
            .select("*, global_labourers(name)") \
            .eq("work_id", work_id) \
            .order("date", desc=True) \
            .execute().data or []
    except Exception as e:
        print(f"Error fetching cash: {e}")
        return []

@app.post("/labour-cash")
def add_labour_cash(item: LabourCash):
    if item.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    if item.type not in ("ADVANCE", "SETTLEMENT"):
        raise HTTPException(status_code=400, detail="type must be ADVANCE or SETTLEMENT")

    data = {k: v for k, v in item.dict().items() if v is not None}
    supabase.table("labour_cash").insert(data).execute()

    new_bal = None
    if item.work_id:
        new_bal = recalculate_balance(item.work_id)
    return {"message": "Cash logged", "current_balance": new_bal}

@app.patch("/labour-cash/{cash_id}")
def update_labour_cash(cash_id: int, data: LabourCashUpdate):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    res = supabase.table("labour_cash").update(update_data).eq("id", cash_id).execute()
    csh = supabase.table("labour_cash").select("work_id").eq("id", cash_id).single().execute()
    if csh.data and csh.data.get("work_id"):
        recalculate_balance(csh.data["work_id"])
    return res.data

@app.delete("/labour-cash/{cash_id}")
def delete_labour_cash(cash_id: int):
    csh = supabase.table("labour_cash").select("work_id").eq("id", cash_id).single().execute()
    work_id = csh.data.get("work_id") if csh.data else None
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

# FIX: Rays machine logs previously had no edit/update route — only Thoofan's
# equivalent did. Added to match update_thoofan_machine_log exactly.
@app.patch("/rays/machine-logs/{log_id}")
def update_rays_machine_log(log_id: int, data: RaysMachineLogUpdate):
    upd = {k: v for k, v in data.dict().items() if v is not None}
    if not upd:
        return {"message": "Nothing to update"}
    return supabase.table("rays_machine_logs").update(upd).eq("id", log_id).execute().data


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
    # FIX: must match the UI formula exactly —
    # Final Salary = (Trip Balance) - (Advance + ByHand Balance)
    # (previously this dropped byhand_balance, overstating every payout)
    d = item.dict()
    d["salary_balance"] = d.get("trip_balance", 0) - d.get("advance", 0) - d.get("byhand_balance", 0)
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
    # FIX: switched from substring (.ilike) matching to exact match — selecting
    # one driver should not also pull in another driver whose name happens to
    # contain the selected name as a substring. Empty string ("All Drivers")
    # skips the filter entirely so all rows are included.
    def apply_driver_filter(query):
        return query.eq("driver_name", driver) if driver else query

    rays = apply_driver_filter(
        supabase.table("rays_vehicle_logs").select("thoofan_giving_balance, byhand_amount, final_balance, advance, vehicle_rent")
        .gte("date", start_date).lte("date", end_date)
    ).execute()

    thoofan = apply_driver_filter(
        supabase.table("thoofan_logs").select("thoofan_giving_balance, byhand_amount, final_balance, advance, vehicle_rent")
        .gte("date", start_date).lte("date", end_date)
    ).execute()

    other = apply_driver_filter(
        supabase.table("other_vehicle_logs").select("thoofan_giving_balance, byhand_amount, final_balance, advance, vehicle_rent")
        .gte("date", start_date).lte("date", end_date)
    ).execute()

    # 1. ADVANCE (Includes ALL Three)
    total_advance = (
        sum(float(r.get("advance") or 0) for r in rays.data or []) +
        sum(float(r.get("advance") or 0) for r in thoofan.data or []) +
        sum(float(r.get("advance") or 0) for r in other.data or [])
    )

    # 2a. THOOFAN GIVING AMOUNT — Rays only
    total_thoofan_giving_rays = sum(float(r.get("thoofan_giving_balance") or 0) for r in rays.data or [])

    # 2b. THOOFAN GIVING AMOUNT — Other only
    total_thoofan_giving_other = sum(float(r.get("thoofan_giving_balance") or 0) for r in other.data or [])

    # 2c. THOOFAN GIVING AMOUNT — Tufa (Thoofan's own logs) only
    # NOTE: this column is normally 0/unused on Thoofan's own log rows since
    # "thoofan_giving_balance" represents what Thoofan owes back to us on
    # Rays/Other jobs — it doesn't conceptually apply to Thoofan's own
    # entries. Included here anyway per request; will just read as ₹0 unless
    # someone has actually populated this field on thoofan_logs rows.
    total_thoofan_giving_tufa = sum(float(r.get("thoofan_giving_balance") or 0) for r in thoofan.data or [])

    # 2. THOOFAN GIVING AMOUNT — combined (Rays + Other only), kept as-is
    total_thoofan_giving = total_thoofan_giving_rays + total_thoofan_giving_other

    # 3. BY HAND GIVEN (Includes ALL Three)
    total_byhand_given = (
        sum(float(r.get("byhand_amount") or 0) for r in rays.data or []) +
        sum(float(r.get("byhand_amount") or 0) for r in thoofan.data or []) +
        sum(float(r.get("byhand_amount") or 0) for r in other.data or [])
    )

    # 4. FINAL BALANCE (Includes ALL Three)
    total_final_balance = (
        sum(float(r.get("final_balance") or 0) for r in rays.data or []) +
        sum(float(r.get("final_balance") or 0) for r in thoofan.data or []) +
        sum(float(r.get("final_balance") or 0) for r in other.data or [])
    )

    # 5. TOTAL VEHICLE RENT — split per company, plus combined
    total_vehicle_rent_rays    = sum(float(r.get("vehicle_rent") or 0) for r in rays.data or [])
    total_vehicle_rent_tufa    = sum(float(r.get("vehicle_rent") or 0) for r in thoofan.data or [])
    total_vehicle_rent_other   = sum(float(r.get("vehicle_rent") or 0) for r in other.data or [])
    total_vehicle_rent = total_vehicle_rent_rays + total_vehicle_rent_tufa + total_vehicle_rent_other

    return {
        "driver": driver,
        "total_advance": total_advance,
        "total_thoofan_giving": total_thoofan_giving,
        "total_thoofan_giving_rays": total_thoofan_giving_rays,
        "total_thoofan_giving_tufa": total_thoofan_giving_tufa,
        "total_byhand_given": total_byhand_given,
        "total_final_balance": total_final_balance,
        "total_vehicle_rent": total_vehicle_rent,
        "total_vehicle_rent_rays": total_vehicle_rent_rays,
        "total_vehicle_rent_tufa": total_vehicle_rent_tufa,
        "total_vehicle_rent_other": total_vehicle_rent_other
    }
     
@app.get("/reports/global-driver-trips")
def get_global_driver_trips(driver: str, start_date: str, end_date: str):
    # FIX: exact match instead of substring — this route always gets a
    # specific driver name from the dropdown (no "All Drivers" case here).
    rays = supabase.table("rays_vehicle_logs").select("total_trip_amount, advance, byhand_balance") \
        .eq("driver_name", driver).gte("date", start_date).lte("date", end_date).execute()

    thoofan = supabase.table("thoofan_logs").select("total_trip_amount, advance, byhand_balance") \
        .eq("driver_name", driver).gte("date", start_date).lte("date", end_date).execute()

    other = supabase.table("other_vehicle_logs").select("total_trip_amount, advance, byhand_balance") \
        .eq("driver_name", driver).gte("date", start_date).lte("date", end_date).execute()

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

# 🌟 ADD THIS NEW CLASS
class GoldLoanUpdate(BaseModel):
    closing_date: Optional[str] = None
    interest_amount: Optional[float] = None
    is_renewal: Optional[bool] = None
    status: Optional[str] = None

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

class ODLogCreate(BaseModel):
    account_name: str
    date: str
    balance_amount: float = 0
    interest_amount: float = 0
    note: Optional[str] = None

# 🌟 ADDED OD UPDATE CLASS
class ODLogUpdate(BaseModel):
    date: Optional[str] = None
    balance_amount: Optional[float] = None
    interest_amount: Optional[float] = None
    note: Optional[str] = None

# 🌟 EXPANDED GOLD LOAN UPDATE CLASS
class GoldLoanUpdate(BaseModel):
    opening_date: Optional[str] = None
    closing_date: Optional[str] = None
    amount: Optional[float] = None
    interest_amount: Optional[float] = None
    is_renewal: Optional[bool] = None
    status: Optional[str] = None

class PurchaseBillUpdate(BaseModel):
    date: Optional[str] = None
    purchase_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    is_split_50_50: Optional[bool] = None
    tds_deducted: Optional[float] = None
    sidko_charges: Optional[float] = None
    other_charges: Optional[float] = None
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

    if existing.data:
        # FIX: don't blindly overwrite note with None — the frontend never sends
        # a note on routine saves, which was silently wiping notes like
        # "Initial Opening Balance" every time someone re-saved that day's balance.
        # Only touch note if the caller actually supplied one.
        payload = {
            "account_id": acc_id,
            "date": data.date,
            "balance": data.balance,
        }
        if data.note is not None:
            payload["note"] = data.note
        return supabase.table("daily_balances").update(payload).eq("id", existing.data[0]["id"]).execute().data
    else:
        # Insert new record — note is fine to include as-is (None is fine for a fresh row)
        payload = {
            "account_id": acc_id,
            "date": data.date,
            "balance": data.balance,
            "note": data.note
        }
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
        .order("id", desc=True) \
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

@app.get("/banking/gold-loans/{account_name}")
def get_gold_loans(account_name: str):
    acc_id = get_account_id(account_name)
    return supabase.table("gold_loans") \
        .select("*") \
        .eq("account_id", acc_id) \
        .order("created_at", desc=True) \
        .order("id", desc=True) \
        .execute().data

@app.post("/banking/gold-loans")
def add_gold_loan(data: GoldLoanCreate):
    acc_id = get_account_id(data.account_name)
    payload = data.dict()
    payload.pop("account_name")
    payload["account_id"] = acc_id
    return supabase.table("gold_loans").insert(payload).execute().data

# 🌟 ADD THIS NEW ROUTE (Allows us to close/renew existing loans)
@app.patch("/banking/gold-loans/{loan_id}")
def update_gold_loan(loan_id: int, data: GoldLoanUpdate):
    upd = {k: v for k, v in data.dict().items() if v is not None}
    return supabase.table("gold_loans").update(upd).eq("id", loan_id).execute().data

# ── 7. TDS & PURCHASE BILLS ──
@app.post("/banking/purchase-bills")
def add_purchase_bill(data: PurchaseBillCreate):
    return supabase.table("purchase_bills").insert(data.dict()).execute().data

@app.get("/banking/purchase-bills")
def get_purchase_bills():
    # Joins with works table to get the project name
    return supabase.table("purchase_bills") \
        .select("*, works(name, panchayaths(name))") \
        .order("date", desc=True) \
        .order("id", desc=True) \
        .execute().data

@app.patch("/banking/purchase-bills/{bill_id}")
def update_purchase_bill(bill_id: int, data: PurchaseBillUpdate):
    upd = {k: v for k, v in data.dict().items() if v is not None}
    return supabase.table("purchase_bills").update(upd).eq("id", bill_id).execute().data

@app.delete("/banking/purchase-bills/{bill_id}")
def delete_purchase_bill(bill_id: int):
    supabase.table("purchase_bills").delete().eq("id", bill_id).execute()
    return {"deleted": True}
# ── 8. FD TOTALS (Linked to Agreements) ──
@app.get("/banking/fd-totals")
def get_fd_totals():
    """Calculates the total locked amount in Bank FDs vs Treasury FDs."""
    agreements = supabase.table("agreements").select("treasury_fd_amount, bank_fd_amount").execute()

    bank_fd = 0
    treasury_fd = 0

    for a in (agreements.data or []):
        bank_fd     += float(a.get("bank_fd_amount") or 0)
        treasury_fd += float(a.get("treasury_fd_amount") or 0)

    return {"Bank FD": bank_fd, "Treasury FD": treasury_fd}
@app.get("/banking/od-logs/{account_name}")
def get_od_logs(account_name: str):
    acc_id = get_account_id(account_name)
    return supabase.table("od_logs") \
        .select("*") \
        .eq("account_id", acc_id) \
        .order("date", desc=True) \
        .order("id", desc=True) \
        .execute().data
# 🌟 MISSING ROUTES FOR EDITING AND DELETING
@app.patch("/banking/od-logs/{log_id}")
def update_od_log(log_id: int, data: ODLogUpdate):
    upd = {k: v for k, v in data.dict().items() if v is not None}
    return supabase.table("od_logs").update(upd).eq("id", log_id).execute().data

@app.delete("/banking/od-logs/{log_id}")
def delete_od_log(log_id: int):
    supabase.table("od_logs").delete().eq("id", log_id).execute()
    return {"deleted": True}

@app.delete("/banking/gold-loans/{loan_id}")
def delete_gold_loan(loan_id: int):
    supabase.table("gold_loans").delete().eq("id", loan_id).execute()
    return {"deleted": True}