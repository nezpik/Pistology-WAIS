"""
Pistology-WAIS v2.1 - Comprehensive Chat UI

Features:
- Simple API key management
- Document upload with Docling
- Multi-agent system with OpenAI
- Pareto and Six Sigma visualizations
- Real-time statistics
- Context-aware conversations
"""

import streamlit as st
from agents.agent_orchestrator import AgentOrchestrator
from pathlib import Path
import os
import logging
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional

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
        background-color: #f8f9fa;
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
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize all session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = None

    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.getenv("OPENAI_API_KEY", "")

    if 'processed_documents' not in st.session_state:
        st.session_state.processed_documents = []

    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False

    if 'agent_models' not in st.session_state:
        st.session_state.agent_models = {
            "supervisor": "gpt-4o",
            "inventory": "gpt-4o",
            "operations": "gpt-4o",
            "math": "gpt-4o",
            "quality": "gpt-4o"
        }


def render_sidebar():
    """Render complete sidebar with all controls"""
    st.sidebar.markdown("## 🏭 Pistology-WAIS v2.1")
    st.sidebar.markdown("---")

    # API Key Configuration
    st.sidebar.header("🔑 Configuration")

    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        value=st.session_state.api_key,
        type="password",
        help="Your OpenAI API key for all agents",
        placeholder="sk-..."
    )
    st.session_state.api_key = api_key

    # Model selection
    with st.sidebar.expander("⚙️ Advanced Settings", expanded=False):
        st.write("**Model Configuration**")
        models = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]

        for agent in ["supervisor", "inventory", "operations", "math", "quality"]:
            model = st.selectbox(
                f"{agent.title()} Agent",
                models,
                index=models.index(st.session_state.agent_models.get(agent, "gpt-4o")),
                key=f"model_{agent}"
            )
            st.session_state.agent_models[agent] = model

    # Initialize/Reset buttons
    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("🚀 Initialize", type="primary", disabled=st.session_state.system_initialized):
            initialize_system()

    with col2:
        if st.button("🔄 Reset", disabled=not st.session_state.system_initialized):
            reset_system()

    st.sidebar.markdown("---")

    # Document Upload
    if st.session_state.system_initialized:
        render_document_upload()
        st.sidebar.markdown("---")
        render_system_status()

    # Help section
    with st.sidebar.expander("❓ Help"):
        st.markdown("""
        **Getting Started:**
        1. Enter your OpenAI API key
        2. Click "Initialize"
        3. Upload documents (optional)
        4. Start chatting!

        **Examples:**
        - "Calculate EOQ for 10,000 units"
        - "Perform ABC classification"
        - "Analyze process capability"
        - "Do Pareto analysis"
        """)


def initialize_system():
    """Initialize the agent orchestrator system"""
    if not st.session_state.api_key or not st.session_state.api_key.startswith("sk-"):
        st.sidebar.error("⚠️ Please provide a valid OpenAI API key (starts with 'sk-')")
        return

    with st.sidebar:
        with st.spinner("🔧 Initializing AI agents..."):
            try:
                # Set environment variable for config module
                os.environ["OPENAI_API_KEY"] = st.session_state.api_key

                # Initialize orchestrator
                st.session_state.orchestrator = AgentOrchestrator()
                st.session_state.system_initialized = True

                st.success("✅ System initialized successfully!")
                st.balloons()
                logger.info("System initialized successfully")

            except Exception as e:
                st.error(f"❌ Initialization failed: {str(e)}")
                logger.error(f"Orchestrator initialization error: {str(e)}", exc_info=True)
                st.session_state.system_initialized = False


def reset_system():
    """Reset the entire system"""
    st.session_state.orchestrator = None
    st.session_state.system_initialized = False
    st.session_state.messages = []
    st.session_state.processed_documents = []

    if st.session_state.orchestrator:
        try:
            st.session_state.orchestrator.document_processor.clear_context()
        except:
            pass

    st.sidebar.success("✅ System reset successfully")
    st.rerun()


def render_document_upload():
    """Render document upload section"""
    st.sidebar.header("📄 Document Upload")

    uploaded_files = st.sidebar.file_uploader(
        "Upload warehouse documents",
        type=["pdf", "docx", "xlsx", "pptx", "txt", "md", "csv", "json"],
        accept_multiple_files=True,
        help="Supported: PDF, Word, Excel, PowerPoint, Text files",
        key="doc_uploader"
    )

    if uploaded_files and st.sidebar.button("📤 Process Documents"):
        process_documents(uploaded_files)


