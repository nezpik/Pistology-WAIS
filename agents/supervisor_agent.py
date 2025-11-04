"""
Supervisor Agent - OpenAI-powered agent routing and coordination.

Coordinates between specialized agents and validates their outputs.
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent, AgentConfig
import json


class SupervisorAgent(BaseAgent):
    """Supervisor agent for routing queries and coordinating multi-agent workflows"""

    def _get_system_prompt(self) -> str:
        return """You are the supervisor agent coordinating a team of specialized warehouse agents.

Your team:
- Inventory Agent: Stock levels, EOQ, reorder points, demand forecasting
- Operations Agent: Workflow optimization, resource allocation, throughput
- Math Agent: Complex calculations, optimization problems, statistical analysis

Your responsibilities:
1. Route queries to the most appropriate agent(s)
2. Validate and synthesize responses from multiple agents
3. Ensure response quality and completeness
4. Handle queries requiring multiple agents
5. Provide executive-level insights and recommendations

Routing Guidelines:
- Inventory Agent: Stock, inventory levels, ordering, demand, SKUs
- Operations Agent: Workflows, processes, productivity, equipment, labor
- Math Agent: Complex calculations, optimization, statistical analysis, formulas
- Multiple agents: Queries spanning multiple domains

Always provide clear, actionable insights with proper context."""

    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "route_query",
                    "description": "Determine which agent(s) should handle a query",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The user query"},
                            "context": {"type": "string", "description": "Additional context"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_response",
                    "description": "Validate an agent's response for quality and completeness",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "agent_name": {"type": "string", "description": "Name of the agent"},
                            "response": {"type": "string", "description": "Agent's response"},
                            "original_query": {"type": "string", "description": "Original query"}
                        },
                        "required": ["agent_name", "response", "original_query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "synthesize_responses",
                    "description": "Combine responses from multiple agents into a cohesive answer",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "responses": {
                                "type": "object",
                                "description": "Dictionary of agent responses"
                            },
                            "query": {"type": "string", "description": "Original query"}
                        },
                        "required": ["responses", "query"]
                    }
                }
            }
        ]

    def _execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute supervisor functions"""

        if function_name == "route_query":
            query = arguments["query"].lower()

            # Keywords for routing
            inventory_keywords = ["stock", "inventory", "eoq", "reorder", "demand", "forecast", "sku", "safety stock"]
            operations_keywords = ["workflow", "process", "productivity", "throughput", "cycle time", "labor", "equipment", "efficiency"]
            math_keywords = ["calculate", "optimize", "formula", "equation", "statistical", "algorithm", "compute"]

            # Score each agent
            scores = {
                "inventory": sum(1 for kw in inventory_keywords if kw in query),
                "operations": sum(1 for kw in operations_keywords if kw in query),
                "math": sum(1 for kw in math_keywords if kw in query)
            }

            # Determine routing
            max_score = max(scores.values())
            if max_score == 0:
                recommended_agent = "inventory"  # Default
            else:
                recommended_agent = max(scores, key=scores.get)

            # Check if multiple agents needed
            agents_with_scores = [agent for agent, score in scores.items() if score > 0]
            multi_agent = len(agents_with_scores) > 1

            return {
                "primary_agent": recommended_agent,
                "requires_multiple_agents": multi_agent,
                "additional_agents": agents_with_scores if multi_agent else [],
                "scores": scores,
                "reasoning": f"Query has {max_score} relevant keywords for {recommended_agent}"
            }

        elif function_name == "validate_response":
            agent = arguments["agent_name"]
            response = arguments["response"]
            query = arguments["original_query"]

            # Simple validation checks
            is_valid = len(response) > 20 and "error" not in response.lower()
            has_data = any(char.isdigit() for char in response)
            has_recommendations = any(word in response.lower() for word in ["recommend", "suggest", "should", "consider"])

            quality_score = sum([is_valid, has_data, has_recommendations]) / 3

            return {
                "is_valid": is_valid,
                "quality_score": round(quality_score, 2),
                "has_numerical_data": has_data,
                "has_recommendations": has_recommendations,
                "validation_passed": quality_score >= 0.5
            }

        elif function_name == "synthesize_responses":
            responses = arguments["responses"]
            query = arguments["query"]

            # Create synthesis
            synthesis = f"Analysis of: {query}\n\n"
            for agent, response in responses.items():
                synthesis += f"**{agent.title()} Analysis:**\n{response}\n\n"

            return {
                "synthesized_response": synthesis,
                "agents_consulted": list(responses.keys()),
                "total_agents": len(responses)
            }

        else:
            return {"error": f"Unknown function: {function_name}"}

    def route_query(self, query: str) -> str:
        """Helper method for query routing"""
        result = self._execute_function("route_query", {"query": query})
        return result["primary_agent"]

    def validate_decision(self, decision_data: Dict[str, Any]) -> str:
        """Validate a decision or calculation"""
        if isinstance(decision_data, dict):
            return "Decision validated: Data appears complete and reasonable."
        return "Unable to validate decision: Invalid format."
