import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import get_db
from models import InvocationEvent, AggregatedMetrics

router = APIRouter()

class EventIn(BaseModel):
    event_id: str
    session_id: str
    trace_id: str
    user_input: str
    primary_skill: str
    confidence: float
    route_chain: List[str]
    cross_skill_invoked: bool = False
    duration_ms: int
    tokens_used: int
    model: str
    l1_score: int
    l1_verdict: str
    l2_triggered: bool = False
    l3_triggered: bool = False
    output_length: int
    output_format: str = "markdown"
    has_pii: bool = False
    failed_dimensions: Optional[List[str]] = None

@router.post("/events")
def collect_event(event: EventIn, db: Session = Depends(get_db)):
    db_event = InvocationEvent(**event.dict())
    db.add(db_event)
    db.commit()
    return {"status": "ok", "event_id": event.event_id}

@router.get("/metrics")
def get_metrics(
    skill: Optional[str] = None,
    period: str = Query("24h", regex="^(1h|24h|7d|30d)$"),
    db: Session = Depends(get_db)
):
    now = datetime.datetime.utcnow()
    delta = {"1h": datetime.timedelta(hours=1), "24h": datetime.timedelta(days=1),
             "7d": datetime.timedelta(days=7), "30d": datetime.timedelta(days=30)}[period]
    start = now - delta

    query = db.query(InvocationEvent).filter(InvocationEvent.timestamp >= start)
    if skill:
        query = query.filter(InvocationEvent.primary_skill == skill)
    events = query.all()

    if not events:
        return {"period": period, "invocations": 0, "skills": {}}

    total = len(events)
    pass_count = sum(1 for e in events if e.l1_verdict == "pass")
    warn_count = sum(1 for e in events if e.l1_verdict == "warn")
    fail_count = sum(1 for e in events if e.l1_verdict == "fail")

    by_skill = {}
    for e in events:
        sid = e.primary_skill
        if sid not in by_skill:
            by_skill[sid] = {"invocations": 0, "scores": [], "durations": []}
        by_skill[sid]["invocations"] += 1
        by_skill[sid]["scores"].append(e.l1_score)
        by_skill[sid]["durations"].append(e.duration_ms)

    skill_metrics = {}
    for sid, data in by_skill.items():
        scores = data["scores"]
        durations = data["durations"]
        skill_metrics[sid] = {
            "invocations": data["invocations"],
            "pass_rate": round(sum(1 for s in scores if s >= 80) / len(scores), 2),
            "avg_score": round(sum(scores) / len(scores), 1),
            "avg_duration_ms": round(sum(durations) / len(durations), 0)
        }

    return {
        "period": period,
        "invocations": total,
        "pass_rate": round(pass_count / total, 2),
        "warn_rate": round(warn_count / total, 2),
        "fail_rate": round(fail_count / total, 2),
        "avg_score": round(sum(e.l1_score for e in events) / total, 1),
        "skills": skill_metrics
    }

@router.get("/events")
def list_events(
    skill: Optional[str] = None,
    verdict: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(InvocationEvent)
    if skill:
        query = query.filter(InvocationEvent.primary_skill == skill)
    if verdict:
        query = query.filter(InvocationEvent.l1_verdict == verdict)
    events = query.order_by(InvocationEvent.timestamp.desc()).limit(limit).all()
    return {
        "events": [
            {
                "event_id": e.event_id,
                "timestamp": e.timestamp.isoformat(),
                "skill": e.primary_skill,
                "l1_score": e.l1_score,
                "l1_verdict": e.l1_verdict,
                "duration_ms": e.duration_ms
            }
            for e in events
        ]
    }
