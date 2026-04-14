"""
FitSense AI Dashboard - NoSQL Explorer Page
==========================================
Interactive MongoDB aggregation query builder and executor with JSON output.
"""

import streamlit as st
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import utilities
from utils.mongodb_client import execute_query, ensure_mongo_connection
from utils.nosql_console import QUERIES, QUERY_CATEGORIES, QUERY_METADATA
from utils.sidebar import render_sidebar

# Page configuration
st.set_page_config(
    page_title="NoSQL Explorer - FitSense AI Dashboard",
    page_icon="assets/logo.svg",
    layout="wide",
)

# Load CSS
css_path = project_root / "assets" / "style.css"
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def highlight_json(json_str: str) -> str:
    """Simple JSON syntax highlighting."""
    if not isinstance(json_str, str):
        json_str = str(json_str)

    # Basic JSON highlighting colors
    json_str = json_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Highlight keys
    import re

    json_str = re.sub(
        r'"([^"]+)"\s*:', r'<span style="color: #A855F7;">"\1"</span>:', json_str
    )
    # Highlight string values
    json_str = re.sub(
        r':\s*"([^"]*)"', r': <span style="color: #10B981;">"\1"</span>', json_str
    )
    # Highlight numbers
    json_str = re.sub(
        r":\s*(\d+\.?\d*)", r': <span style="color: #F59E0B;">\1</span>', json_str
    )
    # Highlight operators like $match, $group, etc.
    json_str = re.sub(
        r'"\$([^"]+)"', r'"<span style="color: #3B82F6;">$\1</span>"', json_str
    )

    return json_str


def format_json(json_str: str) -> str:
    """Format JSON with proper indentation."""
    try:
        parsed = json.loads(json_str)
        return json.dumps(parsed, indent=2, default=str)
    except:
        return json_str


def get_mongodb_shell_command(collection: str, pipeline: list) -> str:
    """
    Generate the equivalent MongoDB shell command for display.

    Args:
        collection: Collection name
        pipeline: Aggregation pipeline

    Returns:
        MongoDB shell command string
    """
    if not pipeline:
        return f"db.{collection}.find({{}}).limit(50)"

    # Check if it's a simple find with filters
    if len(pipeline) == 1:
        first_stage = pipeline[0]
        if "$match" in first_stage:
            match_filter = json.dumps(first_stage["$match"], indent=0, default=str)
            return f"db.{collection}.find({match_filter}).limit(50)"
        if "$sort" in first_stage:
            return f'db.{collection}.find({{}}).sort({json.dumps(first_stage["$sort"], indent=0)})'
        if "$limit" in first_stage:
            return f'db.{collection}.find({{}}).limit({first_stage["$limit"]})'

    # For aggregation pipelines, show the pipeline
    pipeline_str = json.dumps(pipeline, indent=0, default=str)
    return f"db.{collection}.aggregate({pipeline_str})"


def get_query_type(pipeline: list) -> str:
    """Determine query type from MongoDB pipeline structure."""
    if not pipeline:
        return "Unknown"

    pipeline_str = str(pipeline).lower()

    if "$lookup" in pipeline_str:
        return "Lookup (JOIN)"
    if "$unionwith" in pipeline_str:
        return "Set Operations"
    if "$group" in pipeline_str:
        if "$match" in pipeline_str:
            return "Aggregation + Filter"
        return "Aggregation"
    if "$match" in pipeline_str:
        return "Filter"
    if "$sort" in pipeline_str or "$limit" in pipeline_str:
        return "Basic Find"
    return "Pipeline"


