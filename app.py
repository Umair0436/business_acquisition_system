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