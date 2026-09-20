"""Deterministic quick-help knowledge for common Honda ownership questions."""

from dataclasses import dataclass

from .models import DiagnosticAssessment, Vehicle


@dataclass(frozen=True)
class QuickResult:
    title: str
    urgency: str
    summary: str
    checks: list[str]
    stop_conditions: list[str]
    next_step: str


WARNING_LIGHTS = {
    "Check-engine light": QuickResult(
        "Check-engine light", "CAUTION",
        "The engine-control system detected a fault. The light alone does not identify the failed part.",
        ["Check whether the light is steady or flashing.", "Tighten a loose fuel cap only if it is safe and recently disturbed.", "Read stored OBD-II codes before replacing anything."],
        ["A flashing light, severe shaking, power loss, smoke, or overheating requires stopping as soon as safely possible."],
        "Retrieve the diagnostic code and diagnose the system represented by that code.",
    ),
    "Oil-pressure warning": QuickResult(
        "Oil-pressure warning", "STOP",
        "Low oil pressure can damage the engine within moments; it is not merely an oil-change reminder.",
        ["Pull over safely and switch the engine off.", "After waiting on level ground, check the oil level only if safe."],
        ["Do not restart when the level is normal but the warning remains, or when leakage/noise is present."],
        "Arrange towing or qualified inspection when the cause is not clearly a safely correctable low level.",
    ),
    "Battery/charging warning": QuickResult(
        "Battery/charging warning", "URGENT",
        "The vehicle may be running only on stored battery power because the charging system is not operating normally.",
        ["Turn off nonessential electrical loads.", "Look only for an obviously loose or broken drive belt with the engine off."],
        ["Stop for smoke, burning odor, rising temperature, heavy steering, or rapidly dimming displays."],
        "Drive only to the nearest safe service location when conditions remain normal; otherwise request roadside assistance.",
    ),
    "Coolant-temperature warning": QuickResult(
        "Coolant-temperature warning", "STOP",
        "The engine may be overheating.",
        ["Turn off climate-control loads and pull over safely.", "Switch off the engine if the warning persists or steam is present."],
        ["Never open a hot radiator or coolant cap.", "Do not continue driving with steam, coolant loss, or persistent overheating."],
        "Allow the vehicle to cool completely and arrange inspection or towing.",
    ),
    "TPMS warning": QuickResult(
        "Tire-pressure warning", "CAUTION",
        "One or more tires may be underinflated, or the monitoring system may need attention.",
        ["Inspect every tire for visible damage.", "Measure cold pressure and compare it with the driver's-door-jamb placard."],
        ["Do not drive on a visibly flat, damaged, separating, or rapidly deflating tire."],
        "Correct cold pressures and follow the model-year Honda calibration procedure if applicable.",
    ),
    "ABS or brake-system warning": QuickResult(
        "ABS or brake-system warning", "STOP",
        "Braking assistance or the hydraulic brake system may be compromised.",
        ["Confirm the parking brake is fully released only when safely stopped.", "Note pedal feel without repeatedly pumping or road-testing."],
        ["Do not drive with a soft pedal, reduced braking, fluid leakage, grinding, or a red brake warning that remains on."],
        "Arrange professional brake inspection or towing.",
    ),
}


OBD_CODES = {
    "P0300": ("Random/multiple-cylinder misfire detected", "Avoid hard driving; a flashing check-engine light requires stopping."),
    "P0301": ("Cylinder 1 misfire detected", "Diagnose ignition, fuel, compression, and wiring before replacing parts."),
    "P0420": ("Catalyst efficiency below threshold, bank 1", "Do not assume the catalytic converter is the cause; leaks, sensors, and misfires must be checked."),
    "P0171": ("System too lean, bank 1", "Inspect for intake leaks and obtain live data; do not replace sensors blindly."),
    "P0455": ("Large evaporative-emissions leak detected", "Check the fuel cap and visible EVAP connections; fuel odor requires stopping."),
    "P0128": ("Coolant temperature below thermostat-regulating temperature", "Check coolant only when fully cold and diagnose temperature data."),
    "P0562": ("System voltage low", "Test the 12-volt battery and charging system before replacing either."),
}


MAINTENANCE_MINDER = {
    "A": "Replace engine oil.",
    "B": "Replace engine oil and filter, and perform the Honda-specified inspection items.",
    "1": "Rotate tires.",
    "2": "Replace air-cleaner element, inspect the drive belt, and replace the dust/pollen filter as applicable.",
    "3": "Replace transmission fluid as specified for the exact vehicle.",
    "4": "Replace spark plugs and inspect valve clearance as applicable; some engines also specify timing-belt-related service.",
    "5": "Replace engine coolant.",
    "7": "Replace brake fluid where this sub-item is used.",
}


