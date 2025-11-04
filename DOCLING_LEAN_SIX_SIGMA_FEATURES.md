# 📊 Docling, Lean Six Sigma & Pareto Features

**Version:** 2.1.0
**Date:** January 2025

---

## 🎯 Overview

This update adds three major capabilities to Pistology-WAIS:

1. **Docling Document Processing** - Advanced document parsing and context integration
2. **Lean Six Sigma Tools** - DMAIC methodology and process improvement
3. **Pareto Analysis** - 80/20 rule for inventory and process optimization

---

## 📄 1. Docling Document Processing

### Features

**IBM Docling Integration** with fallback support for compatibility.

#### Supported Formats:
- ✅ PDF documents (with OCR)
- ✅ Word documents (.docx)
- ✅ Excel spreadsheets (.xlsx)
- ✅ PowerPoint presentations (.pptx)
- ✅ Images (with OCR)
- ✅ HTML and Markdown
- ✅ Text and CSV files

#### Capabilities:
- **Table Extraction** - Automatically extracts tables from documents
- **OCR** - Optical Character Recognition for scanned documents
- **Metadata Extraction** - File info, page counts, timestamps
- **Context Integration** - Documents added to agent conversation context
- **Search** - Full-text search across all processed documents
- **Fallback Processing** - Uses LangChain when Docling unavailable

### Usage

```python
from agents.agent_orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Process documents
result = orchestrator.process_documents([
    "/path/to/warehouse_report.pdf",
    "/path/to/inventory_data.xlsx",
    "/path/to/process_docs.docx"
])

# Query with document context
response = orchestrator.process_query_with_documents(
    "What are the key findings from the warehouse report?",
    include_document_context=True
)

# Search documents
matches = orchestrator.search_documents("safety stock")
```

### API Methods

| Method | Description |
|--------|-------------|
| `process_documents(file_paths)` | Process multiple files |
| `process_query_with_documents(query)` | Query with doc context |
| `search_documents(query)` | Search processed docs |
| `get_document_statistics()` | Get processing stats |
| `clear_document_context()` | Clear all documents |

---

## 🔧 2. Lean Six Sigma Tools

### New Quality Agent

Dedicated agent for process improvement using Six Sigma methodologies.

#### DMAIC Framework:
1. **Define** - Identify problems and project goals
2. **Measure** - Collect data and establish baselines
3. **Analyze** - Identify root causes
4. **Improve** - Implement solutions
5. **Control** - Maintain improvements

### Six Sigma Functions

#### 1. Process Capability Analysis (`calculate_process_capability`)
```python
# Calculate Cp and Cpk
result = quality_agent.process(
    "Calculate process capability with USL=10, LSL=0",
    {"data": [4.9, 5.1, 5.0, 4.8, 5.2, 5.1, 4.9]}
)
```

**Outputs:**
- Cp (potential capability)
- Cpk (actual capability)
- Sigma level
- DPMO estimate
- Interpretation and recommendations

#### 2. DPMO & Sigma Level (`calculate_dpmo`)
```python
# Defects Per Million Opportunities
result = quality_agent.process(
    "Calculate DPMO for 15 defects in 1000 units",
    {"defects": 15, "units": 1000}
)
```

**Sigma Levels:**
- 6σ: 3.4 DPMO (99.99966% quality) - World Class
- 5σ: 233 DPMO (99.977% quality) - Excellent
- 4σ: 6,210 DPMO (99.379% quality) - Good
- 3σ: 66,807 DPMO (93.32% quality) - Average

#### 3. Process Variation Analysis (`analyze_process_variation`)
```python
# Analyze stability and variation
result = quality_agent.process(
    "Analyze process variation",
    {"data": [/* measurement data */]}
)
```

**Outputs:**
- Mean, median, standard deviation
- Control limits (UCL, LCL)
- Coefficient of variation
- Outlier detection
- Stability assessment

### Quality Agent Capabilities

| Function | Purpose | Key Outputs |
|----------|---------|-------------|
| `pareto_analysis` | 80/20 analysis | Vital few vs trivial many |
| `calculate_process_capability` | Cp/Cpk calculation | Capability indices, sigma level |
| `calculate_dpmo` | Defect rate | DPMO, yield %, sigma level |
| `calculate_sigma_level` | Quality from yield | Sigma level from percentage |
| `analyze_process_variation` | Stability check | Control limits, outliers |
| `abc_analysis` | Priority classification | A/B/C categories |

---

## 📈 3. Pareto Analysis (80/20 Rule)

