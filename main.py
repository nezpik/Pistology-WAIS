from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.inventory_agent import InventoryAgent
from agents.operations_agent import OperationsAgent
from agents.supervisor_agent import SupervisorAgent
from agents.document_processor import DocumentProcessor
from agents.agent_orchestrator import AgentOrchestrator
import uvicorn
import signal
import sys
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up server...")
    yield
    # Shutdown
    print("Shutting down server...")

app = FastAPI(lifespan=lifespan)

# Initialize document processor and agents
document_processor = DocumentProcessor()
inventory_agent = InventoryAgent(document_processor=document_processor)
operations_agent = OperationsAgent(document_processor=document_processor)
supervisor_agent = SupervisorAgent(document_processor=document_processor)

# Initialize orchestrator
orchestrator = AgentOrchestrator(
    inventory_agent=inventory_agent,
    operations_agent=operations_agent,
    supervisor_agent=supervisor_agent,
    document_processor=document_processor
)

class QueryModel(BaseModel):
    query: str
    agent_type: str

@app.post("/query")
async def process_query(query_data: QueryModel):
    try:
        if query_data.agent_type == "inventory":
            result = inventory_agent.process(query_data.query)
        elif query_data.agent_type == "operations":
            result = operations_agent.process(query_data.query)
        else:
            raise HTTPException(status_code=400, detail="Invalid agent type")
        
        # Supervisor validates the result
        validation = supervisor_agent.validate_decision(query_data.agent_type, result)
        
        return {
            "result": result,
            "validation": validation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    return {
        "inventory_state": inventory_agent.get_state(),
        "operations_state": operations_agent.get_state(),
        "supervisor_state": supervisor_agent.get_state()
    }

def signal_handler(sig, frame):
    print("Received shutdown signal")
    sys.exit(0)

def run_server():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,
        reload_delay=0.25,
        workers=1
    )
    server = uvicorn.Server(config)
    server.run()

if __name__ == "__main__":
    run_server()
