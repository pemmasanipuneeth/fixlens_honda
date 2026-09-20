"""Small, source-aware Honda MVP knowledge layer.

This starter corpus intentionally covers only owner-serviceable tasks. It is not
a factory service manual and never supplies torque specifications or part numbers.
"""

from urllib.parse import quote_plus

from .models import Source, Vehicle


HONDA_SOURCES = {
    "honda_owners": Source(
        title="Honda Owner's Manuals & Warranties",
        section="Vehicle-specific manuals and maintenance guidance",
        url="https://owners.honda.com/vehicle-information/manuals",
        vehicle_scope="Honda vehicles; exact content varies by model year",
    ),
    "nhtsa_vpic": Source(
        title="NHTSA vPIC Vehicle API",
        section="VIN decoding and manufacturer-submitted vehicle attributes",
        url="https://vpic.nhtsa.dot.gov/api/",
        vehicle_scope="U.S.-market vehicles",
    ),
    "nhtsa_recalls": Source(
        title="NHTSA Recalls",
        section="Safety recall lookup",
        url="https://www.nhtsa.gov/recalls",
        vehicle_scope="U.S.-market vehicles",
    ),
}


SAFE_COMPONENTS = {
    "engine oil and filter": {
        "risk": "HIGH",
        "tools": [
            "Safety glasses and oil-resistant gloves",
            "Drain pan and funnel",
            "Correct socket and oil-filter tool",
            "Torque wrench",
            "Approved ramps or stands if under-vehicle access is required",
        ],
        "materials": [
            "Honda-specified oil type and quantity for the exact engine",
            "Compatible oil filter and new drain-plug sealing washer",
            "Container for recycling used oil",
        ],
        "steps": [
            "Confirm the exact engine, specified oil, capacity, filter, drain-plug washer, tightening specifications, and Maintenance Minder procedure in the model-year Honda manual.",
            "Park on a firm, level surface, set the parking brake, switch the engine off, and allow hot components to cool. Never work beneath a vehicle supported only by a jack.",
            "If access requires lifting, use only documented lift points and correctly rated ramps or stands. If you cannot do this confidently, stop and use professional service.",
            "Open the oil-fill cap, position the drain pan, remove the drain plug carefully, and allow the oil to drain without contacting hot oil or exhaust components.",
            "Fit a new sealing washer and reinstall the drain plug using the exact documented specification—never guess or rely on a generic value.",
            "Remove the old filter, confirm its gasket came off, clean the sealing surface, prepare the new filter as its instructions specify, and install it to the documented specification.",
            "Add less than the full documented capacity, wait, and check the dipstick on level ground. Add gradually until the level is correct; do not overfill.",
            "Run the engine briefly while checking for leaks, switch it off, wait, recheck the level, reinstall shields, and reset Maintenance Minder only after the service is complete.",
            "Recycle the used oil and filter through an approved collection facility; never pour automotive fluids onto the ground or into drains.",
        ],
        "verify": [
            "Oil level is within the marked range after the documented wait time",
            "No leak appears at the filter or drain plug",
            "Oil-pressure warning turns off normally",
            "Fill cap, dipstick, shields, and tools are accounted for",
        ],
    },
    "washer fluid": {
        "risk": "LOW",
        "tools": ["Funnel if needed"],
        "materials": ["Climate-appropriate automotive windshield-washer fluid"],
        "steps": [
            "Park, switch the vehicle off, set the parking brake, and let the engine bay cool.",
            "Locate the cap marked with the windshield-and-spray symbol; do not confuse it with coolant, brake-fluid, or other reservoirs.",
            "Open the cap and add approved washer fluid slowly without overfilling or spilling on electrical components.",
            "Close the cap securely and test the washers while ensuring the nozzles aim safely.",
        ],
        "verify": ["Correct reservoir was used", "Cap is secure", "Washers spray and wipers clear normally"],
    },
    "key fob battery": {
        "risk": "LOW",
        "tools": ["Small flat plastic pry tool or the mechanical key, as documented"],
        "materials": ["Exact replacement coin-cell battery shown in the owner's manual or existing fob"],
        "steps": [
            "Remove the mechanical key using the documented release.",
            "Open the fob only at the documented slot, protecting the case with a cloth and avoiding excessive force.",
            "Photograph the old battery orientation, then remove it without bending the contacts.",
            "Install the identical battery type in the same polarity orientation without touching both faces unnecessarily.",
            "Align the case halves, press them closed evenly, and reinstall the mechanical key.",
        ],
        "verify": ["Case is fully closed", "Buttons operate", "Vehicle locks, unlocks, and recognizes the fob"],
    },
    "tire pressure": {
        "risk": "LOW",
        "tools": ["Accurate tire-pressure gauge", "Air source if adjustment is needed"],
        "materials": [],
        "steps": [
            "Read the cold-tire pressure specification on the driver's-door-jamb placard; do not use the tire sidewall maximum as the target.",
            "Measure pressure when the tires are cold and the vehicle has been parked as recommended in the owner's manual.",
            "Remove one valve cap, press the gauge squarely onto the valve, and record the reading.",
            "Add or release air in small increments to reach the placard value, then recheck and reinstall the cap.",
            "Repeat for all road tires and inspect for damage or recurring pressure loss.",
        ],
        "verify": ["All cold pressures match the placard", "Valve caps are installed", "TPMS warning clears according to the manual"],
    },
    "engine air filter": {
        "risk": "LOW",
        "tools": ["Clean microfiber cloth", "Screwdriver only if the airbox uses screws"],
        "materials": ["Vehicle-compatible replacement engine air filter"],
        "steps": [
            "Park on level ground, switch the engine off, remove the key, and let the engine cool.",
            "Locate the air-filter housing using the vehicle owner's manual; do not rely on appearance alone.",
            "Photograph the housing and clip orientation before opening it.",
            "Release only the documented clips or screws and lift the cover without stressing attached wiring.",
            "Remove the old filter and compare its dimensions and seal with the replacement.",
            "Wipe loose debris from the housing without allowing debris into the intake opening.",
            "Install the filter in the documented orientation and fully reseat every clip or screw.",
        ],
        "verify": ["Airbox cover sits flush", "Every clip is secured", "No warning light appears after startup"],
    },
    "cabin air filter": {
        "risk": "LOW",
        "tools": ["Flashlight", "Clean gloves"],
        "materials": ["Vehicle-compatible replacement cabin air filter"],
        "steps": [
            "Switch the vehicle off and empty the glove box.",
            "Confirm the access procedure in the exact model-year owner's manual.",
            "Release the glove-box stops gently; stop if the damper or wiring is unclear.",
            "Note the airflow arrow on the existing filter before removal.",
            "Install a dimensionally identical filter in the documented airflow direction.",
            "Reattach the access cover, damper, and glove-box stops before testing operation.",
        ],
        "verify": ["Glove box opens normally", "Blower operates without unusual noise", "Filter cover is latched"],
    },
    "wiper blade": {
        "risk": "LOW",
        "tools": ["Towel to protect the windshield"],
        "materials": ["Correct-length, Honda-compatible replacement blade"],
        "steps": [
            "Turn the vehicle off and confirm the model-specific wiper maintenance position.",
            "Protect the windshield with a folded towel before lifting the arm.",
            "Lift one arm at a time and identify the existing connector style.",
            "Release the old blade without allowing the spring-loaded arm to strike the glass.",
            "Attach the compatible blade until the connector positively locks.",
            "Lower the arm gently and repeat on the other side if needed.",
        ],
        "verify": ["Blade is locked to the arm", "Blade clears the hood", "Washer test shows smooth, streak-free travel"],
    },
    "battery terminal": {
        "risk": "MEDIUM",
        "tools": ["Safety glasses", "Chemical-resistant gloves", "Battery-terminal brush"],
        "materials": ["Battery terminal cleaner approved for automotive use"],
        "steps": [
            "Keep the ignition off, remove the key, ventilate the area, and keep sparks or flames away.",
            "Inspect for a cracked, swollen, leaking, or frozen battery before touching the terminals.",
            "If only light external corrosion is present, follow the exact owner's-manual precautions and cleaner instructions.",
            "Do not disconnect terminals unless the exact vehicle procedure and radio/security implications are known.",
            "Keep cleaner and residue away from skin, paint, electrical connectors, and the battery vents.",
        ],
        "verify": ["No cleaner residue remains", "Terminal is secure", "Vehicle starts normally with no new warnings"],
    },
    "12-volt battery": {
        "risk": "MEDIUM",
        "tools": [
            "Safety glasses and chemical-resistant gloves",
            "Correct-size socket or wrench",
            "Battery-terminal puller only if the terminal is stuck",
        ],
        "materials": [
            "Exact vehicle-compatible 12-volt replacement battery",
            "Terminal protectant approved for automotive batteries",
        ],
        "steps": [
            "Park outside or in a well-ventilated area, select Park, set the parking brake, switch everything off, remove the key, and wait for vehicle electronics to shut down.",
            "Confirm the exact battery type, size, terminal orientation, and any Honda battery-registration or security requirements for the model year before disconnecting anything.",
            "Inspect for swelling, cracking, leakage, freezing, heat, or a sulfur odor. If any is present, do not handle the battery; arrange professional service.",
            "Photograph the cable routing and identify the negative and positive terminals. Disconnect the negative terminal first, isolate it so it cannot spring back, then disconnect the positive terminal.",
            "Remove the factory hold-down hardware while supporting it, then lift the battery upright using its handle. Batteries are heavy; get assistance if the lift is not comfortable.",
            "Clean only light external corrosion using battery-safe products, keeping residue away from paint, wiring, skin, and battery vents.",
            "Place the compatible replacement battery in the same orientation and reinstall the factory hold-down so the battery cannot move. Do not overtighten or guess a torque value.",
            "Reconnect the positive terminal first and the negative terminal last, then follow the exact Honda procedure for clock, windows, security, idle relearn, and warning indicators.",
        ],
        "verify": [
            "Battery is upright and cannot move",
            "Terminal clamps are fully seated and do not rotate by hand",
            "No cable is stretched, pinched, reversed, or near a moving part",
            "Vehicle starts normally and no new warning remains illuminated",
        ],
    },
    "spare tire": {
        "risk": "HIGH",
        "tools": [
            "Vehicle's factory jack",
            "Factory lug wrench",
            "Wheel chock",
            "Torque wrench for final tightening at the documented specification",
            "Reflective vest and warning triangle for roadside visibility",
        ],
        "materials": ["Inflated, compatible temporary spare or full-size wheel"],
        "steps": [
            "Move completely away from traffic to firm, level ground. Select Park, set the parking brake, switch on hazard lights, and keep passengers in a safe location.",
            "If the surface is soft, sloped, unstable, or exposed to traffic—or if you cannot identify the correct jack point—do not continue; call roadside assistance.",
            "Consult the exact model-year Honda owner's manual for the spare, tools, wheel-chock position, and reinforced lifting point. Never guess the lifting point.",
            "With the tire still on the ground, remove the wheel cover if applicable and loosen each lug nut slightly using a crossing pattern; do not remove them yet.",
            "Position only the specified factory jack at the documented reinforced point and raise the vehicle just enough for tire clearance. Never put any part of your body under a jack-supported vehicle.",
            "Remove the loosened lug nuts and wheel. Keep your body out of the vehicle's fall path and place the removed wheel flat away from traffic.",
            "Mount the compatible spare, install every lug nut by hand, and snug them gradually in a crossing pattern.",
            "Lower the vehicle fully, remove the jack, and tighten the lug nuts in a crossing pattern to the specification in the exact Honda manual. Do not let FixLens or a video guess the value.",
            "Check spare-tire pressure and observe every speed and distance restriction printed on the spare. Arrange tire repair and a professional torque recheck promptly.",
        ],
        "verify": [
            "Every lug nut is installed and tightened in a crossing pattern",
            "Spare is inflated and compatible",
            "Jack and tools are removed and secured",
            "No vibration, noise, warning, or instability occurs at low speed",
        ],
    },
    "exterior bulb": {
        "risk": "MEDIUM",
        "tools": ["Clean gloves", "Flashlight"],
        "materials": ["Exact model-year and lamp-position compatible bulb"],
        "steps": [
            "Switch all lights and the ignition off, remove the key, and allow the lamp to cool.",
            "Verify whether the lamp is owner-replaceable; many LED assemblies require dealer service.",
            "Use the exact owner's-manual access path and do not force trim, connectors, or covers.",
            "Handle halogen bulbs only by the base; never touch the glass.",
            "Install an identical specification bulb and fully reseal the weather cover.",
        ],
        "verify": ["Lamp illuminates", "Beam and signaling behavior are normal", "Weather cover is fully sealed"],
    },
}