### Inventory Agent - ABC Classification

Classify inventory using Pareto principle.

```python
# ABC Classification
items = [
    {"sku": "ITEM-001", "annual_value": 50000},
    {"sku": "ITEM-002", "annual_value": 35000},
    {"sku": "ITEM-003", "annual_value": 500},
    # ... more items
]

result = inventory_agent.process(
    "Perform ABC classification",
    {"items": items}
)
```

**Classification:**
- **A Items** (Top 20%): 70-80% of value → Tight controls, daily monitoring
- **B Items** (Next 30%): 15-20% of value → Moderate controls, weekly review
- **C Items** (Bottom 50%): 5-10% of value → Basic controls, monthly review

### Pareto Analysis for Inventory

Identify the vital few SKUs driving metrics.

```python
# Pareto analysis on sales
items = [
    {"sku": "SKU-A", "metric_value": 100000},  # Sales $
    {"sku": "SKU-B", "metric_value": 85000},
    # ... more items
]

result = inventory_agent.process(
    "Perform Pareto analysis on sales",
    {"items": items, "metric_name": "sales_dollars"}
)
```

**Output:**
- Vital few (20% of SKUs → 80% of sales)
- Trivial many (80% of SKUs → 20% of sales)
- Recommendations for resource allocation

### Quality Agent - Pareto for Defects

Identify major defect causes.

```python
# Pareto analysis on defects
defects = [
    {"name": "Misalignment", "value": 45},
    {"name": "Scratches", "value": 32},
    {"name": "Missing parts", "value": 18},
    {"name": "Color variance", "value": 5}
]

result = quality_agent.process(
    "Perform Pareto analysis on defects",
    {"items": defects}
)
```

---

## 🚀 Example Workflows

### Workflow 1: Document-Based Process Improvement

```python
orchestrator = AgentOrchestrator()

# 1. Process warehouse audit documents
docs = orchestrator.process_documents([
    "warehouse_audit_2024.pdf",
    "defect_log.xlsx",
    "process_map.docx"
])

# 2. Query with document context
analysis = orchestrator.process_query_with_documents(
    "Analyze defect patterns and recommend improvements using Six Sigma"
)

# 3. Perform Pareto analysis on defects
defect_analysis = orchestrator.get_agent("quality").process(
    "Perform Pareto analysis to identify top defect causes",
    {"items": [/* defect data from docs */]}
)

# 4. Calculate process capability
capability = orchestrator.get_agent("quality").process(
    "Calculate process capability",
    {"data": [/* process data */], "usl": 10, "lsl": 0}
)
```

### Workflow 2: Inventory Optimization with Pareto

```python
# 1. ABC Classification
abc = orchestrator.get_agent("inventory").process(
    "Classify inventory using ABC analysis",
    {"items": inventory_items}
)

# 2. Focus on A items (vital few)
a_items = [item for item in abc["classification"] if item["category"] == "A"]

# 3. Calculate optimal policies for A items
for item in a_items:
    eoq = orchestrator.get_agent("inventory").process(
        f"Calculate EOQ for {item['sku']}",
        {
            "annual_demand": item["demand"],
            "order_cost": 100,
            "holding_cost": 2.5
        }
    )
```

### Workflow 3: Six Sigma DMAIC Project

```python
# Define Phase
problem = orchestrator.process_query(
    "Identify top 3 warehouse inefficiencies from documents"
)

# Measure Phase
baseline = orchestrator.get_agent("quality").process(
    "Calculate current process capability and DPMO",
    {"data": current_measurements, "usl": spec_usl, "lsl": spec_lsl}
)

# Analyze Phase
root_causes = orchestrator.get_agent("quality").process(
    "Perform Pareto analysis on defect causes",
    {"items": defect_causes}
)

# Improve Phase (implement changes)
# ...

# Control Phase
new_capability = orchestrator.get_agent("quality").process(
    "Calculate improved process capability",
    {"data": new_measurements, "usl": spec_usl, "lsl": spec_lsl}
)
```

---

## 📊 Integration with Existing System

### Agent Ecosystem

