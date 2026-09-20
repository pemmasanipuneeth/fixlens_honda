"""FixLens — a safety-first visual maintenance assistant for Honda owners."""

from __future__ import annotations

import base64
import html
from io import BytesIO
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st
from PIL import Image

from fixlens.config import get_settings
from fixlens.diagnostics import (
    EMERGENCIES,
    SYMPTOMS,
    WARNING_LIGHTS,
    diagnose_question,
    decode_minder,
    explain_obd,
)
from fixlens.knowledge import sources_for_assessment, video_for
from fixlens.models import EvaluationRecord, Vehicle
from fixlens.storage import (
    evaluation_history,
    initialize_database,
    reminder_history,
    save_evaluation,
    save_reminder,
    save_vehicle,
    vehicle_history,
)
from fixlens.vision import (
    analyze_with_nebius,
    compare_repair_images,
    demo_assessment,
    text_maintenance_assessment,
)


ASSET_DIR = Path(__file__).resolve().parent / "assets"


def asset_data_url(path: Path) -> str:
    """Embed a local image so Streamlit CSS can use it without a static server."""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


BACKGROUND_IMAGE = asset_data_url(ASSET_DIR / "fixlens-automotive-background.png")
MODEL_BACKGROUNDS = {
    "Civic": ASSET_DIR / "background-civic-2025.png",
    "Accord": ASSET_DIR / "background-accord-2025.png",
    "CR-V": ASSET_DIR / "background-crv-2025.png",
}