SYMPTOMS = {
    "Car will not start": QuickResult(
        "No-start troubleshooting", "CAUTION", "A no-start can involve the 12-volt battery, starter circuit, fuel, immobilizer, or engine management.",
        ["Note whether the engine cranks, clicks, or stays silent.", "Check interior-light brightness and dashboard messages.", "Try the spare key if an immobilizer warning appears."],
        ["Stop for smoke, melting odor, repeated rapid clicking with hot cables, or fuel odor."],
        "Test 12-volt battery voltage and retrieve codes before replacing components.",
    ),
    "Fluid under the car": QuickResult(
        "Fluid-leak triage", "CAUTION", "Location, color, feel, odor, and whether the AC was operating help distinguish normal condensation from a leak.",
        ["Do not touch or taste unknown fluid.", "Photograph the puddle and its position relative to the car.", "Clear water after AC use may be normal condensation."],
        ["Stop for fuel odor, brake-fluid suspicion, rapid coolant loss, heavy oil loss, smoke, or overheating."],
        "Upload a clear photo and arrange inspection when the fluid is colored, oily, persistent, or unidentified.",
    ),
    "Engine overheating": WARNING_LIGHTS["Coolant-temperature warning"],
    "AC not cooling": QuickResult(
        "Air conditioning not cooling", "NORMAL", "Airflow, cabin filter condition, compressor operation, outside temperature, and refrigerant-system faults can contribute.",
        ["Confirm the blower works and vents are open.", "Inspect or replace a restricted cabin filter.", "Compare cooling while parked and while moving."],
        ["Stop using the system for burning odor, belt noise, smoke, or obvious refrigerant/oil leakage."],
        "Professional diagnosis is needed for refrigerant recovery, leak repair, or compressor work.",
    ),
    "Vibration or pulling": QuickResult(
        "Vibration or pulling", "CAUTION", "Tire damage, pressure, wheel balance, alignment, brakes, or suspension may be involved.",
        ["Inspect tire pressure and visible damage.", "Note whether it occurs during braking, acceleration, or at a particular speed."],
        ["Stop for severe vibration, loose steering, bulges, exposed cords, grinding, or loss of control."],
        "Request tire, wheel, brake, and suspension inspection rather than guessing from symptoms alone.",
    ),
    "Unusual smell or noise": QuickResult(
        "Unusual smell or noise", "CAUTION", "The timing, location, and operating condition are required before narrowing the cause.",
        ["Record the sound from a safe position.", "Note whether it changes with speed, braking, steering, blower use, or engine RPM."],
        ["Stop for fuel odor, electrical burning, smoke, grinding brakes, severe knocking, or overheating."],
        "Upload evidence and arrange inspection if the source is not clearly harmless.",
    ),
}


EMERGENCIES = {
    "Smoke or fire": "Stop, switch off if safe, move everyone well away, call emergency services, and do not open a hot hood when fire is suspected.",
    "Strong fuel odor": "Switch off, avoid sparks or electrical switches, move away, and request emergency roadside assistance.",
    "Brake failure": "Ease off acceleration, activate hazards, downshift progressively if possible, apply the parking brake gradually only as needed, steer to a safe area, and call emergency services.",
    "Overheating or steam": "Pull over, switch off, stay clear of steam, never open a hot cooling system, and arrange towing.",
    "Flat tire in traffic": "Slow smoothly, use hazards, leave the traffic lane if possible, and call emergency services if no safe work area exists.",
    "Battery smoke or swelling": "Switch off, keep flames and sparks away, do not touch or disconnect it, move away, and request professional assistance.",
    "Collision damage": "Move only if required for immediate safety, call emergency services, avoid undeployed airbags/high-voltage components, and do not drive a structurally damaged vehicle.",
    "Flood exposure": "Do not start the vehicle; water can damage electrical, engine, airbag, and high-voltage systems. Arrange towing and inspection.",
}


def decode_minder(code: str) -> list[str]:
    cleaned = "".join(character for character in code.upper() if character.isalnum())
    return [f"{character}: {MAINTENANCE_MINDER[character]}" for character in cleaned if character in MAINTENANCE_MINDER]


def explain_obd(code: str) -> QuickResult:
    cleaned = code.upper().strip()
    if cleaned in OBD_CODES:
        meaning, caution = OBD_CODES[cleaned]
        return QuickResult(cleaned, "CAUTION", meaning, [caution, "Record freeze-frame data and all companion codes."], ["Stop for a flashing check-engine light, overheating, severe shaking, smoke, or loss of power."], "Diagnose the circuit/system before replacing a part.")
    return QuickResult(cleaned or "Unknown code", "UNKNOWN", "This code is not in the starter reference.", ["Confirm the exact five-character code and whether it is current, pending, or permanent."], ["Do not clear codes before recording diagnostic information."], "Use model-specific service information or professional diagnosis.")


