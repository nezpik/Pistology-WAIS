import requests
from .base_agent import BaseAgent
from config import DEEPSEEK_API_KEY, DEEPSEEK_MODEL
from typing import Dict, Any, List
import logging

class InventoryAgent(BaseAgent):
    def __init__(self):
        super().__init__("Inventory")
        self.api_key = DEEPSEEK_API_KEY
        self.model = DEEPSEEK_MODEL
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def _call_deepseek_api(self, messages: List[Dict[str, str]]) -> str:
        """Make a call to the DeepSeek API"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            self.logger.error(f"DeepSeek API error: {str(e)}")
            raise
        
    def process(self, input_data: str, context: Dict[str, Any] = None) -> str:
        """Process inventory-related queries and tasks"""
        try:
            context = context or {}
            task = context.get("task", "general")
            
            if task == "extract_insights":
                return self._extract_inventory_insights(input_data)
            elif task == "process_query":
                # Handle inventory-specific query
                prompt = f"""As an Inventory Management Agent, provide a detailed response to this query:

Query: {input_data}

Consider:
1. Current stock levels and trends
2. Inventory optimization
3. Storage efficiency
4. Stock movement patterns
5. Reorder points and safety stock

Provide specific, actionable insights related to inventory management."""
                
                response = self.model.generate_content(prompt)
                return response.text
            else:
                return self._process_inventory_query(input_data, context)
                
        except Exception as e:
            self.logger.error(f"Error in inventory processing: {str(e)}")
            return f"Error processing inventory request: {str(e)}"
            
    def extract_insights(self, text: str) -> List[Dict[str, Any]]:
        """Extract inventory insights from text"""
        try:
            messages = [{
                "role": "system",
                "content": "You are an inventory analysis expert. Extract key insights from warehouse text."
            }, {
                "role": "user",
                "content": f"""Extract key inventory insights from this warehouse text:
                
                Text: {text}
                
                Focus on:
                1. Stock levels
                2. Inventory turnover
                3. Storage optimization
                4. Demand patterns
                5. Supply chain impacts
                6. Cost implications
                
                Format as bullet points."""
            }]
            
            response = self._call_deepseek_api(messages)
            
            insights = []
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('•') or line.startswith('-'):
                    insights.append({
                        "type": "inventory_insight",
                        "content": line.lstrip('•- ').strip()
                    })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error extracting insights: {str(e)}")
            return []
            
    def _process_inventory_query(self, query: str, context: Dict[str, Any]) -> str:
        """Process a general inventory query"""
        try:
            messages = [{
                "role": "system",
                "content": "You are an inventory management expert assistant. Provide clear, actionable responses to warehouse inventory queries."
            }, {
                "role": "user",
                "content": query
            }]
            
            return self._call_deepseek_api(messages)
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return f"Error processing inventory query: {str(e)}"
            
    def get_status(self) -> str:
        """Get the current status of the agent"""
        return "Ready"
