from typing import List, Dict, Any, Optional
from agents.inventory_agent import InventoryAgent
from agents.operations_agent import OperationsAgent
from agents.supervisor_agent import SupervisorAgent
from agents.document_processor import DocumentProcessor, ProcessingResult
from pathlib import Path
import json
import logging
from dataclasses import asdict, dataclass
from enum import Enum
import queue
import threading
from datetime import datetime

class AgentRole(Enum):
    INVENTORY = "inventory"
    OPERATIONS = "operations"
    SUPERVISOR = "supervisor"

@dataclass
class AgentMessage:
    """Message passed between agents"""
    sender: AgentRole
    receiver: AgentRole
    content: str
    context: Dict[str, Any]
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class AgentOrchestrator:
    def __init__(
        self,
        inventory_agent: InventoryAgent,
        operations_agent: OperationsAgent,
        supervisor_agent: SupervisorAgent,
        document_processor: DocumentProcessor = None
    ):
        """Initialize the agent orchestrator with all required agents"""
        self.inventory_agent = inventory_agent
        self.operations_agent = operations_agent
        self.supervisor_agent = supervisor_agent
        self.document_processor = document_processor or DocumentProcessor()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize message queues for agent communication
        self.message_queues = {
            AgentRole.INVENTORY: queue.Queue(),
            AgentRole.OPERATIONS: queue.Queue(),
            AgentRole.SUPERVISOR: queue.Queue()
        }
        
        # Initialize knowledge base
        self.knowledge_base = {
            "documents": [],
            "insights": [],
            "decisions": []
        }
        
        # Initialize processing directory
        self.processed_dir = Path("processed_documents")
        self.processed_dir.mkdir(exist_ok=True)
        
        # Start message processing threads
        self._start_message_processors()
        
        # Load any existing processing results
        self._load_processing_results()

    def _start_message_processors(self):
        """Start message processing threads for each agent"""
        self.message_processors = {}
        for role in AgentRole:
            thread = threading.Thread(
                target=self._process_messages,
                args=(role,),
                daemon=True
            )
            thread.start()
            self.message_processors[role] = thread

    def _process_messages(self, role: AgentRole):
        """Process messages for a specific agent role"""
        while True:
            try:
                message = self.message_queues[role].get(timeout=1)
                self._handle_message(message)
                self.message_queues[role].task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing message for {role}: {str(e)}")

    def _handle_message(self, message: AgentMessage):
        """Handle an agent message"""
        try:
            # Log message for debugging
            self.logger.debug(f"Message from {message.sender} to {message.receiver}: {message.content[:100]}...")
            
            # Update knowledge base with new information
            if "insight" in message.context:
                self.knowledge_base["insights"].append({
                    "source": message.sender.value,
                    "content": message.context["insight"],
                    "timestamp": message.timestamp
                })
                
            # Route message to appropriate agent
            if message.receiver == AgentRole.SUPERVISOR:
                response = self.supervisor_agent.process(message.content)
            elif message.receiver == AgentRole.INVENTORY:
                response = self.inventory_agent.process(message.content)
            elif message.receiver == AgentRole.OPERATIONS:
                response = self.operations_agent.process(message.content)
                
            # Send response back if needed
            if response and message.context.get("requires_response", False):
                self.send_message(
                    AgentMessage(
                        sender=message.receiver,
                        receiver=message.sender,
                        content=response,
                        context={"in_response_to": message.timestamp}
                    )
                )
                
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")

    def send_message(self, message: AgentMessage):
        """Send a message to an agent"""
        self.message_queues[message.receiver].put(message)

    def process_query(self, query: str, agent_type: Optional[str] = None) -> Dict[str, Any]:
        """Process a query using the appropriate agent with collaborative validation"""
        try:
            # Default to inventory agent if no type specified
            if not agent_type:
                agent_type = "inventory"
                
            # Validate agent type
            if agent_type not in ["inventory", "operations"]:
                raise ValueError(f"Invalid agent type: {agent_type}")
            
            # Process with primary agent
            if agent_type == "inventory":
                response = self.inventory_agent.process(query)
            else:
                response = self.operations_agent.process(query)
                
            # Have supervisor validate the response
            validation = self.supervisor_agent.validate_decision(agent_type, response)
            
            # Update knowledge base
            self.knowledge_base["decisions"].append({
                "query": query,
                "primary_agent": agent_type,
                "response": response,
                "validation": validation,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "response": response,
                "validation": validation,
                "agent_type": agent_type
            }
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return {
                "error": str(e),
                "agent_type": agent_type
            }

    def process_documents(self, file_paths: List[str]) -> List[ProcessingResult]:
        """Process documents with collaborative analysis"""
        try:
            # Process documents
            results = self.document_processor.process_documents(file_paths)
            
            if results:
                # Share results with agents
                self._share_results_with_agents({
                    "results": [result.to_dict() for result in results]
                })
                
                # Collaborative analysis
                for result in results:
                    if result.success:
                        # Get inventory insights
                        inventory_msg = AgentMessage(
                            sender=AgentRole.SUPERVISOR,
                            receiver=AgentRole.INVENTORY,
                            content=result.document_text,
                            context={"task": "extract_insights"}
                        )
                        self.send_message(inventory_msg)
                        
                        # Get operations insights
                        operations_msg = AgentMessage(
                            sender=AgentRole.SUPERVISOR,
                            receiver=AgentRole.OPERATIONS,
                            content=result.document_text,
                            context={"task": "extract_insights"}
                        )
                        self.send_message(operations_msg)
                
            return results
            
        except Exception as e:
            self.logger.error(f"Error in document processing workflow: {str(e)}")
            return []

    def _load_processing_results(self) -> None:
        """Load existing document processing results"""
        try:
            results_dir = Path("processed_documents")
            results_file = results_dir / "processing_results.json"
            
            # Create directory if it doesn't exist
            results_dir.mkdir(parents=True, exist_ok=True)
            
            # Create default results file if it doesn't exist
            if not results_file.exists():
                default_data = {
                    "results": [],
                    "last_updated": datetime.now().isoformat()
                }
                with open(results_file, "w") as f:
                    json.dump(default_data, f, indent=4)
                return
            
            # Load existing results
            try:
                with open(results_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "results" in data:
                        self._share_results_with_agents(data)
                    else:
                        self.logger.warning("Invalid results file format, resetting to default")
                        default_data = {
                            "results": [],
                            "last_updated": datetime.now().isoformat()
                        }
                        with open(results_file, "w") as f:
                            json.dump(default_data, f, indent=4)
            except json.JSONDecodeError:
                self.logger.warning("Corrupted results file, resetting to default")
                default_data = {
                    "results": [],
                    "last_updated": datetime.now().isoformat()
                }
                with open(results_file, "w") as f:
                    json.dump(default_data, f, indent=4)
                    
        except Exception as e:
            self.logger.error(f"Error loading processing results: {str(e)}")

    def _share_results_with_agents(self, data: Dict[str, Any]) -> None:
        """Share processing results with all agents"""
        try:
            # Extract successful documents
            documents = []
            for result in data.get("results", []):
                if result.get("success") and result.get("document_text"):
                    documents.append({
                        "text": result["document_text"],
                        "metadata": result.get("document_metadata", {})
                    })
            
            # Update knowledge base
            self.knowledge_base["documents"].extend(documents)
            
            # Share with each agent via messages
            for doc in documents:
                for role in [AgentRole.INVENTORY, AgentRole.OPERATIONS]:
                    self.send_message(
                        AgentMessage(
                            sender=AgentRole.SUPERVISOR,
                            receiver=role,
                            content=doc["text"],
                            context={
                                "task": "process_document",
                                "metadata": doc["metadata"]
                            }
                        )
                    )
                    
        except Exception as e:
            self.logger.error(f"Error sharing results with agents: {str(e)}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get the current system status including document processor and agent states"""
        try:
            doc_processor_stats = self.document_processor.get_system_stats()
            
            # Get agent statuses
            agent_statuses = {
                "inventory_agent": "Ready" if self.inventory_agent else "Not Initialized",
                "operations_agent": "Ready" if self.operations_agent else "Not Initialized",
                "supervisor_agent": "Ready" if self.supervisor_agent else "Not Initialized"
            }
            
            return {
                "document_processor": doc_processor_stats,
                "agents": agent_statuses,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            self.logger.error(f"Error getting system status: {str(e)}")
            return {
                "document_processor": {
                    "processing_stats": {},
                    "system_info": {}
                },
                "agents": {},
                "error": str(e)
            }
