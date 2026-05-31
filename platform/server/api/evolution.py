import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import get_db
from models import EvolutionPlan, InvocationEvent

router = APIRouter()

class ChangeIn(BaseModel):
    type: str
    field: str
    action: str
    value: str
    reason: str

class TargetSkillIn(BaseModel):
    skill_id: str
    changes: List[ChangeIn]

class PlanIn(BaseModel):
    target_skills: List[TargetSkillIn]
    expected_impact: dict

@router.post("/plans")
def create_plan(plan: PlanIn, db: Session = Depends(get_db)):
    plan_id = f"EVP-{datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-001"
    db_plan = EvolutionPlan(
        plan_id=plan_id,
        target_skills=[s.dict() for s in plan.target_skills],
        expected_impact=plan.expected_impact,
        status="pending"
    )
    db.add(db_plan)
    db.commit()
    return {"status": "ok", "plan_id": plan_id}

@router.get("/plans")
def list_plans(db: Session = Depends(get_db)):
    plans = db.query(EvolutionPlan).order_by(EvolutionPlan.created_at.desc()).all()
    return {"plans": [
        {"plan_id": p.plan_id, "status": p.status, "created_at": p.created_at.isoformat(),
         "target_skills": p.target_skills}
        for p in plans
    ]}

@router.post("/plans/{plan_id}/execute")
def execute_plan(plan_id: str, db: Session = Depends(get_db)):
    plan = db.query(EvolutionPlan).filter(EvolutionPlan.plan_id == plan_id).first()
    if not plan:
        return {"status": "error", "message": "Plan not found"}
    plan.status = "executed"
    plan.executed_at = datetime.datetime.utcnow()
    db.commit()
    return {"status": "ok", "plan_id": plan_id, "executed_at": plan.executed_at.isoformat()}

@router.post("/plans/{plan_id}/rollback")
def rollback_plan(plan_id: str, db: Session = Depends(get_db)):
    plan = db.query(EvolutionPlan).filter(EvolutionPlan.plan_id == plan_id).first()
    if not plan:
        return {"status": "error", "message": "Plan not found"}
    plan.status = "rolled_back"
    db.commit()
    return {"status": "ok", "plan_id": plan_id, "message": "Rolled back successfully"}

@router.post("/auto")
def auto_evolve(db: Session = Depends(get_db)):
    """Auto-generate evolution plan based on telemetry data"""
    now = datetime.datetime.utcnow()
    start = now - datetime.timedelta(days=7)
    events = db.query(InvocationEvent).filter(InvocationEvent.timestamp >= start).all()

    if not events:
        return {"status": "ok", "message": "No data to analyze", "plan": None}

    by_skill = {}
    for e in events:
        sid = e.primary_skill
        if sid not in by_skill:
            by_skill[sid] = {"scores": [], "fails": 0}
        by_skill[sid]["scores"].append(e.l1_score)
        if e.l1_verdict == "fail":
            by_skill[sid]["fails"] += 1

    targets = []
    for sid, data in by_skill.items():
        scores = data["scores"]
        avg = sum(scores) / len(scores)
        fail_rate = data["fails"] / len(scores)
        priority = (1 - avg / 100) * 100 + fail_rate * 500
        targets.append({"skill_id": sid, "avg_score": round(avg, 1), "fail_rate": round(fail_rate, 2), "priority": round(priority, 1)})

    targets.sort(key=lambda x: x["priority"], reverse=True)
    top = targets[:2]

    if not top or top[0]["priority"] < 10:
        return {"status": "ok", "message": "All skills performing well", "plan": None}

    plan_id = f"EVP-{now.strftime('%Y%m%d-%H%M%S')}-AUTO"
    db_plan = EvolutionPlan(
        plan_id=plan_id,
        target_skills=top,
        expected_impact={t["skill_id"]: {"score_delta": "+5"} for t in top},
        status="pending"
    )
    db.add(db_plan)
    db.commit()

    return {"status": "ok", "plan_id": plan_id, "targets": top}
