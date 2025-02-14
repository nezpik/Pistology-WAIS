import streamlit as st
from agents.inventory_agent import InventoryAgent
from agents.operations_agent import OperationsAgent
from agents.supervisor_agent import SupervisorAgent
from agents.math_agent import MathAgent
from agents.agent_orchestrator import AgentOrchestrator
from agents.document_processor import DocumentProcessor, ProcessingResult
import os
from pathlib import Path
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Warehouse Management AI",
    page_icon="🏭",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'document_processor' not in st.session_state:
    st.session_state.document_processor = DocumentProcessor()

if 'processed_documents' not in st.session_state:
    st.session_state.processed_documents = []

def display_chat_history():
    """Display the chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def process_documents(files):
    """Process uploaded documents and return processed results"""
    if not files:
        return []
        
    temp_dir = Path("temp_uploads")
    file_paths = []
        
    try:
        # Create temp directory if it doesn't exist
        temp_dir.mkdir(exist_ok=True)
        
        # Save uploaded files temporarily
        for file in files:
            temp_path = temp_dir / file.name
            with open(temp_path, "wb") as f:
                f.write(file.getvalue())
            file_paths.append(str(temp_path))
            
        # Process documents
        logger.info(f"Processing {len(file_paths)} documents")
        results = st.session_state.document_processor.process_documents(file_paths)
        
        successful_docs = [r for r in results if r.success]
        if successful_docs:
            st.success(f"Successfully processed {len(successful_docs)} documents")
            
            # Add successful documents to orchestrator's knowledge base
            for result in successful_docs:
                st.session_state.agent_orchestrator.knowledge_base["documents"].append({
                    "content": result.document_text,
                    "document_metadata": result.document_metadata,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Display results for each document
            for result in results:
                if result.success:
                    st.info(f"✅ Processed: {result.document_metadata.get('filename', 'Unknown file')}")
                    if 'num_chunks' in result.document_metadata:
                        st.info(f"   Chunks: {result.document_metadata['num_chunks']}")
                else:
                    st.error(f"❌ Failed: {result.error}")
            
            # Update processed documents list
            st.session_state.processed_documents.extend(successful_docs)
            
            # Log the update to knowledge base
            logger.info(f"Added {len(successful_docs)} documents to knowledge base")
            logger.info(f"Knowledge base now contains {len(st.session_state.agent_orchestrator.knowledge_base['documents'])} documents")
        else:
            st.warning("No documents were processed successfully")
            
        return results
        
    except Exception as e:
        error_msg = f"Error processing documents: {str(e)}"
        st.error(error_msg)
        logger.error(error_msg)
        return []
        
    finally:
        # Cleanup temp files
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                logger.warning(f"Could not remove temp file {path}: {str(e)}")
                
        # Try to remove temp directory if empty
        try:
            if temp_dir.exists() and not any(temp_dir.iterdir()):
                temp_dir.rmdir()
        except Exception as e:
            logger.warning(f"Could not remove temp directory: {str(e)}")

def process_user_input(user_input: str):
    """Process user input using the collaborative agent system"""
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)
        
        try:
            # Show processing indicator
            with st.chat_message("assistant"):
                with st.spinner("Processing your request..."):
                    # Get collaborative response
                    response = st.session_state.agent_orchestrator.process_query(user_input)
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Display response immediately
                    st.markdown(response)
            
        except Exception as e:
            error_message = f"Error processing query: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            st.error(error_message)

def main():
    st.title("🏭 Warehouse Management AI")
    
    # Initialize session state for messages if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Initialize agents and orchestrator if not already done
    if 'agent_orchestrator' not in st.session_state:
        try:
            inventory_agent = InventoryAgent()
            operations_agent = OperationsAgent()
            supervisor_agent = SupervisorAgent()
            math_agent = MathAgent()
            
            st.session_state.agent_orchestrator = AgentOrchestrator(
                inventory_agent=inventory_agent,
                operations_agent=operations_agent,
                supervisor_agent=supervisor_agent,
                math_agent=math_agent,
                document_processor=st.session_state.document_processor
            )
        except Exception as e:
            st.error(f"Failed to initialize the AI system: {str(e)}")
            logger.error(f"Agent initialization error: {str(e)}")
            return
    
    # Sidebar for document upload and system status
    with st.sidebar:
        st.header("📄 Document Processing")
        uploaded_files = st.file_uploader(
            "Upload warehouse documents",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            if st.button("Process Documents"):
                with st.spinner("Processing documents..."):
                    results = process_documents(uploaded_files)
                    
                    # Log the results
                    logger.info(f"Document Processing Results: {results}")
                    
                    for result in results:
                        if result.success:
                            st.success(f"Successfully processed {result.document_metadata.get('filename')}")
                        else:
                            st.error(f"Failed to process document: {result.error}")
        
        # Display system status
        st.header("📊 System Status")
        try:
            if st.session_state.agent_orchestrator:
                status = st.session_state.agent_orchestrator.get_system_status()
                
                # Document processing stats
                st.subheader("Document Processor")
                doc_stats = status.get("document_processor", {}).get("processing_stats", {})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Processed", doc_stats.get("total_processed", 0))
                with col2:
                    st.metric("Successful", doc_stats.get("successful", 0))
                with col3:
                    st.metric("Failed", doc_stats.get("failed", 0))
                
                # Agent status
                st.subheader("Agents Status")
                agent_status = status.get("agents", {})
                for agent, state in agent_status.items():
                    st.text(f"{agent.replace('_', ' ').title()}: {state}")
        except Exception as e:
            st.error(f"Error displaying system status: {str(e)}")
            logger.error(f"Status display error: {str(e)}")
    
    # Display chat interface
    st.header("💬 Warehouse Assistant")
    
    # Chat input
    if prompt := st.chat_input("How can I help you with warehouse management?"):
        process_user_input(prompt)

if __name__ == "__main__":
    main()