def process_documents(files):
    """Process uploaded documents using Docling"""
    if not st.session_state.orchestrator:
        st.sidebar.warning("⚠️ Please initialize the system first")
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
            status_text.text("🔍 Processing with Docling...")
            result = st.session_state.orchestrator.process_documents(file_paths)
            progress_bar.progress(1.0)

            # Show results
            if result["successful"] > 0:
                st.success(f"✅ Processed {result['successful']}/{result['processed']} documents")

                # Show document details
                with st.expander("📋 Processing Details", expanded=False):
                    for doc in result["documents"]:
                        if doc["success"]:
                            st.write(f"✅ {doc['filename']} ({doc['processing_time']:.2f}s)")
                        else:
                            st.write(f"❌ {doc['filename']}: {doc.get('error', 'Unknown error')}")

                st.session_state.processed_documents.extend([d for d in result["documents"] if d["success"]])

                # Add success message to chat
                doc_names = [d["filename"] for d in result["documents"] if d["success"]]
                success_msg = f"📄 Successfully processed {len(doc_names)} document(s): {', '.join(doc_names)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": success_msg
                })
            else:
                st.error("❌ No documents processed successfully")

            status_text.empty()
            progress_bar.empty()

    except Exception as e:
        st.sidebar.error(f"❌ Document processing error: {str(e)}")
        logger.error(f"Document processing error: {str(e)}", exc_info=True)
    finally:
        # Cleanup temporary files
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                logger.warning(f"Failed to clean up {path}: {e}")


def render_system_status():
    """Render system status in sidebar"""
    st.sidebar.header("📊 System Status")

    try:
        if st.session_state.orchestrator:
            status = st.session_state.orchestrator.get_system_status()

            # Document stats
            doc_stats = st.session_state.orchestrator.get_document_statistics()
            if doc_stats["total_processed"] > 0:
                col1, col2 = st.sidebar.columns(2)
                col1.metric("📄 Docs", doc_stats["documents_in_context"])
                col2.metric("✅ Processed", doc_stats["total_processed"])

            # Agent status
            with st.sidebar.expander("🤖 Agent Status", expanded=False):
                agents = ["Supervisor", "Inventory", "Operations", "Math", "Quality"]
                for agent in agents:
                    st.text(f"✓ {agent} Agent")

            # Knowledge base
            kb_size = status.get("knowledge_base_size", {})
            if sum(kb_size.values()) > 0:
                with st.sidebar.expander("💾 Knowledge Base", expanded=False):
                    for key, value in kb_size.items():
                        st.text(f"{key}: {value}")

    except Exception as e:
        logger.error(f"Status display error: {str(e)}")


def render_chat_interface():
    """Render main chat interface"""
    st.markdown('<div class="main-header">🏭 Pistology-WAIS v2.1</div>', unsafe_allow_html=True)
    st.markdown("**Warehouse AI System** - OpenAI-Powered Multi-Agent Intelligence with Lean Six Sigma")
    st.markdown("---")

    if not st.session_state.system_initialized:
        st.info("👈 Please configure your OpenAI API key and initialize the system in the sidebar")

        # Show feature cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="agent-card">
            <h3>📦 Inventory Management</h3>
            <ul>
                <li>EOQ Calculation</li>
                <li>Reorder Points</li>
                <li>Safety Stock</li>
                <li><b>ABC Classification</b></li>
                <li><b>Pareto Analysis</b></li>
                <li>Demand Forecasting</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="agent-card">
            <h3>⚙️ Operations</h3>
            <ul>
                <li>Throughput Analysis</li>
                <li>Cycle Time</li>
                <li>Labor Productivity</li>
                <li>Equipment Utilization</li>
                <li>Workflow Optimization</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="agent-card">
            <h3>🔧 Quality (Six Sigma)</h3>
            <ul>
                <li><b>DMAIC Methodology</b></li>
                <li><b>Process Capability (Cp/Cpk)</b></li>
                <li><b>DPMO & Sigma Levels</b></li>
                <li><b>Pareto Analysis</b></li>
                <li><b>ABC Analysis</b></li>
                <li>Process Variation</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### 📄 Document Intelligence
            - **IBM Docling** - Advanced document parsing
            - **OCR** - Scan text from images
            - **Table Extraction** - Automatic table detection
            - **Context Integration** - Documents inform agent responses
            """)

        with col2:
            st.markdown("""
            ### 🎯 Advanced Analytics
            - **80/20 Rule** - Pareto principle analysis
            - **Six Sigma Tools** - Quality management
            - **Statistical Analysis** - Process capability
            - **Interactive Visualizations** - Plotly charts
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
            with st.spinner("🤔 Thinking..."):
                try:
                    # Check if documents are available for context
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
                        with st.expander("🔧 Function Calls", expanded=False):
                            for fc in response.function_calls:
                                st.json(fc)

                    # Check for visualization data and render
                    visualization = extract_visualization_data(response)

                    # Add to messages
                    msg = {"role": "assistant", "content": content}
                    if visualization:
                        msg["visualization"] = visualization
                        render_visualization(visualization)

                    st.session_state.messages.append(msg)

                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    logger.error(f"Query processing error: {str(e)}", exc_info=True)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})