st.set_page_config(
    page_title="FixLens — Honda Visual Care",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
:root {
  --ink:#12201d; --muted:#63736f; --red:#ff4f5e; --coral:#ff7868;
  --mint:#68dfbd; --aqua:#38bfc4; --cream:#fff8ef; --paper:#fffdf9;
  --line:rgba(18,32,29,.10); --shadow:0 20px 70px rgba(28,52,46,.10);
}
html, body, [class*="css"] {font-family:'DM Sans',sans-serif; color:var(--ink);}
.stApp {
  background:
    linear-gradient(180deg,rgba(255,253,249,.90) 0%,rgba(247,251,248,.93) 48%,rgba(255,250,244,.95) 100%),
    radial-gradient(circle at 4% 3%, rgba(104,223,189,.22), transparent 26rem),
    url("__BACKGROUND_IMAGE__") center top / cover fixed no-repeat;
  background-attachment:scroll,scroll,fixed;
}
header[data-testid="stHeader"] {background:transparent;}
[data-testid="stDecoration"] {display:none;}
.block-container {max-width:1240px; padding:1.25rem 2rem 5rem;}
h1,h2,h3 {font-family:'Manrope',sans-serif; letter-spacing:-.035em;}
.topbar {display:flex;align-items:center;justify-content:space-between;padding:.2rem 0 1.3rem;}
.brand {display:flex;align-items:center;gap:.8rem;font:800 1.15rem 'Manrope';}
.brand-mark {width:38px;height:38px;border-radius:13px;display:grid;place-items:center;color:#fff;
  background:linear-gradient(140deg,var(--red),var(--coral));box-shadow:0 9px 24px rgba(255,79,94,.28);}
.brand small {font:600 .68rem 'DM Sans';letter-spacing:.13em;color:var(--muted);display:block;text-transform:uppercase;}
.status-pill {padding:.52rem .8rem;border:1px solid rgba(29,127,105,.16);background:#effbf6;
 border-radius:999px;color:#19785f;font-size:.8rem;font-weight:700;}
.hero {position:relative;overflow:hidden;border-radius:34px;padding:3.15rem 3.2rem;color:#fff;
 background:linear-gradient(120deg,rgba(20,40,35,.98) 0%,rgba(31,93,80,.94) 60%,rgba(51,168,142,.88) 100%);box-shadow:var(--shadow);backdrop-filter:blur(10px);}
.hero:after {content:'';position:absolute;width:330px;height:330px;border:1px solid rgba(255,255,255,.17);
 border-radius:50%;right:-70px;top:-130px;box-shadow:0 0 0 52px rgba(255,255,255,.035),0 0 0 105px rgba(255,255,255,.025);}
.eyebrow {display:inline-flex;gap:.5rem;align-items:center;text-transform:uppercase;letter-spacing:.14em;
 font-size:.72rem;font-weight:800;color:#a8f2da;margin-bottom:1rem;}
.hero h1 {font-size:clamp(2.4rem,5vw,4.65rem);line-height:.98;margin:.1rem 0 1rem;max-width:760px;}
.hero p {font-size:1.08rem;line-height:1.7;max-width:630px;color:rgba(255,255,255,.78);margin:0;}
.hero-badges {display:flex;gap:.6rem;flex-wrap:wrap;margin-top:1.7rem;}
.hero-badge {border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.08);backdrop-filter:blur(10px);
 padding:.58rem .8rem;border-radius:999px;font-size:.78rem;font-weight:600;}
.section-kicker {margin-top:2.6rem;color:var(--red);font-weight:800;text-transform:uppercase;letter-spacing:.13em;font-size:.7rem;}
.section-title {font-size:2rem;margin:.3rem 0 .35rem;}
.section-copy {color:var(--muted);margin:0 0 1.4rem;}
.feature-grid {display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:1.5rem 0 2.5rem;}
.feature-card {padding:1.35rem;border:1px solid var(--line);border-radius:22px;background:rgba(255,255,255,.76);
 box-shadow:0 10px 35px rgba(30,60,51,.05);}
.feature-icon {font-size:1.45rem;background:var(--cream);border-radius:14px;width:44px;height:44px;display:grid;place-items:center;margin-bottom:.8rem;}
.feature-card b {font-family:'Manrope';display:block;margin-bottom:.32rem;}.feature-card span {color:var(--muted);font-size:.88rem;line-height:1.5;}
div[data-testid="stForm"] {border:1px solid var(--line);background:rgba(255,255,255,.84);border-radius:26px;
 padding:1.15rem 1.25rem 1.3rem;box-shadow:0 14px 44px rgba(25,52,44,.06);}
div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input, .stTextArea textarea {
 border-radius:13px!important;border-color:rgba(18,32,29,.12)!important;background:#fbfdfb!important;}
[data-testid="stFileUploaderDropzone"] {background:linear-gradient(135deg,#fff7f0,#f0fbf7)!important;
 border:1.5px dashed rgba(36,120,98,.35)!important;border-radius:20px!important;padding:1.2rem!important;}
.stButton button, .stFormSubmitButton button {border:0!important;border-radius:14px!important;font-weight:800!important;
 min-height:47px;background:linear-gradient(105deg,var(--red),var(--coral))!important;color:#fff!important;
 box-shadow:0 10px 25px rgba(255,79,94,.20)!important;transition:.2s transform,.2s box-shadow!important;}
.stButton button:hover,.stFormSubmitButton button:hover {transform:translateY(-2px);box-shadow:0 14px 30px rgba(255,79,94,.28)!important;}
[data-testid="stTabs"] [data-baseweb="tab-list"] {gap:.5rem;background:rgba(255,255,255,.65);padding:.4rem;border-radius:16px;width:max-content;}
[data-testid="stTabs"] button {border-radius:11px;padding:.3rem 1rem;}
.result-head {display:flex;align-items:center;justify-content:space-between;gap:1rem;background:#142823;color:#fff;
 padding:1.2rem 1.35rem;border-radius:22px;margin:1rem 0;}
.result-head h3 {margin:0;font-size:1.35rem}.result-head p {margin:.25rem 0 0;color:rgba(255,255,255,.65);font-size:.84rem;}
.confidence {background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.16);padding:.7rem 1rem;border-radius:15px;text-align:center;}
.confidence b {display:block;font:800 1.3rem 'Manrope';}.confidence small {color:#a8f2da;text-transform:uppercase;letter-spacing:.1em;}
.risk-LOW {background:#e6faf2;color:#12775c}.risk-MEDIUM {background:#fff5d9;color:#8a6210}
.risk-HIGH,.risk-CRITICAL {background:#ffe7e8;color:#b62938}.risk {display:inline-block;padding:.42rem .72rem;border-radius:999px;font-size:.74rem;font-weight:800;}
.info-card {height:100%;padding:1.15rem 1.2rem;border:1px solid var(--line);border-radius:20px;background:rgba(255,255,255,.84);}
.info-card h4 {font:800 1rem 'Manrope';margin:0 0 .75rem}.info-card ul {padding-left:1.1rem;margin:.2rem 0;color:#40514d;}
.info-card li {margin:.42rem 0;line-height:1.45}.step {display:flex;gap:.9rem;padding:1rem 0;border-bottom:1px solid var(--line);}
.step:last-child {border-bottom:0}.step-num {flex:0 0 34px;height:34px;border-radius:11px;background:#e7f8f2;color:#14745d;
 display:grid;place-items:center;font-weight:800}.step p {margin:.2rem 0;line-height:1.55;color:#334641;}
.source-card {padding:.85rem 1rem;border-left:3px solid var(--mint);background:#f5fbf8;border-radius:4px 14px 14px 4px;margin:.65rem 0;}
.source-card a {font-weight:800;color:#176e5b;text-decoration:none}.source-card small {display:block;color:var(--muted);margin-top:.2rem;}
.disclaimer {padding:1rem 1.1rem;border:1px solid rgba(255,160,93,.28);background:#fff7eb;border-radius:16px;color:#80532c;font-size:.84rem;line-height:1.55;}
.demo-ribbon {padding:.75rem 1rem;background:#fff2d7;color:#75520e;border-radius:14px;font-size:.84rem;font-weight:650;margin-bottom:1rem;}
@media (max-width:800px) {.stApp{background-position:62% top}.block-container{padding:1rem}.hero{padding:2.2rem 1.35rem}.feature-grid{grid-template-columns:1fr}.topbar{align-items:flex-start}.hero h1{font-size:2.6rem}}
</style>
"""
CSS = CSS.replace("__BACKGROUND_IMAGE__", BACKGROUND_IMAGE)
st.markdown(CSS, unsafe_allow_html=True)


def inject_vehicle_background(model: str, year: int) -> None:
    """Immediately switch the page backdrop to the selected Honda model family."""
    path = MODEL_BACKGROUNDS.get(model)
    if not path or not path.exists():
        return
    image_url = asset_data_url(path)
    st.markdown(
        f'<style>.stApp {{background:'
        f'linear-gradient(90deg,rgba(255,253,249,.82) 0%,rgba(247,251,248,.58) 52%,rgba(255,250,244,.16) 100%),'
        f'linear-gradient(180deg,rgba(255,255,255,.08) 0%,rgba(255,250,244,.44) 100%),'
        f'url("{image_url}") right top / cover fixed no-repeat !important;}}'
        f'div[data-testid="stForm"],.feature-card,.info-card{{background:rgba(255,255,255,.91)!important;'
        f'backdrop-filter:blur(16px);}}'
        f'@media(max-width:800px){{.stApp{{background:'
        f'linear-gradient(180deg,rgba(255,253,249,.58),rgba(255,250,244,.76)),'
        f'url("{image_url}") 68% top / cover fixed no-repeat !important;}}}}</style>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="display:inline-flex;align-items:center;gap:.55rem;margin:.3rem 0 1rem;'
        f'padding:.55rem .85rem;border-radius:999px;background:rgba(255,255,255,.84);'
        f'border:1px solid rgba(18,32,29,.10);box-shadow:0 8px 26px rgba(20,40,35,.08);'
        f'backdrop-filter:blur(12px);font-weight:800;font-size:.8rem;">'
        f'<span style="color:#ff4f5e;">●</span> Active vehicle: {year} Honda {esc(model)}</div>',
        unsafe_allow_html=True,
    )


def esc(value: object) -> str:
    return html.escape(str(value))


def bullet_card(title: str, items: list[str], icon: str) -> str:
    safe_items = "".join(f"<li>{esc(item)}</li>" for item in items) or "<li>None identified</li>"
    return f'<div class="info-card"><h4>{icon} {esc(title)}</h4><ul>{safe_items}</ul></div>'


def render_header() -> None:
    settings = get_settings()
    state = "Vision connected" if settings.vision_ready else "Demo mode"
    st.markdown(
        f"""<div class="topbar"><div class="brand"><span class="brand-mark">F</span>
        <div>FixLens<small>Honda visual care</small></div></div>
        <span class="status-pill">● {state}</span></div>""",
        unsafe_allow_html=True,
    )


def render_intro() -> None:
    st.markdown(
        """<section class="hero"><div class="eyebrow">✦ Visual care, grounded in safety</div>
        <h1>Your Honda.<br>Seen more clearly.</h1>
        <p>Upload a photo, describe what you notice, and get a careful component assessment,
        useful follow-up questions, and owner-appropriate next steps.</p>
        <div class="hero-badges"><span class="hero-badge">📷 Photo-guided</span>
        <span class="hero-badge">🛡️ Safety gated</span><span class="hero-badge">🔎 Source aware</span>
        <span class="hero-badge">🚘 Honda focused</span></div></section>
        <div class="feature-grid">
          <div class="feature-card"><div class="feature-icon">👁️</div><b>Evidence before guesses</b><span>Visible details are separated from possible diagnoses and uncertainty.</span></div>
          <div class="feature-card"><div class="feature-icon">🧰</div><b>Practical next steps</b><span>Get tools, preparation, checks, and low-risk owner guidance.</span></div>
          <div class="feature-card"><div class="feature-icon">⛔</div><b>Knows when to stop</b><span>High-risk systems are escalated instead of explained recklessly.</span></div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_assessment(assessment, vehicle: Vehicle, demo: bool) -> None:
    if demo:
        st.markdown(
            '<div class="demo-ribbon">🧪 Demo assessment — connect a Nebius vision model for genuine image analysis. The interface and safety workflow are fully active.</div>',
            unsafe_allow_html=True,
        )
    confidence = round(assessment.confidence * 100)
    st.markdown(
        f"""<div class="result-head"><div><span class="risk risk-{assessment.risk_level.value}">{assessment.risk_level.value} RISK</span>
        <h3>{esc(assessment.suspected_component.title())}</h3>
        <p>{vehicle.year} Honda {esc(vehicle.model)} · Image quality: {esc(assessment.image_quality)}</p></div>
        <div class="confidence"><b>{confidence}%</b><small>confidence</small></div></div>""",
        unsafe_allow_html=True,
    )
    st.write(assessment.summary)
    st.progress(confidence)
    if "cabin air filter" in assessment.suspected_component.lower():
        st.image(
            ASSET_DIR / "cabin-air-filter-location.png",
            caption=(
                "Typical cabin air-filter location behind the passenger glove box. "
                "The exact access method varies by Honda model and year."
            ),
            use_container_width=True,
        )
    left, right = st.columns(2)
    with left:
        st.markdown(bullet_card("What is visible", assessment.visible_evidence, "🔍"), unsafe_allow_html=True)
    with right:
        st.markdown(bullet_card("Questions before action", assessment.questions_needed, "💬"), unsafe_allow_html=True)

    st.markdown("#### Driveability guidance")
    st.info(assessment.safe_to_drive, icon="🚘")
    if assessment.requires_professional:
        st.error("This result is outside FixLens's owner-serviceable scope. Arrange professional Honda service.", icon="🧑‍🔧")

    if assessment.repair_steps:
        tool_col, material_col = st.columns(2)
        with tool_col:
            st.markdown(bullet_card("Tools", assessment.tools, "🧰"), unsafe_allow_html=True)
        with material_col:
            st.markdown(bullet_card("Materials", assessment.materials, "📦"), unsafe_allow_html=True)
        video = video_for(vehicle, assessment.suspected_component)
        st.markdown("#### Video walkthrough")
        if video["curated"]:
            if video["match_quality"] == "exact":
                st.success(
                    f"Direct match for your {vehicle.year} Honda {vehicle.model} · {video['creator']}",
                    icon="🎬",
                )
            else:
                st.warning(
                    f"General walkthrough · {video['creator']} · The layout may differ on your "
                    f"{vehicle.year} Honda {vehicle.model}. Verify every location and specification in the owner's manual.",
                    icon="🎬",
                )
            st.markdown(f"**{video['title']}**")
            st.video(video["url"])
            st.link_button(
                "Open this walkthrough on YouTube ↗",
                video["url"],
                use_container_width=True,
            )
        else:
            st.info(
                "FixLens does not yet have a reviewed exact-match video for this vehicle. "
                "Use the targeted search below and verify the model year, trim, and component before following a video.",
                icon="🎬",
            )
            st.link_button(
                video["title"] + " ↗",
                video["url"],
                use_container_width=True,
            )
            st.caption(f"YouTube search: {video['query']}")
        st.markdown("#### Guided procedure")
        steps = "".join(
            f'<div class="step"><span class="step-num">{index}</span><p>{esc(step)}</p></div>'
            for index, step in enumerate(assessment.repair_steps, 1)
        )
        st.markdown(f'<div class="info-card">{steps}</div>', unsafe_allow_html=True)

    checks, stops = st.columns(2)
    with checks:
        st.markdown(bullet_card("Verify afterward", assessment.verification_steps, "✅"), unsafe_allow_html=True)
    with stops:
        st.markdown(bullet_card("Stop conditions", assessment.stop_conditions, "🛑"), unsafe_allow_html=True)

    with st.expander("Sources and scope"):
        for source in sources_for_assessment(assessment.source_keys):
            st.markdown(
                f'<div class="source-card"><a href="{esc(source.url)}" target="_blank">{esc(source.title)} ↗</a>'
                f'<small>{esc(source.section)} · {esc(source.vehicle_scope)}</small></div>',
                unsafe_allow_html=True,
            )
        st.caption("Source links establish scope; the current starter corpus is not a factory service manual.")
    st.markdown(
        '<div class="disclaimer"><b>Important:</b> FixLens is an educational assistant, not a substitute for inspection by a qualified technician. Never work on a running or hot engine, and do not proceed when the vehicle, component, or procedure is uncertain.</div>',
        unsafe_allow_html=True,
    )


def render_service_options(vehicle: Vehicle, key_suffix: str) -> None:
    st.markdown("#### Need a Honda technician?")
    st.caption("Find an authorized Honda dealer or open Honda Owners to schedule service.")
    zip_code = st.text_input(
        "ZIP code or city (optional)",
        placeholder="90210 or Los Angeles, CA",
        key=f"service_location_{key_suffix}",
    )
    official, schedule, nearby = st.columns(3)
    official.link_button(
        "Find a Honda dealer ↗",
        "https://automobiles.honda.com/tools/dealership-locator",
        use_container_width=True,
    )
    schedule.link_button(
        "Schedule Honda service ↗",
        "https://owners.honda.com/service-maintenance/scheduler/",
        use_container_width=True,
    )
    query = f"Honda service center near {zip_code.strip()}" if zip_code.strip() else "Honda service center near me"
    nearby.link_button(
        "Nearby Honda service ↗",
        f"https://www.google.com/maps/search/?api=1&query={quote_plus(query)}",
        use_container_width=True,
    )


def render_diagnostic_assessment(diagnosis, vehicle: Vehicle) -> None:
    confidence = round(diagnosis.confidence * 100)
    urgency_class = "CRITICAL" if diagnosis.urgency in {"STOP", "URGENT"} else ("MEDIUM" if diagnosis.urgency == "CAUTION" else "LOW")
    st.markdown(
        f"""<div class="result-head"><div><span class="risk risk-{urgency_class}">{esc(diagnosis.urgency)}</span>
        <h3>{esc(diagnosis.title)}</h3><p>{vehicle.year} Honda {esc(vehicle.model)} · Diagnostic guidance, not a confirmed repair diagnosis</p></div>
        <div class="confidence"><b>{confidence}%</b><small>intent confidence</small></div></div>""",
        unsafe_allow_html=True,
    )
    st.write(diagnosis.summary)
    causes, questions = st.columns(2)
    with causes:
        st.markdown(bullet_card("Possible cause groups", diagnosis.possible_causes, "🧭"), unsafe_allow_html=True)
    with questions:
        st.markdown(bullet_card("Questions that narrow it", diagnosis.follow_up_questions, "💬"), unsafe_allow_html=True)
    st.markdown("#### Try these checks in order")
    checks = "".join(
        f'<div class="step"><span class="step-num">{index}</span><p>{esc(step)}</p></div>'
        for index, step in enumerate(diagnosis.immediate_checks, 1)
    )
    st.markdown(f'<div class="info-card">{checks}</div>', unsafe_allow_html=True)
    drive, stops = st.columns(2)
    with drive:
        st.markdown(bullet_card("Driveability", [diagnosis.driveability], "🚘"), unsafe_allow_html=True)
    with stops:
        st.markdown(bullet_card("Stop conditions", diagnosis.stop_conditions, "🛑"), unsafe_allow_html=True)
    st.info(diagnosis.next_step, icon="➡️")
    render_service_options(vehicle, "diagnosis")


def render_diagnose() -> None:
    st.markdown('<div class="section-kicker">Ask FixLens</div><h2 class="section-title">What is happening with your Honda?</h2><p class="section-copy">Ask any diagnostic or maintenance question in plain language. A photo is optional and should avoid plates, documents, faces, and personal information.</p>', unsafe_allow_html=True)
    vehicle_year_col, vehicle_model_col = st.columns(2)
    year = vehicle_year_col.selectbox(
        "Model year",
        list(range(2025, 2017, -1)),
        key="diagnose_year",
    )
    model = vehicle_model_col.selectbox(
        "Honda model",
        ["Civic", "Accord", "CR-V"],
        key="diagnose_model",
    )
    inject_vehicle_background(model, year)
    with st.form("diagnose_form"):
        trim = st.text_input("Trim (optional)", placeholder="EX, Sport, Touring…")
        d, e = st.columns(2)
        engine = d.text_input("Engine (optional)", placeholder="1.5L Turbo, 2.0L…")
        mileage = e.number_input("Mileage (optional)", min_value=0, max_value=500000, step=1000, value=None)
        category = st.selectbox(
            "What area do you think this is?",
            [
                "Not sure",
                "Engine air filter",
                "Cabin air filter",
                "Wiper blade",
                "Battery terminal",
                "12V battery replacement",
                "Flat tire / spare",
                "Exterior bulb",
                "Engine oil & filter",
                "Washer fluid",
                "Key fob battery",
                "Tire pressure",
            ],
        )
        symptoms = st.text_area(
            "Ask your question or describe the symptom",
            placeholder="Example: Why is my car not starting? I hear rapid clicking and the dashboard is dim.",
            height=105,
        )
        upload = st.file_uploader(
            "Upload a Honda component photo (optional)",
            type=["jpg", "jpeg", "png", "webp"],
            help="Add a photo for visual diagnosis, or leave this empty for a known maintenance task.",
        )
        submitted = st.form_submit_button("Get my guide  →", use_container_width=True)

    if upload:
        try:
            preview = Image.open(upload)
            st.image(preview, caption="Uploaded photo", width=520)
        except Exception:
            preview = None
            st.error("That image could not be opened. Try a JPG, PNG, or WebP file.")
    else:
        preview = None

    if submitted:
        if preview is None and category == "Not sure" and not symptoms.strip():
            st.warning(
                "Describe what you want to do, select a maintenance category, or upload a photo.",
                icon="💬",
            )
            return
        vehicle = Vehicle(year=year, model=model, trim=trim or "Unknown", engine=engine or "Unknown", mileage=mileage)
        settings = get_settings()
        try:
            with st.spinner("Inspecting visible details and applying safety rules…"):
                if preview is None:
                    assessment = text_maintenance_assessment(category, symptoms)
                    if assessment.suspected_component == "unidentified component":
                        st.session_state.diagnosis = diagnose_question(vehicle, symptoms)
                        st.session_state.vehicle = vehicle
                        st.session_state.result_type = "diagnosis"
                        st.session_state.assessment = None
                    demo = False
                elif settings.vision_ready:
                    assessment = analyze_with_nebius(preview.copy(), vehicle, symptoms)
                    demo = False
                else:
                    assessment = demo_assessment(category, symptoms)
                    demo = True
            if assessment is not None:
                st.session_state.assessment = assessment
                st.session_state.vehicle = vehicle
                st.session_state.demo_result = demo
                if assessment.suspected_component != "unidentified component":
                    st.session_state.result_type = "repair"
        except Exception as exc:
            st.error(f"The vision assessment could not be completed: {type(exc).__name__}: {exc}")

    if st.session_state.get("result_type") == "diagnosis" and st.session_state.get("diagnosis"):
        render_diagnostic_assessment(st.session_state.diagnosis, st.session_state.vehicle)
    elif st.session_state.get("assessment"):
        render_assessment(
            st.session_state.assessment,
            st.session_state.vehicle,
            st.session_state.get("demo_result", False),
        )
        render_service_options(st.session_state.vehicle, "repair")


def render_safety_center() -> None:
    st.markdown('<div class="section-kicker">Safety center</div><h2 class="section-title">Useful by design. Cautious by default.</h2><p class="section-copy">FixLens only gives procedural guidance for a narrow owner-serviceable scope.</p>', unsafe_allow_html=True)
    safe, inspect, blocked = st.columns(3)
    with safe:
        st.markdown(bullet_card("Guided", ["Air and cabin filters", "Wiper blades", "12V batteries", "Owner-replaceable bulbs", "Washer fluid", "Key-fob batteries", "Tire pressure"], "🟢"), unsafe_allow_html=True)
    with inspect:
        st.markdown(bullet_card("Guarded guidance", ["Oil and filter service", "Emergency spare-tire installation", "Tire wear inspection", "Fluid appearance", "Belts and hoses"], "🟠"), unsafe_allow_html=True)
    with blocked:
        st.markdown(bullet_card("Professional service", ["Airbags and SRS", "Brake fluid and brake repairs", "Steering and suspension", "Fuel systems", "Hybrid high voltage"], "🔴"), unsafe_allow_html=True)


def render_quick_result(result) -> None:
    urgency_colors = {"STOP": "🔴", "URGENT": "🟠", "CAUTION": "🟡", "NORMAL": "🟢", "UNKNOWN": "⚪"}
    st.markdown(f"### {urgency_colors.get(result.urgency, '⚪')} {result.title}")
    st.write(result.summary)
    left, right = st.columns(2)
    with left:
        st.markdown(bullet_card("Checks you can make", result.checks, "🔍"), unsafe_allow_html=True)
    with right:
        st.markdown(bullet_card("Stop conditions", result.stop_conditions, "🛑"), unsafe_allow_html=True)
    st.info(result.next_step, icon="➡️")


def render_quick_help() -> None:
    st.markdown('<div class="section-kicker">Everyday diagnostics</div><h2 class="section-title">Understand what your Honda is telling you.</h2><p class="section-copy">Warnings and symptoms are triaged without pretending one clue proves a diagnosis.</p>', unsafe_allow_html=True)
    warning_tab, symptom_tab, code_tab, minder_tab, verify_tab = st.tabs(
        ["Warning lights", "Symptoms", "OBD-II", "Maintenance Minder", "Before / after"]
    )
    with warning_tab:
        warning = st.selectbox("Choose a warning", list(WARNING_LIGHTS), key="warning_select")
        render_quick_result(WARNING_LIGHTS[warning])
    with symptom_tab:
        symptom = st.selectbox("What is happening?", list(SYMPTOMS), key="symptom_select")
        render_quick_result(SYMPTOMS[symptom])
    with code_tab:
        code = st.text_input("Enter an OBD-II code", placeholder="P0301", max_chars=8)
        if code:
            render_quick_result(explain_obd(code))
    with minder_tab:
        minder = st.text_input("Enter the Honda Maintenance Minder code", placeholder="B12", max_chars=8)
        if minder:
            decoded = decode_minder(minder)
            if decoded:
                st.markdown(bullet_card("Service indicated", decoded, "🗓️"), unsafe_allow_html=True)
                st.warning("Confirm every item in the owner's manual for the exact model year and engine.")
            else:
                st.info("That code is not in the starter reference. Confirm it on the instrument display and owner's manual.")
    with verify_tab:
        st.caption("Visual comparison can find obvious differences, but it cannot certify a repair as mechanically safe.")
        task = st.text_input("Completed task", placeholder="Replaced engine air filter")
        before_col, after_col = st.columns(2)
        before_file = before_col.file_uploader("Before photo", type=["jpg", "jpeg", "png", "webp"], key="before_photo")
        after_file = after_col.file_uploader("After photo", type=["jpg", "jpeg", "png", "webp"], key="after_photo")
        if st.button("Compare visible changes", use_container_width=True):
            if not before_file or not after_file or not task.strip():
                st.warning("Add the task plus both before and after photos.")
            elif not get_settings().vision_ready:
                st.warning("Configure a Nebius vision model to use before/after comparison.")
            else:
                try:
                    with st.spinner("Comparing visible details…"):
                        comparison = compare_repair_images(Image.open(before_file), Image.open(after_file), task)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(bullet_card("Visible changes", comparison.get("visible_changes", []), "👁️"), unsafe_allow_html=True)
                    with c2:
                        st.markdown(bullet_card("Possible concerns", comparison.get("possible_concerns", []), "⚠️"), unsafe_allow_html=True)
                    st.markdown(bullet_card("Checks still required", comparison.get("checks_to_perform", []), "✅"), unsafe_allow_html=True)
                    st.info(comparison.get("conclusion", "No conclusion returned."))
                except Exception as exc:
                    st.error(f"Comparison failed: {type(exc).__name__}: {exc}")


def render_emergency_mode() -> None:
    st.markdown('<div class="section-kicker">Emergency mode</div><h2 class="section-title">Safety first. Diagnosis later.</h2><p class="section-copy">If anyone is in immediate danger, call local emergency services now.</p>', unsafe_allow_html=True)
    issue = st.selectbox("What is happening?", list(EMERGENCIES), key="emergency_select")
    st.error(EMERGENCIES[issue], icon="🚨")
    st.markdown('<div class="disclaimer"><b>Do not rely on an app during an active emergency.</b> Move to safety when possible and follow emergency-services instructions.</div>', unsafe_allow_html=True)


def render_garage() -> None:
    st.markdown('<div class="section-kicker">My garage</div><h2 class="section-title">Keep your Hondas and maintenance in one place.</h2><p class="section-copy">Only the last six VIN characters are stored locally; a full VIN is not required.</p>', unsafe_allow_html=True)
    vehicle_tab, reminder_tab = st.tabs(["Vehicles", "Reminders"])
    with vehicle_tab:
        with st.form("garage_vehicle", clear_on_submit=True):
            cols = st.columns(3)
            nickname = cols[0].text_input("Nickname", placeholder="My Civic")
            year = cols[1].selectbox("Year", list(range(2026, 1999, -1)), key="garage_year")
            model = cols[2].selectbox("Model", ["Civic", "Accord", "CR-V", "HR-V", "Pilot", "Odyssey", "Ridgeline", "Other"], key="garage_model")
            trim = st.text_input("Trim", placeholder="Sport")
            engine = st.text_input("Engine", placeholder="2.0L")
            mileage = st.number_input("Mileage", min_value=0, max_value=1000000, value=None, step=1000)
            vin = st.text_input("VIN last 6 (optional)", max_chars=6)
            save = st.form_submit_button("Save vehicle", use_container_width=True)
        if save:
            if nickname.strip():
                save_vehicle(nickname.strip(), year, model, trim or "Unknown", engine or "Unknown", mileage, vin)
                st.success("Vehicle saved locally.")
            else:
                st.warning("Give the vehicle a nickname.")
        vehicles = vehicle_history()
        if vehicles:
            st.dataframe(pd.DataFrame(vehicles), hide_index=True, use_container_width=True)
    with reminder_tab:
        vehicles = vehicle_history()
        if not vehicles:
            st.info("Save a vehicle before adding reminders.")
        else:
            with st.form("garage_reminder", clear_on_submit=True):
                vehicle_name = st.selectbox("Vehicle", [v["nickname"] for v in vehicles])
                service = st.text_input("Service", placeholder="Rotate tires")
                due = st.number_input("Due mileage (optional)", min_value=0, max_value=1000000, value=None, step=1000)
                notes = st.text_area("Notes", placeholder="Check tread depth at the same time")
                add = st.form_submit_button("Add reminder", use_container_width=True)
            if add and service.strip():
                save_reminder(vehicle_name, service.strip(), due, notes.strip())
                st.success("Reminder added.")
            reminders = reminder_history()
            if reminders:
                st.dataframe(pd.DataFrame(reminders), hide_index=True, use_container_width=True)


def render_evaluation_lab() -> None:
    st.markdown('<div class="section-kicker">Week 6 evaluation lab</div><h2 class="section-title">Document the stress test.</h2><p class="section-copy">Record adversarial prompts and score whether FixLens stayed safe and useful.</p>', unsafe_allow_html=True)
    with st.form("evaluation_form", clear_on_submit=True):
        attack = st.selectbox("Attack family", ["Jailbreaking", "Prompt injection", "Obfuscation", "False certainty", "Hallucination", "Crescendo", "Social engineering", "PII extraction", "Overblocking"])
        prompt = st.text_area("Prompt tested", placeholder="Paste the exact adversarial prompt…")
        outcome = st.segmented_control("Outcome", ["PASS", "WARN", "FAIL"], default="PASS")
        reasoning = st.text_area("Reasoning and evidence", placeholder="What happened, why the score is justified, and what evidence was captured…")
        save = st.form_submit_button("Save evaluation", use_container_width=True)
    if save:
        if not prompt.strip() or not reasoning.strip():
            st.warning("Add the exact prompt and your reasoning before saving.")
        else:
            save_evaluation(EvaluationRecord(attack_family=attack, prompt=prompt.strip(), outcome=outcome or "PASS", reasoning=reasoning.strip()))
            st.success("Evaluation saved to the local FixLens test log.")
    history = evaluation_history()
    if history:
        st.dataframe(pd.DataFrame(history), hide_index=True, use_container_width=True)
    else:
        st.info("No stress-test results yet. Run the first attack and record what happens.")


initialize_database()
render_header()
render_intro()
diagnose_tab, quick_tab, emergency_tab, garage_tab, safety_tab, evaluation_tab = st.tabs(
    ["✦ Diagnose", "⚡ Quick help", "🚨 Emergency", "🚘 My garage", "🛡 Safety", "🧪 Evaluation"]
)
with diagnose_tab:
    render_diagnose()
with quick_tab:
    render_quick_help()
with emergency_tab:
    render_emergency_mode()
with garage_tab:
    render_garage()
with safety_tab:
    render_safety_center()
with evaluation_tab:
    render_evaluation_lab()
