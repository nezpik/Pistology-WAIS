import google.generativeai as genai
from .base_agent import BaseAgent
from config import GEMINI_OPERATIONS_KEY
from typing import Dict, Any, List
import logging

class OperationsAgent(BaseAgent):
    def __init__(self):
        super().__init__("Operations")
        self.api_key = GEMINI_OPERATIONS_KEY
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.logger = logging.getLogger(__name__)
        
    def process(self, input_data: str, context: Dict[str, Any] = None) -> str:
        """Process operations-related queries"""
        try:
            context = context or {}
            task = context.get("task", "process_query")
            
            if task == "extract_insights":
                insights = self.extract_insights(input_data)
                return f"Extracted {len(insights)} operational insights"
            else:
                return self._process_operations_query(input_data, context)
                
        except Exception as e:
            self.logger.error(f"Error in operations processing: {str(e)}")
            return f"Error processing operations request: {str(e)}"
            
    def extract_insights(self, text: str) -> List[Dict[str, Any]]:
        """Extract operational insights from text"""
        try:
            prompt = f"""Extract key operational insights from this warehouse text:
            
            Text: {text}
            
            Focus on:
            1. Process efficiency
            2. Resource utilization
            3. Workflow optimization
            4. Safety and compliance
            5. Equipment usage
            6. Labor allocation
            
            Format as bullet points."""
            
            response = self.model.generate_content(prompt)
            
            insights = []
            for line in response.text.split('\n'):
                line = line.strip()
                if line.startswith('•') or line.startswith('-'):
                    insights.append({
                        "content": line[1:].strip(),
                        "source": "operations",
                        "type": "operational"
                    })
                    
            return insights
            
        except Exception as e:
            self.logger.error(f"Error extracting operational insights: {str(e)}")
            return []
            
    def _process_operations_query(self, query: str, context: Dict[str, Any]) -> str:
        """Process warehouse operations queries"""
        try:
            prompt = f"""As a Warehouse Operations Agent, address this query:
            
            Query: {query}
            
            Consider:
            1. Process optimization
            2. Resource allocation
            3. Safety protocols
            4. Equipment utilization
            5. Labor management
            6. Workflow efficiency
            
            Provide specific, actionable recommendations."""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            self.logger.error(f"Error processing operations query: {str(e)}")
            return "Could not process operations query due to error"
            
    def analyze_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze warehouse workflow data"""
        try:
            workflow_text = str(workflow_data)
            prompt = f"""Analyze this warehouse workflow data and provide insights:
            
            Workflow Data: {workflow_text}
            
            Analyze for:
            1. Bottlenecks
            2. Inefficiencies
            3. Safety concerns
            4. Resource utilization
            5. Improvement opportunities
            
            Format findings as structured recommendations."""
            
            response = self.model.generate_content(prompt)
            
            return {
                "analysis": response.text,
                "timestamp": context.get("timestamp", ""),
                "workflow_id": workflow_data.get("id", "unknown")
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing workflow: {str(e)}")
            return {"error": str(e)}
            
    def optimize_resource_allocation(self, resources: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize resource allocation based on current state"""
        try:
            resources_text = str(resources)
            prompt = f"""Optimize resource allocation for these warehouse resources:
            
            Resources: {resources_text}
            
            Consider:
            1. Labor distribution
            2. Equipment usage
            3. Space utilization
            4. Time management
            5. Cost efficiency
            
            Provide specific allocation recommendations."""
            
            response = self.model.generate_content(prompt)
            
            return {
                "recommendations": response.text,
                "resource_ids": list(resources.keys()),
                "optimization_type": "resource_allocation"
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing resources: {str(e)}")
            return {"error": str(e)}
