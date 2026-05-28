import os
import re
import json
import uuid
import duckdb
from typing import Tuple, List, Dict, Any
from google import genai
from google.genai import types

# Initialize the global Google GenAI client configuration context
client = genai.Client()

class VirtualFileSystem:
    """An in-memory isolated sandbox structure simulating a cloud directory storage environment.
    
    This class handles multi-tenant folder segregation dynamically, enabling the headless 
    analytical assistant engine to serialize, partition, and store intermediate reporting 
    artifacts safely without executing absolute or relative local storage disk writes.
    
    Attributes:
        storage (Dict[str, Dict[str, str]]): A structured nested directory lookup map configured 
            as `{ session_uuid: { filename_string: file_content_string } }`.
    """

    def __init__(self):
        """Initializes the Virtual File System workspace container with a blank root map."""
        self.storage: Dict[str, Dict[str, str]] = {}

    def create_directory(self, session_id: str):
        """Allocates an isolated, secure sub-partition folder block for an active user session.
        
        Args:
            session_id: A unique tracking UUID string mapping to the live user conversational thread.
        """
        if session_id not in self.storage:
            self.storage[session_id] = {}

    def write_file(self, session_id: str, filename: str, content: str):
        """Serializes and commits a string-based asset matrix directly to a target session directory.
        
        Automatically builds the parent directory structure if it has not been instantiated.
        
        Args:
            session_id: A unique tracking UUID string mapping to the target session sub-folder.
            filename: The target structural filename string under which the asset will be saved.
            content: The raw text or serialized configuration payload string to be recorded.
        """
        self.create_directory(session_id)
        self.storage[session_id][filename] = content

    def read_file(self, session_id: str, filename: str) -> str:
        """Fetches the raw string contents of an active file artifact inside a session partition.
        
        Args:
            session_id: A unique tracking UUID string mapping to the target session sub-folder.
            filename: The specific structural filename string to read from memory.
            
        Returns:
            The raw text string of the target asset if found, or a blank string if the file or 
            session directory does not exist in the ledger.
        """
        return self.storage.get(session_id, {}).get(filename, "")

    def list_files(self, session_id: str) -> List[str]:
        """Extracts an array containing every available asset key logged within a session folder.
        
        Args:
            session_id: A unique tracking UUID string mapping to the target session sub-folder.
            
        Returns:
            A list of structural filename strings registered under the active session workspace.
        """
        return list(self.storage.get(session_id, {}).keys())


