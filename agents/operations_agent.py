"""
Operations Agent - OpenAI-powered warehouse operations optimization.

Specializes in workflow efficiency, resource allocation, and process optimization.
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent, AgentConfig


class OperationsAgent(BaseAgent):
    """Warehouse operations optimization agent with tools for process analysis"""

    def _get_system_prompt(self) -> str:
        return """You are an expert warehouse operations agent specializing in operational excellence.

Your responsibilities:
- Workflow optimization and process improvement
- Resource allocation and capacity planning
- Bottleneck identification and resolution
- Equipment utilization analysis
- Labor productivity optimization
- Safety and compliance monitoring
- Performance metrics tracking

When analyzing operations:
1. Identify inefficiencies and bottlenecks
2. Recommend process improvements with ROI estimates
3. Consider safety and compliance requirements
4. Balance efficiency with quality standards
5. Provide actionable, measurable recommendations

Use the provided functions for calculations. Always support recommendations with data."""

    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "calculate_throughput",
                    "description": "Calculate warehouse throughput metrics",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "units_processed": {"type": "number", "description": "Units processed"},
                            "time_period_hours": {"type": "number", "description": "Time period in hours"}
                        },
                        "required": ["units_processed", "time_period_hours"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_cycle_time",
                    "description": "Calculate average cycle time for warehouse operations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "total_time_hours": {"type": "number", "description": "Total time in hours"},
                            "units_completed": {"type": "number", "description": "Number of units completed"}
                        },
                        "required": ["total_time_hours", "units_completed"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_labor_productivity",
                    "description": "Calculate labor productivity metrics",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "units_processed": {"type": "number"},
                            "labor_hours": {"type": "number"},
                            "number_of_workers": {"type": "integer"}
                        },
                        "required": ["units_processed", "labor_hours"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_equipment_utilization",
                    "description": "Analyze equipment utilization rate",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "actual_operating_hours": {"type": "number"},
                            "available_hours": {"type": "number"}
                        },
                        "required": ["actual_operating_hours", "available_hours"]
                    }
                }
            }
        ]

    def _execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute operations management functions"""

        if function_name == "calculate_throughput":
            units = arguments["units_processed"]
            time_hours = arguments["time_period_hours"]
            throughput = units / time_hours
            return {
                "throughput_per_hour": round(throughput, 2),
                "throughput_per_day": round(throughput * 24, 2),
                "units_processed": units,
                "time_period_hours": time_hours
            }

        elif function_name == "calculate_cycle_time":
            total_time = arguments["total_time_hours"]
            units = arguments["units_completed"]
            cycle_time = (total_time * 60) / units  # Convert to minutes per unit
            return {
                "cycle_time_minutes": round(cycle_time, 2),
                "cycle_time_hours": round(cycle_time / 60, 4),
                "units_completed": units,
                "total_time_hours": total_time
            }

        elif function_name == "calculate_labor_productivity":
            units = arguments["units_processed"]
            hours = arguments["labor_hours"]
            workers = arguments.get("number_of_workers", 1)

            productivity = units / hours
            per_worker = units / (hours / workers) if workers > 0 else 0

            return {
                "productivity_units_per_hour": round(productivity, 2),
                "productivity_per_worker": round(per_worker, 2),
                "total_units": units,
                "total_labor_hours": hours,
                "number_of_workers": workers
            }

        elif function_name == "analyze_equipment_utilization":
            actual = arguments["actual_operating_hours"]
            available = arguments["available_hours"]
            utilization = (actual / available) * 100

            if utilization >= 85:
                status = "Excellent - High utilization"
            elif utilization >= 70:
                status = "Good - Healthy utilization"
            elif utilization >= 50:
                status = "Moderate - Room for improvement"
            else:
                status = "Low - Investigate underutilization"

            return {
                "utilization_percentage": round(utilization, 2),
                "actual_hours": actual,
                "available_hours": available,
                "idle_hours": round(available - actual, 2),
                "status": status
            }

        else:
            return {"error": f"Unknown function: {function_name}"}
