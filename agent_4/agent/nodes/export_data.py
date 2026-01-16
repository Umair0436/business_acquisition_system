import pandas as pd
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.state import AgentState
from config.settings import MASTER_EXCEL, MASTER_CSV, NOTION_JSON, AIRTABLE_JSON


def export_data_node(state: AgentState) -> AgentState:
    """Export catalog - single row per business with all data"""

    print("\n" + "=" * 60)
    print("NODE 4: EXPORTING DATA")
    print("=" * 60)

    records = state.get("catalog_records", [])

    if not records:
        print("⚠ No records to export")
        state["current_stage"] = "export_complete"
        return state

    export_data = []

    for record in records:
        record.setdefault("record_id", f"auto_{uuid.uuid4().hex}")
        raw = record.get("raw_data", {})

        # Single row with ALL data
        flat_record = {
            "Record ID": record.get("record_id", ""),
            "Record Type": record.get("record_type", ""),
            "Business Name": raw.get("Business Name", ""),
            "Industry": record.get("industry_tag", ""),
            "Geography": (
                record.get("geography_tag")
                or raw.get("Geography")
                or raw.get("Location")
                or ""
            ),

            "Deal Status": record.get("deal_status", ""),
            "Asking Price": raw.get("Asking Price", ""),
            "Revenue": raw.get("Revenue", ""),
            "EBITDA": raw.get("EBITDA", ""),
            "Years in Operation": raw.get("Years in Operation", ""),
            "Listing URL": raw.get("Listing URL", ""),
            "Source": raw.get("Source", ""),
            "Broker Name": record.get("broker_name", ""),
            "Brokerage Firm": raw.get("brokerage_firm", ""),
            "Email": raw.get("email", ""),
            "Phone": raw.get("phone", ""),
            "LinkedIn": raw.get("linkedin_search_url", ""),
            "Email Subject": raw.get("email_subject", ""),
            "Email Body": raw.get("email_body", ""),
            "Email Tone": raw.get("email_tone", "")
        }

        export_data.append(flat_record)

    df = pd.DataFrame(export_data)

    export_to_excel(df, state)
    export_to_csv(df)
    export_to_notion(records)
    export_to_airtable(records)

    state["output_paths"] = {
        "excel": str(MASTER_EXCEL),
        "csv": str(MASTER_CSV),
        "notion": str(NOTION_JSON),
        "airtable": str(AIRTABLE_JSON)
    }

    state["current_stage"] = "export_complete"

    print("\n✅ Export Complete!")
    print(f"  📊 Excel: {MASTER_EXCEL}")
    print(f"  📄 CSV: {MASTER_CSV}")
    print(f"  🔗 Notion: {NOTION_JSON}")
    print(f"  🔗 Airtable: {AIRTABLE_JSON}")

    return state


def export_to_excel(df: pd.DataFrame, state: AgentState):
    """Export to Excel with single merged sheet"""

    with pd.ExcelWriter(MASTER_EXCEL, engine="openpyxl") as writer:
        # Main sheet - all data in single rows
        df.to_excel(writer, sheet_name="Master Database", index=False)
        
        # Summary sheet
        summary_data = []
        for key, value in state.get("tag_summary", {}).items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    summary_data.append({
                        "Category": key,
                        "Tag": sub_key,
                        "Count": sub_value
                    })

        if summary_data:
            pd.DataFrame(summary_data).to_excel(
                writer, sheet_name="Summary", index=False
            )

    print(f"  ✓ Excel exported with {len(df)} records (single row per business)")


def export_to_csv(df: pd.DataFrame):
    df.to_csv(MASTER_CSV, index=False)
    print(f"  ✓ CSV exported with {len(df)} records")


def export_to_notion(records: list):
    notion_data = {
        "database_title": "Business Acquisition Pipeline",
        "records": []
    }

    for record in records:
        raw = record.get("raw_data", {})
        notion_data["records"].append({
            "properties": {
                "Record ID": {
                    "title": [{"text": {"content": record.get("record_id", "")}}]
                },
                "Business": {
                    "rich_text": [{"text": {"content": raw.get("Business Name", "")}}]
                },
                "Broker": {
                    "rich_text": [{"text": {"content": record.get("broker_name", "")}}]
                },
                "Email": {
                    "email": raw.get("email", "")
                },
                "Phone": {
                    "phone_number": raw.get("phone", "")
                },
                "Industry": {"select": {"name": record.get("industry_tag", "")}},
                "Geography": {"select": {"name": record.get("geography_tag", "")}},
                "Status": {"select": {"name": record.get("deal_status", "")}},
            }
        })

    with open(NOTION_JSON, "w", encoding="utf-8") as f:
        json.dump(notion_data, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Notion JSON exported with {len(records)} records")


def export_to_airtable(records: list):
    airtable_data = {"records": []}

    for record in records:
        raw = record.get("raw_data", {})
        airtable_data["records"].append({
            "fields": {
                "Record ID": record.get("record_id", ""),
                "Business Name": raw.get("Business Name", ""),
                "Broker Name": record.get("broker_name", ""),
                "Email": raw.get("email", ""),
                "Phone": raw.get("phone", ""),
                "Firm": raw.get("brokerage_firm", ""),
                "Industry": record.get("industry_tag", ""),
                "Geography": record.get("geography_tag", ""),
                "Deal Status": record.get("deal_status", ""),
                "Asking Price": raw.get("Asking Price", ""),
                "Revenue": raw.get("Revenue", "")
            }
        })

    with open(AIRTABLE_JSON, "w", encoding="utf-8") as f:
        json.dump(airtable_data, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Airtable JSON exported with {len(records)} records")