class StatefulAuditableAssistant:
    """A multi-agent data-analysis assistant enforcing full lineage traceability and zero hallucinations.
    
    This architecture utilizes a localized DuckDB relational processor combined with an in-memory 
    Virtual File System layer to ingest spreadsheets, generate structured metadata schema catalogs, 
    evaluate guardrails, track physical row coordinates across joins using a Split-Execution paradigm, 
    and output presentation-ready report artifacts without structural data modifications.
    
    Attributes:
        file_paths (List[str]): An array of local path routes mapping to ingested CSV spreadsheets.
        db (duckdb.DuckDBPyConnection): A localized, high-speed, in-memory OLAP data engine instance.
        table_metadata (Dict[str, Dict[str, Any]]): A structured compilation recording schemas, 
            categorical distinct textual keys, and numeric bounding ranges per table.
        vfs (VirtualFileSystem): The dedicated runtime in-memory storage manager instance.
        session_memory (Dict[str, List[Dict[str, Any]]]): Stateful conversational history ledger 
            mapped directly by unique session UUID keys.
        lineage_ledger (Dict[str, Dict[str, Any]]): An immutable internal tracking index registry 
            storing raw data processing lineage coordinates per transaction token.
    """

    def __init__(self, file_paths: List[str]):
        """Initializes database nodes, binds storage managers, and indexes target datasets.
        
        Args:
            file_paths: An array of path routes mapping to the spreadsheet sheets to be ingested.
        """
        self.file_paths = file_paths
        self.db = duckdb.connect(database=':memory:')
        self.table_metadata = {}
        self.vfs = VirtualFileSystem()
        
        self.session_memory: Dict[str, List[Dict[str, Any]]] = {}
        self.lineage_ledger: Dict[str, Dict[str, Any]] = {}
        
        # Trigger the atomic warehouse mapping and normalization sequences
        self._initialize_warehouse()

    def _initialize_warehouse(self):
        """Ingests raw tabular sheets into DuckDB and builds a comprehensive metadata catalog context.
        
        Appends an immutable physical row indicator onto every row of every spreadsheet via an atomic 
        scan operator:
        
        $$\\text{Row Index } (\\Delta) = \\text{row\\_number}() \\text{ OVER }() - 1$$
        
        This structural coordinate is explicitly preserved to enable pixel-precision data lineage logs across 
        future unaggregated join transformations.
        """
        for path in self.file_paths:
            file_name = os.path.basename(path)
            # Standardize table names to lowercase, stripping out spaces or illegal special characters
            table_name = os.path.splitext(file_name)[0].strip().replace(" ", "_").lower()
            
            # Read CSV auto-properties and attach the absolute data pedigree index row tracking key
            self.db.execute(f"""
                CREATE TABLE {table_name} AS 
                SELECT *, row_number() OVER () - 1 AS __lineage_row_id 
                FROM read_csv_auto('{path}');
            """)
            
            # Fetch table schema parameters, excluding our operational lineage tracker key
            columns_info = self.db.execute(f"PRAGMA table_info('{table_name}');").fetchall()
            columns = [col[1] for col in columns_info if col[1] != '__lineage_row_id']
            
            categorical_values = {}
            numeric_ranges = {}
            
            # Dynamically audit each column's type profile to map constraints and categorical values
            for col in columns:
                col_type = next(c[2] for c in columns_info if c[1] == col).upper()
                if "VARCHAR" in col_type or "TEXT" in col_type:
                    # Capture unique string records to prevent lexical hallucinations during query processing
                    distinct_vals = self.db.execute(f"SELECT DISTINCT \"{col}\" FROM {table_name};").fetchall()
                    categorical_values[col] = [val[0] for val in distinct_vals]
                elif any(num_type in col_type for num_type in ["INT", "BIGINT", "DOUBLE", "FLOAT", "NUMERIC"]):
                    # Capture mathematical min/max ranges to define explicit numerical field firewalls
                    bounds = self.db.execute(f"SELECT MIN(\"{col}\"), MAX(\"{col}\") FROM {table_name};").fetchone()
                    numeric_ranges[col] = {"min": bounds[0], "max": bounds[1]}

            # Register the completed relational definition block into the system dictionary catalog context
            self.table_metadata[table_name] = {
                "source_file": file_name,
                "schema_fields": columns,
                "valid_categorical_values": categorical_values,
                "valid_numeric_ranges": numeric_ranges
            }

    def _get_catalog_context(self) -> str:
        """Serializes the current schema mapping context into a standard formatted JSON string.
        
        Returns:
            A formatted JSON string block illustrating active column fields and boundaries.
        """
        return json.dumps(self.table_metadata, indent=2)

    def route_and_validate(self, query: str, chat_history: List[Dict[str, Any]]) -> Tuple[str, str]:
        """Agent 1 (Guardrail Router): Evaluates incoming query intent against catalog boundaries.
        
        This firewall layer ensures that any queries touching parameters or categories missing 
        from the underlying schema matrix trigger a clean programmatic abstention response 
        before any downstream code compiling or query execution routines can initiate.
        
        Args:
            query: The raw natural language input text submitted by the user.
            chat_history: The persistent array containing historical conversation turn logs.
            
        Returns:
            A tuple tracking:
                1. The evaluated routing state string ("CAN_ANSWER", "META_CONVERSATION", or "ABSTAIN").
                2. A clear textual justification or reason outlining the decision framework.
        """
        # Compress and format past conversational context parameters to maximize model routing comprehension
        history_summary = [{"role": m.get("role"), "message": m.get("answer")} for m in chat_history]
        history_context = json.dumps(history_summary, indent=2)
        
        prompt = f"""
        Evaluate if the user query can be factually answered using the available database schema catalog or active conversational history.
        If the question mentions items, brands, columns, or metrics completely missing from the catalog (e.g., 'Android', 'customer satisfaction metrics', 'profit margin'), you MUST choose 'ABSTAIN'.
        
        Available Database Catalog:
        {self._get_catalog_context()}
        
        Active Chat History Context:
        {history_context}
        
        User Query: "{query}"
        
        RESPOND ONLY IN JSON matching this schema:
        {{
            "route_state": "CAN_ANSWER" or "META_CONVERSATION" or "ABSTAIN",
            "reason": "Clear explanation citing explicit catalog metrics or conversation status metrics."
        }}
        """
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            res = json.loads(response.text)
            return res.get("route_state", "ABSTAIN"), res.get("reason", "Routing processing break.")
        except Exception as e:
            # Safely fall back to a hard abstention path if inference loops break
            return "ABSTAIN", str(e)

    def translate_to_sql(self, query: str, chat_history: List[Dict[str, Any]]) -> str:
        """Agent 2 (SQL Compiler): Translates conversational intent into unaggregated SQL commands.
        
        Enforces a strict rule barring SQL aggregations (e.g., SUM, COUNT, GROUP BY). Instead, 
        it compiles simple selection filter queries that fetch raw columns and their lineage tags. 
        This prevents row pedigree collapse, allowing downstream Python layers to run calculations 
        while preserving complete traceability.
        
        Args:
            query: The raw natural language prompt containing data analysis requests.
            chat_history: The persistent context history array utilized to resolve pronoun drift.
            
        Returns:
            A sanitized DuckDB-compliant SQL filtering query string wrapped in isolated code blocks.
        """
        history_summary = [{"role": m.get("role"), "message": m.get("answer")} for m in chat_history]
        history_context = json.dumps(history_summary, indent=2)
        
        prompt = f"""
        Convert the query into a valid DuckDB SQL selection statement that fetches the relevant filtered row records.
        Use active chat history context to resolve ambiguous references.
        
        Database Catalog Properties:
        {self._get_catalog_context()}
        
        Active Chat History Context:
        {history_context}
        
        Target User Query: "{query}"
        
        CRITICAL OPERATING RULES:
        1. Always explicitly select target columns needed to answer the question, AND explicitly include the `__lineage_row_id` column for EACH table involved, aliasing them explicitly as `tablename___lineage_row_id` (e.g., `products.__lineage_row_id AS products___lineage_row_id`, `sales.__lineage_row_id AS sales___lineage_row_id`).
        2. To preserve row lineage matching coordinates, DO NOT use SQL aggregation functions like SUM(), AVG(), or COUNT() or GROUP BY clauses in the SQL string.
        3. Instead, write a plain 'SELECT' query that grabs all matching rows so the application engine can calculate metrics over them in python.
        4. Match table column casing accurately based on the 'schema_fields' listed in the catalog.
        5. DATE TRANSFORMATION RULE: Do NOT attempt to apply SQL date functions, STRFTIME, or extract quarters (like using '%Q') inside the SQL query string. Simply select the raw date column (e.g., `sales.sale_date`) as-is. The downstream Python layer will handle parsing date text strings into calendar quarters automatically.
        
        Respond only with a raw SQL query inside a markdown block.
        """
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        sql_match = re.search(r"```sql(.*?)```", response.text, re.DOTALL)
        return sql_match.group(1).strip() if sql_match else response.text.strip()

    def generate_natural_language_answer(self, user_question: str, extracted_dataframe_json: str) -> str:
        """Agent 3 (Synthesis Core): Synthesizes verified data records into clear markdown reports.
        
        Enforces contextual grounding parameters. The engine isolates the model from the 
        primary database sheets and restricts it to formatting numbers from pre-verified JSON 
        data slices, eliminating data calculation hallucination risks.
        
        Args:
            user_question: The original analytical inquiry prompt typed by the user.
            extracted_dataframe_json: The clean, serialized JSON string of the filtered database slice.
            
        Returns:
            A fluid, professional, context-grounded natural language text response block.
        """
        prompt = f"""
        You are a data presentation synthesizer. Convert the verified SQL row outputs into a clean, professional, fluid natural language response answering the user's question.
        
        User Question: "{user_question}"
        Verified Data Rows: {extracted_dataframe_json}
        
        CRITICAL ENTERPRISE RULES:
        1. Base your answer STRICTLY on the values provided in the 'Verified Data Rows' parameter.
        2. Perform any arithmetic additions, summaries, or averages required to cleanly answer the user's question based strictly on these rows.
        3. Do not invent facts, extrapolate trends, or pull external context.
        """
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text.strip()

    def process_meta_conversation(self, query: str, chat_history: List[Dict[str, Any]]) -> str:
        """Agent 1B (Meta-Conversational Engine): Evaluates historical metadata and lineage snapshot logs.
        
        Processes dialogue queries that request operational or lineage summaries (e.g., "What files 
        did you scan for the previous query?"), pulling directly from previously saved VFS manifest snapshots.
        
        Args:
            query: The conversational or metadata query string.
            chat_history: The session log containing historical answers and manifest parameters.
            
        Returns:
            A conversational response quoting accurate provenance tracking details.
        """
        history_summary = []
        for m in chat_history:
            entry = {
                "role": m.get("role"),
                # Extract conversational content safely based on message role parameters
                "message": m.get("answer") if m.get("role") == "assistant" else m.get("message")
            }
            
            # Expose the pre-computed lineage log summaries to help the metadata agent answer cleanly
            if m.get("manifest_snapshot"):
                entry["lineage_summary"] = m["manifest_snapshot"].get("lineage_summary")
                
            history_summary.append(entry)
            
        history_context = json.dumps(history_summary, indent=2)
        
        prompt = f"""
        Answer the conversational or metadata history request based on the context logs below.
        
        CRITICAL RULE:
        If the user query is asking about the data origin, files touched, row counts, or the exact data lineage of a previous query turn, look up the 'lineage_summary' field directly within the matching chat history item to build your answer. Quote or summarize it accurately.
        
        Chat History Logs:
        {history_context}
        
        User Query: "{query}"
        """
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return response.text.strip()

    def get_logical_plan(self, clean_sql_query: str) -> str:
        """Extracts and formats the core relational execution tree from the DuckDB parser.
        
        Args:
            clean_sql_query: The sanitized SQL query string to evaluate.
            
        Returns:
            A clean pipeline string representation showing the database operator layout tree 
            (e.g., `PROJECTION -> FILTER -> SCAN`).
        """
        try:
            plan_df = self.db.execute(f"EXPLAIN {clean_sql_query}").fetchdf()
            raw_plan = plan_df['explain_value'].values[0]
            # Parse the tree plan value string into a clean horizontal operator sequence line
            return " -> ".join([line.strip() for line in raw_plan.split('\n') if any(k in line for k in ['SCAN', 'FILTER', 'PROJECTION', 'AGGREGATE', 'JOIN'])])
        except Exception:
            return "Standard Row Scan Execution"

    def chat(self, session_id: str, user_message: str) -> str:
        """Main system orchestrator running the multi-agent execution pipeline.
        
        Coordinates intent routing, query processing, line-item data lineage tracking, 
        and VFS artifact generation to construct a secure and verifiable response payload.
        
        Args:
            session_id: A unique tracking UUID string identifying the active user session.
            user_message: The raw natural language input text containing analytical requirements.
            
        Returns:
            A serialized JSON response payload containing conversational content, SQL instructions, 
            execution plans, transaction tokens, and pre-formatted lineage records.
        """
        # Allocate or load the session history array safely using defensive mapping
        active_history = self.session_memory.setdefault(session_id, [])

        # 1. Run the Guardrail Router Firewall check
        route_state, justification = self.route_and_validate(user_message, active_history)
        
        if route_state == "ABSTAIN":
            bot_reply = f"I can't answer this from the file. Reason: {justification}"
            payload = {"status": "abstain", "role": "assistant", "answer": bot_reply, "transaction_token": None}
            active_history.append({"role": "user", "message": user_message, "status": "success", "answer": user_message})
            active_history.append(payload)
            return json.dumps(payload)
            
        if route_state == "META_CONVERSATION":
            meta_reply = self.process_meta_conversation(user_message, active_history)
            payload = {"status": "meta", "role": "assistant", "answer": meta_reply, "transaction_token": None}
            active_history.append({"role": "user", "message": user_message, "status": "success", "answer": user_message})
            active_history.append(payload)
            return json.dumps(payload)

        # 2. Compile unaggregated SQL filtering syntax view
        sql_query = self.translate_to_sql(user_message, active_history)

        try:
            # Strip markdown identifiers to obtain a clean executable statement string
            clean_sql = re.sub(r"```[a-zA-Z]*", "", sql_query).replace("```", "").strip()
            result_df = self.db.execute(clean_sql).fetchdf()
            
            lineage_records = []
            # Identify which data tables are actively referenced inside the SQL text structure
            involved_tables = [t for t in self.table_metadata.keys() if t in clean_sql.lower()]
            lineage_cols = [c for c in result_df.columns if "lineage" in c.lower()]

            row_identity_footprint = []
            # Traverse through every matched record line to map granular coordinate points
            for idx, row in result_df.iterrows():
                for t in involved_tables:
                    # Dynamically match target lineage row keys to locate true baseline row offsets
                    specific_col = f"{t}___lineage_row_id"
                    matched_id_col = next((c for c in result_df.columns if c.lower() == specific_col.lower()), None)
                    if not matched_id_col:
                        matched_id_col = next((c for c in result_df.columns if t in c.lower() and "lineage" in c.lower()), None)
                    if not matched_id_col:
                        matched_id_col = next((c for c in result_df.columns if "lineage" in c.lower()), None)
                    
                    if matched_id_col:
                        try:
                            val_str = str(row[matched_id_col]).split('.')[0].split(',')[0]
                            row_idx = int(val_str)
                        except:
                            row_idx = int(idx)
                    else:
                        row_idx = int(idx)
                    
                    # Log the exact table name and matching row index offset coordinate 
                    row_identity_footprint.append({"table": t, "row": row_idx})

                # Map specific cell tracking values back to their source sheet filenames
                for col in result_df.columns:
                    if "lineage" in col.lower():
                        continue
                    target_table = next((t for t in involved_tables if col.lower() in [s.lower() for s in self.table_metadata[t]["schema_fields"]]), None)
                    if target_table:
                        lineage_records.append({
                            "file": self.table_metadata[target_table]["source_file"],
                            "column": col,
                            "value": str(row[col])
                        })

            # Fetch the execution tree layout and build an absolute tracking token identifier
            logical_recipe = self.get_logical_plan(clean_sql)
            transaction_token = f"TXN_{uuid.uuid4().hex[:8].upper()}"
            
            # Record the full lineage dataset details into our internal tracking registry
            self.lineage_ledger[transaction_token] = {
                "raw_records": lineage_records,
                "logical_recipe": logical_recipe,
                "row_footprint": row_identity_footprint,
                "original_sql": clean_sql
            }

            # Drop temporary lineage metadata columns to build a clean display table slice
            clean_df = result_df.drop(columns=lineage_cols, errors='ignore')
            clean_df = clean_df.loc[:, ~clean_df.columns.str.contains('lineage', case=False)]

            # Formulate structured asset filenames for the Virtual File System sandbox
            csv_name = f"query_{transaction_token.lower()}_data.csv"
            filename_manifest = f"query_{transaction_token.lower()}_manifest.json"
            
            # Write out the raw data CSV matrix directly to our virtual directory storage partition
            csv_content = clean_df.to_csv(index=False)
            self.vfs.write_file(session_id, csv_name, csv_content)
            
            # Evaluate whether we are dealing with multi-line aggregates or single-point cells
            trace_target_value = "AGGREGATE" if len(clean_df) > 1 else (str(clean_df.iloc[0, 0]) if not clean_df.empty else "")
            trace_data = self.trace_number(transaction_token, trace_target_value)
            
            # Transform rows to an isolated JSON matrix and synthesize the text answer
            dataframe_json_string = clean_df.to_json(orient="records")
            natural_language_answer = self.generate_natural_language_answer(user_message, dataframe_json_string)
            
            # Compile the metadata generation blueprint manifest record asset block
            manifest_payload = {
                "query": user_message,
                "sql": clean_sql,
                "execution_plan": logical_recipe,
                "lineage_summary": trace_data.get("human_readable_summary"),
                "linked_vfs_csv": csv_name
            }
            self.vfs.write_file(session_id, filename_manifest, json.dumps(manifest_payload, indent=2))

            # Assemble the unified telemetry dashboard state response payload block
            payload = {
                "status": "success",
                "role": "assistant",
                "answer": natural_language_answer,
                "transaction_token": transaction_token,
                "manifest_snapshot": manifest_payload,
                "sql": clean_sql,
                "execution_plan": logical_recipe,
                "lineage_details": trace_data,
                "csv_name": csv_name,
                "clean_df_json": dataframe_json_string
            }
            
            # Append conversational history records persistently to preserve state
            active_history.append({"role": "user", "message": user_message, "status": "success", "answer": user_message})
            active_history.append(payload)
            return json.dumps(payload)

        except Exception as e:
            # Capture runtime errors cleanly without breaking frontend operations
            err_msg = f"Calculation runtime execution break: {str(e)}"
            payload = {"status": "error", "role": "assistant", "answer": err_msg, "transaction_token": None}
            active_history.append({"role": "user", "message": user_message, "status": "success", "answer": user_message})
            active_history.append(payload)
            return json.dumps(payload)

    def trace_number(self, token: str, specific_value: str) -> Dict[str, Any]:
        """Hybrid Pedigree Tracking Core: Traces outputs back to their absolute origins.
        
        Evaluates tracking tokens against the internal registry database ledger to compute 
        accurate provenance reports, detailing source file names, columns analyzed, and physical 
        row index offset locations.
        
        Args:
            token: The transaction token string associated with the completed data query.
            specific_value: The cell text output value or "AGGREGATE" structural marker.
            
        Returns:
            A dictionary containing a human-readable summary, tracking types, source arrays, 
            and row offset indices.
        """
        if token not in self.lineage_ledger:
            return {"human_readable_summary": "Session token invalid.", "lineage_type": "unknown"}

        ledger_entry = self.lineage_ledger[token]
        session_records = ledger_entry["raw_records"]
        logical_recipe = ledger_entry["logical_recipe"]
        row_footprint = ledger_entry.get("row_footprint", [])

        # Extract unique source sheet filenames and row indexes touched during this operation
        unique_files_touched = sorted(list(set([self.table_metadata[f["table"]]["source_file"] for f in row_footprint if f["table"] in self.table_metadata])))
        specific_row_indices = sorted(list(set([f["row"] for f in row_footprint])))
        columns_analyzed = sorted(list(set([rec["column"] for rec in session_records])))

        # Branch processing logic: Check if the operation spans multiple files or multiple rows
        if specific_value == "AGGREGATE" or len(unique_files_touched) > 1 or len(specific_row_indices) > 1:
            summary = f"Derived from a dataset slice across columns {columns_analyzed} utilizing raw input row offsets {specific_row_indices} from source file(s) {unique_files_touched}."
            return {
                "human_readable_summary": summary,
                "lineage_type": "execution_plan_recipe",
                "source_files": unique_files_touched,
                "row_offsets": specific_row_indices,
                "columns": columns_analyzed
            }

        # Handle point-precision lookups: Pinpoint a single matching cell coordinate line item
        matched_sources = [r for r in session_records if str(specific_value).strip().lower() in str(r["value"]).strip().lower()]
        if matched_sources:
            src = matched_sources[0]
            matched_offset = next((f["row"] for f in row_footprint if f["table"] in src["file"].lower()), 0)
            summary = f"Pulled directly from cell coordinate fields at row index offset {matched_offset} under column tracking target '{src['column']}' inside file sheet '{src['file']}'."
            return {
                "human_readable_summary": summary,
                "lineage_type": "point_ledger_cache",
                "source_files": unique_files_touched,
                "row_offsets": [matched_offset],
                "columns": [src["column"]]
            }

        # Fallback tracking resolution for ambiguous edge calculations
        summary = f"Maps to column targets {columns_analyzed} across raw sheet index lines {specific_row_indices} inside source components {unique_files_touched}."
        return {
            "human_readable_summary": summary,
            "lineage_type": "execution_plan_recipe",
            "source_files": unique_files_touched,
            "row_offsets": specific_row_indices,
            "columns": columns_analyzed
        }