#!/usr/bin/env python3
"""
Master Pipeline Runner
Agent 1 → Agent 2 → Agent 3 → Agent 4
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import shutil
import subprocess

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def find_agent_directory(possible_names):
    current_dir = Path.cwd()
    for name in possible_names:
        agent_dir = current_dir / name
        if agent_dir.exists() and agent_dir.is_dir():
            return agent_dir
    return None


# --------------------------------------------------
# AGENT 1
# --------------------------------------------------

def run_agent_1():
    print("\n" + "=" * 70)
    print("🚀 STARTING AGENT 1: LISTING SCRAPER")
    print("=" * 70)

    agent_dir = "agent_1"
    script = "main.py"

    if not Path(agent_dir).exists():
        raise FileNotFoundError("❌ agent_1 folder not found")

    subprocess.run([sys.executable, script], cwd=agent_dir, check=True)
    print("✅ Agent 1 completed")


def copy_agent1_output():
    print("\n" + "=" * 70)
    print("📋 TRANSFERRING DATA: Agent 1 → Agent 2")
    print("=" * 70)

    source = Path("agent_1/output/listings.csv")
    if not source.exists():
        raise FileNotFoundError("❌ listings.csv not found from Agent 1")

    dest_dir = Path("agent_2/input")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "listings.csv"

    shutil.copy(source, dest)
    print(f"✓ Copied {source} → {dest}")


# --------------------------------------------------
# AGENT 2
# --------------------------------------------------

def run_agent_2():
    print("\n" + "=" * 70)
    print("🚀 STARTING AGENT 2: BROKER INTELLIGENCE")
    print("=" * 70)

    agent_dir = "agent_2"
    script = "main.py"

    if not Path(agent_dir).exists():
        raise FileNotFoundError("❌ agent_2 folder not found")

    subprocess.run([sys.executable, script], cwd=agent_dir, check=True)
    print("✅ Agent 2 completed")


def copy_agent2_output():
    print("\n" + "=" * 70)
    print("📋 TRANSFERRING DATA: Agent 2 → Agent 3")
    print("=" * 70)

    source = Path("agent_2/output/Master_Broker_Database.csv")
    if not source.exists():
        raise FileNotFoundError("❌ Master_Broker_Database.csv not found from Agent 2")

    dest_dir = Path("agent_3/input")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "Master_Broker_Database.csv"

    shutil.copy(source, dest)
    print(f"✓ Copied {source} → {dest}")


# --------------------------------------------------
# AGENT 3
# --------------------------------------------------

def run_agent_3():
    print("\n" + "=" * 70)
    print("🚀 STARTING AGENT 3: EMAIL OUTREACH")
    print("=" * 70)

    possible_names = ["agent_3", "agent_3_email_outreach", "agent3"]
    agent3_dir = find_agent_directory(possible_names)

    if not agent3_dir:
        raise FileNotFoundError("❌ Agent 3 directory not found")

    print(f"✓ Found Agent 3 at: {agent3_dir}")

    subprocess.run(
        [sys.executable, "main.py"],
        cwd=agent3_dir,
        check=True
    )

    print("✅ Agent 3 completed")


# --------------------------------------------------
# AGENT 4 (Data Catalog)
# --------------------------------------------------

def copy_all_to_agent4():
    """Copy all outputs to Agent 4 input"""
    print("\n" + "="*70)
    print("📋 TRANSFERRING DATA TO AGENT 4")
    print("="*70)
    
    files_to_copy = [
        ("agent_1/output/listings.csv", "agent_4/input/listings.csv"),
        ("agent_2/output/Master_Broker_Database.csv", "agent_4/input/Master_Broker_Database.csv"),
        ("agent_3/output/email_drafts.csv", "agent_4/input/email_drafts.csv")
    ]
    
    for src, dest in files_to_copy:
        src_path = Path(src)
        dest_path = Path(dest)
        
        if src_path.exists():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src_path, dest_path)
            print(f"✓ Copied {src_path.name}")
        else:
            print(f"⚠ {src_path} not found")

def run_agent_4():
    """Run Data Catalog Agent"""
    print("\n" + "="*70)
    print("🚀 STARTING AGENT 4: DATA CATALOG")
    print("="*70)
    
    original_dir = os.getcwd()
    possible_names = ["agent_4", "agent_4", "agent4"]
    agent4_dir = find_agent_directory(possible_names)
    
    if not agent4_dir:
        raise FileNotFoundError("❌ Agent 4 directory not found")
    
    print(f"✓ Found Agent 4 at: {agent4_dir}")
    
    try:
        # Agent 4 ko process as a subprocess chalana behtar hai taake conflicts na hon
        subprocess.run([sys.executable, "main.py"], cwd=agent4_dir, check=True)
        print("\n✅ Agent 4 Completed Successfully")
    except Exception as e:
        print(f"\n❌ Agent 4 Failed: {str(e)}")
        raise


# --------------------------------------------------
# VERIFY
# --------------------------------------------------

def verify_outputs():
    print("\n" + "=" * 70)
    print("🔍 VERIFYING OUTPUTS")
    print("=" * 70)

    outputs = {
        "Agent 1 Listings": Path("agent_1/output/listings.csv"),
        "Agent 2 Brokers": Path("agent_2/output/Master_Broker_Database.csv"),
        "Agent 3 Emails": Path("agent_3/output/email_drafts.csv"),
    }

    for name, path in outputs.items():
        if path.exists() and path.stat().st_size > 0:
            print(f"✓ {name}: {path} ({path.stat().st_size} bytes)")
        else:
            print(f"❌ {name}: NOT FOUND or EMPTY")


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------

def main():
    start_time = datetime.now()

    print("\n" + "=" * 70)
    print("🎯 MULTI-AGENT BUSINESS ACQUISITION PIPELINE")
    print("=" * 70)
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    try:
        print("\n📍 STAGE 1/6: Agent 1")
        run_agent_1()

        print("\n📍 STAGE 2/6: Transfer Agent 1 → Agent 2")
        copy_agent1_output()

        print("\n📍 STAGE 3/6: Agent 2")
        run_agent_2()

        print("\n📍 STAGE 3.5/6: Transfer Agent 2 → Agent 3")
        copy_agent2_output()

        print("\n📍 STAGE 4/6: Agent 3")
        run_agent_3()

        print("\n📍 STAGE 4.5/6: Transfer to Agent 4")
        copy_all_to_agent4()

        print("\n📍 STAGE 5/6: Running Data Catalog (Agent 4)")
        run_agent_4()

        print("\n📍 STAGE 6/6: Final Verification")
        verify_outputs()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 70)
        print("🎉 PIPELINE COMPLETE")
        print("=" * 70)
        print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {int(duration // 60)}m {int(duration % 60)}s")
        print("=" * 70)

        return 0

    except KeyboardInterrupt:
        print("\n⚠ Pipeline interrupted by user")
        return 130

    except Exception as e:
        print(f"\n❌ PIPELINE FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())