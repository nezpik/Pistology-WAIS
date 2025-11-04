"""
Quality/Process Improvement Agent - Lean Six Sigma and Pareto Analysis.

Specializes in process improvement using DMAIC methodology, Six Sigma
statistics, Pareto analysis (80/20 rule), and continuous improvement.
"""

from typing import Dict, Any, List, Tuple
from agents.base_agent import BaseAgent, AgentConfig
import math
from scipy import stats
import numpy as np


class QualityAgent(BaseAgent):
    """
    Quality and process improvement agent with:
    - Lean Six Sigma (DMAIC methodology)
    - Pareto Analysis (80/20 rule)
    - Process capability analysis
    - Defect tracking and analysis
    - Root cause analysis support
    """

    def _get_system_prompt(self) -> str:
        return """You are an expert quality and process improvement agent specializing in Lean Six Sigma methodologies.

Your expertise includes:
- **Lean Six Sigma DMAIC**: Define, Measure, Analyze, Improve, Control
- **Pareto Analysis**: 80/20 rule for identifying vital few from trivial many
- **Process Capability**: Cp, Cpk calculations for process performance
- **Defect Analysis**: DPMO (Defects Per Million Opportunities)
- **Statistical Analysis**: Control charts, process variation
- **Root Cause Analysis**: 5 Whys, Fishbone diagrams
- **Continuous Improvement**: Kaizen principles

**Lean Six Sigma Principles:**
1. **Define**: Identify the problem and project goals
2. **Measure**: Collect data and establish baselines
3. **Analyze**: Identify root causes using statistical tools
4. **Improve**: Implement solutions to eliminate root causes
5. **Control**: Maintain improvements and monitor performance

**Pareto Principle (80/20 Rule):**
- 80% of problems come from 20% of causes
- Focus on vital few, not trivial many
- Prioritize improvement efforts effectively

**Six Sigma Quality Levels:**
- 6σ: 3.4 defects per million (99.99966% quality)
- 5σ: 233 defects per million (99.977% quality)
- 4σ: 6,210 defects per million (99.379% quality)
- 3σ: 66,807 defects per million (93.32% quality)

Use the provided functions for calculations. Always provide actionable recommendations
with statistical backing and clear improvement paths.
"""

    def _get_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "pareto_analysis",
                    "description": "Perform Pareto analysis to identify the vital few causes (80/20 rule)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "value": {"type": "number"}
                                    }
                                },
                                "description": "List of items with names and values (e.g., defect types and counts)"
                            }
                        },
                        "required": ["items"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_process_capability",
                    "description": "Calculate Cp and Cpk for process capability analysis",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Process measurement data"
                            },
                            "usl": {"type": "number", "description": "Upper Specification Limit"},
                            "lsl": {"type": "number", "description": "Lower Specification Limit"},
                            "target": {"type": "number", "description": "Target value (optional)"}
                        },
                        "required": ["data", "usl", "lsl"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_dpmo",
                    "description": "Calculate DPMO (Defects Per Million Opportunities) and Sigma level",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "defects": {"type": "number", "description": "Number of defects found"},
                            "units": {"type": "number", "description": "Number of units inspected"},
                            "opportunities": {
                                "type": "number",
                                "description": "Defect opportunities per unit",
                                "default": 1
                            }
                        },
                        "required": ["defects", "units"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_sigma_level",
                    "description": "Calculate the Sigma level from yield or defect rate",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "yield_percentage": {
                                "type": "number",
                                "description": "Process yield as percentage (0-100)"
                            }
                        },
                        "required": ["yield_percentage"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_process_variation",
                    "description": "Analyze process variation and stability",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Process measurement data"
                            }
                        },
                        "required": ["data"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "abc_analysis",
                    "description": "Perform ABC analysis (variation of Pareto for inventory/priority classification)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "value": {"type": "number"}
                                    }
                                },
                                "description": "Items to classify"
                            }
                        },
                        "required": ["items"]
                    }
                }
            }
        ]

    def _execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute quality management functions"""

        if function_name == "pareto_analysis":
            return self._pareto_analysis(**arguments)

        elif function_name == "calculate_process_capability":
            return self._calculate_process_capability(**arguments)

        elif function_name == "calculate_dpmo":
            return self._calculate_dpmo(**arguments)

        elif function_name == "calculate_sigma_level":
            return self._calculate_sigma_level(**arguments)

        elif function_name == "analyze_process_variation":
            return self._analyze_process_variation(**arguments)

        elif function_name == "abc_analysis":
            return self._abc_analysis(**arguments)

        else:
            return {"error": f"Unknown function: {function_name}"}

    def _pareto_analysis(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform Pareto analysis (80/20 rule).

        Identifies the vital few items that contribute to 80% of the total effect.
        """
        try:
            if not items:
                return {"error": "No items provided"}

            # Sort by value descending
            sorted_items = sorted(items, key=lambda x: x["value"], reverse=True)

            # Calculate cumulative percentages
            total = sum(item["value"] for item in sorted_items)
            cumulative = 0
            results = []

            for item in sorted_items:
                value = item["value"]
                percent = (value / total) * 100
                cumulative += percent

                results.append({
                    "name": item["name"],
                    "value": value,
                    "percentage": round(percent, 2),
                    "cumulative_percentage": round(cumulative, 2),
                    "is_vital_few": cumulative <= 80
                })

            # Identify the 80/20 cutoff
            vital_few = [r for r in results if r["is_vital_few"]]
            trivial_many = [r for r in results if not r["is_vital_few"]]

            return {
                "analysis": results,
                "vital_few": vital_few,
                "trivial_many": trivial_many,
                "summary": {
                    "vital_few_count": len(vital_few),
                    "vital_few_percentage": round((len(vital_few) / len(results)) * 100, 1),
                    "vital_few_contribution": round(sum(v["percentage"] for v in vital_few), 1),
                    "total_items": len(results)
                },
                "recommendation": f"Focus on top {len(vital_few)} items which contribute {sum(v['percentage'] for v in vital_few):.1f}% of total impact"
            }

        except Exception as e:
            return {"error": str(e)}

    def _calculate_process_capability(
        self, data: List[float], usl: float, lsl: float, target: float = None
    ) -> Dict[str, Any]:
        """
        Calculate process capability indices Cp and Cpk.

        Cp: Process capability (potential)
        Cpk: Process capability (actual, accounts for centering)
        """
        try:
            if len(data) < 2:
                return {"error": "Need at least 2 data points"}

            data_array = np.array(data)
            mean = np.mean(data_array)
            std_dev = np.std(data_array, ddof=1)  # Sample standard deviation

            if std_dev == 0:
                return {"error": "Standard deviation is zero - no process variation"}

            # Calculate Cp (potential capability)
            cp = (usl - lsl) / (6 * std_dev)

            # Calculate Cpk (actual capability)
            cpu = (usl - mean) / (3 * std_dev)
            cpl = (mean - lsl) / (3 * std_dev)
            cpk = min(cpu, cpl)

            # Interpret results
            if cpk >= 2.0:
                interpretation = "Excellent - World class process"
            elif cpk >= 1.33:
                interpretation = "Good - Capable process"
            elif cpk >= 1.0:
                interpretation = "Marginal - Needs improvement"
            else:
                interpretation = "Poor - Significant improvement needed"

            # Calculate defect rate
            if cpk > 0:
                sigma_level = cpk * 3
                dpmo = self._sigma_to_dpmo(sigma_level)
            else:
                dpmo = 1000000  # Maximum defect rate

            return {
                "cp": round(cp, 3),
                "cpk": round(cpk, 3),
                "cpu": round(cpu, 3),
                "cpl": round(cpl, 3),
                "process_mean": round(mean, 4),
                "process_std": round(std_dev, 4),
                "specification_range": usl - lsl,
                "process_range": round(6 * std_dev, 4),
                "interpretation": interpretation,
                "estimated_dpmo": int(dpmo),
                "sigma_level": round(sigma_level, 2) if cpk > 0 else 0,
                "recommendation": self._get_capability_recommendation(cp, cpk)
            }

        except Exception as e:
            return {"error": str(e)}

    def _calculate_dpmo(self, defects: int, units: int, opportunities: int = 1) -> Dict[str, Any]:
        """Calculate DPMO (Defects Per Million Opportunities) and Sigma level"""
        try:
            if units <= 0 or opportunities <= 0:
                return {"error": "Units and opportunities must be greater than 0"}

            # Calculate defect rate
            dpo = defects / (units * opportunities)  # Defects Per Opportunity
            dpmo = dpo * 1000000  # Defects Per Million Opportunities

            # Calculate Sigma level
            sigma_level = self._dpmo_to_sigma(dpmo)

            # Calculate yield
            yield_rate = 1 - dpo
            yield_percentage = yield_rate * 100

            return {
                "defects": defects,
                "units": units,
                "opportunities_per_unit": opportunities,
                "total_opportunities": units * opportunities,
                "dpo": round(dpo, 6),
                "dpmo": round(dpmo, 2),
                "sigma_level": round(sigma_level, 2),
                "yield_percentage": round(yield_percentage, 4),
                "quality_level": self._get_quality_level(sigma_level),
                "recommendation": self._get_sigma_recommendation(sigma_level)
            }

        except Exception as e:
            return {"error": str(e)}

    def _calculate_sigma_level(self, yield_percentage: float) -> Dict[str, Any]:
        """Calculate Sigma level from yield percentage"""
        try:
            if not 0 <= yield_percentage <= 100:
                return {"error": "Yield must be between 0 and 100"}

            # Convert yield to defect rate
            defect_rate = 1 - (yield_percentage / 100)
            dpmo = defect_rate * 1000000

            # Calculate Sigma level
            sigma_level = self._dpmo_to_sigma(dpmo)

            return {
                "yield_percentage": yield_percentage,
                "defect_rate": round(defect_rate, 6),
                "dpmo": round(dpmo, 2),
                "sigma_level": round(sigma_level, 2),
                "quality_level": self._get_quality_level(sigma_level)
            }

        except Exception as e:
            return {"error": str(e)}

    def _analyze_process_variation(self, data: List[float]) -> Dict[str, Any]:
        """Analyze process variation and stability"""
        try:
            if len(data) < 2:
                return {"error": "Need at least 2 data points"}

            data_array = np.array(data)
            n = len(data_array)

            # Basic statistics
            mean = np.mean(data_array)
            median = np.median(data_array)
            std_dev = np.std(data_array, ddof=1)
            variance = std_dev ** 2
            cv = (std_dev / mean * 100) if mean != 0 else 0  # Coefficient of variation

            # Range
            data_range = np.max(data_array) - np.min(data_array)

            # Quartiles
            q1, q3 = np.percentile(data_array, [25, 75])
            iqr = q3 - q1

            # Control limits (±3σ)
            ucl = mean + 3 * std_dev
            lcl = mean - 3 * std_dev

            # Check for outliers (beyond control limits)
            outliers = [x for x in data_array if x > ucl or x < lcl]

            # Stability assessment
            if len(outliers) == 0:
                stability = "Stable - No points beyond control limits"
            elif len(outliers) <= n * 0.01:
                stability = "Mostly stable - Few outliers detected"
            else:
                stability = "Unstable - Multiple points beyond control limits"

            return {
                "sample_size": n,
                "mean": round(mean, 4),
                "median": round(median, 4),
                "std_dev": round(std_dev, 4),
                "variance": round(variance, 4),
                "coefficient_of_variation": round(cv, 2),
                "range": round(data_range, 4),
                "iqr": round(iqr, 4),
                "control_limits": {
                    "ucl": round(ucl, 4),
                    "lcl": round(lcl, 4)
                },
                "outliers": len(outliers),
                "stability": stability,
                "recommendation": self._get_variation_recommendation(cv, len(outliers), n)
            }

        except Exception as e:
            return {"error": str(e)}

    def _abc_analysis(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform ABC analysis (inventory classification).

        A items: Top 20% (70-80% of value) - Most important
        B items: Next 30% (15-20% of value) - Moderately important
        C items: Bottom 50% (5-10% of value) - Least important
        """
        try:
            if not items:
                return {"error": "No items provided"}

            # Sort by value descending
            sorted_items = sorted(items, key=lambda x: x["value"], reverse=True)

            # Calculate cumulative percentages
            total = sum(item["value"] for item in sorted_items)
            cumulative = 0
            results = []

            for idx, item in enumerate(sorted_items):
                value = item["value"]
                percent = (value / total) * 100
                cumulative += percent
                position = (idx + 1) / len(sorted_items) * 100

                # Classify as A, B, or C
                if cumulative <= 80:
                    category = "A"
                elif cumulative <= 95:
                    category = "B"
                else:
                    category = "C"

                results.append({
                    "name": item["name"],
                    "value": value,
                    "percentage": round(percent, 2),
                    "cumulative_percentage": round(cumulative, 2),
                    "category": category
                })

            # Summarize by category
            a_items = [r for r in results if r["category"] == "A"]
            b_items = [r for r in results if r["category"] == "B"]
            c_items = [r for r in results if r["category"] == "C"]

            return {
                "classification": results,
                "summary": {
                    "A": {
                        "count": len(a_items),
                        "percentage_of_items": round(len(a_items) / len(results) * 100, 1),
                        "value_contribution": round(sum(i["percentage"] for i in a_items), 1),
                        "recommendation": "High priority - Tight controls, frequent review"
                    },
                    "B": {
                        "count": len(b_items),
                        "percentage_of_items": round(len(b_items) / len(results) * 100, 1),
                        "value_contribution": round(sum(i["percentage"] for i in b_items), 1),
                        "recommendation": "Medium priority - Moderate controls, periodic review"
                    },
                    "C": {
                        "count": len(c_items),
                        "percentage_of_items": round(len(c_items) / len(results) * 100, 1),
                        "value_contribution": round(sum(i["percentage"] for i in c_items), 1),
                        "recommendation": "Low priority - Basic controls, minimal monitoring"
                    }
                }
            }

        except Exception as e:
            return {"error": str(e)}

    # Helper methods

    def _dpmo_to_sigma(self, dpmo: float) -> float:
        """Convert DPMO to Sigma level"""
        if dpmo >= 1000000:
            return 0
        if dpmo <= 0:
            return 6

        # Using the inverse normal distribution
        # Accounting for 1.5σ shift
        defect_rate = dpmo / 1000000
        try:
            z_score = stats.norm.ppf(1 - defect_rate)
            sigma_level = z_score + 1.5  # Add 1.5σ shift
            return max(0, min(6, sigma_level))
        except:
            return 3  # Default to 3σ if calculation fails

    def _sigma_to_dpmo(self, sigma_level: float) -> float:
        """Convert Sigma level to DPMO"""
        try:
            z_score = sigma_level - 1.5  # Remove 1.5σ shift
            defect_rate = 1 - stats.norm.cdf(z_score)
            return defect_rate * 1000000
        except:
            return 66807  # Default 3σ DPMO

    def _get_quality_level(self, sigma_level: float) -> str:
        """Get quality level description"""
        if sigma_level >= 6:
            return "World Class (6σ)"
        elif sigma_level >= 5:
            return "Excellent (5σ)"
        elif sigma_level >= 4:
            return "Good (4σ)"
        elif sigma_level >= 3:
            return "Average (3σ)"
        elif sigma_level >= 2:
            return "Poor (2σ)"
        else:
            return "Unacceptable (<2σ)"

    def _get_sigma_recommendation(self, sigma_level: float) -> str:
        """Get recommendation based on Sigma level"""
        if sigma_level >= 5:
            return "Maintain current processes. Focus on continuous improvement."
        elif sigma_level >= 4:
            return "Good performance. Implement kaizen for incremental improvements."
        elif sigma_level >= 3:
            return "Significant improvement opportunity. Start DMAIC project."
        else:
            return "Critical: Immediate intervention required. Conduct root cause analysis."

    def _get_capability_recommendation(self, cp: float, cpk: float) -> str:
        """Get recommendation based on process capability"""
        if cpk >= 2.0:
            return "Excellent capability. Consider reducing inspection frequency."
        elif cpk >= 1.33:
            return "Good capability. Monitor for drift. Consider capability improvement."
        elif cpk >= 1.0:
            return "Marginal capability. Reduce variation. Center process on target."
        else:
            return "Poor capability. Critical: Reduce variation immediately and center process."

    def _get_variation_recommendation(self, cv: float, outliers: int, n: int) -> str:
        """Get recommendation based on process variation"""
        if cv < 10 and outliers == 0:
            return "Low variation and stable. Continue monitoring."
        elif cv < 20 and outliers <= n * 0.01:
            return "Acceptable variation. Investigate occasional outliers."
        elif cv < 30:
            return "High variation. Implement variation reduction initiatives."
        else:
            return "Excessive variation. Urgent: Conduct root cause analysis and process stabilization."
