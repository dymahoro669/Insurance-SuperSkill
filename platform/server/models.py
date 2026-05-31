from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from db import Base
import datetime

class InvocationEvent(Base):
    __tablename__ = "invocation_events"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    session_id = Column(String, index=True)
    trace_id = Column(String, index=True)
    user_input = Column(Text)
    primary_skill = Column(String, index=True)
    confidence = Column(Float)
    route_chain = Column(JSON)
    cross_skill_invoked = Column(Boolean, default=False)
    duration_ms = Column(Integer)
    tokens_used = Column(Integer)
    model = Column(String)
    l1_score = Column(Integer)
    l1_verdict = Column(String)
    l2_triggered = Column(Boolean, default=False)
    l3_triggered = Column(Boolean, default=False)
    output_length = Column(Integer)
    output_format = Column(String)
    has_pii = Column(Boolean, default=False)
    failed_dimensions = Column(JSON)

class AggregatedMetrics(Base):
    __tablename__ = "aggregated_metrics"
    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    skill_id = Column(String, index=True)
    invocations = Column(Integer, default=0)
    avg_duration_ms = Column(Float, default=0.0)
    avg_tokens = Column(Float, default=0.0)
    l1_pass_rate = Column(Float, default=0.0)
    l1_warn_rate = Column(Float, default=0.0)
    l1_fail_rate = Column(Float, default=0.0)
    avg_score = Column(Float, default=0.0)
    dimension_avg = Column(JSON)
    top_issues = Column(JSON)
    routing_accuracy = Column(Float, default=0.0)

class EvolutionPlan(Base):
    __tablename__ = "evolution_plans"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    target_skills = Column(JSON)
    expected_impact = Column(JSON)
    status = Column(String, default="pending")
    executed_at = Column(DateTime, nullable=True)
    results = Column(JSON, nullable=True)
    version_bump = Column(String, nullable=True)

class AuditReport(Base):
    __tablename__ = "audit_reports"
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(String, unique=True, index=True)
    plan_id = Column(String, index=True)
    audited_at = Column(DateTime, default=datetime.datetime.utcnow)
    dimensions = Column(JSON)
    total_score = Column(Float)
    verdict = Column(String)
    recommendations = Column(JSON)

class L2Evaluation(Base):
    __tablename__ = "l2_evaluations"
    id = Column(Integer, primary_key=True, index=True)
    eval_id = Column(String, unique=True, index=True)
    skill_id = Column(String, index=True)
    event_id = Column(String, index=True)
    professional_score = Column(Integer)
    practical_accuracy = Column(Integer)
    scenario_coverage = Column(Integer)
    executability = Column(Integer)
    risk_awareness = Column(Integer)
    overall = Column(Integer)
    evaluation = Column(Text)
    improvements = Column(JSON)
    benchmark = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class L3Evaluation(Base):
    __tablename__ = "l3_evaluations"
    id = Column(Integer, primary_key=True, index=True)
    eval_id = Column(String, unique=True, index=True)
    skill_id = Column(String, index=True)
    event_id = Column(String, index=True)
    reviewer = Column(String)
    expertise_level = Column(String)
    professional_score = Column(Integer)
    practical_score = Column(Integer)
    compliance_score = Column(Integer)
    overall = Column(Integer)
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
