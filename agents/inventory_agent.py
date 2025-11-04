"""
Inventory Agent - OpenAI-powered warehouse inventory management.

This agent specializes in inventory analysis, stock level optimization,
and demand forecasting using OpenAI function calling.
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent, AgentConfig
import math


class InventoryAgent(BaseAgent):
    """
    Inventory management agent with specialized tools for:
    - Stock level analysis
    - EOQ (Economic Order Quantity) calculation
    - Reorder point determination
    - Safety stock calculation
    - Demand forecasting
    """

    def _get_system_prompt(self) -> str:
        return """You are an expert inventory management agent for a warehouse system.

Your responsibilities include:
- Analyzing stock levels and identifying potential stockouts or overstocking
- Calculating optimal order quantities using EOQ (Economic Order Quantity)
- Determining reorder points based on lead time and demand variability
- Computing safety stock levels for desired service levels
- Forecasting demand patterns and trends
- Providing actionable inventory optimization recommendations

When analyzing inventory data:
1. Consider demand patterns and seasonality
2. Account for lead times and variability
3. Balance holding costs vs stockout costs
4. Recommend service level targets
5. Identify slow-moving and fast-moving items

Use the provided functions to perform calculations. Always provide clear, actionable recommendations with supporting data.
"""

    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "calculate_eoq",
                    "description": "Calculate Economic Order Quantity - the optimal order quantity that minimizes total inventory costs",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "annual_demand": {
                                "type": "number",
                                "description": "Annual demand in units"
                            },
                            "order_cost": {
                                "type": "number",
                                "description": "Cost per order (fixed cost)"
                            },
                            "holding_cost": {
                                "type": "number",
                                "description": "Annual holding cost per unit"
                            }
                        },
                        "required": ["annual_demand", "order_cost", "holding_cost"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_reorder_point",
                    "description": "Calculate the reorder point - the inventory level at which a new order should be placed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "daily_demand": {
                                "type": "number",
                                "description": "Average daily demand in units"
                            },
                            "lead_time_days": {
                                "type": "number",
                                "description": "Lead time in days"
                            },
                            "safety_stock": {
                                "type": "number",
                                "description": "Safety stock in units (optional)",
                                "default": 0
                            }
                        },
                        "required": ["daily_demand", "lead_time_days"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_safety_stock",
                    "description": "Calculate safety stock based on demand variability and desired service level",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "daily_demand": {
                                "type": "number",
                                "description": "Average daily demand in units"
                            },
                            "demand_std_dev": {
                                "type": "number",
                                "description": "Standard deviation of daily demand"
                            },
                            "lead_time_days": {
                                "type": "number",
                                "description": "Lead time in days"
                            },
                            "service_level": {
                                "type": "number",
                                "description": "Desired service level (e.g., 0.95 for 95%)",
                                "default": 0.95
                            }
                        },
                        "required": ["daily_demand", "demand_std_dev", "lead_time_days"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_inventory_turnover",
                    "description": "Analyze inventory turnover rate and provide insights",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "cost_of_goods_sold": {
                                "type": "number",
                                "description": "Annual cost of goods sold"
                            },
                            "average_inventory_value": {
                                "type": "number",
                                "description": "Average inventory value"
                            }
                        },
                        "required": ["cost_of_goods_sold", "average_inventory_value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "forecast_demand",
                    "description": "Forecast future demand based on historical data",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "historical_demand": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Array of historical demand values"
                            },
                            "periods_ahead": {
                                "type": "integer",
                                "description": "Number of periods to forecast",
                                "default": 1
                            }
                        },
                        "required": ["historical_demand"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "abc_classification",
                    "description": "Classify inventory items using ABC analysis (Pareto principle). A=high value, B=medium value, C=low value",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "sku": {"type": "string"},
                                        "annual_value": {"type": "number"}
                                    }
                                },
                                "description": "Array of SKUs with annual dollar values"
                            }
                        },
                        "required": ["items"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pareto_analysis_inventory",
                    "description": "Perform Pareto analysis (80/20 rule) on inventory to identify vital few items",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "sku": {"type": "string"},
                                        "metric_value": {"type": "number"}
                                    }
                                },
                                "description": "Items with metric (sales, turns, value, etc.)"
                            },
                            "metric_name": {"type": "string", "description": "Name of the metric being analyzed"}
                        },
                        "required": ["items"]
                    }
                }
            }
        ]

    def _execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute inventory management functions"""

        if function_name == "calculate_eoq":
            return self._calculate_eoq(**arguments)

        elif function_name == "calculate_reorder_point":
            return self._calculate_reorder_point(**arguments)

        elif function_name == "calculate_safety_stock":
            return self._calculate_safety_stock(**arguments)

        elif function_name == "analyze_inventory_turnover":
            return self._analyze_inventory_turnover(**arguments)

        elif function_name == "forecast_demand":
            return self._forecast_demand(**arguments)

        elif function_name == "abc_classification":
            return self._abc_classification(**arguments)

        elif function_name == "pareto_analysis_inventory":
            return self._pareto_analysis_inventory(**arguments)

        else:
            return {"error": f"Unknown function: {function_name}"}

    def _calculate_eoq(self, annual_demand: float, order_cost: float, holding_cost: float) -> Dict[str, Any]:
        """Calculate Economic Order Quantity"""
        try:
            # EOQ = sqrt((2 * D * S) / H)
            # D = annual demand, S = order cost, H = holding cost
            eoq = math.sqrt((2 * annual_demand * order_cost) / holding_cost)

            # Calculate related metrics
            orders_per_year = annual_demand / eoq
            time_between_orders = 365 / orders_per_year
            total_cost = (annual_demand / eoq) * order_cost + (eoq / 2) * holding_cost

            return {
                "eoq": round(eoq, 2),
                "orders_per_year": round(orders_per_year, 2),
                "days_between_orders": round(time_between_orders, 2),
                "total_annual_cost": round(total_cost, 2),
                "average_inventory": round(eoq / 2, 2)
            }
        except Exception as e:
            return {"error": str(e)}

    def _calculate_reorder_point(self, daily_demand: float, lead_time_days: float, safety_stock: float = 0) -> Dict[str, Any]:
        """Calculate reorder point"""
        try:
            # ROP = (Daily Demand * Lead Time) + Safety Stock
            rop = (daily_demand * lead_time_days) + safety_stock

            return {
                "reorder_point": round(rop, 2),
                "lead_time_demand": round(daily_demand * lead_time_days, 2),
                "safety_stock": round(safety_stock, 2),
                "recommendation": f"Place order when inventory reaches {round(rop, 2)} units"
            }
        except Exception as e:
            return {"error": str(e)}

    def _calculate_safety_stock(self, daily_demand: float, demand_std_dev: float,
                                 lead_time_days: float, service_level: float = 0.95) -> Dict[str, Any]:
        """Calculate safety stock for desired service level"""
        try:
            # Z-scores for common service levels
            z_scores = {
                0.90: 1.28,
                0.95: 1.65,
                0.97: 1.88,
                0.99: 2.33,
                0.999: 3.09
            }

            # Get Z-score for service level
            z_score = z_scores.get(service_level, 1.65)  # Default to 95%

            # Safety Stock = Z * σ * sqrt(L)
            # σ = demand standard deviation, L = lead time
            safety_stock = z_score * demand_std_dev * math.sqrt(lead_time_days)

            return {
                "safety_stock": round(safety_stock, 2),
                "service_level": service_level,
                "z_score": z_score,
                "expected_stockout_probability": round(1 - service_level, 4),
                "recommendation": f"Maintain {round(safety_stock, 2)} units as safety stock for {int(service_level * 100)}% service level"
            }
        except Exception as e:
            return {"error": str(e)}

    def _analyze_inventory_turnover(self, cost_of_goods_sold: float, average_inventory_value: float) -> Dict[str, Any]:
        """Analyze inventory turnover rate"""
        try:
            # Inventory Turnover = COGS / Average Inventory
            turnover_rate = cost_of_goods_sold / average_inventory_value
            days_in_inventory = 365 / turnover_rate

            # Determine performance
            if turnover_rate > 12:
                performance = "Excellent - Very fast moving inventory"
            elif turnover_rate > 8:
                performance = "Good - Healthy turnover rate"
            elif turnover_rate > 4:
                performance = "Moderate - Room for improvement"
            else:
                performance = "Low - Potential overstocking issues"

            return {
                "turnover_rate": round(turnover_rate, 2),
                "days_in_inventory": round(days_in_inventory, 2),
                "performance": performance,
                "recommendation": self._get_turnover_recommendation(turnover_rate)
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_turnover_recommendation(self, turnover_rate: float) -> str:
        """Get recommendation based on turnover rate"""
        if turnover_rate > 12:
            return "Continue current practices. Monitor for potential stockouts."
        elif turnover_rate > 8:
            return "Good balance. Consider incremental improvements in forecasting."
        elif turnover_rate > 4:
            return "Review slow-moving items. Consider promotions or reduced order quantities."
        else:
            return "Urgent: Review inventory levels. Implement discounting for slow movers and reduce new orders."

    def _forecast_demand(self, historical_demand: List[float], periods_ahead: int = 1) -> Dict[str, Any]:
        """Simple moving average forecast"""
        try:
            if len(historical_demand) < 3:
                return {"error": "Insufficient historical data (need at least 3 periods)"}

            # Simple moving average (last 3 periods)
            recent_avg = sum(historical_demand[-3:]) / 3

            # Calculate trend
            if len(historical_demand) >= 6:
                first_half_avg = sum(historical_demand[:len(historical_demand)//2]) / (len(historical_demand)//2)
                second_half_avg = sum(historical_demand[len(historical_demand)//2:]) / (len(historical_demand) - len(historical_demand)//2)
                trend = second_half_avg - first_half_avg
            else:
                trend = 0

            # Forecast
            forecasts = []
            for i in range(periods_ahead):
                forecast = recent_avg + (trend * (i + 1))
                forecasts.append(max(0, round(forecast, 2)))  # Ensure non-negative

            return {
                "forecasts": forecasts,
                "method": "Moving Average with Trend",
                "historical_average": round(sum(historical_demand) / len(historical_demand), 2),
                "recent_average": round(recent_avg, 2),
                "trend": round(trend, 2)
            }
        except Exception as e:
            return {"error": str(e)}

    def _abc_classification(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        ABC Classification (Pareto Principle for Inventory).

        A items: Top 20% by value (typically 70-80% of total value)
        B items: Next 30% by value (typically 15-20% of total value)
        C items: Bottom 50% by value (typically 5-10% of total value)
        """
        try:
            if not items:
                return {"error": "No items provided"}

            # Sort by annual value descending
            sorted_items = sorted(items, key=lambda x: x["annual_value"], reverse=True)

            # Calculate total value and cumulative percentages
            total_value = sum(item["annual_value"] for item in sorted_items)
            cumulative = 0
            results = []

            for item in sorted_items:
                value = item["annual_value"]
                percent = (value / total_value) * 100
                cumulative += percent

                # Classify based on cumulative percentage
                if cumulative <= 80:
                    category = "A"
                    priority = "High"
                    control = "Tight inventory controls, frequent monitoring, accurate forecasting"
                elif cumulative <= 95:
                    category = "B"
                    priority = "Medium"
                    control = "Moderate controls, periodic review, standard forecasting"
                else:
                    category = "C"
                    priority = "Low"
                    control = "Basic controls, minimal monitoring, simple reorder systems"

                results.append({
                    "sku": item["sku"],
                    "annual_value": round(value, 2),
                    "percentage_of_total": round(percent, 2),
                    "cumulative_percentage": round(cumulative, 2),
                    "category": category,
                    "priority": priority,
                    "recommended_control": control
                })

            # Summarize by category
            a_items = [r for r in results if r["category"] == "A"]
            b_items = [r for r in results if r["category"] == "B"]
            c_items = [r for r in results if r["category"] == "C"]

            return {
                "classification": results,
                "summary": {
                    "A_items": {
                        "count": len(a_items),
                        "percentage_of_items": round(len(a_items) / len(results) * 100, 1),
                        "value_contribution": round(sum(i["percentage_of_total"] for i in a_items), 1),
                        "management": "Tight controls - Daily/weekly monitoring, accurate forecasts, safety stock"
                    },
                    "B_items": {
                        "count": len(b_items),
                        "percentage_of_items": round(len(b_items) / len(results) * 100, 1),
                        "value_contribution": round(sum(i["percentage_of_total"] for i in b_items), 1),
                        "management": "Moderate controls - Monthly monitoring, standard forecasts"
                    },
                    "C_items": {
                        "count": len(c_items),
                        "percentage_of_items": round(len(c_items) / len(results) * 100, 1),
                        "value_contribution": round(sum(i["percentage_of_total"] for i in c_items), 1),
                        "management": "Basic controls - Quarterly review, simple reorder points"
                    }
                },
                "recommendations": {
                    "A_items": "Focus resources here - 20% of SKUs generating 80% of value",
                    "B_items": "Maintain standard procedures - Moderate attention",
                    "C_items": "Simplify management - Consider bulk orders or vendor-managed inventory"
                }
            }

        except Exception as e:
            return {"error": str(e)}

    def _pareto_analysis_inventory(self, items: List[Dict[str, Any]], metric_name: str = "value") -> Dict[str, Any]:
        """
        Pareto Analysis (80/20 Rule) for inventory.

        Identifies the vital few SKUs that drive the metric (sales, turns, etc.).
        """
        try:
            if not items:
                return {"error": "No items provided"}

            # Sort by metric value descending
            sorted_items = sorted(items, key=lambda x: x["metric_value"], reverse=True)

            # Calculate cumulative percentages
            total = sum(item["metric_value"] for item in sorted_items)
            cumulative = 0
            results = []

            for item in sorted_items:
                value = item["metric_value"]
                percent = (value / total) * 100
                cumulative += percent

                results.append({
                    "sku": item["sku"],
                    "metric_value": round(value, 2),
                    "percentage": round(percent, 2),
                    "cumulative_percentage": round(cumulative, 2),
                    "is_vital_few": cumulative <= 80,
                    "rank": len(results) + 1
                })

            # Split into vital few and trivial many
            vital_few = [r for r in results if r["is_vital_few"]]
            trivial_many = [r for r in results if not r["is_vital_few"]]

            return {
                "metric": metric_name,
                "analysis": results,
                "vital_few": vital_few,
                "trivial_many": trivial_many,
                "summary": {
                    "total_items": len(results),
                    "vital_few_count": len(vital_few),
                    "vital_few_percentage": round((len(vital_few) / len(results)) * 100, 1),
                    "vital_few_contribution": round(sum(v["percentage"] for v in vital_few), 1),
                    "trivial_many_count": len(trivial_many),
                    "trivial_many_percentage": round((len(trivial_many) / len(results)) * 100, 1),
                    "trivial_many_contribution": round(sum(t["percentage"] for t in trivial_many), 1)
                },
                "pareto_principle": f"{len(vital_few)} SKUs ({round((len(vital_few) / len(results)) * 100, 1)}%) generate {round(sum(v['percentage'] for v in vital_few), 1)}% of {metric_name}",
                "recommendation": f"Focus inventory management resources on the top {len(vital_few)} SKUs which drive the majority of {metric_name}"
            }

        except Exception as e:
            return {"error": str(e)}