def extract_visualization_data(response) -> Optional[Dict[str, Any]]:
    """Extract data for visualization from response"""
    try:
        if response.function_calls:
            for fc in response.function_calls:
                func_name = fc.get("function", "")
                result = fc.get("result", {})

                # Pareto analysis
                if "pareto" in func_name.lower() and result:
                    return {"type": "pareto", "data": result}

                # ABC analysis
                elif "abc" in func_name.lower() and result:
                    return {"type": "abc", "data": result}

                # Process capability
                elif "capability" in func_name.lower() and result:
                    return {"type": "capability", "data": result}

                # Process variation
                elif "variation" in func_name.lower() and result:
                    return {"type": "variation", "data": result}

                # DPMO
                elif "dpmo" in func_name.lower() and result:
                    return {"type": "dpmo", "data": result}

    except Exception as e:
        logger.error(f"Visualization extraction error: {str(e)}")

    return None


def render_visualization(viz_data):
    """Render visualizations for analysis results"""
    try:
        viz_type = viz_data.get("type")
        data = viz_data.get("data", {})

        if not data:
            return

        if viz_type == "pareto":
            render_pareto_chart(data)
        elif viz_type == "abc":
            render_abc_chart(data)
        elif viz_type == "capability":
            render_capability_chart(data)
        elif viz_type == "variation":
            render_variation_chart(data)
        elif viz_type == "dpmo":
            render_dpmo_chart(data)

    except Exception as e:
        logger.error(f"Visualization rendering error: {str(e)}")
        st.warning(f"⚠️ Could not render visualization: {str(e)}")


def render_pareto_chart(data):
    """Render Pareto chart (80/20 rule)"""
    try:
        analysis = data.get("analysis", [])
        if not analysis:
            st.warning("No data available for Pareto chart")
            return

        # Create figure
        fig = go.Figure()

        # Extract data
        names = [item.get("name", item.get("sku", f"Item {i}")) for i, item in enumerate(analysis)]
        values = [item.get("value", item.get("metric_value", 0)) for item in analysis]
        cumulative = [item.get("cumulative_percentage", 0) for item in analysis]

        # Bar chart for values
        fig.add_trace(go.Bar(
            x=names,
            y=values,
            name="Value",
            marker_color='lightblue',
            yaxis="y"
        ))

        # Line chart for cumulative %
        fig.add_trace(go.Scatter(
            x=names,
            y=cumulative,
            name="Cumulative %",
            yaxis="y2",
            line=dict(color='red', width=3),
            marker=dict(size=10, color='red')
        ))

        # Add 80% reference line
        fig.add_hline(
            y=80,
            line_dash="dash",
            line_color="orange",
            line_width=2,
            yref="y2",
            annotation_text="80% Line",
            annotation_position="right"
        )

        fig.update_layout(
            title="📊 Pareto Analysis (80/20 Rule)",
            xaxis_title="Items",
            yaxis=dict(title="Value", side="left"),
            yaxis2=dict(
                title="Cumulative Percentage (%)",
                overlaying="y",
                side="right",
                range=[0, 100]
            ),
            hovermode="x unified",
            height=500,
            showlegend=True,
            legend=dict(x=0.01, y=0.99)
        )

        st.plotly_chart(fig, use_container_width=True)

        # Show summary
        summary = data.get("summary", {})
        if summary:
            col1, col2, col3 = st.columns(3)
            col1.metric("🎯 Vital Few Items", summary.get("vital_few_count", 0))
            col2.metric("📊 Vital Few %", f"{summary.get('vital_few_percentage', 0):.1f}%")
            col3.metric("💰 Value Contribution", f"{summary.get('vital_few_contribution', 0):.1f}%")

    except Exception as e:
        logger.error(f"Pareto chart error: {str(e)}")
        st.error(f"Error rendering Pareto chart: {str(e)}")


