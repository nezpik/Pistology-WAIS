from typing import Dict, Any, List, Optional, Union
import logging
import re
import sympy
from .base_agent import BaseAgent
from config import DEEPSEEK_API_KEY

class MathAgent(BaseAgent):
    def __init__(self):
        super().__init__("Math")
        self.api_key = DEEPSEEK_API_KEY
        self.logger = logging.getLogger(__name__)
        # Initialize SymPy for symbolic mathematics
        self.symbolic_vars = {}
        
    def process(self, input_data: str, context: Dict[str, Any] = None) -> str:
        """Process mathematical calculations and optimization tasks"""
        try:
            context = context or {}
            task = context.get("task", "solve")
            
            if task == "solve":
                return self._solve_problem(input_data, context)
            elif task == "process_query":
                # Handle math-specific query
                prompt = f"""As a Warehouse Math Analysis Agent, provide a detailed response to this query:

Query: {input_data}

Consider:
1. Numerical calculations
2. Statistical analysis
3. Optimization problems
4. Performance metrics
5. Efficiency calculations
6. Resource utilization

Provide specific calculations and mathematical insights."""
                
                response = self.model.generate_content(prompt)
                return response.text
            elif task == "verify":
                solution = context.get("solution", "")
                return self._verify_solution(solution, {"original_problem": input_data})
            elif task == "optimize":
                return self._optimize_algorithm(input_data, context)
            else:
                return self._solve_problem(input_data, context)
                
        except Exception as e:
            self.logger.error(f"Error in mathematical processing: {str(e)}")
            return f"Error processing mathematical request: {str(e)}"
            
    def verify_solution(self, problem: str, solution: str) -> str:
        """Public method to verify a solution"""
        try:
            return self._verify_solution(solution, {"original_problem": problem})
        except Exception as e:
            self.logger.error(f"Error verifying solution: {str(e)}")
            return f"Error verifying solution: {str(e)}"
            
    def _solve_problem(self, problem: str, context: Dict[str, Any]) -> str:
        """Solve a mathematical problem using step-by-step reasoning"""
        try:
            self.logger.info(f"Math Agent received problem: {problem}")
            
            # Check for warehouse-specific calculations
            if any(term in problem.lower() for term in ['takt', 'lead time', 'cycle time']):
                return self._calculate_warehouse_metrics(problem)
            
            # Extract numbers and operators from the query
            expression = ''.join(c for c in problem if c.isdigit() or c in '+-*/.() ')
            expression = expression.strip()
            self.logger.info(f"Extracted expression: {expression}")
            
            # Check for basic arithmetic
            if expression and all(c in "0123456789+-*/(). " for c in expression):
                self.logger.info("Detected basic arithmetic expression")
                try:
                    result = eval(expression.replace("^", "**"))
                    self.logger.info(f"Arithmetic result: {result}")
                    return f"The result of {expression} is {result}"
                except Exception as e:
                    self.logger.error(f"Error evaluating arithmetic: {str(e)}")
                    pass  # Fall back to SymPy if eval fails
            
            # Check for inventory optimization
            if "inventory" in problem.lower() and "demand" in problem.lower():
                return self._calculate_inventory_levels(problem)
                
            # Check for definite integral
            if "integral" in problem.lower() or "integrate" in problem.lower():
                return self._handle_definite_integral(problem)
                
            # Extract variables and their domains
            variables = self._extract_variables(problem)
            
            # Convert problem to SymPy expression
            expr = self._to_sympy_expr(problem)
            if expr is None:
                return "Could not parse the mathematical expression. Please check the syntax."
            
            # Generate solution steps
            solution_steps = []
            
            # Step 1: Problem Analysis
            solution_steps.append("Step 1: Problem Analysis")
            solution_steps.append(f"Expression: {expr}")
            solution_steps.append(f"Variables: {', '.join(str(v) for v in variables)}")
            
            # Step 2: Solution Strategy
            solution_steps.append("\nStep 2: Solution Strategy")
            
            # Handle equations (containing =)
            if isinstance(expr, sympy.Equality):
                solution_steps.append("Detected equation")
                # Move everything to left side
                expr = expr.lhs - expr.rhs
                solution_steps.append(f"Standard form: {expr} = 0")
            
            try:
                if expr.is_polynomial():
                    solution_steps.append("Using polynomial solving techniques")
                    result = sympy.solve(expr)
                    solution_steps.append(f"Solution: {result}")
                elif expr.has(sympy.Integral):
                    solution_steps.append("Using integration techniques")
                    result = sympy.integrate(expr)
                    solution_steps.append(f"Solution: {result}")
                elif expr.has(sympy.Derivative):
                    solution_steps.append("Using differentiation techniques")
                    result = sympy.diff(expr)
                    solution_steps.append(f"Solution: {result}")
                else:
                    solution_steps.append("Using algebraic simplification")
                    result = sympy.simplify(expr)
                    solution_steps.append(f"Solution: {result}")
            except AttributeError:
                # If expression type checking fails, try general solving
                solution_steps.append("Using general solving techniques")
                try:
                    result = sympy.solve(expr)
                    solution_steps.append(f"Solution: {result}")
                except Exception as e:
                    solution_steps.append(f"Could not solve: {str(e)}")
                    result = sympy.simplify(expr)
                    solution_steps.append(f"Simplified form: {result}")
                
            # Step 3: Verification
            solution_steps.append("\nStep 3: Verification")
            try:
                # Substitute solution back into original expression
                verification = self._verify_result(expr, result)
                solution_steps.append(f"Verification: {verification}")
            except Exception as e:
                solution_steps.append(f"Could not verify: {str(e)}")
                
            return "\n".join(solution_steps)
            
        except Exception as e:
            self.logger.error(f"Error solving problem: {str(e)}")
            return f"Error solving mathematical problem: {str(e)}"
            
    def _handle_definite_integral(self, problem: str) -> str:
        """Handle definite integral problems"""
        try:
            # Extract the expression and limits
            import re
            
            # Extract numbers from text
            numbers = re.findall(r'-?\d+\.?\d*', problem)
            if len(numbers) >= 2:
                lower_limit = float(numbers[0])
                upper_limit = float(numbers[1])
            else:
                return "Could not find integration limits. Please specify both lower and upper limits."
                
            # Extract the expression to integrate
            expr_match = re.search(r'integral of (.*?) from', problem.lower())
            if not expr_match:
                expr_match = re.search(r'integrate (.*?) from', problem.lower())
            if not expr_match:
                return "Could not find expression to integrate. Please specify the expression clearly."
                
            expr_text = expr_match.group(1).strip()
            
            # Convert expression to SymPy
            x = sympy.Symbol('x')
            try:
                expr = self._to_sympy_expr(expr_text)
                if expr is None:
                    return "Could not parse the expression to integrate. Please check the syntax."
                    
                # Calculate the definite integral
                result = sympy.integrate(expr, (x, lower_limit, upper_limit))
                
                # Generate solution steps
                solution_steps = [
                    "Step 1: Problem Analysis",
                    f"Expression to integrate: {expr}",
                    f"Lower limit: {lower_limit}",
                    f"Upper limit: {upper_limit}",
                    "",
                    "Step 2: Integration",
                    f"Indefinite integral: {sympy.integrate(expr, x)}",
                    "",
                    "Step 3: Evaluate at Limits",
                    f"Result: {result}"
                ]
                
                return "\n".join(solution_steps)
                
            except Exception as e:
                return f"Error computing integral: {str(e)}"
                
        except Exception as e:
            self.logger.error(f"Error handling definite integral: {str(e)}")
            return f"Error processing definite integral: {str(e)}"
            
    def _calculate_inventory_levels(self, problem: str) -> str:
        """Calculate optimal inventory levels based on demand and lead time"""
        try:
            # Extract demand rate and lead time using regex
            import re
            
            # Extract demand rate
            demand_match = re.search(r'demand (?:rate of )?(\d+(?:\.\d+)?)', problem.lower())
            if not demand_match:
                return "Could not find demand rate. Please specify it clearly (e.g., 'demand rate of 100 units/day')."
            demand_rate = float(demand_match.group(1))
            
            # Extract lead time
            lead_match = re.search(r'lead time (?:of )?(\d+(?:\.\d+)?)', problem.lower())
            if not lead_match:
                return "Could not find lead time. Please specify it clearly (e.g., 'lead time of 3 days')."
            lead_time = float(lead_match.group(1))
            
            # Calculate key inventory metrics
            
            # 1. Safety Stock (SS) = Z * σ * √L
            # Using Z = 1.96 for 95% service level
            # Assuming standard deviation is 20% of demand
            z_score = 1.96
            demand_std = 0.2 * demand_rate
            safety_stock = z_score * demand_std * (lead_time ** 0.5)
            
            # 2. Reorder Point (ROP) = D * L + SS
            # where D is daily demand, L is lead time
            reorder_point = (demand_rate * lead_time) + safety_stock
            
            # 3. Economic Order Quantity (EOQ)
            # EOQ = √((2 * D * S) / H)
            # Assuming:
            # S (ordering cost) = $100 per order
            # H (holding cost) = 20% of unit cost per year
            # Unit cost = $50
            ordering_cost = 100
            unit_cost = 50
            holding_cost = 0.2 * unit_cost
            eoq = ((2 * demand_rate * 365 * ordering_cost) / holding_cost) ** 0.5
            
            # 4. Average Inventory Level
            average_inventory = (eoq / 2) + safety_stock
            
            # Generate solution steps
            solution_steps = [
                "Step 1: Input Analysis",
                f"• Demand Rate: {demand_rate} units/day",
                f"• Lead Time: {lead_time} days",
                "",
                "Step 2: Safety Stock Calculation",
                f"• Service Level: 95% (Z = 1.96)",
                f"• Demand Standard Deviation: {demand_std:.2f} units",
                f"• Safety Stock: {safety_stock:.2f} units",
                "",
                "Step 3: Reorder Point Calculation",
                f"• Lead Time Demand: {demand_rate * lead_time:.2f} units",
                f"• Reorder Point: {reorder_point:.2f} units",
                "",
                "Step 4: Economic Order Quantity (EOQ)",
                f"• Annual Demand: {demand_rate * 365:.2f} units",
                f"• Ordering Cost: ${ordering_cost} per order",
                f"• Holding Cost: ${holding_cost:.2f} per unit per year",
                f"• EOQ: {eoq:.2f} units",
                "",
                "Step 5: Average Inventory Level",
                f"• Cycle Stock: {eoq / 2:.2f} units",
                f"• Safety Stock: {safety_stock:.2f} units",
                f"• Average Inventory: {average_inventory:.2f} units",
                "",
                "Summary:",
                f"• Order {eoq:.0f} units when inventory level reaches {reorder_point:.0f} units",
                f"• Maintain safety stock of {safety_stock:.0f} units",
                f"• Average inventory level will be {average_inventory:.0f} units"
            ]
            
            return "\n".join(solution_steps)
            
        except Exception as e:
            self.logger.error(f"Error calculating inventory levels: {str(e)}")
            return f"Error calculating optimal inventory levels: {str(e)}"
            
    def _verify_solution(self, solution: str, context: Dict[str, Any]) -> str:
        """Verify a mathematical solution using formal methods"""
        try:
            original_problem = context.get("original_problem", "")
            
            # Extract original expression
            orig_expr = self._to_sympy_expr(original_problem)
            
            # Extract solution steps
            steps = [s for s in solution.split("\n") if s.strip()]
            
            verification_results = []
            prev_result = None
            
            for i, step in enumerate(steps):
                try:
                    # Skip non-mathematical lines
                    if not any(c.isdigit() or c in "+-*/=(){}[]" for c in step):
                        continue
                        
                    # Extract expression from step
                    step_expr = self._to_sympy_expr(step)
                    
                    # Verify mathematical properties
                    verification_results.append(f"Step {i+1} verification:")
                    
                    # Check if expression is well-formed
                    if step_expr is None:
                        verification_results.append("  - Invalid mathematical expression")
                        continue
                        
                    # Check consistency with previous step
                    if prev_result is not None:
                        try:
                            if not sympy.simplify(step_expr - prev_result).is_zero:
                                verification_results.append("  - Step is consistent with previous result")
                            else:
                                verification_results.append("  - Warning: Step may be inconsistent with previous result")
                        except Exception:
                            verification_results.append("  - Could not verify consistency with previous step")
                            
                    # Check if step maintains solution properties
                    try:
                        if sympy.solve(step_expr) == sympy.solve(orig_expr):
                            verification_results.append("  - Step maintains solution properties")
                        else:
                            verification_results.append("  - Warning: Step may alter solution")
                    except Exception:
                        verification_results.append("  - Could not verify solution properties")
                        
                    prev_result = step_expr
                        
                except Exception as e:
                    verification_results.append(f"  - Error verifying step: {str(e)}")
                    
            return "\n".join(verification_results)
            
        except Exception as e:
            self.logger.error(f"Error verifying solution: {str(e)}")
            return f"Error in verification: {str(e)}"
            
    def _extract_variables(self, text: str) -> List[sympy.Symbol]:
        """Extract variables from a mathematical expression"""
        try:
            # Find all variable names using regex
            var_names = set(re.findall(r'[a-zA-Z][a-zA-Z0-9]*', text))
            
            # Convert to SymPy symbols
            return [sympy.Symbol(name) for name in var_names]
        except Exception as e:
            self.logger.error(f"Error extracting variables: {str(e)}")
            return []
            
    def _to_sympy_expr(self, text: str) -> Optional[sympy.Expr]:
        """Convert text to SymPy expression"""
        try:
            # Clean up the text
            math_text = text.strip()
            
            # Handle equations
            if "=" in math_text:
                left, right = math_text.split("=", 1)
                try:
                    left_expr = sympy.sympify(left.strip())
                    right_expr = sympy.sympify(right.strip())
                    return sympy.Eq(left_expr, right_expr)
                except Exception:
                    return None
            
            # Handle other expressions
            try:
                # Replace common mathematical functions
                math_text = math_text.replace("^", "**")  # Power
                math_text = math_text.replace("sin", "sympy.sin")  # Sine
                math_text = math_text.replace("cos", "sympy.cos")  # Cosine
                math_text = math_text.replace("tan", "sympy.tan")  # Tangent
                math_text = math_text.replace("exp", "sympy.exp")  # Exponential
                math_text = math_text.replace("log", "sympy.log")  # Logarithm
                math_text = math_text.replace("sqrt", "sympy.sqrt")  # Square root
                
                # Parse expression
                return sympy.sympify(math_text)
            except Exception:
                return None
                
        except Exception as e:
            self.logger.error(f"Error converting to SymPy: {str(e)}")
            return None
            
    def _verify_result(self, expr: sympy.Expr, result: Any) -> str:
        """Verify a result against the original expression"""
        try:
            # Get variables
            variables = list(expr.free_symbols)
            
            # Try substituting result back
            if isinstance(result, (list, tuple)):
                verifications = []
                for r in result:
                    try:
                        # Create substitution dict
                        subs = {var: r for var in variables}
                        # Verify
                        if sympy.simplify(expr.subs(subs)).is_zero:
                            verifications.append(f"Verified for {r}")
                        else:
                            verifications.append(f"Failed verification for {r}")
                    except Exception as e:
                        verifications.append(f"Could not verify {r}: {str(e)}")
                return "\n".join(verifications)
            else:
                # Single result
                subs = {var: result for var in variables}
                if sympy.simplify(expr.subs(subs)).is_zero:
                    return "Solution verified"
                else:
                    return "Solution failed verification"
                    
        except Exception as e:
            return f"Error in verification: {str(e)}"
            
    def _calculate_warehouse_metrics(self, problem: str) -> str:
        """Calculate warehouse-specific metrics like takt time and lead time"""
        try:
            # Extract numbers using regex
            numbers = [float(n) for n in re.findall(r'-?\d+\.?\d*', problem)]
            
            if 'takt' in problem.lower():
                if len(numbers) >= 2:
                    available_time = numbers[0]  # Usually in minutes or hours
                    customer_demand = numbers[1]  # Units demanded
                    takt_time = available_time / customer_demand
                    return f"""
Takt Time Calculation:
- Available Production Time: {available_time} minutes
- Customer Demand: {customer_demand} units
- Takt Time = {takt_time:.2f} minutes per unit

This means you need to complete one unit every {takt_time:.2f} minutes to meet customer demand.
"""
                else:
                    return "Please provide both available production time and customer demand for takt time calculation."
            
            elif 'lead time' in problem.lower():
                if len(numbers) >= 3:
                    processing_time = numbers[0]
                    queue_time = numbers[1]
                    transport_time = numbers[2]
                    total_lead_time = processing_time + queue_time + transport_time
                    return f"""
Lead Time Calculation:
- Processing Time: {processing_time} minutes
- Queue Time: {queue_time} minutes
- Transport Time: {transport_time} minutes
- Total Lead Time = {total_lead_time} minutes

Breakdown:
- Processing: {(processing_time/total_lead_time)*100:.1f}%
- Queue: {(queue_time/total_lead_time)*100:.1f}%
- Transport: {(transport_time/total_lead_time)*100:.1f}%
"""
                else:
                    return "Please provide processing time, queue time, and transport time for lead time calculation."
            
            return "Please specify if you want to calculate takt time or lead time, along with the required values."
            
        except Exception as e:
            self.logger.error(f"Error calculating warehouse metrics: {str(e)}")
            return f"Error in warehouse calculations: {str(e)}"
            
    def get_status(self) -> str:
        """Get the current status of the agent"""
        return "Ready"
