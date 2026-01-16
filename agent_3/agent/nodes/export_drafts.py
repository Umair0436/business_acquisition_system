import pandas as pd
import sys
from pathlib import Path
from agent.nodes.export_html import export_html_drafts

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.state import AgentState
from config.settings import EMAIL_DRAFTS_CSV, USER_INFO  # ← FIXED


def export_drafts_node(state: AgentState) -> AgentState:
    """Export email drafts to CSV"""

    print("\n" + "="*60)
    print("NODE 3: EXPORTING EMAIL DRAFTS")
    print("="*60)

    drafts = state.get("email_drafts", [])

    if not drafts:
        print("⚠ No drafts to export")
        state["current_stage"] = "export_complete"
        export_html_drafts(state)
        return state

    # Clean email bodies for CSV
    for draft in drafts:
        body = draft.get('email_body', '')
        draft['email_body'] = body

    # Create DataFrame
    df = pd.DataFrame(drafts)

    column_order = [
        "broker_name",
        "broker_firm",
        "broker_email",
        "email_subject",
        "email_body",
        "tone",
        "generation_timestamp"
    ]
    df = df[column_order]

    # Save with proper quoting
    df.to_csv(EMAIL_DRAFTS_CSV, index=False, quoting=1)

    state["output_path"] = str(EMAIL_DRAFTS_CSV)
    state["current_stage"] = "export_complete"

    print(f"✓ Exported {len(drafts)} email drafts to:")
    print(f"  {EMAIL_DRAFTS_CSV}")

    # Summary
    print("\n📊 Summary:")
    print(f"  - Total Drafts: {len(drafts)}")
    print(f"  - Tone Used: {state.get('selected_tone', 'N/A')}")
    print(f"  - Avg Subject Length: {df['email_subject'].str.len().mean():.0f} chars")
    print(f"  - Avg Body Length: {df['email_body'].str.len().mean():.0f} chars")

    # Sample preview
    if len(drafts) > 0:
        sample = drafts[0]
        print(f"\n" + "="*60)
        print("📧 SAMPLE EMAIL PREVIEW")
        print("="*60)
        print(f"To: {sample['broker_name']} <{sample['broker_email']}>")
        print(f"From: {USER_INFO['name']} <{USER_INFO['email']}>")
        print(f"Subject: {sample['email_subject']}")
        print(f"\n{sample['email_body']}")
        print("="*60)

    # Export HTML
    export_html_drafts(state)

    return state