def render_abc_chart(data):
    """Render ABC classification chart"""
    try:
        classification = data.get("classification", [])
        summary = data.get("summary", {})

        if not classification or not summary:
            st.warning("No data available for ABC chart")
            return

        # Pie chart for ABC distribution
        categories = ["A", "B", "C"]
        counts = [summary.get(f"{cat}_items", {}).get("count", 0) for cat in categories]

        # Only include categories with items
        valid_categories = [cat for cat, count in zip(categories, counts) if count > 0]
        valid_counts = [count for count in counts if count > 0]

        if not valid_counts:
            st.warning("No items in ABC classification")
            return

        fig = go.Figure(data=[go.Pie(
            labels=valid_categories,
            values=valid_counts,
            hole=0.3,
            marker_colors=['#ff6b6b', '#ffd93d', '#6bcf7f'],
            textinfo='label+percent',
            textfont_size=14
        )])

        fig.update_layout(
            title="📊 ABC Classification Distribution",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Show details
        st.markdown("### Category Details")
        col1, col2, col3 = st.columns(3)

        for idx, cat in enumerate(categories):
            cat_data = summary.get(f"{cat}_items", {})
            if cat_data.get("count", 0) > 0:
                with [col1, col2, col3][idx]:
                    st.markdown(f"**Category {cat}**")
                    st.metric("Items", cat_data.get("count", 0))
                    st.metric("% of Items", f"{cat_data.get('percentage_of_items', 0):.1f}%")
                    st.metric("Value %", f"{cat_data.get('value_contribution', 0):.1f}%")
                    mgmt = cat_data.get("management", "")
                    if mgmt:
                        st.caption(mgmt)

    except Exception as e:
        logger.error(f"ABC chart error: {str(e)}")
        st.error(f"Error rendering ABC chart: {str(e)}")


def render_capability_chart(data):
    """Render process capability chart"""
    try:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Cp (Potential)", f"{data.get('cp', 0):.3f}")
        col2.metric("Cpk (Actual)", f"{data.get('cpk', 0):.3f}")
        col3.metric("Sigma Level", f"{data.get('sigma_level', 0):.2f}σ")
        col4.metric("Est. DPMO", f"{data.get('estimated_dpmo', 0):,.0f}")

        # Interpretation
        interpretation = data.get("interpretation", "")
        if interpretation:
            if "Excellent" in interpretation or "World-class" in interpretation:
                st.success(f"✅ {interpretation}")
            elif "Good" in interpretation or "Capable" in interpretation:
                st.info(f"ℹ️ {interpretation}")
            elif "Marginal" in interpretation or "Fair" in interpretation:
                st.warning(f"⚠️ {interpretation}")
            else:
                st.error(f"❌ {interpretation}")

        recommendation = data.get("recommendation", "")
        if recommendation:
            st.write(f"**💡 Recommendation:** {recommendation}")

    except Exception as e:
        logger.error(f"Capability chart error: {str(e)}")
        st.error(f"Error rendering capability chart: {str(e)}")


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
        if stability:
            if "Stable" in stability:
                st.success(f"✅ {stability}")
            else:
                st.warning(f"⚠️ {stability}")

        # Control limits
        limits = data.get("control_limits", {})
        if limits:
            col1, col2, col3 = st.columns(3)
            col1.metric("UCL", f"{limits.get('ucl', 0):.4f}")
            col2.metric("Center", f"{limits.get('center', data.get('mean', 0)):.4f}")
            col3.metric("LCL", f"{limits.get('lcl', 0):.4f}")

    except Exception as e:
        logger.error(f"Variation chart error: {str(e)}")
        st.error(f"Error rendering variation chart: {str(e)}")


def render_dpmo_chart(data):
    """Render DPMO and sigma level metrics"""
    try:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("DPMO", f"{data.get('dpmo', 0):,.0f}")
        col2.metric("Sigma Level", f"{data.get('sigma_level', 0):.2f}σ")
        col3.metric("Yield %", f"{data.get('yield_percentage', 0):.3f}%")
        col4.metric("DPU", f"{data.get('dpu', 0):.4f}")

        # Quality level interpretation
        sigma = data.get('sigma_level', 0)
        if sigma >= 6:
            st.success("✅ World-class quality (6σ)")
        elif sigma >= 5:
            st.info("ℹ️ Excellent quality (5σ)")
        elif sigma >= 4:
            st.warning("⚠️ Good quality (4σ)")
        elif sigma >= 3:
            st.warning("⚠️ Average quality (3σ)")
        else:
            st.error("❌ Poor quality (<3σ)")

        interpretation = data.get("interpretation", "")
        if interpretation:
            st.write(f"**Analysis:** {interpretation}")

    except Exception as e:
        logger.error(f"DPMO chart error: {str(e)}")
        st.error(f"Error rendering DPMO chart: {str(e)}")


def render_statistics_tab():
    """Render statistics and analytics tab"""
    if not st.session_state.system_initialized:
        st.info("👈 Initialize the system to view statistics")
        return

    st.subheader("📊 System Analytics & Performance")

    try:
        # Get statistics
        status = st.session_state.orchestrator.get_system_status()
        doc_stats = st.session_state.orchestrator.get_document_statistics()

        # Overview metrics
        st.markdown("### 📈 Overview")
        col1, col2, col3, col4 = st.columns(4)

        kb_size = status.get("knowledge_base_size", {})
        col1.metric("💬 Conversations", kb_size.get("conversations", 0))
        col2.metric("📄 Documents", doc_stats.get("documents_in_context", 0))
        col3.metric("💡 Insights", kb_size.get("insights", 0))
        col4.metric("✅ Decisions", kb_size.get("decisions", 0))

        st.markdown("---")

        # Document statistics
        if doc_stats.get("total_processed", 0) > 0:
            st.markdown("### 📄 Document Processing")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Processed", doc_stats["total_processed"])
            col2.metric("Successful", doc_stats["successful"])
            col3.metric("Failed", doc_stats.get("failed", 0))
            col4.metric("Avg Time", f"{doc_stats.get('average_processing_time', 0):.2f}s")

            # File types
            if doc_stats.get("file_types"):
                st.write("**File Types:**", ", ".join(doc_stats["file_types"]))

            # Show processed documents
            if st.session_state.processed_documents:
                with st.expander("📋 Processed Documents", expanded=False):
                    for doc in st.session_state.processed_documents:
                        st.text(f"✅ {doc.get('filename', 'Unknown')}")

            st.markdown("---")

        # Agent performance
        st.markdown("### 🤖 Agent Performance")

        col1, col2, col3, col4, col5 = st.columns(5)
        agents = [
            ("Supervisor", "🎯"),
            ("Inventory", "📦"),
            ("Operations", "⚙️"),
            ("Math", "🔢"),
            ("Quality", "🔧")
        ]

        for col, (agent, emoji) in zip([col1, col2, col3, col4, col5], agents):
            with col:
                st.markdown(f"**{emoji} {agent}**")
                st.markdown("Status: ✅ Ready")
                st.markdown(f"Model: {st.session_state.agent_models.get(agent.lower(), 'gpt-4o')}")

        st.markdown("---")

        # Chat statistics
        if st.session_state.messages:
            st.markdown("### 💬 Chat Statistics")
            col1, col2, col3 = st.columns(3)

            user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
            assistant_msgs = len([m for m in st.session_state.messages if m["role"] == "assistant"])

            col1.metric("User Messages", user_msgs)
            col2.metric("Assistant Messages", assistant_msgs)
            col3.metric("Total Messages", len(st.session_state.messages))

    except Exception as e:
        st.error(f"Error loading statistics: {str(e)}")
        logger.error(f"Statistics error: {str(e)}", exc_info=True)


def render_about_tab():
    """Render about/info tab"""
    st.markdown("""
    ## 🏭 Pistology-WAIS v2.1

    **Warehouse AI Intelligence System** powered by OpenAI

    ### 🌟 Features

    #### 🤖 Multi-Agent System
    - **Supervisor Agent**: Intelligent query routing and coordination
    - **Inventory Agent**: EOQ, ROP, ABC/Pareto, demand forecasting
    - **Operations Agent**: Throughput, cycle time, productivity analysis
    - **Math Agent**: Complex calculations, statistics, symbolic math
    - **Quality Agent**: Six Sigma, DMAIC, process capability

    #### 📄 Document Intelligence
    - **IBM Docling**: Advanced document parsing and analysis
    - **OCR**: Extract text from scanned documents and images
    - **Table Extraction**: Automatic detection and extraction
    - **Context Integration**: Documents inform all agent responses

    #### 📈 Lean Six Sigma Tools
    - **DMAIC**: Define, Measure, Analyze, Improve, Control methodology
    - **Process Capability**: Cp/Cpk calculations for quality assessment
    - **DPMO**: Defects Per Million Opportunities measurement
    - **Sigma Levels**: 1σ to 6σ quality level determination
    - **Process Variation**: Control charts and stability analysis

    #### 🎯 Pareto & ABC Analysis
    - **80/20 Rule**: Identify vital few from trivial many
    - **ABC Classification**: Inventory prioritization (A/B/C categories)
    - **Resource Optimization**: Focus on high-impact items
    - **Interactive Visualizations**: Plotly charts and graphs

    ---

    ### 🚀 Quick Start

    1. **Configure API Key**: Enter your OpenAI API key in the sidebar
    2. **Initialize System**: Click the "Initialize" button
    3. **Upload Documents** (optional): Add warehouse reports for context
    4. **Start Chatting**: Ask questions or request analysis

    ---

    ### 💡 Example Queries

    **Inventory Management:**
    - "Calculate EOQ for 10,000 units annual demand, $50 order cost, $5 holding cost"
    - "Perform ABC classification on my inventory items"
    - "What's the reorder point with 500 units daily demand?"

    **Quality & Six Sigma:**
    - "Calculate process capability with USL=10, LSL=0, data=[5.1, 4.9, 5.2, ...]"
    - "Analyze defects: 15 defects in 1000 units, 3 opportunities per unit"
    - "Do Pareto analysis on these defect causes..."

    **Operations:**
    - "Calculate throughput for 500 units in 8 hours"
    - "Analyze cycle time with these values..."
    - "What's the equipment utilization rate?"

    **Document Analysis:**
    - "What are the key findings from the uploaded report?"
    - "Summarize the defects mentioned in the document"
    - "Extract inventory data from the uploaded Excel file"

    ---

    ### 📚 Version History

    - **v2.1.0** (Jan 2025) - Docling, Six Sigma, Pareto features
    - **v2.0.0** (Jan 2025) - OpenAI SDK migration, modern agentic workflows
    - **v1.0.0** - Initial release with multi-agent system

    ---

    ### 🛠️ Technology Stack

    - **AI**: OpenAI GPT-4o, GPT-4o-mini
    - **Framework**: Streamlit, Python 3.x
    - **Visualization**: Plotly
    - **Document Processing**: IBM Docling, LangChain
    - **Scientific Computing**: NumPy, Pandas, SciPy, SymPy

    ---

    ### 📖 Documentation

    - **Full Documentation**: See `DOCLING_LEAN_SIX_SIGMA_FEATURES.md`
    - **Upgrade Guide**: See `UPGRADE_SUMMARY.md`
    - **Configuration**: See `.env.example`

    ---

    ### ⚙️ Advanced Configuration

    **Model Selection**: Choose different models for each agent in Advanced Settings
    - **gpt-4o**: Best performance, higher cost
    - **gpt-4o-mini**: Good balance, lower cost
    - **gpt-4-turbo**: Legacy model
    - **gpt-3.5-turbo**: Fastest, lowest cost

    **Supported Document Formats:**
    - PDF, Word (.docx), Excel (.xlsx), PowerPoint (.pptx)
    - Text (.txt), Markdown (.md), CSV, JSON
    - Images (with OCR capability)

    ---

    ### 🤝 Support

    For issues, questions, or feature requests, please refer to the project documentation.

    ---

    **Built with ❤️ for warehouse management excellence**
    """)


def main():
    """Main application entry point"""
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Add clear chat button
    if st.sidebar.button("🗑️ Clear Chat History") and st.session_state.system_initialized:
        st.session_state.messages = []
        st.rerun()

    # Main interface tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Statistics", "ℹ️ About"])

    with tab1:
        render_chat_interface()

    with tab2:
        render_statistics_tab()

    with tab3:
        render_about_tab()


if __name__ == "__main__":
    main()