def diagnose_question(vehicle: Vehicle, question: str) -> DiagnosticAssessment:
    """Return a useful safe diagnosis path for any non-empty car question."""
    text = question.lower().strip()
    matched: QuickResult | None = None
    causes: list[str] = []
    questions: list[str] = []

    if any(term in text for term in ("not start", "won't start", "wont start", "doesn't start", "does not start", "no start", "clicking when")):
        matched = SYMPTOMS["Car will not start"]
        causes = [
            "Weak or discharged 12-volt battery",
            "Loose or corroded battery connection",
            "Starter, starter relay, or related circuit fault",
            "Key/immobilizer recognition problem",
            "Fuel, ignition, or engine-management fault if the engine cranks normally",
        ]
        questions = [
            "Does the engine crank, click once, click rapidly, or remain completely silent?",
            "Do the dashboard and headlights appear normal, dim, or dead?",
            "Are there warning or key/immobilizer messages?",
            "Did this begin after the car sat, after battery work, or suddenly while driving?",
        ]
    elif any(term in text for term in ("leak", "fluid under", "puddle", "dripping")):
        matched = SYMPTOMS["Fluid under the car"]
        causes = ["Normal air-conditioning condensation", "Engine oil or coolant leak", "Washer-fluid leak", "Transmission or brake-system leak"]
        questions = ["What color and consistency is the fluid?", "Where is the puddle relative to the vehicle?", "Was the AC operating?", "Are any warning lights or odors present?"]
    elif any(term in text for term in ("overheat", "temperature", "steam", "hot engine")):
        matched = SYMPTOMS["Engine overheating"]
        causes = ["Low coolant from a leak", "Cooling-fan fault", "Thermostat or circulation fault", "Restricted radiator or airflow"]
        questions = ["Is there steam or visible coolant?", "Does it overheat while moving, idling, or both?", "Is the cabin heater producing heat?"]
    elif any(term in text for term in ("air condition", "ac ", "a/c", "not cooling", "no cold air")):
        matched = SYMPTOMS["AC not cooling"]
        causes = ["Restricted cabin filter", "Blower or airflow fault", "Refrigerant leak", "Compressor/control fault"]
        questions = ["Is airflow weak or simply not cold?", "Does cooling improve while driving?", "Are there unusual noises or odors?"]
    elif any(term in text for term in ("vibrat", "pulling", "pulls", "shake", "wobble")):
        matched = SYMPTOMS["Vibration or pulling"]
        causes = ["Incorrect tire pressure or tire damage", "Wheel balance or alignment", "Brake-related vibration", "Steering or suspension wear"]
        questions = ["At what speed does it occur?", "Does it happen during braking or acceleration?", "Is the steering wheel or the whole vehicle affected?"]
    elif any(term in text for term in ("smell", "noise", "sound", "squeak", "grind", "rattle", "knock")):
        matched = SYMPTOMS["Unusual smell or noise"]
        causes = ["Accessory, belt, brake, tire, exhaust, or engine-related source", "Loose trim or heat shield", "Electrical or fluid-related fault if an odor is present"]
        questions = ["When exactly does it occur?", "Where does it seem to come from?", "Does speed, braking, steering, blower use, or engine RPM change it?"]

    if matched:
        return DiagnosticAssessment(
            title=f"Diagnostic path: {matched.title}",
            confidence=0.90,
            urgency=matched.urgency,
            summary=matched.summary,
            possible_causes=causes,
            immediate_checks=matched.checks,
            follow_up_questions=questions,
            stop_conditions=matched.stop_conditions,
            driveability=("Do not continue driving until the stop conditions are ruled out." if matched.urgency in {"STOP", "URGENT"} else "Drive only if the vehicle behaves normally and no stop condition is present."),
            next_step=matched.next_step,
        )

    return DiagnosticAssessment(
        title="General Honda diagnostic starting point",
        confidence=0.45,
        urgency="UNKNOWN",
        summary=f"FixLens needs more observations to narrow this question for the {vehicle.year} Honda {vehicle.model}.",
        possible_causes=["More than one vehicle system may produce this symptom", "A model-specific inspection or scan may be necessary"],
        immediate_checks=["Note every warning light and message.", "Record when the problem happens and whether it is repeatable.", "Look for visible leaks, smoke, damage, loose parts, or unusual odors without touching hot or moving components.", "Retrieve OBD-II codes when a warning light is present."],
        follow_up_questions=["What exact symptom do you see, hear, or feel?", "When did it start and what changed immediately before it?", "Does it occur while starting, idling, accelerating, braking, steering, or using climate control?", "Are there warning lights, odors, leaks, smoke, or unusual temperatures?"],
        stop_conditions=["Stop driving for smoke, fuel odor, brake or steering loss, overheating, severe vibration, grinding, or an oil-pressure warning."],
        driveability="Driveability cannot be determined from the current description.",
        next_step="Answer the follow-up questions, upload a relevant photo, or schedule a Honda inspection.",
    )
