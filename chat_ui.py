"""
Pistology-WAIS v2.1 - Comprehensive Chat UI

Features:
- API key management for each agent
- Document upload with Docling
- Multi-agent selection
- Pareto and Six Sigma visualizations
- Real-time statistics
- Context-aware conversations
"""

import streamlit as st
from agents.agent_orchestrator import AgentOrchestrator
from agents.base_agent import AgentConfig
from pathlib import Path
import os
import logging
from datetime import datetime
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Pistology-WAIS v2.1",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .agent-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize all session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None

    if 'api_keys' not in st.session_state:
        st.session_state.api_keys = {
            "master": os.getenv("OPENAI_API_KEY", ""),
            "supervisor": "",
            "inventory": "",
            "operations": "",
            "math": "",
            "quality": ""
        }

    if 'processed_documents' not in st.session_state:
        st.session_state.processed_documents = []

    if 'agent_models' not in st.session_state:
        st.session_state.agent_models = {
            "supervisor": "gpt-4o",
            "inventory": "gpt-4o",
            "operations": "gpt-4o",
            "math": "gpt-4o",
            "quality": "gpt-4o"
        }

    if 'use_master_key' not in st.session_state:
        st.session_state.use_master_key = True


def render_api_key_config():
    """Render API key configuration sidebar"""
    st.sidebar.header("🔑 API Configuration")

    # Master key option
    use_master = st.sidebar.checkbox(
        "Use single API key for all agents",
        value=st.session_state.use_master_key,
        help="Use one API key for all agents, or configure separately"
    )
    st.session_state.use_master_key = use_master

    if use_master:
        master_key = st.sidebar.text_input(
            "OpenAI API Key",
            value=st.session_state.api_keys["master"],
            type="password",
            help="Your OpenAI API key for all agents"
        )
        st.session_state.api_keys["master"] = master_key

        if master_key:
            # Set all agent keys to master key
            for agent in ["supervisor", "inventory", "operations", "math", "quality"]:
                st.session_state.api_keys[agent] = master_key
    else:
        st.sidebar.subheader("Agent-Specific Keys")
        with st.sidebar.expander("Configure Each Agent", expanded=False):
            for agent in ["supervisor", "inventory", "operations", "math", "quality"]:
                key = st.text_input(
                    f"{agent.title()} Agent",
                    value=st.session_state.api_keys.get(agent, ""),
                    type="password",
                    key=f"api_key_{agent}"
                )
                st.session_state.api_keys[agent] = key

    # Model selection
    with st.sidebar.expander("⚙️ Model Configuration", expanded=False):
        st.write("Select models for each agent:")
        models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]

        for agent in ["supervisor", "inventory", "operations", "math", "quality"]:
            model = st.selectbox(
                f"{agent.title()}",
                models,
                index=models.index(st.session_state.agent_models.get(agent, "gpt-4o")),
                key=f"model_{agent}"
            )
            st.session_state.agent_models[agent] = model

    # Initialize button
    if st.sidebar.button("🚀 Initialize System", type="primary", use_container_width=True):
        initialize_orchestrator()


def initialize_orchestrator():
    """Initialize the agent orchestrator with configured API keys"""
    try:
        # Check if we have at least the master key
        if st.session_state.use_master_key:
            if not st.session_state.api_keys["master"]:
                st.sidebar.error("Please provide an OpenAI API key")
                return
        else:
            # Check if all agent keys are provided
            missing = [k for k, v in st.session_state.api_keys.items() if k != "master" and not v]
            if missing:
                st.sidebar.error(f"Missing API keys for: {', '.join(missing)}")
                return

        with st.sidebar:
            with st.spinner("Initializing AI agents..."):
                # Temporarily set environment variable for config module
                os.environ["OPENAI_API_KEY"] = st.session_state.api_keys["master"] or st.session_state.api_keys["supervisor"]

                # Initialize orchestrator
                st.session_state.orchestrator = AgentOrchestrator()

                st.success("✅ System initialized successfully!")
                st.balloons()

    except Exception as e:
        st.sidebar.error(f"Initialization failed: {str(e)}")
        logger.error(f"Orchestrator initialization error: {str(e)}")


