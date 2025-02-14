from typing import List, Dict, Any, Optional
from agents.inventory_agent import InventoryAgent
from agents.operations_agent import OperationsAgent
from agents.supervisor_agent import SupervisorAgent
from agents.math_agent import MathAgent
from agents.document_processor import DocumentProcessor, ProcessingResult
from pathlib import Path
import json
import logging
import re
from dataclasses import asdict, dataclass
from enum import Enum
import queue
import threading
from datetime import datetime

class AgentRole(Enum):
    INVENTORY = "inventory"
    OPERATIONS = "operations"
    SUPERVISOR = "supervisor"
    MATH = "math"

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
        math_agent: MathAgent,
        document_processor: DocumentProcessor = None
    ):
        """Initialize the agent orchestrator with all required agents"""
        self.inventory_agent = inventory_agent
        self.operations_agent = operations_agent
        self.supervisor_agent = supervisor_agent
        self.math_agent = math_agent
        self.document_processor = document_processor or DocumentProcessor()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize message queues for agent communication
        self.message_queues = {
            AgentRole.INVENTORY: queue.Queue(),
            AgentRole.OPERATIONS: queue.Queue(),
            AgentRole.SUPERVISOR: queue.Queue(),
            AgentRole.MATH: queue.Queue()
        }
        
        # Initialize knowledge base
        self.knowledge_base = {
            "documents": [],
            "insights": [],
            "decisions": [],
            "calculations": []  # New section for mathematical results
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
            elif message.receiver == AgentRole.MATH:
                response = self.math_agent.process(message.content, message.context)
                
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
            # Detect if query requires mathematical reasoning
            if self._requires_math_reasoning(query):
                math_response = self.math_agent.process(query, {"task": "solve"})
                
                # Verify the mathematical solution
                verification = self.math_agent.process(math_response, {
                    "task": "verify",
                    "original_problem": query
                })
                
                # Store mathematical results
                self.knowledge_base["calculations"].append({
                    "query": query,
                    "solution": math_response,
                    "verification": verification,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Get supervisor validation
                validation = self.supervisor_agent.validate_decision({
                    "problem": query,
                    "solution": math_response,
                    "verification": verification
                })
                
                return {
                    "response": math_response,
                    "verification": verification,
                    "validation": validation
                }
            
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

    def _requires_math_reasoning(self, query: str) -> bool:
        """Detect if a query requires mathematical reasoning"""
        math_indicators = [
            r'\d+[\+\-\*/\^][\d\+\-\*/\^()]*',  # Mathematical operations
            r'calculate|compute|solve|equation|formula|algorithm',  # Mathematical keywords
            r'optimize|efficiency|complexity|performance',  # Optimization keywords
            r'proof|prove|theorem|lemma',  # Mathematical proofs
            r'integral|derivative|sum|product',  # Calculus terms
            r'matrix|vector|linear|algebra',  # Linear algebra terms
            r'probability|statistics|distribution',  # Statistical terms
            r'geometry|trigonometry|angle|distance'  # Geometric terms
        ]
        
        return any(re.search(pattern, query, re.IGNORECASE) for pattern in math_indicators)

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
                "supervisor_agent": "Ready" if self.supervisor_agent else "Not Initialized",
                "math_agent": "Ready" if self.math_agent else "Not Initialized"
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

    def process_query_with_validation(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a user query through the appropriate agent"""
        try:
            # Initialize context if None
            context = context or {}
            
            # Route the query to determine which agent should handle it
            agent_type = self.supervisor_agent.route_query(query)
            
            # Process based on agent type
            if agent_type == "inventory":
                response = self.inventory_agent.process(query, context)
            elif agent_type == "operations":
                response = self.operations_agent.process(query, context)
            elif agent_type == "math":
                response = self._handle_math_query(query, context)
            else:
                response = self.inventory_agent.process(query, context)  # Default to inventory
                
            # Validate the response
            validation_context = {
                "query": query,
                "agent_type": agent_type,
                "context": context
            }
            
            validated_response = self.supervisor_agent.validate_response(response, validation_context)
            return validated_response
            
        except Exception as e:
            self.logger.error(f"Error in query processing: {str(e)}")
            return f"Error processing query: {str(e)}"

    def _handle_math_query(self, query: str, context: Dict[str, Any]) -> str:
        """Handle mathematical queries with validation"""
        try:
            # Get solution from math agent
            solution = self.math_agent.process(query, context)
            
            # Prepare decision data for validation
            decision_data = {
                "problem": query,
                "solution": solution,
                "verification": self.math_agent.verify_solution(query, solution)
            }
            
            # Get validation from supervisor
            validation = self.supervisor_agent.validate_decision(decision_data)
            
            return f"""Solution: {solution}
            
Validation: {validation}"""
            
        except Exception as e:
            self.logger.error(f"Error in math query handling: {str(e)}")
            return f"Error processing mathematical query: {str(e)}"

    def process_document_with_insights(self, document_path: str) -> str:
        """Process a document and extract relevant information"""
        try:
            # Process the document
            processing_result = self.document_processor.process_document(document_path)
            
            if not processing_result.success:
                return f"Error processing document: {processing_result.error}"
                
            # Extract insights using supervisor
            insights = self.supervisor_agent.extract_insights(processing_result.content)
            
            # Format insights
            formatted_insights = "\n".join([
                f"• {insight['content']}" for insight in insights
            ])
            
            return f"""Document processed successfully.
            
Key Insights:
{formatted_insights}"""
            
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            return f"Error processing document: {str(e)}"

    def get_agent_status(self) -> Dict[str, str]:
        """Get the status of all agents"""
        return {
            "inventory": self.inventory_agent.get_status(),
            "operations": self.operations_agent.get_status(),
            "supervisor": self.supervisor_agent.get_status(),
            "math": self.math_agent.get_status(),
            "document_processor": "Ready"
        }
