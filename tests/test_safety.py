from fixlens.models import RepairAssessment, RiskLevel
from fixlens.models import Vehicle
from fixlens.knowledge import video_for
from fixlens.safety import enforce_safety
from fixlens.vision import text_maintenance_assessment


def assessment(component: str, confidence: float = 0.9) -> RepairAssessment:
    return RepairAssessment(
        image_quality="GOOD",
        suspected_component=component,
        confidence=confidence,
        visible_evidence=["test"],
        risk_level=RiskLevel.LOW,
        safe_to_drive="unknown",
        summary="test",
    )


def test_safe_component_receives_curated_steps():
    result = enforce_safety(assessment("engine air filter"))
    assert result.risk_level == RiskLevel.LOW
    assert result.repair_steps
    assert result.source_keys


def test_critical_component_never_receives_steps():
    result = enforce_safety(assessment("airbag SRS module"))
    assert result.risk_level == RiskLevel.CRITICAL
    assert result.requires_professional
    assert result.repair_steps == []


def test_low_confidence_suppresses_steps():
    result = enforce_safety(assessment("wiper blade", confidence=0.4))
    assert result.repair_steps == []
    assert result.questions_needed


def test_text_only_cabin_filter_request_receives_guide():
    result = text_maintenance_assessment(
        "Not sure", "How do I change my cabin air filter?"
    )
    assert result.suspected_component == "cabin air filter"
    assert result.image_quality == "NOT_REQUIRED"
    assert result.repair_steps


def test_exact_civic_cabin_video_is_curated():
    video = video_for(
        Vehicle(year=2024, model="Civic"), "cabin air filter"
    )
    assert video["curated"]
    assert "youtube.com/watch" in video["url"]


def test_other_models_get_a_direct_reviewed_video():
    video = video_for(
        Vehicle(year=2023, model="CR-V"), "engine air filter"
    )
    assert video["curated"]
    assert "youtube.com/watch" in video["url"]


def test_text_battery_replacement_has_steps_and_direct_video():
    result = text_maintenance_assessment(
        "Not sure", "How do I change the front battery under the hood?"
    )
    assert result.suspected_component == "12-volt battery"
    assert result.confidence > 0.9
    assert result.repair_steps
    video = video_for(Vehicle(year=2024, model="Accord"), result.suspected_component)
    assert "youtube.com/watch" in video["url"]


def test_text_tire_change_has_guarded_steps_and_direct_video():
    result = text_maintenance_assessment(
        "Not sure", "How can I change a flat tire myself?"
    )
    assert result.suspected_component == "spare tire"
    assert result.risk_level == RiskLevel.HIGH
    assert result.confidence > 0.9
    assert result.repair_steps
    assert any("Never put any part" in step for step in result.repair_steps)
    video = video_for(Vehicle(year=2023, model="Civic"), result.suspected_component)
    assert "youtube.com/watch" in video["url"]


def test_oil_change_has_guarded_steps_and_video():
    result = text_maintenance_assessment("Not sure", "How do I do an oil change?")
    assert result.suspected_component == "engine oil and filter"
    assert result.risk_level == RiskLevel.HIGH
    assert result.repair_steps
    video = video_for(Vehicle(year=2022, model="CR-V"), result.suspected_component)
    assert "youtube.com/watch" in video["url"]


def test_brake_fluid_is_professional_only():
    result = text_maintenance_assessment("Not sure", "How do I replace brake fluid?")
    assert result.suspected_component == "brake fluid service"
    assert result.risk_level == RiskLevel.CRITICAL
    assert result.requires_professional
    assert not result.repair_steps
