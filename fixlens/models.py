"""Typed domain models used by the UI and vision service."""

from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Vehicle(BaseModel):
    year: int
    model: str
    trim: str = "Unknown"
    engine: str = "Unknown"
    mileage: int | None = None


class Source(BaseModel):
    title: str
    section: str
    url: str
    vehicle_scope: str


class RepairAssessment(BaseModel):
    image_quality: str = "UNKNOWN"
    suspected_component: str
    confidence: float = Field(ge=0, le=1)
    visible_evidence: list[str]
    alternative_diagnoses: list[str] = Field(default_factory=list)
    questions_needed: list[str] = Field(default_factory=list)
    risk_level: RiskLevel
    safe_to_drive: str
    summary: str
    tools: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    repair_steps: list[str] = Field(default_factory=list)
    stop_conditions: list[str] = Field(default_factory=list)
    verification_steps: list[str] = Field(default_factory=list)
    source_keys: list[str] = Field(default_factory=list)
    requires_professional: bool = False


class EvaluationRecord(BaseModel):
    attack_family: str
    prompt: str
    outcome: str
    reasoning: str


class DiagnosticAssessment(BaseModel):
    title: str
    confidence: float = Field(ge=0, le=1)
    urgency: str
    summary: str
    possible_causes: list[str] = Field(default_factory=list)
    immediate_checks: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    stop_conditions: list[str] = Field(default_factory=list)
    driveability: str
    next_step: str
