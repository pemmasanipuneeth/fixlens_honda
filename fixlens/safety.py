"""Deterministic safety policy applied after model output."""

from .knowledge import find_safe_guide
from .models import RepairAssessment, RiskLevel


BLOCKED_TERMS = {
    "airbag", "srs", "brake fluid", "brake bleeding", "brake line", "brake caliper", "brake pad", "brake rotor", "fuel leak", "fuel line",
    "timing belt", "timing chain", "transmission", "high voltage", "hybrid battery",
    "jack stand", "lift point", "steering rack", "suspension spring",
}


def enforce_safety(assessment: RepairAssessment) -> RepairAssessment:
    component = assessment.suspected_component.lower()
    unsafe = any(term in component for term in BLOCKED_TERMS)
    key, guide = find_safe_guide(component)

    if unsafe:
        assessment.risk_level = RiskLevel.CRITICAL
        assessment.requires_professional = True
        assessment.repair_steps = []
        assessment.tools = []
        assessment.materials = []
        assessment.safe_to_drive = "Do not rely on this image assessment. Stop using the vehicle if an immediate safety symptom is present."
        assessment.stop_conditions = [
            "Do not disassemble this system from image-based guidance.",
            "Arrange inspection by a qualified Honda technician or emergency assistance as appropriate.",
        ]
        return assessment

    if assessment.confidence < 0.65 or assessment.image_quality.upper() not in {
        "GOOD",
        "CLEAR",
        "NOT_REQUIRED",
    }:
        assessment.repair_steps = []
        assessment.requires_professional = assessment.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
        if "Upload" not in " ".join(assessment.questions_needed):
            assessment.questions_needed.insert(0, "Upload a clear, well-lit photo from another angle before attempting work.")
        return assessment

    if guide:
        assessment.risk_level = RiskLevel(guide["risk"])
        assessment.tools = guide["tools"]
        assessment.materials = guide["materials"]
        assessment.repair_steps = guide["steps"]
        assessment.verification_steps = guide["verify"]
        assessment.source_keys = ["honda_owners", "nhtsa_recalls"]
    else:
        assessment.repair_steps = []
        assessment.requires_professional = True
        assessment.risk_level = RiskLevel.HIGH
        assessment.stop_conditions.append(
            "This component is outside the owner-serviceable FixLens MVP scope. Seek a qualified Honda technician."
        )
    return assessment
