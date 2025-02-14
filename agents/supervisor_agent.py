import google.generativeai as genai
import tensorflow as tf
from .base_agent import BaseAgent
from config import GEMINI_SUPERVISOR_KEY
from typing import Dict, Any, List

class SupervisorAgent(BaseAgent):
    def __init__(self):
        super().__init__("Supervisor")
        self.api_key = GEMINI_SUPERVISOR_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def process(self, input_data: str, context: Dict[str, Any] = None) -> str:
        """Process and validate other agents' outputs"""
        try:
            context = context or {}
            task = context.get("task", "validate_response")
            
            if task == "route_query":
                return self.route_query(input_data)
            elif task == "validate_response":
                return self.validate_response(input_data, context)
            elif task == "extract_insights":
                insights = self.extract_insights(input_data)
                return f"Extracted {len(insights)} insights"
            else:
                return self._process_general_query(input_data, context)
                
        except Exception as e:
            self.logger.error(f"Error in supervisor processing: {str(e)}")
            return f"Error processing request: {str(e)}"
            
    def route_query(self, query: str) -> str:
        """Determine the best agent to handle a query"""
        try:
            prompt = f"""As a Supervisor Agent, determine which specialized agent should handle this query:
            Query: {query}
            
            Available agents:
            1. Inventory Agent - Handles inventory management, stock levels, ordering
            2. Operations Agent - Handles warehouse operations, logistics, processes
            
            Choose one: 'inventory' or 'operations'
            Respond with ONLY the agent name, no other text."""
            
            response = self.model.generate_content(prompt)
            agent_type = response.text.strip().lower()
            
            if agent_type in ["inventory", "operations"]:
                return agent_type
            return "inventory"  # Default to inventory if unclear
            
        except Exception as e:
            self.logger.error(f"Error routing query: {str(e)}")
            return "inventory"
            
    def validate_response(self, response: str, context: Dict[str, Any]) -> str:
        """Validate and enhance agent responses"""
        try:
            original_query = context.get("original_query", "")
            
            prompt = f"""As a Supervisor Agent, validate and enhance this response:
            
            Original Query: {original_query}
            Agent Response: {response}
            
            Validate for:
            1. Accuracy and completeness
            2. Alignment with warehouse management best practices
            3. Practical feasibility
            4. Safety and compliance
            
            Provide:
            1. Validation status
            2. Any necessary corrections or enhancements
            3. Additional recommendations if needed"""
            
            validation = self.model.generate_content(prompt)
            return validation.text
            
        except Exception as e:
            self.logger.error(f"Error validating response: {str(e)}")
            return "Could not validate response due to error"
            
    def extract_insights(self, text: str) -> List[Dict[str, Any]]:
        """Extract high-level insights from text"""
        try:
            prompt = f"""Extract key insights from this text related to warehouse management:
            
            Text: {text}
            
            Focus on:
            1. Strategic implications
            2. Cross-functional impacts
            3. Potential optimizations
            4. Risk factors
            
            Format as bullet points."""
            
            response = self.model.generate_content(prompt)
            
            # Convert bullet points to insights
            insights = []
            for line in response.text.split('\n'):
                line = line.strip()
                if line.startswith('•') or line.startswith('-'):
                    insights.append({
                        "content": line[1:].strip(),
                        "source": "supervisor",
                        "type": "strategic"
                    })
                    
            return insights
            
        except Exception as e:
            self.logger.error(f"Error extracting insights: {str(e)}")
            return []
            
    def validate_decision(self, agent_type: str, response: str) -> str:
        """Validate a decision from an agent"""
        try:
            prompt = f"""As a Supervisor Agent, validate this {agent_type} agent's response:
            
            Response: {response}
            
            Validate for:
            1. Accuracy and completeness
            2. Alignment with warehouse management best practices
            3. Practical feasibility
            4. Safety and compliance
            
            Provide a brief validation summary."""
            
            validation = self.model.generate_content(prompt)
            return validation.text.strip()
            
        except Exception as e:
            self.logger.error(f"Error validating decision: {str(e)}")
            return "Could not validate decision due to error"

    def _process_general_query(self, query: str, context: Dict[str, Any]) -> str:
        """Process general queries that don't fit specific tasks"""
        try:
            prompt = f"""As a Warehouse Management Supervisor, address this query:
            
            Query: {query}
            
            Consider:
            1. Overall warehouse efficiency
            2. Cross-functional coordination
            3. Resource optimization
            4. Risk management
            
            Provide a comprehensive response."""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            self.logger.error(f"Error processing general query: {str(e)}")
            return "Could not process query due to error"
