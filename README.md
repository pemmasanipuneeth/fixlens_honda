# FixLens — Honda Visual Care

FixLens is a safety-first Streamlit prototype for inspecting photos of selected
Honda maintenance components. It combines a polished guided interface, optional
Nebius multimodal analysis, deterministic safety controls, and a Week 6 red-team
evaluation log.

The interface uses an original project-local automotive background at
`assets/fixlens-automotive-background.png`, embedded into the Streamlit CSS with
a translucent readability layer.

The Diagnose model selector also switches among project-local 2025 Civic,
Accord, and CR-V visual backgrounds. The selected year is retained in the active
vehicle context and all diagnostic, maintenance, and video routing.

Images are optional. A user can name a supported maintenance task—such as
changing a cabin air filter—and receive the grounded guide without uploading a
photo. Photos add visual assessment when diagnosis is needed.

## Supported MVP scope

- Honda Civic, Accord, and CR-V, model years 2018–2025
- Engine and cabin air filters
- Wiper blades
- Battery-terminal inspection
- Under-hood 12-volt battery replacement
- Emergency spare-tire installation with strict lifting safeguards
- Owner-replaceable exterior bulbs
- Engine oil and filter service with lifting safeguards
- Washer-fluid refill, key-fob battery replacement, and tire-pressure adjustment

Safety-critical brake-fluid, braking, steering, airbag, fuel-system, and
high-voltage procedures are deliberately escalated rather than presented as DIY
instructions. This boundary is part of the project's Week 6 guardrail design.

High-risk systems are escalated to a qualified technician and do not receive
procedural instructions.

## Run locally

```bash
cd "week 6/fixlens_honda"
python3 -m pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Without a configured Nebius vision model, FixLens runs in a clearly labeled demo
mode so the interface and safety workflow can be tested. Put secrets only in
`.env`; never commit that file.

## Configuration

```env
NEBIUS_API_KEY=...
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1/
NEBIUS_VISION_MODEL=<an image-capable model available to your account>
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=fixlens-honda
PINECONE_NAMESPACE=honda-mvp-v1
```

The starter build includes source-aware local guidance. Pinecone ingestion of
vehicle-specific Honda manual sections is the next data milestone.

## Daily-use features

- Warning-light triage and stop-driving conditions
- Symptom decision support for no-starts, leaks, overheating, AC issues,
  vibration, pulling, noises, and smells
- Starter OBD-II code explanations
- Honda Maintenance Minder decoding
- Emergency-response guidance
- Before/after photo comparison with Nebius vision
- Locally saved Honda vehicles and maintenance reminders
- Parts, tools, verification steps, and vehicle-specific YouTube routing for
  supported maintenance procedures
- Free-form diagnostic questions with likely cause groups, ordered safe checks,
  follow-up questions, driveability guidance, and stop conditions
- Official Honda dealer locator, Honda Owners appointment scheduler, and optional
  ZIP/city-based nearby Honda service search on diagnostic and repair results

The cabin-air-filter assessment includes an original educational location image
under `assets/cabin-air-filter-location.png`. It illustrates a common layout only;
users must confirm the exact access method for their Honda model and year.

Supported maintenance results also include a video walkthrough section. Reviewed
exact model-generation matches are embedded directly. When an exact match is not
available, FixLens embeds a reviewed general walkthrough and clearly labels it as
non-vehicle-specific so the user can verify the layout against the owner's manual.
