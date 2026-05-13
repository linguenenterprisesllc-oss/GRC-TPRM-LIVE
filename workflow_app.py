import streamlit as st
import anthropic
import json
import re
import datetime

st.set_page_config(page_title="Live TPRM Workflow — OneTrust | Linguen Enterprises", page_icon="🛡️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600&family=Source+Serif+4:ital,wght@0,300;0,400;0,500;0,600;1,400&family=DM+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'Source Serif 4',Georgia,serif;}
[data-testid="stAppViewContainer"]{background-color:#f5f4f0;}
[data-testid="stHeader"]{background:transparent;}
[data-testid="stToolbar"]{display:none;}
[data-testid="stSidebar"]{display:none;}
.block-container{padding-top:0;padding-bottom:4rem;max-width:900px;}
.top-rule{height:4px;background:#1a2d4a;border-radius:1px;margin-bottom:2rem;}
h1,h2{font-family:'Playfair Display',Georgia,serif!important;color:#1a2d4a!important;}
h3{font-family:'Source Serif 4',serif!important;color:#1a1814!important;font-size:16px!important;}
.company-label{font-family:'DM Mono',monospace;font-size:11px;letter-spacing:.12em;color:#9a948a;text-transform:uppercase;margin-bottom:4px;}
.company-name{font-family:'Playfair Display',serif;font-size:20px;font-weight:600;color:#1a2d4a;margin-bottom:1.25rem;}
/* LIFECYCLE BAR */
.lifecycle-bar{display:flex;gap:4px;margin-bottom:6px;}
.lc-phase{flex:1;padding:6px 8px;text-align:center;font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.08em;color:#fff;font-weight:500;border-radius:3px 3px 0 0;transition:all .2s;}
.stage-bar{display:flex;gap:0;margin-bottom:2rem;border-radius:0 0 4px 4px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08);}
.stage-step{flex:1;padding:12px 4px;text-align:center;font-family:'DM Mono',monospace;font-size:9px;letter-spacing:.05em;text-transform:uppercase;border-right:2px solid rgba(255,255,255,.25);transition:all .2s;}
.stage-step:last-child{border-right:none;}
.stage-step .snum{font-family:'Playfair Display',serif;font-size:15px;font-weight:600;display:block;margin-bottom:2px;}
.stage-step .sname{font-size:9px;letter-spacing:.06em;}
/* Phase colors */
.irq-step   {background:#1a2d4a;color:rgba(255,255,255,.45);}
.dd-step    {background:#1a4a6b;color:rgba(255,255,255,.45);}
.appr-step  {background:#7a4f1a;color:rgba(255,255,255,.45);}
.stage-step.active{color:#fff!important;opacity:1;}
.stage-step.active::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;background:rgba(255,255,255,.5);}
.stage-step{position:relative;}
.stage-step.done{opacity:.65;}
.stage-step.locked{opacity:.3;}
/* CARDS */
.card{background:#fff;border:1px solid #ddd9d0;border-radius:4px;padding:1.5rem;margin-bottom:1rem;box-shadow:0 1px 3px rgba(0,0,0,.04);}
.card-green{background:#eaf4ee;border:1px solid #b8ddc8;border-left:3px solid #1a6b45;border-radius:4px;padding:1.25rem 1.5rem;margin-bottom:1rem;}
.card-blue{background:#eaf0f4;border:1px solid #b8cedd;border-left:3px solid #1a4a6b;border-radius:4px;padding:1.25rem 1.5rem;margin-bottom:1rem;}
.card-amber{background:#f4f0ea;border:1px solid #ddc8b8;border-left:3px solid #7a4f1a;border-radius:4px;padding:1.25rem 1.5rem;margin-bottom:1rem;}
.card-red{background:#f4eaea;border:1px solid #ddb8b8;border-left:3px solid #6b1a1a;border-radius:4px;padding:1.25rem 1.5rem;margin-bottom:1rem;}
.flabel{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.08em;color:#9a948a;text-transform:uppercase;margin-bottom:4px;}
.fval{font-size:14px;color:#1a1814;line-height:1.55;margin-bottom:1rem;}
.slabel{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.1em;color:#9a948a;text-transform:uppercase;margin-bottom:.75rem;}
.tier{display:inline-block;font-family:'DM Mono',monospace;font-size:11px;font-weight:500;padding:3px 12px;border-radius:2px;}
.tier-Critical{color:#6b1a1a;background:#f4eaea;border:1px solid #ddb8b8;}
.tier-High{color:#7a4f1a;background:#f4f0ea;border:1px solid #ddc8b8;}
.tier-Moderate{color:#1a4a6b;background:#eaf0f4;border:1px solid #b8cedd;}
.tier-Low{color:#1a6b45;background:#eaf4ee;border:1px solid #b8ddc8;}
.badge{display:inline-block;font-family:'DM Mono',monospace;font-size:10px;padding:2px 10px;border-radius:2px;}
.badge-received{color:#1a6b45;background:#eaf4ee;border:1px solid #b8ddc8;}
.badge-not-provided{color:#6b1a1a;background:#f4eaea;border:1px solid #ddb8b8;}
.vendor-header{background:#1a2d4a;border-radius:4px;padding:1.25rem 1.5rem;margin-bottom:1.5rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.75rem;}
.vendor-title{font-family:'Playfair Display',serif;font-size:20px;font-weight:600;color:#fff;}
.vendor-sub{font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,.5);letter-spacing:.08em;margin-top:3px;}
.stage-label{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.12em;color:#9a948a;text-transform:uppercase;margin-bottom:6px;}
.stage-title{font-family:'Playfair Display',serif;font-size:22px;font-weight:600;color:#1a2d4a;margin-bottom:.25rem;}
.stage-desc{font-size:14px;color:#9a948a;font-style:italic;margin-bottom:1.5rem;}
.irq-row{display:flex;justify-content:space-between;align-items:flex-start;padding:8px 0;border-bottom:1px solid #ddd9d0;gap:1rem;}
.irq-row:last-child{border-bottom:none;}
.irq-q{font-size:12px;color:#9a948a;font-family:'DM Mono',monospace;flex:1;}
.irq-a{font-size:13px;color:#1a1814;flex:1;text-align:right;}
.q-section{background:#fff;border:1px solid #ddd9d0;border-radius:4px;margin-bottom:1rem;overflow:hidden;}
.q-section-header{background:#f0eeea;padding:10px 1rem;font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.08em;color:#1a2d4a;text-transform:uppercase;border-bottom:1px solid #ddd9d0;}
.q-item{padding:10px 1rem;border-bottom:1px solid #ddd9d0;}
.q-item:last-child{border-bottom:none;}
.q-text{font-size:13px;color:#5a5650;margin-bottom:4px;}
.q-answer{font-size:13px;color:#1a1814;font-weight:500;}
.q-answer.gap{color:#6b1a1a;}
.gap-note{font-size:11px;color:#6b1a1a;margin-top:3px;font-family:'DM Mono',monospace;}
.finding-item{padding:10px 12px;background:#f4eaea;border:1px solid #ddb8b8;border-radius:3px;margin-bottom:6px;font-size:13px;}
.finding-label{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:.08em;color:#6b1a1a;text-transform:uppercase;margin-bottom:3px;}
.complete-banner{text-align:center;background:#1a2d4a;border-radius:4px;padding:2.5rem 2rem;margin:2rem 0;}
.complete-title{font-family:'Playfair Display',serif;font-size:28px;font-weight:600;color:#fff;margin-bottom:8px;}
.complete-sub{font-size:14px;color:rgba(255,255,255,.6);font-style:italic;}
div[data-testid="stTextInput"] input,div[data-testid="stTextArea"] textarea{background-color:#fff!important;border:1px solid #c8c3b8!important;border-radius:3px!important;color:#1a1814!important;font-family:'Source Serif 4',serif!important;}
div[data-testid="stTextInput"] input:focus,div[data-testid="stTextArea"] textarea:focus{border-color:#1a2d4a!important;box-shadow:0 0 0 3px rgba(26,45,74,.08)!important;}
div[data-testid="stSelectbox"]>div{background-color:#fff!important;border:1px solid #c8c3b8!important;color:#1a1814!important;}
div[data-testid="stCheckbox"] label{color:#1a1814!important;font-size:14px!important;}
.stButton>button{background-color:#1a2d4a!important;color:#fff!important;border:none!important;border-radius:3px!important;font-family:'Source Serif 4',serif!important;font-weight:500!important;padding:.5rem 1.5rem!important;}
.stButton>button:hover{background-color:#243d62!important;}
label,.stSelectbox label,.stTextArea label,.stTextInput label{color:#5a5650!important;font-size:13px!important;font-family:'Source Serif 4',serif!important;font-weight:500!important;}
[data-testid="stMarkdownContainer"] p{color:#5a5650;font-size:14px;}
hr{border-color:#ddd9d0!important;}
.dash-stat{background:#fff;border:1px solid #ddd9d0;border-radius:4px;padding:1.25rem;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.04);}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ──────────────────────────────────────────────────────────────────
VENDOR_NAME = "OneTrust"
VENDOR_DESC = "Privacy, Security & Data Governance Platform"
VENDOR_URL  = "onetrust.com"

TIERS = ["Low", "Moderate", "High", "Critical"]

QUESTIONNAIRES = [
    "SIG Lite", "SIG Core", "Custom Questionnaire", "CAIQ (Cloud Security Alliance)",
    "Privacy Questionnaire", "Cloud Security Questionnaire",
    "Business Resiliency Questionnaire", "Generative AI Questionnaire",
]
DOCUMENT_REQUESTS = [
    "Third-Party Audit Report (e.g. SOC 2 Type II)",
    "Third-Party Audit Certification (e.g. ISO 27001)",
    "External Penetration Test Report",
    "Certificate of Insurance",
    "Data Processing Addendum (DPA)",
    "PCI DSS Audit Report",
]

DATA_CLASS_OPTS = ["Internal", "Confidential", "Customer Confidential", "Confidential Sensitive"]
RECORD_OPTS     = ["0", "1–1,000", "1,001–10,000", "10,001–100,000", "100,001–500,000", "500,001–1,000,000", "1,000,000+"]
RISK_OPTS       = ["Low", "Medium", "High"]
APPROVAL_OPTS   = ["Approve", "Approve with Conditions", "Reject", "Defer — Additional Information Required"]

ONETRUST_PROFILE = """OneTrust (onetrust.com) is a leading privacy, security, data governance, and compliance management platform used by thousands of enterprises globally. It provides tools for privacy program management, consent management, data subject request (DSAR) automation, vendor risk management, cookie compliance, and regulatory compliance (GDPR, CCPA, HIPAA, and more). Cloud-based SaaS, processes significant volumes of customer PII and sensitive compliance data, integrates with third-party systems via APIs, serves legal/privacy/compliance/security teams. SOC 2 Type II certified, ISO 27001 certified, GDPR compliant. Data stored in AWS with multi-region support. Subprocessors include AWS, Salesforce, and various analytics tools. OneTrust has a published trust center at trust.onetrust.com."""

TIER_DEFS = """
LOW: Minimal/no sensitive data, no regulatory exposure, non-critical, no system access.
MODERATE: Limited sensitive data (internal), some regulatory awareness, limited integrations.
HIGH: Significant PII/PHI/financial data, meaningful regulatory scope, production access, business-critical.
CRITICAL: Highly sensitive data, privileged/production access, critical regulatory obligations, broad external impact.
"""

# ── SESSION STATE ──────────────────────────────────────────────────────────────
defaults = {
    "stage": 0,
    "irq_answers": {}, "irq_submitted": False,
    "use_case": "", "business_unit": "",
    "confirmed_tier": None, "assessor_notes": "",
    "selected_q": [], "selected_d": [],
    "vendor_responses": None,
    "student_findings": "",
    "risk_summary": "", "residual_tier": "",
    "ai_validation": None,
    "team_reviews": None,
    "approval_decision": None,
    "show_final_decision": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── API + PASSWORDS ────────────────────────────────────────────────────────────
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    st.error("⚠️ ANTHROPIC_API_KEY not configured in Streamlit secrets.")
    st.stop()
try:
    INSTRUCTOR_PASS = st.secrets.get("INSTRUCTOR_PASSWORD", "tprm2024")
except Exception:
    INSTRUCTOR_PASS = "tprm2024"

# ── HELPERS ────────────────────────────────────────────────────────────────────
def call_claude(prompt: str, max_tokens: int = 2000) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-5", max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()

def parse_json(raw: str) -> dict:
    return json.loads(re.sub(r"```json|```", "", raw).strip())

def tier_chip(t: str) -> str:
    cls = {"Critical":"tier-Critical","High":"tier-High","Moderate":"tier-Moderate","Low":"tier-Low"}.get(t,"tier-Low")
    return f'<span class="{cls}">{(t or "").upper()}</span>'

def rec_color(r: str) -> str:
    return {"Approve":"#1a6b45","Approve with Conditions":"#7a4f1a","Escalate to DPO":"#6b1a1a","Escalate to CISO":"#6b1a1a"}.get(r,"#9a948a")

def reset_app():
    for k, v in defaults.items():
        st.session_state[k] = v

def advance():
    st.session_state.stage += 1
    st.rerun()

def check_pw(pw: str) -> bool:
    return pw == INSTRUCTOR_PASS

# ── LIFECYCLE + STAGE BAR ──────────────────────────────────────────────────────
STAGE_DEFS = [
    {"label":"IRQ Submission",  "phase":"irq",  "phaseColor":"#1a2d4a"},
    {"label":"IRQ Review",      "phase":"irq",  "phaseColor":"#1a2d4a"},
    {"label":"DD Selection",    "phase":"dd",   "phaseColor":"#1a4a6b"},
    {"label":"Responses",       "phase":"dd",   "phaseColor":"#1a4a6b"},
    {"label":"Assessment",      "phase":"dd",   "phaseColor":"#1a4a6b"},
    {"label":"Risk Summary",    "phase":"dd",   "phaseColor":"#1a4a6b"},
    {"label":"Approvals",       "phase":"appr", "phaseColor":"#7a4f1a"},
]
PHASE_GROUPS = [
    {"name":"IRQ",          "color":"#1a2d4a", "steps":[0,1]},
    {"name":"Due Diligence","color":"#1a4a6b", "steps":[2,3,4,5]},
    {"name":"Approvals",    "color":"#7a4f1a", "steps":[6]},
]

def render_lifecycle():
    cur = st.session_state.stage
    # Lifecycle group bar
    lc_html = '<div class="lifecycle-bar">'
    for g in PHASE_GROUPS:
        all_done  = all(i < cur for i in g["steps"])
        any_active = any(i <= cur for i in g["steps"])
        bg = "#1a6b45" if all_done else g["color"]
        op = "1" if any_active else "0.35"
        lc_html += f'<div class="lc-phase" style="background:{bg};opacity:{op};">{g["name"]}</div>'
    lc_html += '</div>'

    # Step bar
    sb_html = '<div class="stage-bar">'
    for i, s in enumerate(STAGE_DEFS):
        status = "done" if i < cur else ("active" if i == cur else "locked")
        phase_cls = {"irq":"irq-step","dd":"dd-step","appr":"appr-step"}.get(s["phase"],"irq-step")
        sb_html += f'<div class="stage-step {phase_cls} {status}"><span class="snum">{i+1}</span><span class="sname">{s["label"]}</span></div>'
    sb_html += '</div>'
    st.markdown(lc_html + sb_html, unsafe_allow_html=True)

def inst_advance(label: str, key: str):
    """Render instructor password + advance button. Returns True if advanced."""
    st.markdown("---")
    st.markdown('<div style="background:#f0eeea;border:1px solid #ddd9d0;border-radius:4px;padding:1.25rem;"><div style="font-family:\'DM Mono\',monospace;font-size:10px;letter-spacing:.1em;color:#9a948a;text-transform:uppercase;margin-bottom:.75rem;">Instructor — Advance Stage</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2,1])
    with c1:
        pw = st.text_input("Password to advance", type="password", key=f"pw_{key}", label_visibility="collapsed", placeholder="Instructor password")
    with c2:
        if st.button(label, key=f"btn_{key}"):
            if check_pw(pw):
                return True
            else:
                st.error("Incorrect password.")
    st.markdown('</div>', unsafe_allow_html=True)
    return False

# ── PAGE HEADER ────────────────────────────────────────────────────────────────
st.markdown('<div class="top-rule"></div>', unsafe_allow_html=True)
st.markdown('<div class="company-label">Presented by</div><div class="company-name">Linguen Enterprises LLC</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="vendor-header">
  <div><div class="vendor-title">{VENDOR_NAME}</div><div class="vendor-sub">{VENDOR_DESC} &nbsp;·&nbsp; {VENDOR_URL}</div></div>
  <div style="text-align:right;"><div class="vendor-sub">LIVE TPRM WORKFLOW EXERCISE</div><div style="font-family:'DM Mono',monospace;font-size:11px;color:rgba(255,255,255,.5);margin-top:2px;">Instructor View · Linguen Enterprises</div></div>
</div>""", unsafe_allow_html=True)
render_lifecycle()

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 0 — IRQ SUBMISSION
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.stage == 0:
    st.markdown('<div class="stage-label">Stage 1 of 7</div><div class="stage-title">IRQ Submission</div><div class="stage-desc">Complete the Inherent Risk Questionnaire as the business owner requesting OneTrust.</div>', unsafe_allow_html=True)

    if st.session_state.irq_submitted:
        ans = st.session_state.irq_answers
        rows = "".join(f'<div class="irq-row"><div class="irq-q">{k.replace("_"," ").title()}</div><div class="irq-a">{v or "—"}</div></div>' for k,v in ans.items() if v and v != "— select —")
        st.markdown(f'<div class="card"><div class="slabel">Submitted IRQ — {VENDOR_NAME} · {st.session_state.business_unit}</div>{rows}</div>', unsafe_allow_html=True)
        if inst_advance("Advance to IRQ Review →", "s0"):
            advance()
    else:
        uc = st.text_input("Business purpose / use case for OneTrust", placeholder="e.g. We are procuring OneTrust to manage our privacy compliance program and handle DSARs...", value=st.session_state.use_case)
        bu = st.text_input("Business unit requesting this vendor", placeholder="e.g. Legal, Privacy, Compliance", value=st.session_state.business_unit)
        st.markdown("---")
        st.markdown("### Inherent Risk Questionnaire")

        a = {}
        a["use_plan"]             = uc
        a["nonpublic_data"]       = st.selectbox("1. Will this vendor be exposed to any non-public data?", ["— select —","Yes","No"])
        if a["nonpublic_data"] == "Yes":
            a["data_scope"]       = st.text_area("   If yes — describe in detail the data in scope", placeholder="Describe the specific non-public data...", height=80)
        else:
            a["data_scope"]       = "N/A"
        a["data_classification"]  = st.selectbox("2. What type of data will the third party be handling?", ["— select —"] + DATA_CLASS_OPTS)
        st.markdown('<p style="font-size:13px;color:#9a948a;font-style:italic;margin-bottom:1rem;">Vendor type: Cloud SaaS (pre-set for this exercise)</p>', unsafe_allow_html=True)
        a["service_type"]         = "Cloud SaaS"
        a["pii"]                  = st.selectbox("3. Will the vendor host, process, store or transmit PII?", ["— select —","Yes","No"])
        a["record_count"]         = st.selectbox("4. Estimated volume of records (PII, PHI, or PCI data) in scope for this engagement", ["— select —"] + RECORD_OPTS)
        a["phi"]                  = st.selectbox("5. Will the vendor host, process, store or transmit PHI?", ["— select —","Yes","No"])
        a["internal_access"]      = st.selectbox("6. Will the vendor have access to company internal systems, applications or networks?", ["— select —","Yes","No"])
        a["cloud_storage"]        = st.selectbox("7. Will the third party store data in the cloud?", ["— select —","Yes","No","Unknown"])
        a["ai_use"]               = st.selectbox("8. Will the vendor use AI to process or deliver these services?", ["— select —","Yes","No","Unknown"])
        a["conf_risk"]            = st.selectbox("9. Confidentiality Risk", ["— select —"] + RISK_OPTS)
        a["int_risk"]             = st.selectbox("10. Integrity Risk", ["— select —"] + RISK_OPTS)
        a["avail_risk"]           = st.selectbox("11. Availability Risk", ["— select —"] + RISK_OPTS)
        a["contact_name"]         = st.text_input("12. Vendor Contact Name", placeholder="e.g. Jane Smith")
        a["contact_email"]        = st.text_input("13. Vendor Contact Email", placeholder="e.g. jane@onetrust.com")

        if st.button("Submit IRQ →"):
            required = ["nonpublic_data","data_classification","pii","record_count","phi","internal_access","cloud_storage","ai_use","conf_risk","int_risk","avail_risk"]
            if a["nonpublic_data"] == "Yes": required.append("data_scope")
            empty = [k for k in required if not a.get(k) or a.get(k) == "— select —"]
            if not uc.strip(): st.error("Please enter the business use case.")
            elif empty: st.error("Please complete all required fields.")
            else:
                st.session_state.use_case = uc
                st.session_state.business_unit = bu
                st.session_state.irq_answers = a
                st.session_state.irq_submitted = True
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 1 — IRQ REVIEW
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == 1:
    st.markdown('<div class="stage-label">Stage 2 of 7</div><div class="stage-title">IRQ Review & Inherent Risk Confirmation</div><div class="stage-desc">Review the submitted IRQ as the TPRM assessor. Confirm the inherent risk tier and close the IRQ.</div>', unsafe_allow_html=True)

    ans = st.session_state.irq_answers
    rows = "".join(f'<div class="irq-row"><div class="irq-q">{k.replace("_"," ").title()}</div><div class="irq-a">{v or "—"}</div></div>' for k,v in ans.items() if v and v != "— select —")
    st.markdown(f'<div class="card"><div class="slabel">Submitted IRQ — {VENDOR_NAME}</div>{rows}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Assessor Review")
    tier_idx = (["— select —"] + TIERS).index(st.session_state.confirmed_tier) if st.session_state.confirmed_tier in TIERS else 0
    confirmed_tier = st.selectbox("Confirm inherent risk tier", ["— select —"] + TIERS, index=tier_idx)
    assessor_notes = st.text_area("Assessor notes", placeholder="Document observations, concerns, or justification for the risk tier...", height=120, value=st.session_state.assessor_notes)
    st.session_state.assessor_notes = assessor_notes
    if confirmed_tier != "— select —": st.session_state.confirmed_tier = confirmed_tier

    if inst_advance("Close IRQ & Kick Off Due Diligence →", "s1"):
        if not st.session_state.confirmed_tier: st.error("Please confirm the inherent risk tier first.")
        else: advance()

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 2 — DUE DILIGENCE SELECTION
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == 2:
    st.markdown('<div class="stage-label">Stage 3 of 7</div><div class="stage-title">Due Diligence Kickoff</div><div class="stage-desc">Select the questionnaires and document requests to send to OneTrust.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card"><div class="slabel">Confirmed Inherent Risk</div><div style="margin-bottom:{"8px" if st.session_state.assessor_notes else "0"}">{tier_chip(st.session_state.confirmed_tier or "")}</div>{"<div style=\'font-size:13px;color:#5a5650;margin-top:8px;\'>"+st.session_state.assessor_notes+"</div>" if st.session_state.assessor_notes else ""}</div>', unsafe_allow_html=True)

    st.markdown("### Select Questionnaires to Send")
    sel_q = []
    for q in QUESTIONNAIRES:
        if st.checkbox(q, value=q in st.session_state.selected_q, key=f"q_{q}"): sel_q.append(q)

    st.markdown("### Select Document Requests")
    sel_d = []
    for d in DOCUMENT_REQUESTS:
        if st.checkbox(d, value=d in st.session_state.selected_d, key=f"d_{d}"): sel_d.append(d)

    st.session_state.selected_q = sel_q
    st.session_state.selected_d = sel_d

    if inst_advance("Send to Vendor →", "s2"):
        if not sel_q and not sel_d: st.error("Please select at least one questionnaire or document request.")
        else: advance()

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 3 — VENDOR RESPONSES
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == 3:
    st.markdown('<div class="stage-label">Stage 4 of 7</div><div class="stage-title">Vendor Responses Received</div><div class="stage-desc">OneTrust has responded to your due diligence request. Review their questionnaire responses and document submissions.</div>', unsafe_allow_html=True)

    if st.session_state.vendor_responses is None:
        with st.spinner("Receiving vendor responses from OneTrust..."):
            q_list = "\n".join(f"- {q}" for q in st.session_state.selected_q)
            d_list = "\n".join(f"- {d}" for d in st.session_state.selected_d)
            prompt = f"""You are simulating vendor responses for a TPRM exercise. The vendor is OneTrust (onetrust.com).
{ONETRUST_PROFILE}
Questionnaires sent:\n{q_list}\nDocument requests:\n{d_list}
IMPORTANT: Generate exactly 4 Q&A pairs per questionnaire (not more). Keep answers concise — 1-2 sentences max. Include exactly 1 gap per questionnaire.
SOC 2 Type II, ISO 27001, DPA, Pen Test = Received. COI and PCI DSS = Not Provided.
Respond ONLY in valid JSON (no markdown, no extra text):
{{"questionnaire_responses":[{{"name":"name","responses":[{{"question":"short question","answer":"concise 1-2 sentence answer","hasGap":false,"gapNote":""}}]}}],"document_status":[{{"name":"name","status":"Received or Not Provided","note":"brief note"}}]}}"""
            try:
                st.session_state.vendor_responses = parse_json(call_claude(prompt, 5000))
            except Exception as e:
                st.error(f"Error generating vendor responses: {e}")
                st.stop()

    resp = st.session_state.vendor_responses
    for qr in resp.get("questionnaire_responses", []):
        st.markdown(f'<div class="q-section"><div class="q-section-header">{qr["name"]}</div>', unsafe_allow_html=True)
        for item in qr.get("responses", []):
            gap_cls = " gap" if item.get("hasGap") else ""
            gap_note = f'<div class="gap-note">⚠ {item.get("gapNote","")}</div>' if item.get("hasGap") else ""
            st.markdown(f'<div class="q-item"><div class="q-text">{item["question"]}</div><div class="q-answer{gap_cls}">{item["answer"]}</div>{gap_note}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Document Requests")
    rows = "".join(f'<div class="irq-row"><div class="irq-q">{d["name"]}</div><div style="text-align:right;"><span class="badge {"badge-received" if d["status"]=="Received" else "badge-not-provided"}">{d["status"]}</span><div style="font-size:11px;color:#9a948a;margin-top:3px;">{d.get("note","")}</div></div></div>' for d in resp.get("document_status", []))
    st.markdown(f'<div class="card">{rows}</div>', unsafe_allow_html=True)

    if inst_advance("Begin Assessment →", "s3"): advance()

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 4 — ASSESSMENT REVIEW
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == 4:
    st.markdown('<div class="stage-label">Stage 5 of 7</div><div class="stage-title">Assessment Review</div><div class="stage-desc">Document your findings — gaps, red flags, and areas requiring follow-up.</div>', unsafe_allow_html=True)

    resp = st.session_state.vendor_responses
    if resp:
        with st.expander("📋 Reference — Vendor Responses"):
            for qr in resp.get("questionnaire_responses", []):
                st.markdown(f"**{qr['name']}**")
                for item in qr.get("responses", []):
                    st.markdown(f"- *{item['question']}* → {item['answer']}{'  ⚠' if item.get('hasGap') else ''}")
            st.markdown("**Documents:**")
            for doc in resp.get("document_status", []):
                st.markdown(f"- {doc['name']}: **{doc['status']}**")

    findings = st.text_area("Findings, gaps, and red flags", value=st.session_state.student_findings, placeholder="List all gaps, red flags, missing documents, vague responses, and follow-up items...", height=250)
    st.session_state.student_findings = findings

    if inst_advance("Advance to Risk Summary →", "s4"):
        if not findings.strip(): st.error("Please document findings before advancing.")
        else: advance()

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 5 — RISK SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == 5:
    st.markdown('<div class="stage-label">Stage 6 of 7</div><div class="stage-title">Risk Assessment Summary</div><div class="stage-desc">Write the final risk assessment. AI will validate it against OneTrust\'s profile and your findings.</div>', unsafe_allow_html=True)

    if st.session_state.ai_validation:
        val = st.session_state.ai_validation
        vc = {"Excellent":"#1a6b45","Good":"#1a4a6b","Needs Improvement":"#7a4f1a","Incomplete":"#6b1a1a"}.get(val.get("summaryQuality",""), "#9a948a")
        st.markdown(f'<div class="card" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;"><div><div style="font-family:\'Playfair Display\',serif;font-size:16px;font-weight:500;color:{vc};">{val.get("summaryQuality","")}</div><div style="font-size:12px;color:#9a948a;margin-top:3px;">Risk Assessment Quality</div></div><div style="display:flex;gap:16px;flex-wrap:wrap;"><div><div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#9a948a;margin-bottom:3px;">YOU CONCLUDED</div>{tier_chip(val.get("studentResidualTier",""))}</div><div><div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#9a948a;margin-bottom:3px;">AI ASSESSMENT</div>{tier_chip(val.get("recommendedResidualTier",""))}</div></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><div class="slabel">What you got right</div><p style="color:#5a5650;font-size:14px;line-height:1.65;">{val.get("whatRight","")}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card"><div class="slabel">What you missed</div><p style="color:#5a5650;font-size:14px;line-height:1.65;">{val.get("whatMissed","")}</p></div>', unsafe_allow_html=True)
        risks_html = "".join(f'<div class="finding-item"><div class="finding-label">Risk Factor</div>{r}</div>' for r in val.get("keyRisks",[]))
        st.markdown(f'<div class="card-red"><div class="slabel">Key Risk Factors</div>{risks_html}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card-green"><div class="slabel">Model Risk Assessment Summary</div><p style="color:#5a5650;font-size:14px;line-height:1.65;">{val.get("modelSummary","")}</p></div>', unsafe_allow_html=True)
        controls_html = "".join(f'<div style="padding:6px 0;border-bottom:1px solid #b8ddc8;font-size:13px;color:#1a1814;">→ {r}</div>' for r in val.get("recommendedControls",[]))
        st.markdown(f'<div class="card-green"><div class="slabel">Recommended Controls</div>{controls_html}</div>', unsafe_allow_html=True)
        if inst_advance("Advance to Approvals →", "s5"): advance()
    else:
        with st.expander("📋 Reference — Your Findings"):
            st.markdown(st.session_state.student_findings)
        summary = st.text_area("Risk Assessment Summary", value=st.session_state.risk_summary, placeholder="Include: overall risk narrative, inherent risk tier, key risks, residual risk tier, recommended controls, and recommendation (Approve / Approve with conditions / Reject)", height=300)
        st.session_state.risk_summary = summary
        residual_tier = st.selectbox("Your residual risk determination", ["— select —"] + TIERS)

        if st.button("Submit for AI Validation →"):
            if not summary.strip() or residual_tier == "— select —":
                st.error("Please complete your summary and select a residual risk tier.")
            else:
                with st.spinner("Validating your risk assessment..."):
                    resp = st.session_state.vendor_responses or {}
                    gaps = ", ".join([i["gapNote"] for qr in resp.get("questionnaire_responses",[]) for i in qr.get("responses",[]) if i.get("hasGap")]) or "None"
                    not_provided = ", ".join([d["name"] for d in resp.get("document_status",[]) if d["status"]=="Not Provided"]) or "None"
                    prompt = f"""You are a senior TPRM analyst validating a risk assessment for OneTrust.
{ONETRUST_PROFILE}
{TIER_DEFS}
Inherent Risk: {st.session_state.confirmed_tier} | Questionnaires: {', '.join(st.session_state.selected_q)}
Documents not provided: {not_provided} | Gaps: {gaps}
Student findings: {st.session_state.student_findings}
Student summary: {summary} | Student residual tier: {residual_tier}
Respond ONLY in valid JSON (no markdown):
{{"summaryQuality":"Excellent|Good|Needs Improvement|Incomplete","studentResidualTier":"{residual_tier}","recommendedResidualTier":"Low|Moderate|High|Critical","whatRight":"2-3 sentences","whatMissed":"2-4 sentences","keyRisks":["3-5 key risk factors"],"modelSummary":"4-5 sentence professional summary","recommendedControls":["4-6 specific controls"]}}"""
                    try:
                        st.session_state.ai_validation = parse_json(call_claude(prompt, 2000))
                        st.session_state.residual_tier = residual_tier
                        st.rerun()
                    except Exception as e:
                        st.error(f"Validation error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# STAGE 6 — APPROVALS (Parallel Privacy + Security Engineering reviews)
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == 6:
    tier = st.session_state.ai_validation.get("recommendedResidualTier") if st.session_state.ai_validation else st.session_state.residual_tier or "Moderate"
    tier_colors = {"Critical":"#6b1a1a","High":"#7a4f1a","Moderate":"#1a4a6b","Low":"#1a6b45"}
    tc = tier_colors.get(tier,"#1a4a6b")

    if st.session_state.approval_decision:
        # Show closed record
        d = st.session_state.approval_decision
        pr = (st.session_state.team_reviews or {}).get("privacyReview",{})
        sr = (st.session_state.team_reviews or {}).get("securityReview",{})
        dec_color = {"Approve":"#1a6b45","Approve with Conditions":"#7a4f1a","Reject":"#6b1a1a","Defer — Additional Information Required":"#1a4a6b"}.get(d["decision"],"#9a948a")
        st.markdown('<div class="complete-banner"><div class="complete-title">Workflow Closed</div><div class="complete-sub">OneTrust · TPRM Exercise · Linguen Enterprises LLC</div></div>', unsafe_allow_html=True)
        rows = f"""<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem 2rem;">
          <div><div class="flabel">Vendor</div><div class="fval">OneTrust</div></div>
          <div><div class="flabel">Final Decision</div><div class="fval"><strong style="color:{dec_color};">{d["decision"]}</strong></div></div>
          <div><div class="flabel">Inherent Risk</div><div class="fval">{tier_chip(st.session_state.confirmed_tier or "")}</div></div>
          <div><div class="flabel">Residual Risk</div><div class="fval">{tier_chip(tier)}</div></div>
          <div><div class="flabel">Approver</div><div class="fval">{d["approver"]}</div></div>
          <div><div class="flabel">Date</div><div class="fval">{d["date"]}</div></div>
          {"<div style='grid-column:span 2;'><div class='flabel'>Conditions / Notes</div><div class='fval'>" + d["conditions"] + "</div></div>" if d.get("conditions") else ""}
        </div>"""
        st.markdown(f'<div class="card"><div class="slabel">Final Record</div>{rows}</div>', unsafe_allow_html=True)
        pr_rec = pr.get("recommendation","")
        sr_rec = sr.get("recommendation","")
        team_rows = f"""
        <div style="padding:10px 0;border-bottom:1px solid #ddd9d0;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
          <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#1a4a6b;letter-spacing:.06em;">PRIVACY TEAM</div><div style="font-size:12px;color:#9a948a;margin-top:2px;">{pr.get("reviewer","")}</div></div>
          <span style="font-family:'DM Mono',monospace;font-size:11px;color:{rec_color(pr_rec)};background:{rec_color(pr_rec)}18;border:1px solid {rec_color(pr_rec)}40;padding:2px 10px;border-radius:2px;">{pr_rec.upper()}</span>
        </div>
        <div style="padding:10px 0;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
          <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#7a4f1a;letter-spacing:.06em;">SECURITY ENGINEERING</div><div style="font-size:12px;color:#9a948a;margin-top:2px;">{sr.get("reviewer","")}</div></div>
          <span style="font-family:'DM Mono',monospace;font-size:11px;color:{rec_color(sr_rec)};background:{rec_color(sr_rec)}18;border:1px solid {rec_color(sr_rec)}40;padding:2px 10px;border-radius:2px;">{sr_rec.upper()}</span>
        </div>"""
        st.markdown(f'<div class="card"><div class="slabel">Team Review Summary</div>{team_rows}</div>', unsafe_allow_html=True)
        st.markdown("---")
        with st.expander("🔒 Instructor — Reset Exercise"):
            pw = st.text_input("Password to reset", type="password", key="pw_reset", label_visibility="collapsed", placeholder="Instructor password")
            if st.button("Reset All Stages"):
                if check_pw(pw): reset_app(); st.rerun()
                else: st.error("Incorrect password.")
        st.stop()

    st.markdown('<div class="stage-label">Stage 7 of 7 — Approvals</div><div class="stage-title">Parallel Team Reviews</div><div class="stage-desc">The risk assessment has triggered parallel reviews from Privacy and Security Engineering. Both teams are reviewing simultaneously.</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="card" style="border-left:4px solid {tc};"><div class="slabel">Risk Posture Triggering Review</div><div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">{tier_chip(st.session_state.confirmed_tier or "")} <span style="color:#9a948a;font-size:18px;">→</span> {tier_chip(tier)}</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card" style="border-top:3px solid #1a4a6b;"><div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#1a4a6b;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">Privacy Team</div><div style="font-family:\'Playfair Display\',serif;font-size:15px;color:#1a2d4a;margin-bottom:6px;">Privacy Review</div><p style="font-size:12px;color:#9a948a;line-height:1.55;">Reviews data handling, GDPR/CCPA, DPA adequacy, consent mechanisms, and data subject rights obligations.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card" style="border-top:3px solid #7a4f1a;"><div style="font-family:\'DM Mono\',monospace;font-size:10px;color:#7a4f1a;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">Security Engineering</div><div style="font-family:\'Playfair Display\',serif;font-size:15px;color:#1a2d4a;margin-bottom:6px;">Security Review</div><p style="font-size:12px;color:#9a948a;line-height:1.55;">Reviews technical controls, access management, encryption, pen test, integration security, and architecture.</p></div>', unsafe_allow_html=True)

    if st.session_state.team_reviews is None:
        with st.spinner("Both teams are reviewing OneTrust's profile..."):
            resp = st.session_state.vendor_responses or {}
            gaps = ", ".join([i["gapNote"] for qr in resp.get("questionnaire_responses",[]) for i in qr.get("responses",[]) if i.get("hasGap")]) or "None"
            not_provided = ", ".join([d["name"] for d in resp.get("document_status",[]) if d["status"]=="Not Provided"]) or "None"
            controls = "; ".join(st.session_state.ai_validation.get("recommendedControls",[]) if st.session_state.ai_validation else [])
            prompt = f"""You are simulating parallel team reviews for a TPRM exercise. Vendor: OneTrust.
{ONETRUST_PROFILE}
Inherent Risk: {st.session_state.confirmed_tier} | Residual Risk: {tier}
Documents not provided: {not_provided} | Gaps: {gaps} | Recommended controls: {controls}
Student findings: {st.session_state.student_findings}
Generate realistic parallel reviews from Privacy Team and Security Engineering. Each team focuses on their domain. Include 1-2 real concerns even if approving — make it instructive.
Respond ONLY in valid JSON (no markdown):
{{"privacyReview":{{"reviewer":"name and title","summary":"2-3 sentence assessment","findings":["3-4 privacy findings"],"conditions":["1-3 required actions"],"recommendation":"Approve or Approve with Conditions or Escalate to DPO","recommendationNote":"1 sentence"}},"securityReview":{{"reviewer":"name and title","summary":"2-3 sentence assessment","findings":["3-4 security findings"],"conditions":["1-3 required actions"],"recommendation":"Approve or Approve with Conditions or Escalate to CISO","recommendationNote":"1 sentence"}}}}"""
            try:
                st.session_state.team_reviews = parse_json(call_claude(prompt, 2000))
                st.rerun()
            except Exception as e:
                st.error(f"Error generating team reviews: {e}")
                st.stop()
    else:
        pr = st.session_state.team_reviews.get("privacyReview",{})
        sr = st.session_state.team_reviews.get("securityReview",{})

        def team_card(review, label, accent):
            findings = "".join(f'<div style="padding:6px 0;border-bottom:1px solid #ddd9d0;font-size:13px;color:#5a5650;">• {f}</div>' for f in review.get("findings",[]))
            conditions = "".join(f'<div style="padding:5px 0;font-size:13px;color:#1a1814;border-bottom:1px solid #ddc8b8;">→ {c}</div>' for c in review.get("conditions",[]))
            rec = review.get("recommendation","")
            rc = rec_color(rec)
            return f"""<div class="card" style="border-top:3px solid {accent};">
              <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:1rem;">
                <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:{accent};letter-spacing:.08em;text-transform:uppercase;margin-bottom:3px;">{label}</div>
                <div style="font-size:13px;font-weight:500;color:#9a948a;">{review.get("reviewer","")}</div></div>
                <span style="font-family:'DM Mono',monospace;font-size:11px;color:{rc};background:{rc}18;border:1px solid {rc}40;padding:2px 10px;border-radius:2px;">{rec.upper()}</span>
              </div>
              <p style="font-size:14px;color:#5a5650;line-height:1.65;margin-bottom:1rem;font-style:italic;">"{review.get("summary","")}"</p>
              <div class="slabel">Findings</div><div style="margin-bottom:1rem;">{findings}</div>
              <div class="slabel" style="color:#7a4f1a;">Conditions Required</div>
              <div style="background:#f4f0ea;border:1px solid #ddc8b8;border-radius:3px;padding:.75rem 1rem;">{conditions}</div>
              <p style="font-size:12px;color:#9a948a;margin-top:.75rem;font-style:italic;">{review.get("recommendationNote","")}</p>
            </div>"""

        st.markdown(team_card(pr, "Privacy Team", "#1a4a6b"), unsafe_allow_html=True)
        st.markdown(team_card(sr, "Security Engineering", "#7a4f1a"), unsafe_allow_html=True)

        if not st.session_state.get("show_final_decision"):
            if inst_advance("Record Final Approval Decision →", "s6"):
                st.session_state.show_final_decision = True
                st.rerun()
        else:
            st.markdown("---")
            st.markdown("### Final Approval Decision")
            pr_rec = pr.get("recommendation","")
            sr_rec = sr.get("recommendation","")
            st.markdown(f"""<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.25rem;">
              <div style="background:#eaf0f4;border:1px solid #b8cedd;border-radius:4px;padding:1rem;"><div style="font-family:'DM Mono',monospace;font-size:10px;color:#1a4a6b;letter-spacing:.08em;margin-bottom:4px;">PRIVACY TEAM</div><span style="font-family:'DM Mono',monospace;font-size:11px;color:{rec_color(pr_rec)};background:{rec_color(pr_rec)}18;border:1px solid {rec_color(pr_rec)}40;padding:2px 10px;border-radius:2px;">{pr_rec.upper()}</span></div>
              <div style="background:#f4f0ea;border:1px solid #ddc8b8;border-radius:4px;padding:1rem;"><div style="font-family:'DM Mono',monospace;font-size:10px;color:#7a4f1a;letter-spacing:.08em;margin-bottom:4px;">SECURITY ENGINEERING</div><span style="font-family:'DM Mono',monospace;font-size:11px;color:{rec_color(sr_rec)};background:{rec_color(sr_rec)}18;border:1px solid {rec_color(sr_rec)}40;padding:2px 10px;border-radius:2px;">{sr_rec.upper()}</span></div>
            </div>""", unsafe_allow_html=True)
            decision = st.selectbox("Final approval decision", ["— select —"] + APPROVAL_OPTS)
            conditions = st.text_area("Conditions / Notes", placeholder="Document conditions of approval, compensating controls, or reasons for rejection...", height=120)
            approver = st.text_input("Approver Name", placeholder="e.g. Bree Williams, TPRM Lead")
            date_val = st.text_input("Approval Date", placeholder=datetime.date.today().strftime("%B %d, %Y"))
            if st.button("Record Decision & Close Workflow →"):
                if not decision or decision == "— select —": st.error("Please select an approval outcome.")
                elif decision in ("Approve with Conditions","Reject") and not conditions.strip(): st.error("Please document conditions or reason.")
                else:
                    st.session_state.approval_decision = {"decision":decision,"conditions":conditions,"approver":approver or "Instructor","date":date_val or datetime.date.today().strftime("%B %d, %Y")}
                    st.rerun()

