import sys
from pathlib import Path
from datetime import datetime
import os

from dotenv import load_dotenv
import google.generativeai as genai

# ------------------------------------------------------------------
# ENV & GEMINI CONFIG
# ------------------------------------------------------------------
load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

# ------------------------------------------------------------------
# PROJECT IMPORTS
# ------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.state import AgentState, EmailDraft
from prompts.professional import PROFESSIONAL_SYSTEM_PROMPT, PROFESSIONAL_TEMPLATE
from prompts.relationship import RELATIONSHIP_SYSTEM_PROMPT, RELATIONSHIP_TEMPLATE
from prompts.direct import DIRECT_SYSTEM_PROMPT, DIRECT_TEMPLATE
from config.settings import USER_INFO


# ------------------------------------------------------------------
# NODE: GENERATE EMAILS
# ------------------------------------------------------------------
def generate_emails_node(state: AgentState) -> AgentState:
    """Generate personalized email drafts using Gemini"""

    print("\n" + "=" * 60)
    print("NODE 2: GENERATING EMAIL DRAFTS")
    print("=" * 60)

    brokers = state.get("broker_database", [])
    tone = state.get("selected_tone", "professional")

    if not brokers:
        print("⚠ No brokers in state")
        state["current_stage"] = "emails_generated"
        return state

    prompts = {
        "professional": (PROFESSIONAL_SYSTEM_PROMPT, PROFESSIONAL_TEMPLATE),
        "relationship": (RELATIONSHIP_SYSTEM_PROMPT, RELATIONSHIP_TEMPLATE),
        "direct": (DIRECT_SYSTEM_PROMPT, DIRECT_TEMPLATE),
    }

    system_prompt, user_template = prompts.get(tone, prompts["professional"])

    print(f"✓ Tone: {tone}")
    print(f"✓ Generating {len(brokers)} emails...\n")

    model = genai.GenerativeModel("gemini-2.5-flash")

    email_drafts = []
    generated = 0

    for idx, broker in enumerate(brokers, 1):
        broker_name = broker.get("broker_name", "Unknown")
        broker_firm = broker.get("brokerage_firm", "Independent")
        broker_email = broker.get("email", "")

        print(f"[{idx}/{len(brokers)}] {broker_name} @ {broker_firm}")

        try:
            user_prompt = user_template.format(
                broker_name=broker_name,
                broker_firm=broker_firm,
                geography=broker.get("geography", "Not specified"),
                industry_focus=broker.get("industry_focus", "Not specified"),
                sender_name=USER_INFO["name"],
                sender_company=USER_INFO["company"],
                sender_title=USER_INFO["title"],
            )

            full_prompt = f"""
{system_prompt}

{user_prompt}

OUTPUT FORMAT (STRICT):
Subject: <email subject>

<email body>
Full email body starting with greeting and ending with a professional signature.
</email body>
"""

            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.5,
                    "max_output_tokens": 2000,
                },
            )

            response_text = response.text.strip()
            subject, body = parse_email_response(response_text)

            # Safety check (debug-friendly)
            if len(body) < 200:
                print("  ⚠ Warning: Short email body detected")

            email_draft: EmailDraft = {
                "broker_name": broker_name,
                "broker_firm": broker_firm,
                "broker_email": broker_email,
                "email_subject": subject,
                "email_body": body,
                "tone": tone,
                "generation_timestamp": datetime.now().isoformat(),
            }

            email_drafts.append(email_draft)
            generated += 1

            print(f"  ✓ Generated: {subject[:60]}...")

        except Exception as e:
            error_msg = f"Failed: {str(e)[:80]}"
            state["errors"].append(error_msg)
            print(f"  ❌ {error_msg}")

    state["email_drafts"] = email_drafts
    state["drafts_generated"] = generated
    state["current_stage"] = "emails_generated"

    print(f"\n✓ Generated {generated} email drafts")
    return state


# ------------------------------------------------------------------
# HELPER: SUBJECT / BODY PARSER (ROBUST)
# ------------------------------------------------------------------
def parse_email_response(text: str) -> tuple:
    """
    Robust parser for Gemini email output.
    Expected format:

    Subject: ...

    <email body>
    """

    if not text:
        return (
            "Exploring Off-Market Business Opportunities",
            ""
        )

    lines = [l.rstrip() for l in text.splitlines()]

    subject = ""
    body_lines = []
    subject_found = False

    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()

        # Detect subject
        if lower.startswith("subject:") and not subject_found:
            subject = stripped.split(":", 1)[1].strip()
            subject_found = True
            continue

        # Everything after subject = body
        if subject_found:
            body_lines.append(line)

    body = "\n".join(body_lines).strip()

    # ---- FALLBACKS ----
    if not subject:
        subject = "Exploring Off-Market Business Opportunities"

    if not body:
        body = text.strip()

    return subject, body
