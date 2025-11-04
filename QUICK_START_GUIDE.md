# 🚀 Quick Start Guide - Pistology-WAIS v2.1

## Getting Started in 3 Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Launch the UI

```bash
streamlit run chat_ui.py
```

### 3. Configure & Initialize

1. Enter your OpenAI API key in the sidebar
2. Click "🚀 Initialize"
3. Start chatting!

---

## 📖 Using the System

### Basic Workflow

1. **API Key**: Enter your OpenAI API key (starts with `sk-`)
2. **Initialize**: Click the Initialize button to start the agents
3. **Upload Documents** (optional): Add PDFs, Word docs, Excel files for context
4. **Ask Questions**: Type your query in the chat

### Example Queries

#### Inventory Management
```
"Calculate EOQ for 10,000 units annual demand, $50 order cost, $5 holding cost"
"Perform ABC classification on these items: [items data]"
"What's the reorder point with 500 units daily demand?"
```

#### Six Sigma & Quality
```
"Calculate process capability with USL=10, LSL=0, data=[5.1, 4.9, 5.2, 5.0, 4.8]"
"Analyze defects: 15 defects in 1000 units, 3 opportunities per unit"
"Do Pareto analysis on these defect causes..."
```

#### Operations
```
"Calculate throughput for 500 units in 8 hours"
"What's the cycle time with these values?"
"Analyze equipment utilization rate"
```

#### Document Analysis
```
"What are the key findings from the uploaded report?"
"Summarize the defects mentioned in the document"
"Extract inventory data from the uploaded Excel file"
```

---

## 🎯 Key Features

### 🤖 Multi-Agent System
- **Supervisor**: Routes queries to the right agent
- **Inventory**: EOQ, ROP, ABC, Pareto, forecasting
- **Operations**: Throughput, cycle time, productivity
- **Math**: Complex calculations, statistics
- **Quality**: Six Sigma, DMAIC, Cp/Cpk, DPMO

### 📄 Document Intelligence
- **IBM Docling**: Advanced document parsing
- **OCR**: Extract text from images
- **Table Extraction**: Automatic detection
- **Context Integration**: Documents inform all responses

### 📊 Interactive Visualizations
- **Pareto Charts**: 80/20 rule analysis
- **ABC Classification**: Inventory prioritization
- **Process Capability**: Cp/Cpk metrics
- **DPMO Charts**: Sigma level quality

---

## ⚙️ Advanced Configuration

### Model Selection

Click "Advanced Settings" in the sidebar to choose models for each agent:

- **gpt-4o**: Best performance, higher cost
- **gpt-4o-mini**: Good balance, lower cost (recommended)
- **gpt-4-turbo**: Legacy model
- **gpt-3.5-turbo**: Fastest, lowest cost

### Supported Document Formats

- **Documents**: PDF, Word (.docx), PowerPoint (.pptx)
- **Spreadsheets**: Excel (.xlsx), CSV
- **Text**: .txt, .md, .json
- **Images**: PNG, JPG (with OCR)

---

## 🔧 Troubleshooting

### "Please provide a valid OpenAI API key"
- Ensure your key starts with `sk-`
- Check that the key is valid and has credits

### "Initialization failed"
- Verify internet connection
- Check OpenAI API status
- Review the error message for details

### Document Upload Issues
- Ensure file size is under 10MB
- Check that file format is supported
- Try uploading one file at a time

### Visualization Not Showing
- Ensure you're using a query that generates data
- Check that the analysis completed successfully
- Try refreshing the page

---

## 📊 Understanding Visualizations

### Pareto Chart (80/20 Rule)
- **Bar Chart**: Individual item values
- **Red Line**: Cumulative percentage
- **Orange Dash**: 80% threshold
- **Vital Few**: Items above 80% line contribute most value

### ABC Classification
- **Category A** (Red): High-value items (top 20%, 70-80% of value)
  - Tight controls, daily monitoring
- **Category B** (Yellow): Medium-value items (next 30%, 15-20% of value)
  - Moderate controls, weekly review
- **Category C** (Green): Low-value items (bottom 50%, 5-10% of value)
  - Basic controls, monthly review

### Process Capability
- **Cp**: Potential capability (process width vs spec width)
- **Cpk**: Actual capability (accounting for centering)
- **Interpretation**:
  - Cpk ≥ 2.0: Excellent (6σ)
  - Cpk ≥ 1.33: Good (4σ)
  - Cpk ≥ 1.0: Marginal (3σ)
  - Cpk < 1.0: Poor (needs improvement)

### Sigma Levels
- **6σ**: 3.4 DPMO - World-class
- **5σ**: 233 DPMO - Excellent
- **4σ**: 6,210 DPMO - Good
- **3σ**: 66,807 DPMO - Average
- **<3σ**: Poor quality

---

## 💡 Tips for Best Results

### Writing Effective Queries

**Good:**
```
"Calculate EOQ for 10,000 units annual demand, $50 order cost, $5 holding cost"
```

**Better:**
```
"I have 10,000 units annual demand, $50 per order, and $5 per unit holding cost.
Calculate EOQ and tell me the optimal order quantity and total cost."
```

### Using Documents

1. **Upload First**: Add documents before asking questions about them
2. **Be Specific**: Reference specific sections or data
3. **Ask Follow-ups**: Build on previous responses

### Getting Visualizations

Use these keywords to trigger visualizations:
- "Pareto analysis"
- "ABC classification"
- "Process capability"
- "DPMO"
- "Process variation"

---

## 🎓 Learning Resources

### Six Sigma Concepts

- **DMAIC**: Define → Measure → Analyze → Improve → Control
- **Cp/Cpk**: Process capability indices
- **DPMO**: Defects Per Million Opportunities
- **Sigma Level**: Statistical measure of quality

### Lean Principles

- **Pareto Principle**: 80% of effects from 20% of causes
- **ABC Analysis**: Inventory classification by value
- **Waste Reduction**: Eliminate non-value-adding activities

### Inventory Management

- **EOQ**: Economic Order Quantity - optimal order size
- **ROP**: Reorder Point - when to order
- **Safety Stock**: Buffer inventory for uncertainty
- **Lead Time**: Time from order to receipt

---

## 📚 Additional Documentation

- **Full Feature Guide**: `DOCLING_LEAN_SIX_SIGMA_FEATURES.md`
- **Upgrade Summary**: `UPGRADE_SUMMARY.md`
- **Environment Setup**: `.env.example`

---

## 🆘 Getting Help

### Error Messages

The system provides detailed error messages. Read them carefully for:
- Missing parameters
- Invalid data formats
- API issues
- Processing errors

### Logs

Check the console/terminal for detailed logs:
```bash
# The Streamlit terminal shows:
# - Initialization status
# - Processing progress
# - Error details
# - System warnings
```

### Reset System

If something goes wrong:
1. Click "🔄 Reset" button in sidebar
2. Re-enter API key
3. Click "🚀 Initialize" again

---

## ✅ System Health Check

After launching, verify:

1. ✅ API key accepted
2. ✅ System initialized successfully
3. ✅ Agents show as "Ready"
4. ✅ Chat responds to queries
5. ✅ Documents can be uploaded
6. ✅ Visualizations render

---

## 🎉 You're Ready!

The system is now fully operational. Start by:

1. Uploading a warehouse document (optional)
2. Asking a simple question like "What can you help me with?"
3. Trying a calculation like "Calculate EOQ for 5000 units"
4. Requesting an analysis like "Do ABC classification"

**Happy analyzing! 📊**
