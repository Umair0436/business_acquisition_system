<<<<<<< HEAD
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
    p = Path(path)
    return p.exists() and p.stat().st_size > 0

def ensure_directory(path):
    """Ensure directory exists"""
    Path(path).mkdir(parents=True, exist_ok=True)

def save_status():
    """Save current status to a JSON file"""
    status_file = Path("pipeline_status.json")
    status_data = {
        'agent_status': st.session_state.agent_status,
        'logs': st.session_state.logs[-50:],  # Keep last 50 logs
        'pipeline_running': st.session_state.pipeline_running,
        'pipeline_complete': st.session_state.pipeline_complete,
        'current_agent': st.session_state.current_agent,
        'timestamp': datetime.now().isoformat()
    }
    try:
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
    except:
        pass

def load_status():
    """Load status from JSON file if exists"""
    status_file = Path("pipeline_status.json")
    if status_file.exists():
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
                
            # Check if data is recent (within last hour)
            saved_time = datetime.fromisoformat(status_data['timestamp'])
            if (datetime.now() - saved_time).seconds < 3600:
                st.session_state.agent_status = status_data['agent_status']
                st.session_state.logs = status_data['logs']
                st.session_state.pipeline_running = status_data['pipeline_running']
                st.session_state.pipeline_complete = status_data['pipeline_complete']
                st.session_state.current_agent = status_data['current_agent']
                return True
        except:
            pass
    return False

