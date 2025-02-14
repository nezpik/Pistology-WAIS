import google.generativeai as genai
import tensorflow as tf
from .base_agent import BaseAgent
from config import GEMINI_API_KEY_SUPERVISOR, GEMINI_MODEL
from typing import Dict, Any, List

class SupervisorAgent(BaseAgent):
    def __init__(self):
        super().__init__("Supervisor")
        self.api_key = GEMINI_API_KEY_SUPERVISOR
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        
    def process(self, input_data: str, context: Dict[str, Any] = None) -> str:
        """Process and validate other agents' outputs"""
        try:
            context = context or {}
            task = context.get("task", "validate_response")
            
            if task == "route_query":
                return self.route_query(input_data)
            elif task == "validate_response":
                return self.validate_response(input_data, context)
            elif task == "validate_decision":
                return self.validate_decision(input_data)
            elif task == "extract_insights":
                insights = self.extract_insights(input_data)
                return f"Extracted {len(insights)} insights"
            elif task == "analyze_query":
                return self.analyze_query(input_data, context.get("context", []))
            elif task == "synthesize_responses":
                return self.synthesize_responses(input_data, context.get("agent_responses", {}), context.get("context", []))
            elif task == "process_query":
                # Analyze the query
                analysis = self.analyze_query(input_data)
                
                # For direct supervisor queries, provide oversight response
                prompt = f"""As a Warehouse Management Supervisor, provide a response to this query:

Query: {input_data}

Consider:
1. Overall warehouse efficiency
2. Resource allocation
3. Process optimization
4. Safety and compliance
5. Team coordination

Provide a clear, actionable response that demonstrates leadership and expertise."""
                
                response = self.model.generate_content(prompt)
                return response.text
            else:
                return self._process_general_query(input_data, context)
                
        except Exception as e:
            self.logger.error(f"Error in supervisor processing: {str(e)}")
            return f"Error processing request: {str(e)}"
            
    def validate_decision(self, decision_data: Dict[str, Any]) -> str:
        """Validate a decision or solution"""
        try:
            # Extract relevant information from the decision data
            problem = decision_data.get("problem", "")
            solution = decision_data.get("solution", "")
            verification = decision_data.get("verification", "")
            
            # Construct prompt for validation
            prompt = f"""As a Supervisor Agent, validate this solution:

Problem:
{problem}

Solution:
{solution}

Verification Results:
{verification}

Validate for:
1. Correctness
2. Completeness
3. Clarity
4. Efficiency
5. Best practices

Provide a concise validation summary."""

            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            self.logger.error(f"Error validating decision: {str(e)}")
            return f"Error in validation: {str(e)}"
            
    def route_query(self, query: str) -> str:
        """Determine the best agent to handle a query"""
        try:
            prompt = f"""As a Supervisor Agent, determine which specialized agent should handle this query:
            Query: {query}
            
            Available agents:
            1. Inventory Agent - Handles inventory management, stock levels, ordering
            2. Operations Agent - Handles warehouse operations, logistics, processes
            3. Math Agent - Handles mathematical calculations, optimizations, and proofs
            
            Choose one: 'inventory', 'operations', or 'math'
            Respond with ONLY the agent name, no other text."""
            
            response = self.model.generate_content(prompt)
            agent_type = response.text.strip().lower()
            
            if agent_type in ["inventory", "operations", "math"]:
                return agent_type
            else:
                return "inventory"  # Default to inventory agent
                
        except Exception as e:
            self.logger.error(f"Error routing query: {str(e)}")
            return "inventory"  # Default to inventory agent on error
            
    def validate_response(self, response: str, context: Dict[str, Any]) -> str:
        """Validate an agent's response"""
        try:
            query = context.get("query", "")
            agent_type = context.get("agent_type", "unknown")
            
            prompt = f"""As a Supervisor Agent, validate this response:

Query: {query}
Agent Type: {agent_type}
Response: {response}

Validate for:
1. Relevance to query
2. Accuracy
3. Completeness
4. Clarity
5. Actionability

Provide a concise validation summary."""
            
            validation = self.model.generate_content(prompt)
            return validation.text.strip()
            
        except Exception as e:
            self.logger.error(f"Error validating response: {str(e)}")
            return f"Error in validation: {str(e)}"
            
    def extract_insights(self, text: str) -> List[Dict[str, Any]]:
        """Extract insights from text"""
        try:
            prompt = f"""Extract key insights from this text:
            
            Text: {text}
            
            Focus on:
            1. Decision points
            2. Action items
            3. Critical information
            4. Recommendations
            5. Risks and issues
            
            Format as bullet points."""
            
            response = self.model.generate_content(prompt)
            
            insights = []
            for line in response.text.split('\n'):
                line = line.strip()
                if line.startswith('•') or line.startswith('-'):
                    insights.append({
                        "content": line[1:].strip(),
                        "source": "supervisor",
                        "type": "insight"
                    })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error extracting insights: {str(e)}")
            return []
            
    def _process_general_query(self, query: str, context: Dict[str, Any]) -> str:
        """Process a general supervision query"""
        try:
            prompt = f"""As a Warehouse Supervisor Agent, address this query:
            
            Query: {query}
            
            Consider:
            1. Safety and compliance
            2. Efficiency and optimization
            3. Resource allocation
            4. Quality control
            5. Risk management
            
            Provide specific, actionable guidance."""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            self.logger.error(f"Error processing general query: {str(e)}")
            return "Could not process query due to error"
            
    def analyze_query(self, query: str, context: List[Dict] = None) -> Dict[str, Any]:
        """Analyze a query to determine required agents and processing steps"""
        try:
            # Prepare context for analysis
            context_str = ""
            if context:
                context_str = "\n".join([
                    f"Context {i+1}:\n{item.get('content', '')}"
                    for i, item in enumerate(context)
                ])

            # Construct prompt for analysis
            prompt = f"""Analyze this warehouse management query and determine required agents:

Query:
{query}

Available Agents:
- Inventory Agent: Handles inventory management, stock levels, warehouse layout
- Operations Agent: Handles workflow optimization, process management, resource allocation
- Math Agent: Handles calculations, optimization, statistical analysis

{context_str if context_str else ''}

Determine:
1. Which agents are needed
2. What information is required
3. Processing priority

Format response as JSON with these fields:
- needs_inventory_data (boolean)
- needs_operations_data (boolean)
- needs_calculations (boolean)
- processing_steps (list)
- priority_order (list)"""

            # Get model response
            response = self.model.generate_content(prompt)
            response_text = response.text

            # Parse response to extract requirements
            import json
            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback if response is not valid JSON
                analysis = {
                    "needs_inventory_data": "inventory" in query.lower(),
                    "needs_operations_data": "operat" in query.lower(),
                    "needs_calculations": any(word in query.lower() for word in ["calculate", "compute", "how many", "optimize"]),
                    "processing_steps": ["analyze query", "gather data", "process"],
                    "priority_order": ["supervisor", "inventory", "operations", "math"]
                }

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing query: {str(e)}")
            # Return default analysis
            return {
                "needs_inventory_data": True,
                "needs_operations_data": True,
                "needs_calculations": True,
                "processing_steps": ["analyze", "process"],
                "priority_order": ["supervisor"]
            }

    def synthesize_responses(self, query: str, agent_responses: Dict[str, str], context: List[Dict] = None) -> str:
        """Synthesize responses from multiple agents into a coherent answer"""
        try:
            # Prepare context string
            context_str = ""
            if context:
                context_str = "\n".join([
                    f"Context {i+1}:\n{item.get('content', '')}"
                    for i, item in enumerate(context)
                ])

            # Construct prompt for synthesis
            prompt = f"""Synthesize a comprehensive response for this warehouse management query:

Original Query:
{query}

Agent Responses:
{chr(10).join([f"{agent}: {response}" for agent, response in agent_responses.items()])}

{context_str if context_str else ''}

Create a clear, concise response that:
1. Addresses the original query
2. Integrates insights from all agents
3. Provides actionable recommendations
4. Maintains professional tone"""

            # Get model response
            response = self.model.generate_content(prompt)
            synthesized_response = response.text

            return synthesized_response

        except Exception as e:
            self.logger.error(f"Error synthesizing responses: {str(e)}")
            # Return a simple concatenation of responses as fallback
            return "\n\n".join([
                f"{agent}:\n{response}"
                for agent, response in agent_responses.items()
            ])

    def get_status(self) -> str:
        """Get the current status of the agent"""
        return "Ready"
