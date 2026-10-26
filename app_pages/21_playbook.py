import streamlit as st

from lib.ui import hero, inject_css, section

inject_css()
hero("The bootcamp <em>playbook</em>", "What the most successful career-change programs actually do in the classroom - "
     "reverse-engineered and rebuilt inside Laksh. Hiring and placement services are intentionally left out until you're an expert.",
     eyebrow="Research · teaching patterns", quote_tags=["grind"])

st.info("Sources are the programs' own public pages (fetched October 2026) plus long-standing industry practice where noted. "
        "Outcome numbers are as each program reports them, not independently verified.", icon=":material/fact_check:")

PLAYBOOK = [
    {
        "name": "Launch School", "model": "Mastery-based learning (8-16+ months core, then Capstone)",
        "source": "https://launchschool.com/mastery",
        "patterns": [
            "**Replace time with mastery** - you move to the next topic only after passing an assessment, never because a week ended.",
            "**Local mastery before integration** - atomic concepts (A, B) must be mastered before compound ones (AB).",
            "**Assessments modeled on hiring** - 1-on-1 live coding, oral technical evaluations, take-home projects. \"There's no place to hide.\"",
            "**\"Not yet\" instead of fail**, with a mandatory wait before retaking.",
            "**Going back up the tree is normal** - refresh a faded prerequisite without stigma.",
            "**Measure hours, not milestones**; study sustainably, never cram; focus on things that don't change.",
            "**Three learning phases**: Explore (top-down, play) → Study (bottom-up, deconstruct, deliberate practice) → Professional (trade-offs, architecture).",
            "Pedagogy draws on Barbara Oakley, Carol Dweck, K. Anders Ericsson, Kathy Sierra and Henry Roediger III.",
        ],
        "laksh": [("Mastery gates with prerequisites, \"Not yet\" + 24h/72h waits", "app_pages/18_gates.py"),
                 ("Teach-back (oral-style) assessments", "app_pages/18_gates.py"),
                 ("Locked-in hours as the core metric", "app_pages/12_lock_in.py")],
    },
    {
        "name": "Le Wagon", "model": "~400-hour immersive, rated #1 across 6,000+ reviews",
        "source": "https://www.lewagon.com/how-it-works",
        "patterns": [
            "**Fixed daily rhythm**: lecture 9:00-10:30 → challenges with a buddy 10:30-17:00 → live correction 17:00-18:00.",
            "**Learning by doing** - most of the day is spent solving challenges, not listening.",
            "**Fast help** - live support with a target of under 10 minutes.",
            "**Live correction** at the end of each day: the teacher walks through the important challenges.",
            "**Real projects** that become the portfolio.",
        ],
        "laksh": [("Bootcamp-day schedule on Today's mission", "app_pages/15_mission.py"),
                 ("Auto-graded challenges + reference-solution review", "app_pages/19_challenge_lab.py")],
    },
    {
        "name": "Hack Reactor", "model": "16-week full-time beginner immersive, 14,000+ graduates",
        "source": "https://www.hackreactor.com/",
        "patterns": [
            "**Fundamentals first, AI as an accelerator** - use AI to unpack tough concepts, then explain them in your own code.",
            "**Debug AI-generated code like a professional**, and reflect critically on its limits.",
            "**Daily algorithmic warm-ups (\"toy problems\")** - a long-standing part of the immersive format (industry practice).",
        ],
        "laksh": [("Toy problem of the day", "app_pages/19_challenge_lab.py"),
                 ("Feynman debrief: explain it in your own words", "app_pages/15_mission.py")],
    },
    {
        "name": "App Academy", "model": "Zero-experience to software engineer; 4,500+ hired at 2,000+ companies",
        "source": "https://www.appacademy.io/",
        "patterns": [
            "Reports a **95% placement rate in New York** (2019 campus program, among graduates who job-searched).",
            "**Frequent, high-stakes assessments** that you must pass to continue - widely described by alumni (industry practice).",
            "**Productive struggle norms** - work on a problem for a set time before asking for help (common bootcamp practice).",
        ],
        "laksh": [("Exams, quizzes at 80%+, mastery gates", "app_pages/08_exams.py"),
                 ("The 20-minute rule before hints and solutions", "app_pages/19_challenge_lab.py")],
    },
    {
        "name": "Interview Kickstart", "model": "Interview & AI/ML upskilling taught by FAANG+ practitioners",
        "source": "https://www.interviewkickstart.com/how-it-works",
        "patterns": [
            "**\"NOT a list of interview questions\"** - the goal is to understand concepts deeply.",
            "**Mock interviews with real interviewers** and detailed feedback.",
            "**Train your brain to think and communicate under real interview conditions.**",
            "Rigor: successful alumni put in a few hours a day, every day.",
        ],
        "laksh": [("Timed interview gauntlet with model key points", "app_pages/17_gauntlet.py"),
                 ("Daily locked-in hours goal", "app_pages/12_lock_in.py")],
    },
    {
        "name": "Codesmith", "model": "Engineering training now delivered to enterprises and government",
        "source": "https://www.codesmith.io/",
        "patterns": [
            "**Define → Develop → Validate → Deploy → Measure.**",
            "**Validate demonstrated capability** through practical work, technical assessment and applied performance - not attendance.",
            "Curriculum built around **real technical work**.",
        ],
        "laksh": [("Mastery Index: only provable capability counts", "app_pages/13_career_stock.py"),
                 ("Capstone projects in the study plan", "app_pages/02_study_plan.py")],
    },
    {
        "name": "Wall Street analyst training", "model": "Bank training programs and providers like Wall Street Prep / Training The Street",
        "source": "https://www.wallstreetprep.com",
        "patterns": [
            "**Accounting first** - the three statements before any valuation (industry practice).",
            "**Build models from a blank sheet**, not templates.",
            "**Timed modeling tests** - paper LBOs in minutes, three-statement builds under a clock.",
            "Memorize IRR shortcuts (2x in 3 years ≈ 26%, 2x in 5 years ≈ 15%, 3x in 5 years ≈ 25%).",
        ],
        "laksh": [("Finance challenges incl. timed paper LBO", "app_pages/19_challenge_lab.py"),
                 ("F2 → F3 gate order (accounting before valuation)", "app_pages/18_gates.py")],
    },
    {
        "name": "Quant & trading firm preparation", "model": "How candidates prepare for prop-trading and quant screens",
        "source": "https://www.quantguide.io",
        "patterns": [
            "**Timed mental-math tests** (e.g. many questions in 8 minutes) are a common first screen (industry practice).",
            "**Daily probability and brain-teaser practice** (Heard on the Street, the \"Green Book\").",
            "**Market-making games and expected-value reasoning** under time pressure.",
        ],
        "laksh": [("Speed drills in trading-firm format", "app_pages/20_speed_drills.py"),
                 ("Quant brain teasers in the gauntlet", "app_pages/17_gauntlet.py")],
    },
]