def render_document_upload():
    """Render document upload section"""
    st.sidebar.header("📄 Document Upload")

    uploaded_files = st.sidebar.file_uploader(
        "Upload warehouse documents",
        type=["pdf", "docx", "xlsx", "pptx", "txt", "md", "csv", "json"],
        accept_multiple_files=True,
        help="Supported: PDF, Word, Excel, PowerPoint, Text, Markdown, CSV, JSON"
    )

    if uploaded_files and st.sidebar.button("📤 Process Documents", use_container_width=True):
        process_documents(uploaded_files)


def process_documents(files):
    """Process uploaded documents using Docling"""
    if not st.session_state.orchestrator:
        st.sidebar.warning("Please initialize the system first")
        return

    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    file_paths = []

    try:
        with st.sidebar:
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Save files
            for i, file in enumerate(files):
                temp_path = temp_dir / file.name
                with open(temp_path, "wb") as f:
                    f.write(file.getvalue())
                file_paths.append(str(temp_path))
                progress_bar.progress((i + 1) / (len(files) * 2))
                status_text.text(f"Saving {file.name}...")

            # Process documents
            status_text.text("Processing with Docling...")
            result = st.session_state.orchestrator.process_documents(file_paths)
            progress_bar.progress(1.0)

            # Show results
            if result["successful"] > 0:
                st.success(f"✅ Processed {result['successful']}/{result['processed']} documents")

                # Show document details
                with st.expander("📋 Processing Details"):
                    for doc in result["documents"]:
                        if doc["success"]:
                            st.write(f"✅ {doc['filename']} ({doc['processing_time']:.2f}s)")
                        else:
                            st.write(f"❌ {doc['filename']}: {doc['error']}")

                st.session_state.processed_documents.extend(result["documents"])
            else:
                st.error("❌ No documents processed successfully")

            status_text.empty()
            progress_bar.empty()

    except Exception as e:
        st.sidebar.error(f"Document processing error: {str(e)}")
        logger.error(f"Document processing error: {str(e)}")
    finally:
        # Cleanup
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except:
                pass


def render_system_status():
    """Render system status in sidebar"""
    if not st.session_state.orchestrator:
        return

    st.sidebar.header("📊 System Status")

    try:
        status = st.session_state.orchestrator.get_system_status()

        # Document stats
        doc_stats = st.session_state.orchestrator.get_document_statistics()
        if doc_stats["total_processed"] > 0:
            col1, col2 = st.sidebar.columns(2)
            col1.metric("Documents", doc_stats["documents_in_context"])
            col2.metric("Processed", doc_stats["total_processed"])

        # Agent status
        with st.sidebar.expander("🤖 Agent Status"):
            agents = status.get("agents", {})
            for agent_name, agent_status in agents.items():
                st.text(f"{agent_name}: {agent_status}")

        # Knowledge base
        kb_size = status.get("knowledge_base_size", {})
        if sum(kb_size.values()) > 0:
            with st.sidebar.expander("💾 Knowledge Base"):
                for key, value in kb_size.items():
                    st.text(f"{key}: {value}")

    except Exception as e:
        logger.error(f"Status display error: {str(e)}")