```
┌─────────────────────────────────────────────┐
│        Agent Orchestrator                   │
│  - Document Processor (Docling)             │
│  - Context Management                       │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┴─────────────────────────────┐
    │                                        │
┌───▼────────┐  ┌──────────┐  ┌───────────┐ │
│ Inventory  │  │Operations│  │  Quality  │ │
│  Agent     │  │  Agent   │  │  Agent    │ │
│            │  │          │  │           │ │
│ - EOQ      │  │- Metrics │  │- Six Sigma│ │
│ - ROP      │  │- Optimize│  │- Pareto   │ │
│ - ABC      │  │- Cycle   │  │- DPMO     │ │
│ - Pareto   │  │  Time    │  │- Cp/Cpk   │ │
└────────────┘  └──────────┘  └───────────┘ │
                                             │
                    ┌────────────────────────┘
                    │
            ┌───────▼────────┐
            │  Supervisor    │
            │    Agent       │
            │                │
            │  - Routing     │
            │  - Validation  │
            └────────────────┘
```

### Document Context Flow

```
User uploads files
       │
       ▼
Docling Processor
   │   ├── Extract text
   │   ├── Extract tables
   │   └── Extract metadata
       │
       ▼
Document Context Storage
       │
       ▼
Available to all agents
   │   ├── Inventory Agent
   │   ├── Operations Agent
   │   ├── Quality Agent
   │   ├── Math Agent
   │   └── Supervisor Agent
```

---

## 🎓 Best Practices

### Document Processing

1. **File Formats**: Use PDF for reports, Excel for data, Word for procedures
2. **File Size**: Keep documents under 10MB for optimal processing
3. **Context Limits**: System uses up to 50K characters of context
4. **Clear Context**: Clear document context when switching projects

### Six Sigma Projects

1. **Data Collection**: Gather at least 30 data points for statistical significance
2. **Baseline First**: Always establish baseline before improvements
3. **Control Limits**: Use ±3σ for control chart limits
4. **Target Capability**: Aim for Cpk ≥ 1.33 for capable processes

### Pareto Analysis

1. **Data Quality**: Ensure accurate counts/values for all items
2. **Appropriate Metrics**: Use value for ABC, frequency for defects
3. **Action Focus**: Concentrate resources on vital few (top 20%)
4. **Regular Review**: Update Pareto charts quarterly

---

## 📝 Configuration

### Environment Variables

```bash
# No additional configuration needed!
# Uses existing OPENAI_API_KEY
```

### Dependencies

```bash
# New dependencies
pip install docling>=1.0.0
pip install scipy>=1.11.0

# Already included
pip install numpy pandas sympy
```

---

## 🔍 Troubleshooting

### Docling Issues

**Problem**: "Docling not available"
**Solution**: `pip install docling` or system uses fallback processing

**Problem**: Large PDF not processing
**Solution**: Reduce file size or split into smaller documents

### Six Sigma Calculations

**Problem**: "Need at least 2 data points"
**Solution**: Provide more measurement data for statistical analysis

**Problem**: Cpk calculation shows "Poor capability"
**Solution**: Review process variation and centering; may need process improvements

### Pareto Analysis

**Problem**: "No items provided"
**Solution**: Ensure items array is not empty and has valid structure

**Problem**: Classification seems wrong
**Solution**: Verify values are correct and represent the intended metric

---

## 📚 References

### Lean Six Sigma
- **DMAIC**: Define, Measure, Analyze, Improve, Control
- **Sigma Levels**: Statistical measure of process quality
- **DPMO**: Defects Per Million Opportunities

### Pareto Principle
- **80/20 Rule**: 80% of effects from 20% of causes
- **ABC Analysis**: Inventory classification (A=high, B=medium, C=low value)
- **Vital Few vs Trivial Many**: Focus resources on high-impact items

### Document Processing
- **Docling**: IBM's document parsing library
- **OCR**: Optical Character Recognition
- **Context Window**: Amount of text included in AI prompts

---

## ✅ Summary

### What's New:

✨ **Docling Document Processing**
- Process PDFs, Word, Excel, images with OCR
- Automatic table extraction
- Full-text search
- Context integration with all agents

✨ **Lean Six Sigma Tools**
- Process capability (Cp/Cpk)
- DPMO and Sigma level calculation
- Process variation analysis
- DMAIC methodology support

✨ **Pareto Analysis**
- 80/20 rule for inventory
- ABC classification
- Defect cause prioritization
- Resource allocation optimization

### Benefits:

📈 **Improved Decision Making** - Data-driven insights from documents
🎯 **Focus Resources** - Pareto identifies high-impact areas
⚡ **Process Excellence** - Six Sigma tools drive quality improvements
📊 **Statistical Rigor** - Professional-grade analytics
🔄 **Continuous Improvement** - DMAIC framework for ongoing optimization

---

**🎊 Your warehouse management system now includes professional-grade quality tools and document intelligence! 🎊**
