# Pistology-WAIS

An intelligent, collaborative Warehouse AI System (WAIS) for document processing and warehouse management using multiple AI agents.

## Features

- Multi-agent AI system with specialized agents:
  - Inventory Agent (DeepSeek)
  - Operations Agent (Gemini)
  - Supervisor Agent (Gemini)
- Document processing with LangChain
- Real-time system monitoring
- Interactive chat interface
- Secure API key management

## Prerequisites

- Python 3.12+
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nezpik/Pistology-WAIS.git
cd Pistology-WAIS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Edit the `.env` file and add your API keys:
- DEEPSEEK_API_KEY
- GEMINI_API_KEY
- GEMINI_OPERATIONS_KEY
- GEMINI_SUPERVISOR_KEY
- GEMINI_INVENTORY_KEY

## Security Notes

- Never commit the `.env` file to version control
- Keep your API keys secure and never share them
- Regularly rotate your API keys
- The `.gitignore` file is set up to exclude sensitive files
- All API keys are loaded from environment variables for security

## Running the Application

Start the FastAPI server:
```bash
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints

- POST `/query`: Send queries to specific agents
- GET `/status`: Get current state of all agents

## Example Usage

```python
import requests

# Query the inventory agent
response = requests.post("http://localhost:8000/query", 
    json={
        "query": "Check stock levels for item A123",
        "agent_type": "inventory"
    }
)

# Get system status
status = requests.get("http://localhost:8000/status")
```

## Architecture

- Each agent inherits from `BaseAgent` class
- TensorFlow integration available for machine learning tasks
- Supervisor agent validates decisions made by other agents
- FastAPI provides REST API interface