def render_chat_interface():
    """Render main chat interface"""
    st.markdown('<div class="main-header">🏭 Pistology-WAIS v2.1</div>', unsafe_allow_html=True)
    st.markdown("**Warehouse AI System** - OpenAI-Powered Multi-Agent Intelligence with Lean Six Sigma")

    if not st.session_state.orchestrator:
        st.info("👈 Please configure API keys and initialize the system in the sidebar")

        # Show feature cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            ### 📦 Inventory Management
            - EOQ Calculation
            - Reorder Points
            - Safety Stock
            - **ABC Classification**
            - **Pareto Analysis**
            - Demand Forecasting
            """)

        with col2:
            st.markdown("""
            ### ⚙️ Operations
            - Throughput Analysis
            - Cycle Time
            - Labor Productivity
            - Equipment Utilization
            - Workflow Optimization
            """)

        with col3:
            st.markdown("""
            ### 🔧 Quality (Six Sigma)
            - **DMAIC Methodology**
            - **Process Capability (Cp/Cpk)**
            - **DPMO & Sigma Levels**
            - **Pareto Analysis**
            - **ABC Analysis**
            - Process Variation
            """)

        st.markdown("---")
        st.markdown("""
        ### 📄 Document Intelligence
        - **IBM Docling** - Advanced document parsing
        - **OCR** - Scan text from images
        - **Table Extraction** - Automatic table detection
        - **Context Integration** - Documents inform agent responses
        """)

        return

    # Chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show visualizations if present
            if message["role"] == "assistant" and "visualization" in message:
                render_visualization(message["visualization"])

    # Chat input
    if prompt := st.chat_input("Ask about inventory, operations, quality, or upload documents for analysis..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Check if documents are available
                    if len(st.session_state.processed_documents) > 0:
                        response = st.session_state.orchestrator.process_query_with_documents(
                            prompt,
                            include_document_context=True
                        )
                    else:
                        response = st.session_state.orchestrator.process_query(prompt)

                    content = response.content

                    # Display response
                    st.markdown(content)

                    # Show function calls if any
                    if response.function_calls:
                        with st.expander("🔧 Function Calls"):
                            for fc in response.function_calls:
                                st.json(fc)

                    # Check for Pareto or Six Sigma results and visualize
                    visualization = extract_visualization_data(response)

                    # Add to messages
                    msg = {"role": "assistant", "content": content}
                    if visualization:
                        msg["visualization"] = visualization
                        render_visualization(visualization)

                    st.session_state.messages.append(msg)

                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})


def extract_visualization_data(response):
    """Extract data for visualization from response"""
    try:
        if response.function_calls:
            for fc in response.function_calls:
                func_name = fc.get("function")
                result = fc.get("result", {})

                # Pareto analysis
                if "pareto" in func_name.lower():
                    return {"type": "pareto", "data": result}

                # ABC analysis
                elif "abc" in func_name.lower():
                    return {"type": "abc", "data": result}

                # Process capability
                elif "capability" in func_name.lower():
                    return {"type": "capability", "data": result}

                # Process variation
                elif "variation" in func_name.lower():
                    return {"type": "variation", "data": result}
    except Exception as e:
        logger.error(f"Visualization extraction error: {str(e)}")

    return None


def render_visualization(viz_data):
    """Render visualizations for analysis results"""
    try:
        viz_type = viz_data.get("type")
        data = viz_data.get("data", {})

        if viz_type == "pareto":
            render_pareto_chart(data)
        elif viz_type == "abc":
            render_abc_chart(data)
        elif viz_type == "capability":
            render_capability_chart(data)
        elif viz_type == "variation":
            render_variation_chart(data)

    except Exception as e:
        logger.error(f"Visualization rendering error: {str(e)}")


def render_pareto_chart(data):
    """Render Pareto chart (80/20 rule)"""
    try:
        analysis = data.get("analysis", [])
        if not analysis:
            return

        df = pd.DataFrame(analysis)

        fig = go.Figure()

        # Bar chart for values
        fig.add_trace(go.Bar(
            x=[item.get("name", item.get("sku", f"Item {i}")) for i, item in enumerate(analysis)],
            y=[item.get("value", item.get("metric_value", 0)) for item in analysis],
            name="Value",
            marker_color='lightblue'
        ))

        # Line chart for cumulative %
        fig.add_trace(go.Scatter(
            x=[item.get("name", item.get("sku", f"Item {i}")) for i, item in enumerate(analysis)],
            y=[item.get("cumulative_percentage", 0) for item in analysis],
            name="Cumulative %",
            yaxis="y2",
            line=dict(color='red', width=2),
            marker=dict(size=8)
        ))

        # Add 80% reference line
        fig.add_hline(y=80, line_dash="dash", line_color="orange", yref="y2",
                     annotation_text="80% Line", annotation_position="right")

        fig.update_layout(
            title="Pareto Analysis (80/20 Rule)",
            xaxis_title="Items",
            yaxis_title="Value",
            yaxis2=dict(
                title="Cumulative %",
                overlaying="y",
                side="right",
                range=[0, 100]
            ),
            hovermode="x unified",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # Show summary
        summary = data.get("summary", {})
        if summary:
            col1, col2, col3 = st.columns(3)
            col1.metric("Vital Few Count", summary.get("vital_few_count", 0))
            col2.metric("Vital Few %", f"{summary.get('vital_few_percentage', 0)}%")
            col3.metric("Value Contribution", f"{summary.get('vital_few_contribution', 0)}%")

    except Exception as e:
        logger.error(f"Pareto chart error: {str(e)}")


def render_abc_chart(data):
    """Render ABC classification chart"""
    try:
        classification = data.get("classification", [])
        if not classification:
            return

        df = pd.DataFrame(classification)

        # Pie chart for ABC distribution
        summary = data.get("summary", {})
        categories = ["A", "B", "C"]
        counts = [summary.get(f"{cat}_items", {}).get("count", 0) for cat in categories]
        values = [summary.get(f"{cat}_items", {}).get("value_contribution", 0) for cat in categories]

        fig = go.Figure(data=[go.Pie(
            labels=categories,
            values=counts,
            hole=0.3,
            marker_colors=['#ff6b6b', '#ffd93d', '#6bcf7f']
        )])

        fig.update_layout(
            title="ABC Classification Distribution",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Show details
        col1, col2, col3 = st.columns(3)
        for idx, cat in enumerate(categories):
            cat_data = summary.get(f"{cat}_items", {})
            with [col1, col2, col3][idx]:
                st.markdown(f"### Category {cat}")
                st.metric("Items", cat_data.get("count", 0))
                st.metric("% of Items", f"{cat_data.get('percentage_of_items', 0)}%")
                st.metric("Value %", f"{cat_data.get('value_contribution', 0)}%")
                st.caption(cat_data.get("management", ""))

    except Exception as e:
        logger.error(f"ABC chart error: {str(e)}")


def render_capability_chart(data):
    """Render process capability chart"""
    try:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Cp (Potential)", data.get("cp", 0))
        col2.metric("Cpk (Actual)", data.get("cpk", 0))
        col3.metric("Sigma Level", f"{data.get('sigma_level', 0):.2f}σ")
        col4.metric("Est. DPMO", data.get("estimated_dpmo", 0))

        # Interpretation
        interpretation = data.get("interpretation", "")
        if "Excellent" in interpretation:
            st.success(f"✅ {interpretation}")
        elif "Good" in interpretation:
            st.info(f"ℹ️ {interpretation}")
        elif "Marginal" in interpretation:
            st.warning(f"⚠️ {interpretation}")
        else:
            st.error(f"❌ {interpretation}")

        st.write(f"**Recommendation:** {data.get('recommendation', '')}")

    except Exception as e:
        logger.error(f"Capability chart error: {str(e)}")


def render_variation_chart(data):
    """Render process variation chart"""
    try:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Mean", f"{data.get('mean', 0):.4f}")
        col2.metric("Std Dev", f"{data.get('std_dev', 0):.4f}")
        col3.metric("CV", f"{data.get('coefficient_of_variation', 0):.2f}%")
        col4.metric("Outliers", data.get('outliers', 0))

        # Stability status
        stability = data.get("stability", "")
        if "Stable" in stability:
            st.success(f"✅ {stability}")
        else:
            st.warning(f"⚠️ {stability}")

        # Control limits
        limits = data.get("control_limits", {})
        if limits:
            col1, col2 = st.columns(2)
            col1.metric("UCL", f"{limits.get('ucl', 0):.4f}")
            col2.metric("LCL", f"{limits.get('lcl', 0):.4f}")

    except Exception as e:
        logger.error(f"Variation chart error: {str(e)}")


def render_statistics_tab():
    """Render statistics and analytics tab"""
    if not st.session_state.orchestrator:
        st.info("Initialize the system to view statistics")
        return

    st.subheader("📊 System Analytics")

    # Get statistics
    status = st.session_state.orchestrator.get_system_status()
    doc_stats = st.session_state.orchestrator.get_document_statistics()

    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)

    kb_size = status.get("knowledge_base_size", {})
    col1.metric("Conversations", kb_size.get("conversations", 0))
    col2.metric("Documents", doc_stats.get("documents_in_context", 0))
    col3.metric("Insights", kb_size.get("insights", 0))
    col4.metric("Decisions", kb_size.get("decisions", 0))

    # Document statistics
    if doc_stats.get("total_processed", 0) > 0:
        st.subheader("📄 Document Processing")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Processed", doc_stats["total_processed"])
        col2.metric("Successful", doc_stats["successful"])
        col3.metric("Average Time", f"{doc_stats.get('average_processing_time', 0):.2f}s")

        # File types
        if doc_stats.get("file_types"):
            st.write("**File Types:**", ", ".join(doc_stats["file_types"]))

    # Agent performance
    st.subheader("🤖 Agent Performance")
    agents = status.get("agents", {})

    if agents:
        agent_df = pd.DataFrame([
            {"Agent": name, "Status": "Ready" if "Ready" in stat else "Active"}
            for name, stat in agents.items()
        ])
        st.dataframe(agent_df, use_container_width=True)


def main():
    """Main application entry point"""
    initialize_session_state()

    # Sidebar
    render_api_key_config()
    render_document_upload()
    render_system_status()

    # Add clear button
    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    # Main interface tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Statistics", "ℹ️ About"])

    with tab1:
        render_chat_interface()

    with tab2:
        render_statistics_tab()

    with tab3:
        st.markdown("""
        ## 🏭 Pistology-WAIS v2.1

        **Warehouse AI Intelligence System** powered by OpenAI

        ### Features

        #### 🤖 Multi-Agent System
        - **Supervisor Agent**: Query routing and coordination
        - **Inventory Agent**: EOQ, ROP, ABC/Pareto, forecasting
        - **Operations Agent**: Throughput, cycle time, productivity
        - **Math Agent**: Calculations, statistics, SymPy
        - **Quality Agent**: Six Sigma, DMAIC, process capability

        #### 📄 Document Intelligence
        - **IBM Docling**: Advanced document parsing
        - **OCR**: Text extraction from images
        - **Table Extraction**: Automatic table detection
        - **Context Integration**: Documents inform responses

        #### 📈 Lean Six Sigma
        - **DMAIC**: Define, Measure, Analyze, Improve, Control
        - **Process Capability**: Cp/Cpk calculations
        - **DPMO**: Defects Per Million Opportunities
        - **Sigma Levels**: 1σ to 6σ quality measurement
        - **Process Variation**: Control charts, stability

        #### 🎯 Pareto Analysis
        - **80/20 Rule**: Identify vital few from trivial many
        - **ABC Classification**: Inventory prioritization
        - **Resource Optimization**: Focus on high-impact items

        ### Usage

        1. **Configure API Keys**: Add your OpenAI API key(s)
        2. **Initialize System**: Click "Initialize System"
        3. **Upload Documents** (optional): Add warehouse reports
        4. **Chat**: Ask questions or request analysis

        ### Examples

        - "Calculate EOQ for 10,000 units annual demand"
        - "Perform ABC classification on my inventory"
        - "Analyze process capability with USL=10, LSL=0"
        - "What defects are identified in the uploaded report?"
        - "Do Pareto analysis to find top causes"

        ### Version
        - **v2.1.0** - Docling, Six Sigma, Pareto
        - **v2.0.0** - OpenAI SDK migration
        - **v1.0.0** - Initial release

        ---

        **Built with:** OpenAI GPT-4o, Streamlit, Plotly, Pandas

        **Documentation:** See DOCLING_LEAN_SIX_SIGMA_FEATURES.md
        """)


if __name__ == "__main__":
    main()
