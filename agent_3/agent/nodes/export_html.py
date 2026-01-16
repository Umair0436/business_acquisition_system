import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.state import AgentState
from config.settings import OUTPUT_DIR


def export_html_drafts(state: AgentState) -> None:
    """Export emails as HTML for easy viewing"""

    drafts = state.get("email_drafts", [])
    if not drafts:
        return

    html_file = OUTPUT_DIR / "email_drafts.html"

    # ---- HEADER HTML (use f-string, NOT .format) ----
    timestamp = drafts[0]["generation_timestamp"][:19]
    count = len(drafts)

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Email Drafts</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 20px auto; 
        }}
        .email {{ 
            border: 1px solid #ccc; 
            margin: 20px 0; 
            padding: 20px; 
            background: #f9f9f9; 
        }}
        .header {{ 
            background: #007bff; 
            color: white; 
            padding: 10px; 
            margin: -20px -20px 20px -20px; 
        }}
        .subject {{ 
            font-size: 18px; 
            font-weight: bold; 
            margin: 10px 0; 
        }}
        .body {{ 
            white-space: pre-wrap; 
            line-height: 1.6; 
        }}
        .meta {{ 
            color: #666; 
            font-size: 12px; 
            margin-top: 15px; 
            padding-top: 15px; 
            border-top: 1px solid #ddd; 
        }}
    </style>
</head>
<body>
    <h1>📧 Email Drafts - Generated {timestamp}</h1>
    <p><strong>Total Drafts:</strong> {count}</p>
"""

    # ---- EMAIL BLOCKS ----
    for i, draft in enumerate(drafts, 1):
        html_content += f"""
    <div class="email">
        <div class="header">
            <strong>Email {i}/{count}</strong>
        </div>
        <p><strong>To:</strong> {draft.get('broker_name', 'N/A')} &lt;{draft.get('broker_email', 'LOOKUP REQUIRED')}&gt;</p>
        <p><strong>Firm:</strong> {draft.get('broker_firm', 'Independent')}</p>
        <div class="subject">{draft.get('email_subject', '')}</div>
        <div class="body">{draft.get('email_body', '')}</div>
        <div class="meta">
            Tone: {draft.get('tone', '')} |
            Generated: {draft.get('generation_timestamp', '')[:19]}
        </div>
    </div>
"""

    # ---- FOOTER HTML ----
    html_content += """
</body>
</html>
"""

    # ---- WRITE FILE ----
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✓ HTML preview generated: {html_file}")
