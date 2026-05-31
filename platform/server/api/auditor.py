import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import get_db
from models import AuditReport, EvolutionPlan

router = APIRouter()

class DimensionIn(BaseModel):
    score: float
    findings: List[str] = []

class AuditIn(BaseModel):
    plan_id: str
    dimensions: dict
    recommendations: List[str] = []

DIMENSION_WEIGHTS = {
    "INT": 0.20, "USA": 0.20, "CON": 0.15,
    "EFF": 0.15, "PRO": 0.15, "REA": 0.15
}

@router.post("/audit")
def audit_plan(audit: AuditIn, db: Session = Depends(get_db)):
    plan = db.query(EvolutionPlan).filter(EvolutionPlan.plan_id == audit.plan_id).first()
    if not plan:
        return {"status": "error", "message": "Plan not found"}

    dims = audit.dimensions
    total = 0.0
    min_dim_score = 100.0
    for dim, weight in DIMENSION_WEIGHTS.items():
        score = dims.get(dim, {}).get("score", 0)
        total += score * weight
        min_dim_score = min(min_dim_score, score)

    total = round(total, 1)

    if total >= 80 and min_dim_score >= 60:
        verdict = "pass"
    elif total >= 60 and min_dim_score >= 40:
        verdict = "warn"
    else:
        verdict = "fail"

    audit_id = f"AUD-{datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-001"
    db_audit = AuditReport(
        audit_id=audit_id,
        plan_id=audit.plan_id,
        dimensions=dims,
        total_score=total,
        verdict=verdict,
        recommendations=audit.recommendations
    )
    db.add(db_audit)

    if verdict == "pass":
        plan.status = "published"
    elif verdict == "fail":
        plan.status = "rejected"
    else:
        plan.status = "warning"

    db.commit()
    return {"status": "ok", "audit_id": audit_id, "total_score": total, "verdict": verdict}

@router.get("/reports")
def list_reports(plan_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(AuditReport)
    if plan_id:
        query = query.filter(AuditReport.plan_id == plan_id)
    reports = query.order_by(AuditReport.audited_at.desc()).all()
    return {"reports": [
        {"audit_id": r.audit_id, "plan_id": r.plan_id, "total_score": r.total_score,
         "verdict": r.verdict, "audited_at": r.audited_at.isoformat()}
        for r in reports
    ]}
