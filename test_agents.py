from agents.inventory_agent import InventoryAgent
from agents.operations_agent import OperationsAgent
from agents.supervisor_agent import SupervisorAgent
from agents.agent_orchestrator import AgentOrchestrator

def test_agents():
    print("Initializing agents...")
    try:
        # Initialize agents
        inventory_agent = InventoryAgent()
        operations_agent = OperationsAgent()
        supervisor_agent = SupervisorAgent()
        
        # Create orchestrator
        orchestrator = AgentOrchestrator(
            inventory_agent, operations_agent, supervisor_agent
        )
        
        # Test query
        test_query = "What is the current inventory level of product SKU-123?"
        print(f"\nTesting query: {test_query}")
        
        response = orchestrator.process_query(test_query)
        
        print("\nResults:")
        print("Inventory Response:", response["inventory_response"])
        print("Operations Response:", response["operations_response"])
        print("Supervisor Response:", response["supervisor_response"])
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    test_agents()