def add_log_to_queue(message):
    """Add log message to queue (thread-safe)"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    log_queue.put(log_entry)
    print(log_entry)  # Also print to console

def process_log_queue():
    """Process all queued log messages"""
    while not log_queue.empty():
        try:
            log_entry = log_queue.get_nowait()
            st.session_state.logs.append(log_entry)
        except queue.Empty:
            break
    save_status()

def update_status_file(agent, status):
    """Update status file directly (thread-safe)"""
    status_file = Path("pipeline_status.json")
    try:
        # Load current status
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
        
        # Update status
        status_data['agent_status'][agent] = status
        status_data['timestamp'] = datetime.now().isoformat()
        
        # Save
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
    except:
        pass

def transfer_file(src, dest):
    """Transfer file from source to destination"""
    try:
        if file_exists(src):
            ensure_directory(Path(dest).parent)
            shutil.copy2(src, dest)
            add_log_to_queue(f"✅ Transferred: {Path(src).name} → {Path(dest).parent.name}")
            return True
        else:
            add_log_to_queue(f"⚠️ File not found: {src}")
            return False
    except Exception as e:
        add_log_to_queue(f"❌ Transfer error: {str(e)[:100]}")
        return False

def run_agent_direct(agent_name, agent_dir):
    """Run agent using subprocess.run (blocking but more reliable)"""
    try:
        # Update status file
        update_status_file(agent_name, 'processing')
        add_log_to_queue(f"🚀 Starting {agent_name.upper()}...")
        
        # Verify paths
        agent_path = Path(agent_dir)
        if not agent_path.exists():
            add_log_to_queue(f"❌ Directory not found: {agent_dir}")
            update_status_file(agent_name, 'failed')
            return False
        
        main_file = agent_path / "main.py"
        if not main_file.exists():
            add_log_to_queue(f"❌ main.py not found in {agent_dir}")
            update_status_file(agent_name, 'failed')
            return False
        
        add_log_to_queue(f"📂 Executing: {main_file}")
        add_log_to_queue(f"⏳ Please wait (this may take several minutes)...")
        
        # Run the agent
        result = subprocess.run(
            [sys.executable, "main.py"],
            cwd=str(agent_path),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=900  # 15 minutes timeout
        )
        
        # Check result
        if result.returncode == 0:
            add_log_to_queue(f"✅ {agent_name.upper()} completed successfully")
            update_status_file(agent_name, 'completed')
            return True
        else:
            add_log_to_queue(f"❌ {agent_name.upper()} failed with return code {result.returncode}")
            
            # Show error details
            if result.stderr:
                error_lines = result.stderr.strip().split('\n')[-5:]  # Last 5 lines
                for line in error_lines:
                    if line.strip():
                        add_log_to_queue(f"   {line[:100]}")
            
            update_status_file(agent_name, 'failed')
            return False
            
    except subprocess.TimeoutExpired:
        add_log_to_queue(f"❌ {agent_name.upper()} timeout after 15 minutes")
        update_status_file(agent_name, 'failed')
        return False
    except Exception as e:
        add_log_to_queue(f"❌ {agent_name.upper()} exception: {str(e)[:200]}")
        update_status_file(agent_name, 'failed')
        return False

def run_pipeline_background(max_listings, email_tone):
    """Run the complete pipeline in background thread"""
    try:
        add_log_to_queue("=" * 50)
        add_log_to_queue("🚀 PIPELINE STARTED")
        add_log_to_queue(f"📊 Settings: {max_listings} listings, {email_tone} tone")
        add_log_to_queue("=" * 50)
        
        # Create config files
        add_log_to_queue("⚙️ Creating configuration files...")
        
        # Agent 1 config
        ensure_directory("agent_1")
        with open("agent_1/config.py", "w", encoding='utf-8') as f:
            f.write("# Agent 1 Configuration File\n")
            f.write("# Auto-generated by Dashboard\n\n")
            f.write("# Website Scraping Configuration\n")
            f.write("SCRAPING_CONFIG = {\n")
            f.write("    'bizbuysell': {\n")
            f.write(f"        'max_listings': {max_listings},\n")
            f.write("        'max_pages': 10,\n")
            f.write("        'url': 'https://www.bizbuysell.com/businesses-for-sale/',\n")
            f.write("        'enabled': True\n")
            f.write("    },\n")
            f.write("    'bizquest': {\n")
            f.write(f"        'max_listings': {max_listings},\n")
            f.write("        'max_pages': 10,\n")
            f.write("        'url': 'https://www.bizquest.com/businesses-for-sale/',\n")
            f.write("        'enabled': True\n")
            f.write("    },\n")
            f.write("    'loopnet': {\n")
            f.write(f"        'max_listings': {max_listings},\n")
            f.write("        'max_pages': 10,\n")
            f.write("        'url': 'https://www.loopnet.com/search/businesses-for-sale/',\n")
            f.write("        'enabled': True\n")
            f.write("    }\n")
            f.write("}\n\n")
            f.write("# Output Configuration\n")
            f.write("OUTPUT_CONFIG = {\n")
            f.write("    'output_file': 'output/listings.csv',\n")
            f.write("    'save_intermediate': True,\n")
            f.write("    'format': 'csv'\n")
            f.write("}\n\n")
            f.write("# Browser Configuration\n")
            f.write(f"NUM_LISTINGS = {max_listings}  # Auto-set by dashboard\n")
            f.write(f"MAX_LISTINGS = {max_listings}\n")
            f.write("HEADLESS_MODE = False\n")
            f.write("TIMEOUT = 30\n")
            f.write("RETRY_ATTEMPTS = 3\n")
        add_log_to_queue("✅ Agent 1 config created")
        
        # Agent 3 config
        ensure_directory("agent_3")
        with open("agent_3/config.py", "w", encoding='utf-8') as f:
            f.write("# Agent 3 Configuration File\n")
            f.write("# Auto-generated by Dashboard\n\n")
            f.write("EMAIL_CONFIG = {\n")
            f.write(f"    'tone': '{email_tone.lower()}',\n")
            f.write("    'max_emails': 100\n")
            f.write("}\n\n")
            f.write(f"EMAIL_TONE = '{email_tone.lower()}'\n")
        add_log_to_queue("✅ Agent 3 config created")
        
        # Ensure all directories exist
        for i in range(1, 5):
            ensure_directory(f"agent_{i}/output")
            ensure_directory(f"agent_{i}/input")
        add_log_to_queue("✅ All directories created")
        add_log_to_queue("")
        
        # ========== AGENT 1 ==========
        add_log_to_queue("📍 STAGE 1/4: Listing Scraper")
        if run_agent_direct('agent_1', 'agent_1'):
            if not file_exists("agent_1/output/listings.csv"):
                add_log_to_queue("❌ Agent 1 did not produce listings.csv")
                update_status_file('pipeline_running', False)
                return
            
            add_log_to_queue("")
            
            # ========== AGENT 2 ==========
            add_log_to_queue("📍 STAGE 2/4: Broker Intelligence")
            transfer_file("agent_1/output/listings.csv", "agent_2/input/listings.csv")
            
            if run_agent_direct('agent_2', 'agent_2'):
                if not file_exists("agent_2/output/Master_Broker_Database.csv"):
                    add_log_to_queue("❌ Agent 2 did not produce Master_Broker_Database.csv")
                    update_status_file('pipeline_running', False)
                    return
                
                add_log_to_queue("")
                
                # ========== AGENT 3 ==========
                add_log_to_queue("📍 STAGE 3/4: Email Outreach")
                transfer_file("agent_2/output/Master_Broker_Database.csv", 
                             "agent_3/input/Master_Broker_Database.csv")
                
                if run_agent_direct('agent_3', 'agent_3'):
                    if not file_exists("agent_3/output/email_drafts.csv"):
                        add_log_to_queue("❌ Agent 3 did not produce email_drafts.csv")
                        update_status_file('pipeline_running', False)
                        return
                    
                    add_log_to_queue("")
                    
                    # ========== AGENT 4 ==========
                    add_log_to_queue("📍 STAGE 4/4: Data Catalog")
                    transfer_file("agent_1/output/listings.csv", "agent_4/input/listings.csv")
                    transfer_file("agent_2/output/Master_Broker_Database.csv", 
                                 "agent_4/input/Master_Broker_Database.csv")
                    transfer_file("agent_3/output/email_drafts.csv", 
                                 "agent_4/input/email_drafts.csv")
                    
                    if run_agent_direct('agent_4', 'agent_4'):
                        add_log_to_queue("")
                        add_log_to_queue("=" * 50)
                        add_log_to_queue("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
                        add_log_to_queue("=" * 50)
                        
                        # Mark complete in status file
                        status_file = Path("pipeline_status.json")
                        if status_file.exists():
                            with open(status_file, 'r', encoding='utf-8') as f:
                                status_data = json.load(f)
                            status_data['pipeline_complete'] = True
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
        add_log_to_queue(f"❌ Pipeline error: {str(e)}")
        # Mark pipeline as not running
        status_file = Path("pipeline_status.json")
        if status_file.exists():
            with open(status_file, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
            status_data['pipeline_running'] = False
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2)

# ============================================
# SIDEBAR - SETTINGS
# ============================================

st.sidebar.markdown("## ⚙️ Pipeline Settings")

# Listings per website
max_listings = st.sidebar.number_input(
    "📊 Listings per Website",
    min_value=1,
    max_value=10000,
    value=20,
    step=1,
    help="Enter any number of listings (1 to 10000)"
)

# Email tone selection
st.sidebar.markdown("### 📧 Email Tone")
email_tone = st.sidebar.selectbox(
    "Select outreach tone:",
    ["Professional", "Relationship-Based", "Direct"],
    index=0
)

st.sidebar.markdown("---")

# Start Pipeline Button
start_button = st.sidebar.button(
    "🚀 START PIPELINE",
    disabled=st.session_state.pipeline_running,
    use_container_width=True
)

# Reset Button
if st.sidebar.button("🔄 RESET", use_container_width=True):
    # Clear status file
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

# Show current status in sidebar
if st.session_state.pipeline_running:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Status")
    current = st.session_state.current_agent or 'Processing...'
    st.sidebar.warning(f"🔄 Running: {current}")
    
    # Auto-refresh
    if st.sidebar.button("🔃 Refresh Status", use_container_width=True):
        load_status()
        st.rerun()

# ============================================
# MAIN DASHBOARD
# ============================================

# Load saved status on startup
load_status()

# Process any queued logs
process_log_queue()

# Header
st.markdown('<div class="main-header">🏢 Business Acquisition Pipeline</div>', unsafe_allow_html=True)
st.markdown("---")

# Create two columns: Agents (left) and Logs (right)
col1, col2 = st.columns([2, 1])

# ============================================
# AGENT STATUS BOXES (Left Column)
# ============================================

with col1:
    st.markdown("### 🤖 Agent Status")
    
    # Status display info
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
    
    # First row: Agent 1 and Agent 2
    row1_col1, row1_col2 = st.columns(2)
    
    # Agent 1
    with row1_col1:
        status = st.session_state.agent_status['agent_1']
        status_class = f'agent-{status}'
        
        st.markdown(f"""
        <div class="agent-box {status_class}">
            <div style="font-size: 1.2rem;">🔍 Agent 1</div>
            <div style="font-size: 1rem; font-weight: normal;">Listing Scraper</div>
            <div style="font-size: 0.85rem; font-weight: normal; margin-top: 0.3rem; color: #666;">Scraping business listings</div>
            <div style="margin-top: 0.5rem; font-size: 1.1rem;">{status_emoji[status]} {status_text[status]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Agent 2
    with row1_col2:
        status = st.session_state.agent_status['agent_2']
        status_class = f'agent-{status}'
        
        st.markdown(f"""
        <div class="agent-box {status_class}">
            <div style="font-size: 1.2rem;">👔 Agent 2</div>
            <div style="font-size: 1rem; font-weight: normal;">Broker Intelligence</div>
            <div style="font-size: 0.85rem; font-weight: normal; margin-top: 0.3rem; color: #666;">Extracting broker info</div>
            <div style="margin-top: 0.5rem; font-size: 1.1rem;">{status_emoji[status]} {status_text[status]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Second row: Agent 3 and Agent 4
    row2_col1, row2_col2 = st.columns(2)
    
    # Agent 3
    with row2_col1:
        status = st.session_state.agent_status['agent_3']
        status_class = f'agent-{status}'
        
        st.markdown(f"""
        <div class="agent-box {status_class}">
            <div style="font-size: 1.2rem;">✉️ Agent 3</div>
            <div style="font-size: 1rem; font-weight: normal;">Email Outreach</div>
            <div style="font-size: 0.85rem; font-weight: normal; margin-top: 0.3rem; color: #666;">Generating emails</div>
            <div style="margin-top: 0.5rem; font-size: 1.1rem;">{status_emoji[status]} {status_text[status]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Agent 4
    with row2_col2:
        status = st.session_state.agent_status['agent_4']
        status_class = f'agent-{status}'
        
        st.markdown(f"""
        <div class="agent-box {status_class}">
            <div style="font-size: 1.2rem;">📁 Agent 4</div>
            <div style="font-size: 1rem; font-weight: normal;">Data Catalog</div>
            <div style="font-size: 0.85rem; font-weight: normal; margin-top: 0.3rem; color: #666;">Organizing data</div>
            <div style="margin-top: 0.5rem; font-size: 1.1rem;">{status_emoji[status]} {status_text[status]}</div>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# LOGS (Right Column)
# ============================================

with col2:
    st.markdown("### 📋 Activity Log")
    
    if st.session_state.logs:
        # Create scrollable log container with better visibility
        log_text = "\n".join(st.session_state.logs[-30:])  # Show last 30 logs
        st.markdown(f'<div class="log-box"><pre>{log_text}</pre></div>', unsafe_allow_html=True)
        
        # Add clear logs button
        if st.button("🗑️ Clear Logs", use_container_width=True):
            st.session_state.logs = []
            save_status()
            st.rerun()
    else:
        st.markdown("""
        <div style='background-color: #e8f4f8; border: 2px solid #b3d9e6; border-radius: 8px; 
                    padding: 1.5rem; text-align: center; color: #2c5f7a;'>
            <strong>📋 No activity yet</strong><br>
            <span style='font-size: 0.9rem;'>Click 'START PIPELINE' to begin</span>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# SUCCESS BANNER
# ============================================

if st.session_state.pipeline_complete:
    st.markdown("""
    <div class="success-banner">
        🎉 Pipeline Successfully Completed! 🎉<br>
        All agents finished processing. Download your files below.
    </div>
    """, unsafe_allow_html=True)

# ============================================
# FILE DOWNLOADS
# ============================================

if st.session_state.pipeline_complete or any(
    status == 'completed' for status in st.session_state.agent_status.values()
):
    st.markdown("---")
    st.markdown("### 📥 Download Files")
    
    download_col1, download_col2, download_col3, download_col4 = st.columns(4)
    
    # Agent 1 Output
    with download_col1:
        if file_exists("agent_1/output/listings.csv"):
            with open("agent_1/output/listings.csv", "rb") as f:
                st.download_button(
                    label="📄 Listings.csv",
                    data=f,
                    file_name=f"listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.button("📄 Listings.csv", disabled=True, use_container_width=True)
    
    # Agent 2 Output
    with download_col2:
        if file_exists("agent_2/output/Master_Broker_Database.csv"):
            with open("agent_2/output/Master_Broker_Database.csv", "rb") as f:
                st.download_button(
                    label="👔 Brokers.csv",
                    data=f,
                    file_name=f"brokers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.button("👔 Brokers.csv", disabled=True, use_container_width=True)
    
    # Agent 3 Output
    with download_col3:
        if file_exists("agent_3/output/email_drafts.csv"):
            with open("agent_3/output/email_drafts.csv", "rb") as f:
                st.download_button(
                    label="✉️ Emails.csv",
                    data=f,
                    file_name=f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.button("✉️ Emails.csv", disabled=True, use_container_width=True)
    
    # Agent 4 Output
    with download_col4:
        if file_exists("agent_4/output/final_catalog.csv"):
            with open("agent_4/output/final_catalog.csv", "rb") as f:
                st.download_button(
                    label="📁 Catalog.csv",
                    data=f,
                    file_name=f"catalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.button("📁 Catalog.csv", disabled=True, use_container_width=True)

# ============================================
# PIPELINE EXECUTION
# ============================================

if start_button:
    st.session_state.pipeline_running = True
    st.session_state.pipeline_complete = False
    
    # Start pipeline in background thread
    pipeline_thread = threading.Thread(
        target=run_pipeline_background,
        args=(max_listings, email_tone),
        daemon=True
    )
    pipeline_thread.start()
    
    # Immediately rerun to show "processing" status
    st.rerun()

# Auto-refresh during execution - every 1 second
if st.session_state.pipeline_running:
    time.sleep(1)
    load_status()
    process_log_queue()
    st.rerun()

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🏢 Business Acquisition Multi-Agent System</p>
    <p style='font-size: 0.9rem;'>Automated listing scraping, broker intelligence & email outreach</p>
</div>
""", unsafe_allow_html=True)
=======
import streamlit as st
import pandas as pd
import subprocess
import sys
import os
import shutil
from pathlib import Path
import time
from datetime import datetime
import json
import threading
from queue import Queue

st.set_page_config(
    page_title="Business Acquisition System",
    page_icon="🏢",
    layout="wide"
)

# Initialize session state
if 'pipeline_running' not in st.session_state:
    st.session_state.pipeline_running = False
if 'pipeline_logs' not in st.session_state:
    st.session_state.pipeline_logs = []
if 'current_stage' not in st.session_state:
    st.session_state.current_stage = ""

class AgentRunner:
    def __init__(self):
        self.log_queue = Queue()
        self.current_agent = ""
        
    def log_message(self, message):
        """Add message to log queue"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put(f"[{timestamp}] {message}")
        
    def run_agent_1(self, num_listings=10):
        """Run Agent 1 with proper configuration"""
        try:
            self.current_agent = "Agent 1"
            self.log_message("🚀 Starting Agent 1: Business Listing Scraper")
            
            # Update config dynamically
            config_path = Path("agent_1/config.py")
            if config_path.exists():
                config_content = config_path.read_text()
                # Update max_listings for all websites
                config_content = config_content.replace(
                    '"max_listings": 1',
                    f'"max_listings": {num_listings}'
                )
                config_path.write_text(config_content)
                self.log_message(f"✓ Updated config: {num_listings} listings per website")
            
            # Run agent 1
            result = subprocess.run(
                [sys.executable, "main.py"],
                cwd="agent_1",
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                self.log_message("✅ Agent 1 completed successfully")
                self.log_message(result.stdout)
                
                # Copy output to agent 2
                self.copy_agent1_to_agent2()
                return True
            else:
                self.log_message(f"❌ Agent 1 failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_message("⏰ Agent 1 timed out")
            return False
        except Exception as e:
            self.log_message(f"❌ Agent 1 error: {str(e)}")
            return False
    
    def copy_agent1_to_agent2(self):
        """Copy Agent 1 output to Agent 2 input"""
        try:
            source = Path("agent_1/output/listings.csv")
            dest_dir = Path("agent_2/input")
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / "listings.csv"
            
            if source.exists():
                shutil.copy(source, dest)
                self.log_message(f"✓ Copied listings to Agent 2 input")
            else:
                self.log_message("⚠ No listings.csv found from Agent 1")
                
        except Exception as e:
            self.log_message(f"❌ Copy error: {str(e)}")
    
    def run_agent_2(self):
        """Run Agent 2: Broker Intelligence"""
        try:
            self.current_agent = "Agent 2"
            self.log_message("🚀 Starting Agent 2: Broker Intelligence")
            
            result = subprocess.run(
                [sys.executable, "main.py"],
                cwd="agent_2",
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                self.log_message("✅ Agent 2 completed successfully")
                self.log_message(result.stdout)
                
                # Copy output to agent 3
                self.copy_agent2_to_agent3()
                return True
            else:
                self.log_message(f"❌ Agent 2 failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_message("⏰ Agent 2 timed out")
            return False
        except Exception as e:
            self.log_message(f"❌ Agent 2 error: {str(e)}")
            return False
    
    def copy_agent2_to_agent3(self):
        """Copy Agent 2 output to Agent 3 input"""
        try:
            source = Path("agent_2/output/Master_Broker_Database.csv")
            dest_dir = Path("agent_3/input")
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / "Master_Broker_Database.csv"
            
            if source.exists():
                shutil.copy(source, dest)
                self.log_message(f"✓ Copied broker database to Agent 3 input")
            else:
                self.log_message("⚠ No Master_Broker_Database.csv found from Agent 2")
                
        except Exception as e:
            self.log_message(f"❌ Copy error: {str(e)}")
    
    def run_agent_3(self, email_tone='professional'):
        """Run Agent 3: Email Outreach"""
        try:
            self.current_agent = "Agent 3"
            self.log_message("🚀 Starting Agent 3: Email Outreach")
            
            # Create a modified main.py for non-interactive execution
            agent3_main = Path("agent_1/main_non_interactive.py")
            # We'll modify the agent to accept tone as parameter
            
            result = subprocess.run(
                [sys.executable, "main.py"],
                cwd="agent_3",
                capture_output=True,
                text=True,
                timeout=600,
                input=f"{email_tone[0]}\n"  # Provide tone input
            )
            
            if result.returncode == 0:
                self.log_message("✅ Agent 3 completed successfully")
                self.log_message(result.stdout)
                
                # Copy output to agent 4
                self.copy_agent3_to_agent4()
                return True
            else:
                self.log_message(f"❌ Agent 3 failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_message("⏰ Agent 3 timed out")
            return False
        except Exception as e:
            self.log_message(f"❌ Agent 3 error: {str(e)}")
            return False
    
    def copy_agent3_to_agent4(self):
        """Copy Agent 3 output to Agent 4 input"""
        try:
            source = Path("agent_3/output/email_drafts.csv")
            dest_dir = Path("agent_4/input")
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / "email_drafts.csv"
            
            if source.exists():
                shutil.copy(source, dest)
                self.log_message(f"✓ Copied email drafts to Agent 4 input")
            else:
                self.log_message("⚠ No email_drafts.csv found from Agent 3")
                
        except Exception as e:
            self.log_message(f"❌ Copy error: {str(e)}")
    
    def copy_all_to_agent4(self):
        """Copy all outputs to Agent 4"""
        try:
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
                    self.log_message(f"✓ Copied {src_path.name} to Agent 4")
                else:
                    self.log_message(f"⚠ {src_path.name} not found")
                    
        except Exception as e:
            self.log_message(f"❌ Copy to Agent 4 error: {str(e)}")
    
    def run_agent_4(self):
        """Run Agent 4: Data Catalog"""
        try:
            self.current_agent = "Agent 4"
            self.log_message("🚀 Starting Agent 4: Data Catalog")
            
            # First copy all files to agent 4
            self.copy_all_to_agent4()
            
            result = subprocess.run(
                [sys.executable, "main.py"],
                cwd="agent_4",
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                self.log_message("✅ Agent 4 completed successfully")
                self.log_message(result.stdout)
                return True
            else:
                self.log_message(f"❌ Agent 4 failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_message("⏰ Agent 4 timed out")
            return False
        except Exception as e:
            self.log_message(f"❌ Agent 4 error: {str(e)}")
            return False

def check_agent_status():
    """Check if all agent directories exist"""
    agents = {
        "Agent 1 (Scraper)": Path("agent_1"),
        "Agent 2 (Broker Intel)": Path("agent_2"),
        "Agent 3 (Email)": Path("agent_3"),
        "Agent 4 (Data Catalog)": Path("agent_4")
    }
    
    status = {}
    for name, path in agents.items():
        status[name] = path.exists() and (path / "main.py").exists()
    
    return status

def get_output_files():
    """Get available output files"""
    files = {}
    
    output_paths = {
        "Business Listings": "agent_1/output/listings.csv",
        "Broker Database": "agent_2/output/Master_Broker_Database.csv",
        "Email Drafts": "agent_3/output/email_drafts.csv"
    }
    
    for name, path in output_paths.items():
        if Path(path).exists():
            files[name] = path
    
    return files

# Main UI
st.title("🏢 Business Acquisition System")
st.markdown("---")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Dashboard", "Run Pipeline", "View Results", "Settings"])

if page == "Dashboard":
    st.header("📊 System Dashboard")
    
    # Agent Status
    st.subheader("🤖 Agent Status")
    agent_status = check_agent_status()
    
    cols = st.columns(2)
    for i, (name, status) in enumerate(agent_status.items()):
        with cols[i % 2]:
            if status:
                st.success(f"✅ {name}: Ready")
            else:
                st.error(f"❌ {name}: Missing")
    
    # Recent Outputs
    st.subheader("📁 Recent Outputs")
    output_files = get_output_files()
    
    if output_files:
        for name, path in output_files.items():
            file_size = Path(path).stat().st_size
            file_date = datetime.fromtimestamp(Path(path).stat().st_mtime)
            st.info(f"📄 {name}: {file_size} bytes (Updated: {file_date.strftime('%Y-%m-%d %H:%M')})")
    else:
        st.warning("⏳ No output files found. Run the pipeline to generate results.")

elif page == "Run Pipeline":
    st.header("🚀 Run Pipeline")
    
# Pipeline Configuration
    with st.expander("⚙️ Pipeline Configuration", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            num_listings = st.number_input(
                "Listings per website", 
                min_value=1, 
                max_value=50, 
                value=5,
                help="Maximum number of listings to scrape from each website"
            )
            
        with col2:
            email_tone = st.selectbox(
                "Email Tone",
                ["professional", "relationship", "direct"],
                help="Tone for generated email drafts"
            )
        
        run_mode = st.selectbox(
            "Run Mode",
            ["Full Pipeline", "Individual Agents"],
            help="Run complete pipeline or select specific agents"
        )
        
        # Initialize agent selection variables
        agent1_run = agent2_run = agent3_run = agent4_run = True
        
        if run_mode == "Individual Agents":
            st.subheader("Select Agents to Run")
            agent1_run = st.checkbox("Agent 1: Listing Scraper", value=True)
            agent2_run = st.checkbox("Agent 2: Broker Intelligence", value=True)
            agent3_run = st.checkbox("Agent 3: Email Outreach", value=True)
            agent4_run = st.checkbox("Agent 4: Data Catalog", value=True)
    
    # Pipeline Control
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🚀 Start Pipeline", type="primary", disabled=st.session_state.pipeline_running):
            st.session_state.pipeline_running = True
            st.session_state.pipeline_logs = []
            st.session_state.current_stage = "Initializing..."
            
            # Start pipeline in background
            def run_pipeline():
                runner = AgentRunner()
                
                try:
                    if run_mode == "Full Pipeline":
                        st.session_state.current_stage = "Agent 1: Scraping Listings"
                        success = runner.run_agent_1(num_listings)
                        
                        if success:
                            st.session_state.current_stage = "Agent 2: Broker Intelligence"
                            success = runner.run_agent_2()
                        
                        if success:
                            st.session_state.current_stage = "Agent 3: Email Outreach"
                            success = runner.run_agent_3(email_tone)
                        
                        if success:
                            st.session_state.current_stage = "Agent 4: Data Catalog"
                            success = runner.run_agent_4()
                        
                        if success:
                            st.session_state.current_stage = "✅ Pipeline Complete!"
                            runner.log_message("🎉 Full pipeline completed successfully!")
                        else:
                            st.session_state.current_stage = "❌ Pipeline Failed"
                            runner.log_message("❌ Pipeline failed during execution")
                    
                    else:
                        # Individual agents
                        agents_to_run = []
                        if agent1_run: agents_to_run.append(("Agent 1", lambda: runner.run_agent_1(num_listings)))
                        if agent2_run: agents_to_run.append(("Agent 2", runner.run_agent_2))
                        if agent3_run: agents_to_run.append(("Agent 3", lambda: runner.run_agent_3(email_tone)))
                        if agent4_run: agents_to_run.append(("Agent 4", runner.run_agent_4))
                        
                        for agent_name, agent_func in agents_to_run:
                            st.session_state.current_stage = f"Running {agent_name}"
                            success = agent_func()
                            if not success:
                                runner.log_message(f"❌ {agent_name} failed")
                                break
                        
                        if all([agent_func() for _, agent_func in agents_to_run]):
                            st.session_state.current_stage = "✅ Selected Agents Complete!"
                            runner.log_message("🎉 All selected agents completed successfully!")
                
                except Exception as e:
                    st.session_state.current_stage = f"❌ Error: {str(e)}"
                    runner.log_message(f"❌ Pipeline error: {str(e)}")
                
                finally:
                    st.session_state.pipeline_running = False
            
            # Run pipeline in thread
            pipeline_thread = threading.Thread(target=run_pipeline)
            pipeline_thread.start()
    
    with col2:
        if st.button("⏹️ Stop Pipeline", disabled=not st.session_state.pipeline_running):
            st.session_state.pipeline_running = False
            st.session_state.current_stage = "Stopped"
    
    # Progress Display
    if st.session_state.pipeline_running or st.session_state.pipeline_logs:
        st.subheader("📊 Pipeline Progress")
        
        # Current Stage
        if st.session_state.current_stage:
            st.info(f"🔄 Current Stage: {st.session_state.current_stage}")
        
        # Logs
        if st.session_state.pipeline_logs:
            st.subheader("📝 Execution Logs")
            log_container = st.container()
            with log_container:
                for log in st.session_state.pipeline_logs[-20:]:  # Show last 20 logs
                    st.text(log)

elif page == "View Results":
    st.header("📊 View Results")
    
    output_files = get_output_files()
    
    if not output_files:
        st.warning("⚠ No output files found. Run the pipeline first to generate results.")
        st.info("💡 Go to 'Run Pipeline' page to execute the agents and generate data.")
    else:
        # File Selection
        selected_file = st.selectbox("Select file to view", list(output_files.keys()))
        file_path = output_files[selected_file]
        
        if Path(file_path).exists():
            try:
                df = pd.read_csv(file_path)
                
                st.subheader(f"📄 {selected_file}")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Rows", f"{df.shape[0]:,}")
                with col2:
                    st.metric("Columns", df.shape[1])
                with col3:
                    file_size = Path(file_path).stat().st_size
                    st.metric("File Size", f"{file_size / 1024:.1f} KB")
                
                # Data Preview
                st.subheader("📋 Data Preview")
                
                # Search/Filter
                search_term = st.text_input("🔍 Search data (optional)", placeholder="Enter search term...")
                
                if search_term:
                    mask = df.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)
                    filtered_df = df[mask]
                    st.write(f"Showing {len(filtered_df)} of {len(df)} matching results")
                    st.dataframe(filtered_df, use_container_width=True)
                else:
                    st.dataframe(df, use_container_width=True)
                
                # Column Information
                with st.expander("📊 Column Information"):
                    col_info = pd.DataFrame({
                        'Column': df.columns,
                        'Type': df.dtypes.values,
                        'Non-Null Count': df.count().values,
                        'Unique Values': df.nunique().values
                    })
                    st.dataframe(col_info, use_container_width=True)
                
                # Download Options
                st.subheader("💾 Download Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name=f"{selected_file.lower().replace(' ', '_')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    try:
                        from io import BytesIO
                        excel_buffer = BytesIO()
                        df.to_excel(excel_buffer, index=False, engine='openpyxl')
                        excel_data = excel_buffer.getvalue()
                        st.download_button(
                            label="📥 Download Excel",
                            data=excel_data,
                            file_name=f"{selected_file.lower().replace(' ', '_')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except:
                        st.warning("Excel download not available (openpyxl not installed)")
                
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")

elif page == "Settings":
    st.header("⚙️ System Settings")
    
    # Agent Configuration
    st.subheader("🤖 Agent Configuration")
    
    # Agent 1 Settings
    with st.expander("🔍 Agent 1: Scraping Settings"):
        st.write("Configure business listing scraping parameters")
        
        # Read current config
        config_path = Path("agent_1/config.py")
        if config_path.exists():
            st.info("Current configuration loaded from agent_1/config.py")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Websites:**")
            st.checkbox("BizBuySell", value=True, disabled=True)
            st.checkbox("BizQuest", value=True, disabled=True)
            st.checkbox("LoopNet", value=True, disabled=True)
        
        with col2:
            st.write("**Limits:**")
            st.number_input("Max listings per site", min_value=1, max_value=100, value=10, disabled=True)
            st.number_input("Max pages per site", min_value=1, max_value=10, value=3, disabled=True)
    
    # System Information
    st.subheader("💻 System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Environment:**")
        st.code(f"Python: {sys.version.split()[0]}")
        st.code(f"Working Dir: {Path.cwd()}")
        
        try:
            import streamlit
            st.code(f"Streamlit: {streamlit.__version__}")
        except:
            pass
    
    with col2:
        st.write("**Agent Status:**")
        agent_status = check_agent_status()
        for name, status in agent_status.items():
            status_icon = "✅" if status else "❌"
            st.code(f"{status_icon} {name}")
    
    # Output Files Status
    st.subheader("📁 Output Files Status")
    
    output_files = get_output_files()
    expected_files = {
        "Business Listings": "agent_1/output/listings.csv",
        "Broker Database": "agent_2/output/Master_Broker_Database.csv", 
        "Email Drafts": "agent_3/output/email_drafts.csv"
    }
    
    for name, path in expected_files.items():
        if Path(path).exists():
            file_size = Path(path).stat().st_size
            file_date = datetime.fromtimestamp(Path(path).stat().st_mtime)
            st.success(f"✅ {name}: {file_size} bytes ({file_date.strftime('%Y-%m-%d %H:%M')})")
        else:
            st.warning(f"⏳ {name}: Not generated yet")

# Auto-refresh logs when pipeline is running
if st.session_state.pipeline_running and page == "Run Pipeline":
    time.sleep(1)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("**Business Acquisition System** - Integrated Multi-Agent Pipeline for Business Opportunity Analysis")
>>>>>>> 7ba3c8725efb6a2051e9ac9233640be8c397066a
