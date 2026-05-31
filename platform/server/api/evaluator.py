import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import get_db
from models import L2Evaluation, L3Evaluation, InvocationEvent

router = APIRouter()

class L2EvalIn(BaseModel):
    eval_id: str
    skill_id: str
    event_id: str
    professional_score: int
    practical_accuracy: int
    scenario_coverage: int
    executability: int
    risk_awareness: int
    overall: int
    evaluation: str
    improvements: List[str]
    benchmark: str

class L3EvalIn(BaseModel):
    eval_id: str
    skill_id: str
    event_id: str
    reviewer: str
    expertise_level: str
    professional_score: int
    practical_score: int
    compliance_score: int
    overall: int
    feedback: str

@router.post("/l2")
def submit_l2(evaluation: L2EvalIn, db: Session = Depends(get_db)):
    db_eval = L2Evaluation(**evaluation.dict())
    db.add(db_eval)
    db.commit()
    return {"status": "ok", "eval_id": evaluation.eval_id}

@router.post("/l3")
def submit_l3(evaluation: L3EvalIn, db: Session = Depends(get_db)):
    db_eval = L3Evaluation(**evaluation.dict())
    db.add(db_eval)
    db.commit()
    return {"status": "ok", "eval_id": evaluation.eval_id}

@router.get("/l2")
def list_l2(skill_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(L2Evaluation)
    if skill_id:
        query = query.filter(L2Evaluation.skill_id == skill_id)
    evals = query.order_by(L2Evaluation.created_at.desc()).limit(50).all()
    return {"evaluations": [
        {"eval_id": e.eval_id, "skill_id": e.skill_id, "overall": e.overall,
         "created_at": e.created_at.isoformat()}
        for e in evals
    ]}

@router.get("/l3")
def list_l3(skill_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(L3Evaluation)
    if skill_id:
        query = query.filter(L3Evaluation.skill_id == skill_id)
    evals = query.order_by(L3Evaluation.created_at.desc()).limit(50).all()
    return {"evaluations": [
        {"eval_id": e.eval_id, "skill_id": e.skill_id, "overall": e.overall,
         "reviewer": e.reviewer, "created_at": e.created_at.isoformat()}
        for e in evals
    ]}

@router.post("/auto-l2")
def auto_l2(event_id: str, db: Session = Depends(get_db)):
    """Auto-generate L2 evaluation template for an event"""
    event = db.query(InvocationEvent).filter(InvocationEvent.event_id == event_id).first()
    if not event:
        return {"status": "error", "message": "Event not found"}

    eval_id = f"L2-{event_id}"
    db_eval = L2Evaluation(
        eval_id=eval_id,
        skill_id=event.primary_skill,
        event_id=event_id,
        professional_score=80,
        practical_accuracy=80,
        scenario_coverage=80,
        executability=80,
        risk_awareness=80,
        overall=80,
        evaluation="Auto-generated placeholder evaluation. Please review and update.",
        improvements=["Review required"],
        benchmark="Industry standard"
    )
    db.add(db_eval)
    db.commit()
    return {"status": "ok", "eval_id": eval_id, "message": "Auto L2 evaluation created"}