def find_safe_guide(component: str) -> tuple[str | None, dict | None]:
    normalized = component.lower().replace("_", " ").strip()
    for key, guide in SAFE_COMPONENTS.items():
        if key in normalized or normalized in key:
            return key, guide
    return None, None


def sources_for_assessment(source_keys: list[str]) -> list[Source]:
    keys = source_keys or ["honda_owners", "nhtsa_recalls"]
    return [HONDA_SOURCES[key] for key in keys if key in HONDA_SOURCES]


CURATED_VIDEOS = [
    {
        "model": "Civic",
        "year_start": 2022,
        "year_end": 2025,
        "component": "cabin air filter",
        "title": "2022–2025 Honda Civic cabin air-filter replacement",
        "url": "https://www.youtube.com/watch?v=fr_yyYsN8JM",
        "creator": "How It's Fixed",
    },
    {
        "model": "Civic",
        "year_start": 2022,
        "year_end": 2025,
        "component": "engine air filter",
        "title": "2022–2025 Honda Civic engine air-filter replacement",
        "url": "https://www.youtube.com/watch?v=3B2nxT39bK8",
        "creator": "Friendly Mechanic",
    },
    {
        "model": "Civic",
        "year_start": 2022,
        "year_end": 2025,
        "component": "wiper blade",
        "title": "2022–2025 Honda Civic windshield-wiper replacement",
        "url": "https://www.youtube.com/watch?v=2TeYahTefSE",
        "creator": "YouTube automotive creator",
    },
    {
        "model": "Civic",
        "year_start": 2022,
        "year_end": 2024,
        "component": "engine oil and filter",
        "title": "2022–2024 Honda Civic 2.0L oil and filter change",
        "url": "https://www.youtube.com/watch?v=wW5m3OKhCDI",
        "creator": "YouTube automotive creator",
    },
    {
        "model": "Civic",
        "year_start": 2022,
        "year_end": 2025,
        "component": "key fob battery",
        "title": "2022–2025 Honda Civic key-fob battery replacement",
        "url": "https://www.youtube.com/watch?v=d20D42yJdUI",
        "creator": "FobBattery",
    },
    # Reviewed general videos ensure every owner-serviceable guide has one
    # direct walkthrough. Their locations/specifications must be checked
    # against the selected Honda's manual before work begins.
    {
        "model": None,
        "component": "spare tire",
        "title": "How to change a flat tire safely",
        "url": "https://www.youtube.com/watch?v=QjZ5ohr7sGA",
        "creator": "Cars.com",
    },
    {
        "model": None,
        "component": "tire pressure",
        "title": "How to check tire pressure correctly",
        "url": "https://www.youtube.com/watch?v=dn0ShsQRgho",
        "creator": "Michelin USA",
    },
    {
        "model": None,
        "component": "washer fluid",
        "title": "How to refill windshield-washer fluid",
        "url": "https://www.youtube.com/watch?v=KcyTLme8g0Q",
        "creator": "Helpful DIY",
    },
    {
        "model": None,
        "component": "exterior bulb",
        "title": "How to replace an owner-serviceable headlight bulb",
        "url": "https://www.youtube.com/watch?v=GcsNu_9_Di8",
        "creator": "O'Reilly Auto Parts",
    },
    {
        "model": None,
        "component": "12-volt battery",
        "title": "Honda Civic 12-volt battery replacement and terminal care",
        "url": "https://www.youtube.com/watch?v=R0BF-okEMcA",
        "creator": "YouTube automotive creator",
    },
    {
        "model": None,
        "component": "battery terminal",
        "title": "Honda Civic battery-terminal removal and cleaning",
        "url": "https://www.youtube.com/watch?v=R0BF-okEMcA",
        "creator": "YouTube automotive creator",
    },
]