section("The eight common patterns")
c = st.columns(4)
COMMON = [
    ("Mastery gates", "Advance on proof, not time."),
    ("Active practice > lectures", "Most of the day is spent doing."),
    ("Hiring-grade assessments", "Live, timed, no place to hide."),
    ("Productive struggle", "Effort before hints."),
    ("Tight feedback loops", "Tests, corrections, reviews daily."),
    ("Fixed daily rhythm", "Same structure every day removes decisions."),
    ("Explain to learn", "Teach-backs, oral exams, debriefs."),
    ("Real projects", "Portfolio-grade capstones."),
]
for i, (t, b) in enumerate(COMMON):
    with c[i % 4]:
        with st.container(border=True, height="stretch"):
            st.markdown(f"**{t}**")
            st.caption(b)

for p in PLAYBOOK:
    section(p["name"])
    st.caption(p["model"])
    left, right = st.columns([3, 2], gap="large")
    with left:
        for line in p["patterns"]:
            st.markdown(f"- {line}")
        st.link_button("Source", p["source"], icon=":material/open_in_new:")
    with right:
        with st.container(border=True):
            st.markdown("**Inside Laksh**")
            for label, page in p["laksh"]:
                st.page_link(page, label=label, icon=":material/arrow_forward:")

section("Deliberately not copied (yet)")
st.markdown("Job guarantees, hiring-partner networks, resume services and placement teams. Those come after the expertise - "
            "the route is becoming the best; the job is the consequence.")