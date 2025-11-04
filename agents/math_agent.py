"""
Math Agent - OpenAI-powered mathematical analysis with SymPy integration.

Specializes in complex calculations, optimization, and statistical analysis.
"""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent, AgentConfig
import sympy
from sympy import symbols, solve, simplify, integrate, diff
import math


class MathAgent(BaseAgent):
    """Mathematical agent with SymPy for symbolic computation"""

    def __init__(self, config: AgentConfig, api_key: str):
        super().__init__(config, api_key)
        # Initialize common symbolic variables
        self.x, self.y, self.z = symbols('x y z')

    def _get_system_prompt(self) -> str:
        return """You are an expert mathematical analysis agent for warehouse operations.

Your capabilities:
- Complex mathematical calculations
- Statistical analysis
- Optimization problems (linear, nonlinear)
- Symbolic mathematics
- Warehouse metrics (EOQ, ROP, safety stock)
- Calculus (derivatives, integrals)
- Algorithm complexity analysis

When solving problems:
1. Break down complex problems into steps
2. Show your work and reasoning
3. Verify calculations when possible
4. Provide practical interpretations
5. Use appropriate precision (2-4 decimal places)

Use the provided functions for calculations. Always explain the mathematical reasoning."""

    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "solve_equation",
                    "description": "Solve algebraic equations using SymPy",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "equation": {"type": "string", "description": "Equation to solve (e.g., 'x**2 - 4 = 0')"},
                            "variable": {"type": "string", "description": "Variable to solve for", "default": "x"}
                        },
                        "required": ["equation"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_derivative",
                    "description": "Calculate derivative of a function",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string", "description": "Mathematical expression"},
                            "variable": {"type": "string", "description": "Variable for differentiation", "default": "x"}
                        },
                        "required": ["expression"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_integral",
                    "description": "Calculate definite or indefinite integral",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string", "description": "Expression to integrate"},
                            "variable": {"type": "string", "description": "Integration variable", "default": "x"},
                            "lower_limit": {"type": "number", "description": "Lower limit (optional)"},
                            "upper_limit": {"type": "number", "description": "Upper limit (optional)"}
                        },
                        "required": ["expression"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "optimize_linear",
                    "description": "Solve linear optimization problems",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "objective": {"type": "string", "description": "Objective function to optimize"},
                            "constraints": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of constraint equations"
                            }
                        },
                        "required": ["objective"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_statistics",
                    "description": "Calculate statistical measures",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Array of numerical data"
                            },
                            "measures": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Statistical measures to calculate",
                                "default": ["mean", "median", "std"]
                            }
                        },
                        "required": ["data"]
                    }
                }
            }
        ]

    def _execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute mathematical functions"""

        if function_name == "solve_equation":
            try:
                equation_str = arguments["equation"]
                var = arguments.get("variable", "x")

                # Parse equation
                var_symbol = symbols(var)
                # Handle equations with '=' sign
                if '=' in equation_str:
                    left, right = equation_str.split('=')
                    equation = sympy.sympify(left) - sympy.sympify(right)
                else:
                    equation = sympy.sympify(equation_str)

                # Solve
                solutions = solve(equation, var_symbol)

                return {
                    "solutions": [str(sol) for sol in solutions],
                    "numerical_solutions": [float(sol.evalf()) if sol.is_real else str(sol) for sol in solutions],
                    "equation": equation_str,
                    "variable": var
                }
            except Exception as e:
                return {"error": str(e)}

        elif function_name == "calculate_derivative":
            try:
                expr_str = arguments["expression"]
                var = arguments.get("variable", "x")

                var_symbol = symbols(var)
                expr = sympy.sympify(expr_str)
                derivative = diff(expr, var_symbol)

                return {
                    "derivative": str(derivative),
                    "simplified": str(simplify(derivative)),
                    "original_expression": expr_str
                }
            except Exception as e:
                return {"error": str(e)}

        elif function_name == "calculate_integral":
            try:
                expr_str = arguments["expression"]
                var = arguments.get("variable", "x")
                lower = arguments.get("lower_limit")
                upper = arguments.get("upper_limit")

                var_symbol = symbols(var)
                expr = sympy.sympify(expr_str)

                if lower is not None and upper is not None:
                    # Definite integral
                    result = integrate(expr, (var_symbol, lower, upper))
                    return {
                        "result": str(result),
                        "numerical_value": float(result.evalf()),
                        "type": "definite",
                        "limits": [lower, upper]
                    }
                else:
                    # Indefinite integral
                    result = integrate(expr, var_symbol)
                    return {
                        "result": str(result) + " + C",
                        "type": "indefinite"
                    }
            except Exception as e:
                return {"error": str(e)}

        elif function_name == "optimize_linear":
            return {
                "message": "Linear optimization requires scipy.optimize. This is a placeholder.",
                "suggestion": "Use inventory EOQ functions for warehouse optimization"
            }

        elif function_name == "calculate_statistics":
            try:
                data = arguments["data"]
                measures = arguments.get("measures", ["mean", "median", "std"])

                results = {}

                if "mean" in measures:
                    results["mean"] = round(sum(data) / len(data), 4)

                if "median" in measures:
                    sorted_data = sorted(data)
                    n = len(sorted_data)
                    if n % 2 == 0:
                        results["median"] = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
                    else:
                        results["median"] = sorted_data[n//2]

                if "std" in measures or "variance" in measures:
                    mean = sum(data) / len(data)
                    variance = sum((x - mean) ** 2 for x in data) / len(data)
                    results["variance"] = round(variance, 4)
                    results["std"] = round(math.sqrt(variance), 4)

                if "min" in measures:
                    results["min"] = min(data)

                if "max" in measures:
                    results["max"] = max(data)

                results["count"] = len(data)

                return results
            except Exception as e:
                return {"error": str(e)}

        else:
            return {"error": f"Unknown function: {function_name}"}
