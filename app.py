#!/usr/bin/env python3
"""
Streamlit Dashboard for Business Acquisition Pipeline
Real-time Agent Monitoring & File Downloads
"""

import streamlit as st
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import time
import shutil
import json
import threading
import queue

# Thread-safe log queue
log_queue = queue.Queue()

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Business Acquisition Pipeline",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .agent-box {
        padding: 1.2rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        text-align: center;
        font-size: 1rem;
        font-weight: bold;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .agent-pending {
        background-color: #f0f2f6;
        border: 2px solid #d3d3d3;
        color: #666;
    }
    
    .agent-processing {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        color: #856404;
        animation: pulse 1.5s infinite;
    }
    
    .agent-completed {
        background-color: #d4edda;
        border: 2px solid #28a745;
        color: #155724;
    }
    
    .agent-failed {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        color: #721c24;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    .success-banner {
        background-color: #d4edda;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        text-align: center;
        font-size: 1.5rem;
        color: #155724;
        margin: 2rem 0;
    }
    
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.75rem 1rem;
        font-size: 1.1rem;
    }
    
    .stButton>button:hover {
        background-color: #0d5fa3;
    }
    
    .log-box {
        background-color: #1e1e1e;
        border: 2px solid #3a3a3a;
        border-radius: 8px;
        padding: 1.2rem;
        max-height: 500px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: #e0e0e0;
        line-height: 1.6;
    }
    
    .log-box pre {
        margin: 0;
        color: #e0e0e0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    .log-box::-webkit-scrollbar {
        width: 8px;
    }
    
    .log-box::-webkit-scrollbar-track {
        background: #2a2a2a;
        border-radius: 4px;
    }
    
    .log-box::-webkit-scrollbar-thumb {
        background: #4a4a4a;
        border-radius: 4px;
    }
    
    .log-box::-webkit-scrollbar-thumb:hover {
        background: #5a5a5a;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if 'agent_status' not in st.session_state:
    st.session_state.agent_status = {
        'agent_1': 'pending',
        'agent_2': 'pending',
        'agent_3': 'pending',
        'agent_4': 'pending'
    }

if 'pipeline_running' not in st.session_state:
    st.session_state.pipeline_running = False

if 'pipeline_complete' not in st.session_state:
    st.session_state.pipeline_complete = False

if 'logs' not in st.session_state:
    st.session_state.logs = []

if 'current_agent' not in st.session_state:
    st.session_state.current_agent = None

# ============================================
# HELPER FUNCTIONS
# ============================================

def file_exists(path):
    """Check if file exists and has content"""
    try:
        p = Path(path)
        return p.exists() and p.stat().st_size > 0
    except:
        return False

def ensure_directory(path):
    """Ensure directory exists"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
    except:
        pass

def save_status():
    """Save current status to a JSON file"""
    status_file = Path("pipeline_status.json")
    status_data = {
        'agent_status': st.session_state.agent_status,
        'logs': st.session_state.logs[-100:],
        'pipeline_running': st.session_state.pipeline_running,
        'pipeline_complete': st.session_state.pipeline_complete,
        'current_agent': st.session_state.current_agent,
        'timestamp': datetime.now().isoformat()
    }
    try:
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        print(f"Save status error: {e}")

def load_status():
    """Load status from JSON file if exists"""
    status_file = Path("pipeline_status.json")
    if status_file.exists():
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
            
            st.session_state.agent_status = status_data.get('agent_status', st.session_state.agent_status)
            st.session_state.logs = status_data.get('logs', [])
            st.session_state.pipeline_running = status_data.get('pipeline_running', False)
            st.session_state.pipeline_complete = status_data.get('pipeline_complete', False)
            st.session_state.current_agent = status_data.get('current_agent', None)
            return True
        except Exception as e:
            print(f"Load status error: {e}")
    return False

def add_log(message):
    """Add log message (thread-safe)"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    log_queue.put(log_entry)
    print(log_entry)

def process_log_queue():
    """Process queued logs into session state"""
    while not log_queue.empty():
        try:
            log_entry = log_queue.get_nowait()
            if 'logs' not in st.session_state:
                st.session_state.logs = []
            st.session_state.logs.append(log_entry)
        except queue.Empty:
            break

def update_agent_status(agent, status):
    """Update agent status (thread-safe via file)"""
    status_file = Path("pipeline_status.json")
    try:
        if status_file.exists():
            with open(status_file, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
        else:
            status_data = {
                'agent_status': {
                    'agent_1': 'pending',
                    'agent_2': 'pending',
                    'agent_3': 'pending',
                    'agent_4': 'pending'
                },
                'logs': [],
                'pipeline_running': True,
                'pipeline_complete': False,
                'current_agent': None
            }
        
        status_data['agent_status'][agent] = status
        status_data['current_agent'] = agent if status == 'processing' else None
        status_data['timestamp'] = datetime.now().isoformat()
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        print(f"Update status error: {e}")

def parse_pipeline_output(line):
    """Parse run_pipeline.py output and update status"""
    line = line.strip()
    
    # Agent started
    if "STARTING AGENT 1" in line:
        update_agent_status('agent_1', 'processing')
        add_log("🚀 Agent 1: Listing Scraper started")
    elif "STARTING AGENT 2" in line:
        update_agent_status('agent_1', 'completed')
        update_agent_status('agent_2', 'processing')
        add_log("🚀 Agent 2: Broker Intelligence started")
    elif "STARTING AGENT 3" in line:
        update_agent_status('agent_2', 'completed')
        update_agent_status('agent_3', 'processing')
        add_log("🚀 Agent 3: Email Outreach started")
    elif "STARTING AGENT 4" in line or "DATA CATALOG" in line:
        update_agent_status('agent_3', 'completed')
        update_agent_status('agent_4', 'processing')
        add_log("🚀 Agent 4: Data Catalog started")
    
    # Agent completed
    elif "Agent 1 completed" in line:
        update_agent_status('agent_1', 'completed')
        add_log("✅ Agent 1 completed")
    elif "Agent 2 completed" in line:
        update_agent_status('agent_2', 'completed')
        add_log("✅ Agent 2 completed")
    elif "Agent 3 completed" in line:
        update_agent_status('agent_3', 'completed')
        add_log("✅ Agent 3 completed")
    elif "Agent 4 Completed" in line:
        update_agent_status('agent_4', 'completed')
        add_log("✅ Agent 4 completed")
    
    # Pipeline complete
    elif "PIPELINE COMPLETE" in line:
        st.session_state.pipeline_complete = True
        st.session_state.pipeline_running = False
        add_log("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        save_status()
    
    # Errors
    elif "FAILED" in line or "ERROR" in line or "❌" in line:
        add_log(f"❌ {line}")
    
    # Other important messages
    elif any(word in line for word in ["STAGE", "TRANSFER", "VERIFY", "✓", "⚠"]):
        add_log(f"   {line[:150]}")

def run_pipeline_background(max_listings, email_tone):
    """Run the pipeline using run_pipeline.py"""
    try:
        add_log("=" * 50)
        add_log("🚀 PIPELINE STARTED")
        add_log(f"📊 Settings: {max_listings} listings, {email_tone} tone")
        add_log("=" * 50)
        
        # Create config files
        add_log("⚙️ Creating configuration files...")
        
        # Agent 1 Config
        ensure_directory("agent_1")
        config_content = f"""# Agent 1 Configuration
MAX_LISTINGS = {max_listings}
NUM_LISTINGS = {max_listings}
HEADLESS_MODE = False
TIMEOUT = 30
RETRY_ATTEMPTS = 3

SCRAPING_CONFIG = {{
    'bizbuysell': {{
        'max_listings': {max_listings},
        'max_pages': 10,
        'url': 'https://www.bizbuysell.com/businesses-for-sale/',
        'enabled': True
    }},
    'bizquest': {{
        'max_listings': {max_listings},
        'max_pages': 10,
        'url': 'https://www.bizquest.com/businesses-for-sale/',
        'enabled': True
    }},
    'loopnet': {{
        'max_listings': {max_listings},
        'max_pages': 10,
        'url': 'https://www.loopnet.com/search/businesses-for-sale/',
        'enabled': True
    }}
}}

OUTPUT_CONFIG = {{
    'output_file': 'output/listings.csv',
    'save_intermediate': True,
    'format': 'csv'
}}
"""
        with open("agent_1/config.py", "w", encoding='utf-8') as f:
            f.write(config_content)
        add_log("✅ Agent 1 config created")
        
        # Agent 3 Config
        ensure_directory("agent_3")
        with open("agent_3/config.py", "w", encoding='utf-8') as f:
            f.write(f"EMAIL_TONE = '{email_tone.lower()}'\n")
            f.write(f"EMAIL_CONFIG = {{'tone': '{email_tone.lower()}', 'max_emails': 100}}\n")
        add_log("✅ Agent 3 config created")
        
        # Create directories
        for i in range(1, 5):
            ensure_directory(f"agent_{i}/output")
            ensure_directory(f"agent_{i}/input")
        add_log("✅ All directories created")
        add_log("")
        
        # Run the pipeline using run_pipeline.py
        add_log("🚀 Executing run_pipeline.py...")
        
        process = subprocess.Popen(
            [sys.executable, "run_pipeline.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            universal_newlines=True
        )
        
        # Read output in real-time
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
            if line:
                parse_pipeline_output(line)
        
        return_code = process.wait()
        
        if return_code == 0:
            add_log("=" * 50)
            add_log("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            add_log("=" * 50)
            
            # Update status file
            status_file = Path("pipeline_status.json")
            if status_file.exists():
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                status_data['pipeline_complete'] = True
                status_data['pipeline_running'] = False
                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump(status_data, f, indent=2)
        else:
            add_log(f"❌ Pipeline failed with return code {return_code}")
            # Mark any processing agent as failed
            status_file = Path("pipeline_status.json")
            if status_file.exists():
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                for agent, status in status_data.get('agent_status', {}).items():
                    if status == 'processing':
                        status_data['agent_status'][agent] = 'failed'
                status_data['pipeline_running'] = False
                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump(status_data, f, indent=2)
        
        # Mark pipeline as not running
        status_file = Path("pipeline_status.json")
        if status_file.exists():
            with open(status_file, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
            status_data['pipeline_running'] = False
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2)
        
    except Exception as e:
        add_log(f"❌ Pipeline error: {str(e)}")
        # Mark as not running
        try:
            status_file = Path("pipeline_status.json")
            if status_file.exists():
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                status_data['pipeline_running'] = False
                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump(status_data, f, indent=2)
        except:
            pass

# ============================================
# SIDEBAR
# ============================================

st.sidebar.markdown("## ⚙️ Pipeline Settings")

max_listings = st.sidebar.number_input(
    "📊 Listings per Website",
    min_value=1,
    max_value=10000,
    value=20,
    step=1,
    help="Number of listings to scrape from each website"
)

st.sidebar.markdown("### 📧 Email Tone")
email_tone = st.sidebar.selectbox(
    "Select outreach tone:",
    ["Professional", "Relationship-Based", "Direct"],
    index=0,
    help="Choose the tone for email generation"
)

st.sidebar.markdown("---")

start_button = st.sidebar.button(
    "🚀 START PIPELINE",
    disabled=st.session_state.pipeline_running,
    use_container_width=True
)

if st.sidebar.button("🔄 RESET", use_container_width=True):
    status_file = Path("pipeline_status.json")
    if status_file.exists():
        status_file.unlink()
    
    st.session_state.agent_status = {
        'agent_1': 'pending',
        'agent_2': 'pending',
        'agent_3': 'pending',
        'agent_4': 'pending'
    }
    st.session_state.pipeline_running = False
    st.session_state.pipeline_complete = False
    st.session_state.logs = []
    st.session_state.current_agent = None
    st.rerun()

if st.session_state.pipeline_running:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Status")
    
    current_agent = None
    for agent, status in st.session_state.agent_status.items():
        if status == 'processing':
            current_agent = agent
            break
    
    if current_agent:
        st.sidebar.warning(f"🔄 Running: {current_agent.upper()}")
    else:
        st.sidebar.info("🔄 Pipeline active...")

# ============================================
# MAIN DASHBOARD
# ============================================

load_status()

st.markdown('<div class="main-header">🏢 Business Acquisition Pipeline</div>', unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3 = st.columns([2, 1.5, 1.5])

# ============================================
# AGENT STATUS (Left Column)
# ============================================

with col1:
    st.markdown("### 🤖 Agent Status")
    
    status_emoji = {
        'pending': '⏳',
        'processing': '⚙️',
        'completed': '✅',
        'failed': '❌'
    }
    status_text = {
        'pending': 'Pending',
        'processing': 'Processing...',
        'completed': 'Completed',
        'failed': 'Failed'
    }
    
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        status = st.session_state.agent_status['agent_1']
        st.markdown(f"""
        <div class="agent-box agent-{status}">
            <div style="font-size: 1.2rem;">🔍 Agent 1</div>
            <div style="font-size: 1rem; font-weight: normal;">Listing Scraper</div>
            <div style="font-size: 0.85rem; font-weight: normal; margin-top: 0.3rem; color: #666;">Scraping listings</div>
            <div style="margin-top: 0.5rem; font-size: 1.1rem;">{status_emoji[status]} {status_text[status]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with row1_col2:
        status = st.session_state.agent_status['agent_2']
        st.markdown(f"""
        <div class="agent-box agent-{status}">
            <div style="font-size: 1.2rem;">👔 Agent 2</div>
            <div style="font-size: 1rem; font-weight: normal;">Broker Intelligence</div>
            <div style="font-size: 0.85rem; font-weight: normal; margin-top: 0.3rem; color: #666;">Extracting brokers</div>
            <div style="margin-top: 0.5rem; font-size: 1.1rem;">{status_emoji[status]} {status_text[status]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        status = st.session_state.agent_status['agent_3']
        st.markdown(f"""
        <div class="agent-box agent-{status}">
            <div style="font-size: 1.2rem;">✉️ Agent 3</div>
            <div style="font-size: 1rem; font-weight: normal;">Email Outreach</div>
            <div style="font-size: 0.85rem; font-weight: normal; margin-top: 0.3rem; color: #666;">Creating emails</div>
            <div style="margin-top: 0.5rem; font-size: 1.1rem;">{status_emoji[status]} {status_text[status]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with row2_col2:
        status = st.session_state.agent_status['agent_4']
        st.markdown(f"""
        <div class="agent-box agent-{status}">
            <div style="font-size: 1.2rem;">📁 Agent 4</div>
            <div style="font-size: 1rem; font-weight: normal;">Data Catalog</div>
            <div style="font-size: 0.85rem; font-weight: normal; margin-top: 0.3rem; color: #666;">Organizing data</div>
            <div style="margin-top: 0.5rem; font-size: 1.1rem;">{status_emoji[status]} {status_text[status]}</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# ACTIVITY LOGS (Middle Column)
# ============================================

with col2:
    st.markdown("### 📋 Activity Log")
    
    if st.session_state.logs:
        log_text = "\n".join(st.session_state.logs[-30:])
        st.markdown(f'<div class="log-box"><pre>{log_text}</pre></div>', unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Logs", use_container_width=True, key="clear_logs"):
            st.session_state.logs = []
            save_status()
            st.rerun()
    else:
        st.markdown("""
        <div style='background-color: #e8f4f8; border: 2px solid #b3d9e6; border-radius: 8px; 
                    padding: 1.5rem; text-align: center; color: #2c5f7a;'>
            <strong>📋 No activity yet</strong><br>
            <span style='font-size: 0.9rem;'>Click "START PIPELINE" to begin</span>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# DOWNLOAD FILES (Right Column)
# ============================================

with col3:
    st.markdown("### 📥 Download Files")
    
    if file_exists("agent_1/output/listings.csv"):
        with open("agent_1/output/listings.csv", "rb") as f:
            st.download_button(
                label="📄 Listings",
                data=f,
                file_name=f"listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="dl_listings"
            )
    else:
        st.button("📄 Listings", disabled=True, use_container_width=True, key="dl_listings_disabled")
    
    if file_exists("agent_2/output/Master_Broker_Database.csv"):
        with open("agent_2/output/Master_Broker_Database.csv", "rb") as f:
            st.download_button(
                label="👔 Brokers",
                data=f,
                file_name=f"brokers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="dl_brokers"
            )
    else:
        st.button("👔 Brokers", disabled=True, use_container_width=True, key="dl_brokers_disabled")
    
    if file_exists("agent_3/output/email_drafts.csv"):
        with open("agent_3/output/email_drafts.csv", "rb") as f:
            st.download_button(
                label="✉️ Emails",
                data=f,
                file_name=f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="dl_emails"
            )
    else:
        st.button("✉️ Emails", disabled=True, use_container_width=True, key="dl_emails_disabled")
    
    if file_exists("agent_4/output/final_catalog.csv"):
        with open("agent_4/output/final_catalog.csv", "rb") as f:
            st.download_button(
                label="📁 Catalog",
                data=f,
                file_name=f"catalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="dl_catalog"
            )
    else:
        st.button("📁 Catalog", disabled=True, use_container_width=True, key="dl_catalog_disabled")

# ============================================
# SUCCESS BANNER
# ============================================

if st.session_state.pipeline_complete:
    st.markdown("""
    <div class="success-banner">
        🎉 Pipeline Complete! All files are ready for download 🎉
    </div>
    """, unsafe_allow_html=True)

# ============================================
# PIPELINE EXECUTION
# ============================================

if start_button:
    st.session_state.pipeline_running = True
    st.session_state.pipeline_complete = False
    
    # Reset all agent statuses
    st.session_state.agent_status = {
        'agent_1': 'pending',
        'agent_2': 'pending',
        'agent_3': 'pending',
        'agent_4': 'pending'
    }
    st.session_state.logs = []
    save_status()
    
    # Start pipeline in background thread
    pipeline_thread = threading.Thread(
        target=run_pipeline_background,
        args=(max_listings, email_tone),
        daemon=True
    )
    pipeline_thread.start()
    st.rerun()

# Auto-refresh when pipeline is running
if st.session_state.pipeline_running:
    time.sleep(2)
    st.rerun()

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🏢 Business Acquisition Multi-Agent System</p>
    <p style='font-size: 0.85rem;'>Powered by run_pipeline.py</p>
</div>
""", unsafe_allow_html=True)