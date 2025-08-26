% Kenya SHIF Analyzer — Demo Runbook (Video Script + Shot List)

This runbook provides a step‑by‑step script to record a complete demo video of the Streamlit app. It includes a speaking script, shot list, and timing. Target duration: 8–12 minutes.

## Recording Setup
- Resolution: 1920×1080 (1080p), 30 fps.
- Mic: Any clean USB mic or headset mic.
- App window: Full‑screen browser with Streamlit app.
- Optional: Capture the terminal briefly when launching.
- Recommended: OBS Studio, Scene = “Desktop + Mic”.

## Pre‑Flight Checklist (1–2 min, off‑camera)
- Verify `.env` has `OPENAI_API_KEY`.
- Confirm the SHIF PDF exists at the project root: `TARIFFS TO THE BENEFIT PACKAGE TO THE SHI.pdf`.
- Start the app: `streamlit run streamlit_comprehensive_analyzer.py`.
- Ensure the sidebar shows PDF status “Ready”.

## Shot List + Script

1) Title + Purpose (0:00 – 0:40)
- Visual: App home, header visible.
- Script: “Welcome. This demo shows an end‑to‑end SHIF policy analyzer: robust PDF extraction, Kenya‑aware AI insights, and ready‑to‑download CSV/JSON outputs, all in one UI.”

2) PDF & Sidebar Tour (0:40 – 1:30)
- Visual: Hover over sidebar, show PDF size.
- Script: “The app auto‑loads the SHIF PDF from the repository. Here we see the file is ready. The sidebar provides actions: a legacy pattern pipeline and the Integrated Analyzer, which is the recommended flow with extended AI.”

3) Run Integrated Analyzer (1:30 – 3:00)
- Visual: Click “🧠 Run Integrated Analyzer (Extended AI)”; show progress.
- Script: “The Integrated Analyzer performs validated extraction for pages 1–18 and the annex, then runs extended AI analyses: quality/outliers, a rules contradiction map, batch service analysis, plus Kenya‑specific checks like facility‑level validation, alignment, and equity.”
- Note: If already run once, mention caching: “Analyses are cached to avoid repeated token costs.”

4) Dashboard Overview (3:00 – 4:00)
- Visual: Switch to “📊 Dashboard Overview”.
- Script: “We get KPIs across services, contradictions and gaps. This section also provides quick status and a comprehensive download area for CSV, JSON, and a ZIP bundle.”

5) Structured Rules (Task 1) (4:00 – 4:40)
- Visual: “📋 Task 1: Structured Rules” tab.
- Script: “Pages 1–18 are parsed with header‑aware logic and multi‑line merging. We see facility levels and tariff metrics. You can export the structured rules as CSV.”

6) Contradictions & Gaps (Task 2) (4:40 – 5:20)
- Visual: “🔍 Task 2: Contradictions & Coverage Gaps”.
- Script: “Policy contradictions and coverage gaps are summarized with severity and impact. High‑priority issues are highlighted.”

7) Kenya Context (Task 3) (5:20 – 5:40)
- Visual: “🌍 Task 3: Kenya/SHIF Context Integration”.
- Script: “This tab anchors analyses in Kenya’s 6‑tier system and county structure.”

8) Advanced Analytics (5:40 – 6:30)
- Visual: “📈 Advanced Analytics” tab.
- Script: “Deeper insight: tariff distributions, specialty coverage, rule complexity, and a simple policy coherence view.”

9) AI‑Powered Insights (6:30 – 8:30)
- Visual: “🤖 AI‑Powered Insights” tab.
- Sequence:
  - “Analyze Contradictions”: Run briefly; mention `.md` + CSV persistence.
  - “Analyze Coverage Gaps”: Same persistence behavior.
  - “Executive Policy Recommendations”: JSON or markdown output; saved to JSON/CSV.
  - “Predictive Scenario Analysis”: Enter a short scenario, run; results saved to JSON/CSV.
  - “Integrated Extended AI Outputs”: Show the expanders (annex quality, rules map, batch analysis, summaries, canonicalization, facility validation, alignment, equity).
- Script: “All AI outputs are cached and persisted. CSV breakouts make data easy to analyze in spreadsheets.”

10) Downloads (8:30 – 9:30)
- Visual: Back to “📊 Dashboard Overview” → “Download Generated Files”.
- Script: “Legacy outputs appear here, and integrated outputs are listed with download buttons: structured policy CSV, annex CSV, executive and predictive JSON/CSVs, and a ZIP bundle for everything.”

11) Wrap‑Up (9:30 – 10:00)
- Script: “That’s the Kenya SHIF Analyzer: robust extraction, clinical AI insights with Kenya context, and clean exports. It’s built to be repeatable, cached, and presentation‑ready.”

## Tips
- If the integrated run is complete, panels reuse cached results; mention this efficiency.
- When bandwidth is limited, avoid re‑running AI panels in the recording; instead, expand saved results.
- Keep narration crisp. Pause a second when switching tabs.

---

## Alternate Short Demo (3–4 minutes)
- Quick run of the Integrated Analyzer, then jump to Dashboard → Downloads, AI Insights overview, and a 30‑second wrap.