def video_for(vehicle: Vehicle, component: str) -> dict:
    """Return the best reviewed direct video, preferring an exact vehicle match."""
    normalized = component.lower().replace("_", " ").strip()

    # Exact model/generation matches always win.
    for video in CURATED_VIDEOS:
        if (
            video["model"] == vehicle.model
            and video.get("year_start", vehicle.year) <= vehicle.year <= video.get("year_end", vehicle.year)
            and video["component"] in normalized
        ):
            return {**video, "curated": True, "match_quality": "exact"}

    # A reviewed general tutorial is still more useful than a results page,
    # but the UI must identify it as non-vehicle-specific.
    for video in CURATED_VIDEOS:
        if video["model"] is None and video["component"] in normalized:
            return {**video, "curated": True, "match_quality": "general"}

    # If the catalog has a reviewed tutorial for the task but not this Honda,
    # show that single video as a visual overview and label it non-exact.
    for video in CURATED_VIDEOS:
        if video["component"] in normalized:
            return {**video, "curated": True, "match_quality": "general"}

    query = f"{vehicle.year} Honda {vehicle.model} {normalized} replacement how to"
    return {
        "title": f"Find a {vehicle.year} Honda {vehicle.model} walkthrough",
        "url": f"https://www.youtube.com/results?search_query={quote_plus(query)}",
        "creator": "YouTube results for the exact vehicle and task",
        "curated": False,
        "match_quality": "search",
        "query": query,
    }
