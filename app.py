import streamlit as st
import pandas as pd
import json
import uuid
import os
from engine import StatefulAuditableAssistant

# Configure Premium High-Fidelity App Real-Estate Layout
st.set_page_config(
    page_title="Data Analysis Assistant",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styled header branding injections
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 95%; }
    .stAlert { padding: 10px; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DYNAMIC MULTI-FILE FILE UPLOADER & EXCEL TAB EXTRACTOR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("📁 Data Source")
    st.caption("Drop user spreadsheets (.csv or .xlsx) here.")
    
    # PRODUCTION UPDATE: Added support for both csv and xlsx file formats
    uploaded_files = st.file_uploader(
        "Upload sheets (.csv or .xlsx)", 
        type=["csv", "xlsx"], 
        accept_multiple_files=True,
        key="production_uploader"
    )
    
    file_paths = []
    if uploaded_files:
        for u_file in uploaded_files:
            if u_file.name.endswith(".xlsx"):
                # PRODUCTION UPDATE: Read all sheets dynamically from workbook
                try:
                    excel_workbook = pd.read_excel(u_file, sheet_name=None)
                    base_workbook_name = os.path.splitext(u_file.name)[0].strip().replace(" ", "_").lower()
                    
                    for sheet_name, df in excel_workbook.items():
                        clean_sheet_name = sheet_name.strip().replace(" ", "_").lower()
                        # Output every sheet as a decoupled csv asset
                        csv_filename = f"{base_workbook_name}_{clean_sheet_name}.csv"
                        df.to_csv(csv_filename, index=False)
                        file_paths.append(csv_filename)
                except Exception as excel_err:
                    st.sidebar.error(f"Failed to process workbook sheets inside '{u_file.name}': {str(excel_err)}")
            else:
                # Standard CSV pipeline mapping
                with open(u_file.name, "wb") as f:
                    f.write(u_file.getbuffer())
                file_paths.append(u_file.name)
                
        storage_signature = "UPLOADED:" + ",".join(sorted(file_paths))
    else:
        # Graceful auto-detect baseline sheets if pre-loaded inside working directory
        sample_default_files = ["category.csv", "products.csv", "sales.csv", "stores.csv"]
        if all(os.path.exists(f) for f in sample_default_files):
            file_paths = sample_default_files
            storage_signature = "DEFAULT:" + ",".join(sorted(file_paths))
        else:
            storage_signature = "EMPTY"

    if storage_signature != "EMPTY":
        if "active_sig" not in st.session_state or st.session_state.active_sig != storage_signature:
            with st.spinner("Unpacking sheets and compiling schema metadata structures..."):
                st.session_state.assistant = StatefulAuditableAssistant(file_paths=file_paths)
                st.session_state.active_sig = storage_signature
                st.session_state.session_uuid = f"SESSION_{uuid.uuid4().hex[:6].upper()}"
                st.success("Database catalog compiled cleanly!")

# -----------------------------------------------------------------------------
# SIDEBAR PANEL: VFS BACKEND STORAGE MONITOR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.divider()
    st.title("🛡️ VFS Sandbox")
    st.caption("Inspect reporting files written inside memory by the query pipelines.")
    
    if "session_uuid" in st.session_state and "assistant" in st.session_state:
        session_id = st.session_state.session_uuid
        assistant = st.session_state.assistant
        
        st.info(f"**Session Identifier ID:** `{session_id}`")
        st.divider()
        
        vfs_files = assistant.vfs.list_files(session_id)
        if not vfs_files:
            st.warning("No sandbox reporting components compiled yet.")
        else:
            selected_vfs_asset = st.selectbox(
                "Select a VFS container file:",
                vfs_files,
                key="production_vfs_selectbox"
            )
            
            if selected_vfs_asset:
                file_raw_content = assistant.vfs.read_file(session_id, selected_vfs_asset)
                st.markdown(f"**Inspecting file:** `{selected_vfs_asset}`")
                if selected_vfs_asset.endswith(".json"):
                    st.json(json.loads(file_raw_content))
                else:
                    st.text("Raw Table Sheet Preview:")
                    st.code(file_raw_content, language="csv")
                    
        st.divider()
        if st.button("Reset Converse Memory Logs", type="secondary"):
            assistant.session_memory[session_id] = []
            if session_id in assistant.vfs.storage:
                assistant.vfs.storage[session_id] = {}
            st.rerun()

# -----------------------------------------------------------------------------
# MAIN APP WORKSPACE: INTERACTIVE CONVERSATIONAL LAYER
# -----------------------------------------------------------------------------
st.title("🔮 Data Analysis Assistant Dashboard")
st.markdown(
    "Submit conversational inquiries or relational joins across corporate documents. "
    "Every surfaced output number triggers **automated pixel-level lineage tracing logs** across files."
)
st.divider()

if storage_signature == "EMPTY":
    st.error("Data Warehouse Uninitialized. Drag and drop your CSV or Excel workbook sheets into the sidebar to construct the analysis framework.")
else:
    session_id = st.session_state.session_uuid
    assistant = st.session_state.assistant
    
    # Use setdefault to make KeyErrors physically impossible
    active_history = assistant.session_memory.setdefault(session_id, [])
        
    # Render state-persisted conversational text blocks
    for msg in active_history:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["answer"])
            else:
                st.markdown(msg["answer"])
                
                # If the action compiled records successfully, draw native lineage tools
                if msg.get("status") == "success":
                    with st.expander(f"🔍 Click to view Data Lineage Audit Trail ({msg.get('transaction_token')})"):
                        tab1, tab2, tab3 = st.tabs(["📋 Lineage Summary", "⚙️ Compiler Blueprint", "📊 Data Frame Slice"])
                        
                        details = msg.get("lineage_details", {})
                        
                        with tab1:
                            st.info(f"{details.get('human_readable_summary')}")
                            st.write("") # Quick spacing buffer
                            
                            # Elegant multi-column metric dashboard split
                            c1, c2, c3 = st.columns(3)
                            
                            with c1:
                                st.markdown("**Source File Elements**")
                                for src_file in details.get("source_files", []):
                                    st.markdown(f"📄 `{src_file}`")
                                    
                            c2.metric(label="Scanned Row Count", value=f"{len(details.get('row_offsets', []))} Rows")
                            c3.metric(label="Involved Schema Headers", value=f"{len(details.get('columns', []))} Fields")
                        
                        with tab2:
                            st.markdown("**Compiled SQL Execution Instruction:**")
                            st.code(msg.get("sql"), language="sql")
                            st.markdown("**DuckDB Logical Plan Transformation String:**")
                            st.code(msg.get("execution_plan"))
                            
                        with tab3:
                            st.markdown(f"**Raw Dataset Cached inside VFS File Container:** `{msg.get('csv_name')}`")
                            raw_json_str = msg.get("clean_df_json")
                            if raw_json_str:
                                df_slice = pd.DataFrame(json.loads(raw_json_str))
                                st.dataframe(df_slice, use_container_width=True)
                            else:
                                st.text("[Empty Result Set]")

    # Capture real-time user dashboard prompt actions
    if user_prompt := st.chat_input("Ask here..."):
        with st.chat_message("user"):
            st.markdown(user_prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Processing ..."):
                assistant.chat(session_id, user_prompt)
                
        st.rerun()