def main():
    """Main NoSQL Explorer page."""

    # Render sidebar
    render_sidebar()

    st.markdown(
        """
    <div style="padding: 10px 0 30px 0;">
        <h1 style="color: #F1F5F9; margin: 0; font-size: 2.0rem;">📦 NoSQL Explorer</h1>
        <p style="color: #94A3B8; margin: 10px 0 0 0;">
            Execute MongoDB aggregation queries and explore your NoSQL data
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Ensure MongoDB connection is established
    ensure_mongo_connection()

    if not st.session_state.get("mongo_connected", False):
        st.warning(
            "Please ensure MongoDB is connected. Check the main page for setup instructions."
        )
        return

    # Initialize session state
    if "nosql_explorer_history" not in st.session_state:
        st.session_state.nosql_explorer_history = []
    if "current_pipeline" not in st.session_state:
        st.session_state.current_pipeline = ""

    # Main layout - split panel
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### Query Editor")

        # Predefined queries dropdown
        st.markdown("**Load Predefined Query:**")

        # Build query options from QUERY_CATEGORIES
        query_options = [""]  # Empty option for custom query
        query_map = {}

        for category, query_ids in QUERY_CATEGORIES.items():
            for qid in query_ids:
                query_data = QUERIES.get(qid)
                metadata = QUERY_METADATA.get(qid)
                if query_data and metadata:
                    option = f"[{category}] {metadata.get('name', qid)}"
                    query_options.append(option)
                    query_map[option] = {
                        "query": query_data,
                        "name": metadata.get("name", qid),
                        "type": metadata.get("type", "Unknown"),
                        "page": metadata.get("page", "Unknown"),
                        "id": qid,
                    }

        selected_query = st.selectbox(
            "Select a predefined query", query_options, label_visibility="collapsed"
        )

        if selected_query:
            query_data = query_map.get(selected_query, {})
            pipeline = query_data.get("query", {}).get("pipeline", [])
            st.session_state.current_pipeline = json.dumps(
                pipeline, indent=2, default=str
            )
            st.session_state.current_collection = query_data.get("query", {}).get(
                "collection", ""
            )

            # Show query metadata
            if query_data:
                with st.expander("📋 Query Info", expanded=False):
                    st.markdown(f"**Name:** {query_data.get('name', 'N/A')}")
                    st.markdown(f"**Type:** {query_data.get('type', 'N/A')}")
                    st.markdown(f"**Page:** {query_data.get('page', 'N/A')}")
                    st.markdown(
                        f"**Collection:** {st.session_state.current_collection}"
                    )

        # Collection name input
        collection_name = st.text_input(
            "Collection Name",
            value=st.session_state.get("current_collection", ""),
            placeholder="e.g., users, workouts, exercises",
            help="Enter the MongoDB collection name",
        )

        # Pipeline text area
        pipeline_input = st.text_area(
            "Aggregation Pipeline (JSON)",
            value=st.session_state.current_pipeline,
            height=200,
            placeholder='[\n    {"$match": {"field": "value"}},\n    {"$limit": 50}\n]',
            label_visibility="collapsed",
        )

        # Update session state
        st.session_state.current_pipeline = pipeline_input
        st.session_state.current_collection = collection_name

        # Buttons
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

        with col_btn1:
            run_button = st.button("▶️ Run Query", type="primary", width="stretch")

        with col_btn2:
            format_button = st.button("✨ Format JSON", width="stretch")

        with col_btn3:
            clear_button = st.button("🗑️ Clear", width="stretch")

        # Format JSON
        if format_button and pipeline_input:
            formatted = format_json(pipeline_input)
            st.session_state.current_pipeline = formatted
            st.rerun()

        # Clear
        if clear_button:
            st.session_state.current_pipeline = ""
            st.session_state.current_collection = ""
            st.rerun()

        # Execute query
        result_container = st.container()

        if run_button and pipeline_input and collection_name:
            # Parse the pipeline
            try:
                pipeline = json.loads(pipeline_input)
                if not isinstance(pipeline, list):
                    pipeline = [pipeline]
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {str(e)}")
                return

            query_data = {"collection": collection_name, "pipeline": pipeline}

            try:
                df, exec_time = execute_query(query_data)

                if not df.empty:
                    results = df.to_dict(orient="records")

                    st.session_state.nosql_explorer_history.append(
                        {
                            "collection": collection_name,
                            "pipeline": pipeline,
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "rows": len(results),
                        }
                    )

                    st.success(
                        f"✅ Query returned {len(results)} documents in {exec_time:.3f}s"
                    )

                    # JSON Output code block
                    # Convert results to JSON
                    formatted_json = json.dumps(results, indent=2, default=str)

                    # MongoDB Shell Command (equivalent)
                    mongo_cmd = get_mongodb_shell_command(collection_name, pipeline)
                    st.markdown("#### MongoDB Query")
                    st.code(mongo_cmd, language="javascript")

                    # Download button for JSON
                    st.download_button(
                        label="📥 Download JSON",
                        data=formatted_json,
                        file_name="query_results.json",
                        mime="application/json",
                        width="stretch",
                    )

                    # Result
                    st.markdown("#### Result")
                    st.code(formatted_json, language="json")
                    # Aggregation Pipeline display with highlighting
                    st.markdown("#### Aggregation Pipeline")
                    st.code(pipeline_input, language="json")

                    # Query type badge
                    query_type = get_query_type(pipeline)
                    st.markdown(
                        f"""
                    <span style="background: rgba(168, 85, 247, 0.2); color: #A855F7; padding: 4px 12px; border-radius: 20px; font-size: 12px;">
                        {query_type}
                    </span>
                    """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.info("Query returned no results.")

            except Exception as e:
                st.error(f"❌ Query Error: {str(e)}")
                st.info("Please check that the MongoDB collections contain data.")

        elif run_button and not (pipeline_input and collection_name):
            st.warning("Please enter a collection name and aggregation pipeline first.")

    # Right panel - Query History
    with col_right:
        st.markdown("### 📜 Query History")

        if st.session_state.nosql_explorer_history:
            for i, item in enumerate(
                reversed(st.session_state.nosql_explorer_history[-10:])
            ):
                with st.expander(
                    f"📦 {item['collection']} ({item['rows']} docs)", expanded=False
                ):
                    pipeline_str = json.dumps(item["pipeline"], indent=2, default=str)
                    st.code(pipeline_str, language="json")
        else:
            st.info("No queries executed yet.")

        st.divider()

        # MongoDB Reference
        st.markdown("### 📚 MongoDB Reference")

        st.markdown(
            """
        <div style="background: rgba(30, 41, 59, 0.5); border-radius: 8px; padding: 15px; margin-top: 15px;">
            <h4 style="color: #F1F5F9; margin-top: 0;">Read-Only Access</h4>
            <ul style="color: #94A3B8; line-height: 1.8;">
                <li><code style="color: #10B981;">find()</code> - Allowed</li>
                <li><code style="color: #10B981;">aggregate()</code> - Allowed</li>
                <li><span style="color: #EF4444; text-decoration: line-through;">insert</span> - Blocked</li>
                <li><span style="color: #EF4444; text-decoration: line-through;">update</span> - Blocked</li>
                <li><span style="color: #EF4444; text-decoration: line-through;">delete</span> - Blocked</li>
            </ul>
            <p style="color: #94A3B8; margin-top: 10px; font-size: 0.85rem;">
                This dashboard is configured for read-only access to protect your data.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div style="background: rgba(30, 41, 59, 0.5); border-radius: 8px; padding: 15px; margin-top: 15px;">
            <h4 style="color: #F1F5F9; margin-top: 0;">MongoDB Collections</h4>
            <ul style="color: #94A3B8; line-height: 1.8;">
                <li><code style="color: #10B981;">users</code></li>
                <li><code style="color: #10B981;">user_profiles</code></li>
                <li><code style="color: #10B981;">workouts</code></li>
                <li><code style="color: #10B981;">exercises</code></li>
                <li><code style="color: #10B981;">goals</code></li>
                <li><code style="color: #10B981;">sleep_logs</code></li>
                <li><code style="color: #10B981;">calorie_logs</code></li>
                <li><code style="color: #10B981;">weight_logs</code></li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div style="background: rgba(30, 41, 59, 0.5); border-radius: 8px; padding: 15px; margin-top: 15px;">
            <h4 style="color: #F1F5F9; margin-top: 0;">Aggregation Operators</h4>
            <ul style="color: #94A3B8; line-height: 1.8; font-size: 0.85rem;">
                <li><code style="color: #3B82F6;">$match</code> - Filter documents</li>
                <li><code style="color: #3B82F6;">$group</code> - Group documents</li>
                <li><code style="color: #3B82F6;">$project</code> - Shape documents</li>
                <li><code style="color: #3B82F6;">$sort</code> - Sort documents</li>
                <li><code style="color: #3B82F6;">$limit</code> - Limit results</li>
                <li><code style="color: #3B82F6;">$lookup</code> - Join collections</li>
                <li><code style="color: #3B82F6;">$unwind</code> - Deconstruct arrays</li>
                <li><code style="color: #3B82F6;">$sum/$avg</code> - Accumulator ops</li>
            </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
