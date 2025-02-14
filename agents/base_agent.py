from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from .document_processor import DocumentProcessor
import tensorflow as tf
import logging
from datetime import datetime

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.state = {
            "documents_processed": 0,
            "queries_processed": 0,
            "last_activity": None,
            "insights": []
        }
        self.document_processor = DocumentProcessor()
        
        # Setup logging
        self.logger = logging.getLogger(f"agent.{name}")
        
    @abstractmethod
    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process input data and return a response
        
        Args:
            input_data: Input string to process
            context: Optional context dictionary with task information
            
        Returns:
            Processed response
        """
        pass
        
    def extract_insights(self, text: str) -> List[Dict[str, Any]]:
        """Extract insights from text"""
        # Should be implemented by specific agents
        return []
        
    def route_query(self, query: str) -> str:
        """Determine best agent to handle query"""
        # Should be implemented by specific agents
        return "inventory"  # Default to inventory
        
    def validate_response(self, response: str, context: Dict[str, Any]) -> str:
        """Validate and enhance a response"""
        # Should be implemented by specific agents
        return response
        
    def update_state(self, new_state: Dict[str, Any]) -> None:
        """Update agent state"""
        self.state.update(new_state)
        self.state["last_activity"] = datetime.now().isoformat()
        
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the agent"""
        return self.state
        
    def get_status(self) -> str:
        """Get the current status of the agent"""
        return (
            f"Active - Processed: {self.state['documents_processed']} documents, "
            f"{self.state['queries_processed']} queries, "
            f"Insights: {len(self.state['insights'])}"
        )
        
    def see_document(self, document: Dict[str, Any]) -> None:
        """Process a new document and extract insights"""
        try:
            self.state["documents_processed"] += 1
            
            # Extract insights if text is present
            if "text" in document:
                insights = self.extract_insights(document["text"])
                if insights:
                    self.state["insights"].extend(insights)
                    
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            
    def process_task(self, task: str, content: str, context: Dict[str, Any]) -> Optional[str]:
        """Process a specific task"""
        try:
            if task == "extract_insights":
                insights = self.extract_insights(content)
                if insights:
                    self.state["insights"].extend(insights)
                return f"Extracted {len(insights)} insights"
                
            elif task == "route_query":
                return self.route_query(content)
                
            elif task == "validate_response":
                return self.validate_response(content, context)
                
            elif task == "process_document":
                self.see_document({"text": content, "metadata": context.get("metadata", {})})
                return None
                
            else:
                return self.process(content, context)
                
        except Exception as e:
            self.logger.error(f"Error processing task {task}: {str(e)}")
            return None
