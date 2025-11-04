"""
Modern Agent Orchestrator - OpenAI-powered multi-agent coordination.

Implements Swarm-like agent handoffs, parallel execution, and streaming support.
"""

from typing import Dict, Any, List, Optional, Generator
from agents.base_agent import BaseAgent, AgentConfig, AgentResponse
from agents.inventory_agent import InventoryAgent
from agents.operations_agent import OperationsAgent
from agents.supervisor_agent import SupervisorAgent
from agents.math_agent import MathAgent
from agents.quality_agent import QualityAgent
from agents.document_processor import DocumentProcessor
from datetime import datetime
import logging
import json
from config import (
    OPENAI_API_KEY,
    AGENT_MODELS,
    AGENT_TEMPERATURES,
    MAX_TOKENS,
    ENABLE_STREAMING
)


class AgentOrchestrator:
    """
    Modern multi-agent orchestrator with:
    - Swarm-like agent handoffs
    - Intelligent routing
    - Parallel agent execution
    - Streaming support
    - Context management
    - Document processing with Docling
    - Lean Six Sigma and Pareto analysis
    """

    def __init__(self):
        """Initialize orchestrator with all agents"""
        self.logger = logging.getLogger(__name__)

        # Initialize document processor
        self.document_processor = DocumentProcessor()

        # Initialize all agents
        self.agents = self._initialize_agents()

        # Knowledge base for shared context
        self.knowledge_base = {
            "conversations": [],
            "insights": [],
            "decisions": [],
            "calculations": []
        }

        self.logger.info("Agent Orchestrator initialized with OpenAI-powered agents + Document Processor")

    def _initialize_agents(self) -> Dict[str, BaseAgent]:
        """Initialize all specialized agents"""
        agents = {}

        try:
            # Supervisor Agent
            supervisor_config = AgentConfig(
                name="supervisor",
                model=AGENT_MODELS["supervisor"],
                temperature=AGENT_TEMPERATURES["supervisor"],
                max_tokens=MAX_TOKENS
            )
            agents["supervisor"] = SupervisorAgent(supervisor_config, OPENAI_API_KEY)

            # Inventory Agent
            inventory_config = AgentConfig(
                name="inventory",
                model=AGENT_MODELS["inventory"],
                temperature=AGENT_TEMPERATURES["inventory"],
                max_tokens=MAX_TOKENS
            )
            agents["inventory"] = InventoryAgent(inventory_config, OPENAI_API_KEY)

            # Operations Agent
            operations_config = AgentConfig(
                name="operations",
                model=AGENT_MODELS["operations"],
                temperature=AGENT_TEMPERATURES["operations"],
                max_tokens=MAX_TOKENS
            )
            agents["operations"] = OperationsAgent(operations_config, OPENAI_API_KEY)

            # Math Agent
            math_config = AgentConfig(
                name="math",
                model=AGENT_MODELS["math"],
                temperature=AGENT_TEMPERATURES["math"],
                max_tokens=MAX_TOKENS
            )
            agents["math"] = MathAgent(math_config, OPENAI_API_KEY)

            # Quality Agent (Lean Six Sigma + Pareto)
            quality_config = AgentConfig(
                name="quality",
                model=AGENT_MODELS.get("quality", "gpt-4o"),
                temperature=AGENT_TEMPERATURES.get("quality", 0.5),
                max_tokens=MAX_TOKENS
            )
            agents["quality"] = QualityAgent(quality_config, OPENAI_API_KEY)

            self.logger.info(f"Initialized {len(agents)} agents successfully (including Quality/Six Sigma agent)")

        except Exception as e:
            self.logger.error(f"Error initializing agents: {str(e)}")
            raise

        return agents

    def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Process a query with intelligent agent routing and handoffs.

        Args:
            query: User query
            context: Optional context dictionary

        Returns:
            AgentResponse from the appropriate agent(s)
        """
        try:
            self.logger.info(f"Processing query: {query[:100]}...")

            # Step 1: Use supervisor to route the query
            routing_result = self.agents["supervisor"].route_query(query)
            primary_agent = routing_result

            self.logger.info(f"Routed to: {primary_agent}")

            # Step 2: Process with primary agent
            if primary_agent in self.agents:
                response = self.agents[primary_agent].process(query, context)
            else:
                # Fallback to inventory agent
                response = self.agents["inventory"].process(query, context)

            # Step 3: Store in knowledge base
            self.knowledge_base["conversations"].append({
                "query": query,
                "agent": primary_agent,
                "response": response.content,
                "timestamp": datetime.now().isoformat()
            })

            return response

        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return AgentResponse(
                content=f"Error: {str(e)}",
                agent_name="orchestrator",
                metadata={"error": True}
            )

    def process_query_stream(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Generator[str, None, None]:
        """
        Process query with streaming response.

        Args:
            query: User query
            context: Optional context

        Yields:
            Response chunks as they arrive
        """
        try:
            if not ENABLE_STREAMING:
                # Fall back to non-streaming
                response = self.process_query(query, context)
                yield response.content
                return

            # Route the query
            routing_result = self.agents["supervisor"].route_query(query)
            primary_agent = routing_result

            # Stream from primary agent
            if primary_agent in self.agents:
                for chunk in self.agents[primary_agent].process_stream(query, context):
                    yield chunk
            else:
                # Fallback
                for chunk in self.agents["inventory"].process_stream(query, context):
                    yield chunk

        except Exception as e:
            self.logger.error(f"Error in streaming: {str(e)}")
            yield f"Error: {str(e)}"

    def process_with_handoff(
        self,
        query: str,
        initial_agent: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process query with explicit agent handoffs (Swarm pattern).

        Args:
            query: User query
            initial_agent: Starting agent name
            context: Optional context

        Returns:
            Dictionary with final response and handoff history
        """
        handoff_history = []
        current_agent = initial_agent
        max_handoffs = 5  # Prevent infinite loops

        try:
            for i in range(max_handoffs):
                # Process with current agent
                response = self.agents[current_agent].process(query, context)

                # Record handoff
                handoff_history.append({
                    "agent": current_agent,
                    "response": response.content,
                    "timestamp": datetime.now().isoformat()
                })

                # Check if handoff is needed
                # (This is a simplified version - in production, agents would
                # explicitly signal handoffs in their responses)
                if len(handoff_history) == 1 and current_agent == "supervisor":
                    # Supervisor routes to appropriate agent
                    next_agent = self.agents["supervisor"].route_query(query)
                    if next_agent != current_agent and next_agent in self.agents:
                        current_agent = next_agent
                        continue

                # No more handoffs needed
                break

            return {
                "final_response": handoff_history[-1]["response"],
                "handoff_chain": [h["agent"] for h in handoff_history],
                "handoff_history": handoff_history
            }

        except Exception as e:
            self.logger.error(f"Error in handoff processing: {str(e)}")
            return {
                "error": str(e),
                "handoff_history": handoff_history
            }

    def process_multi_agent(
        self,
        query: str,
        agents: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, AgentResponse]:
        """
        Process query with multiple agents in parallel.

        Args:
            query: User query
            agents: List of agent names to consult
            context: Optional context

        Returns:
            Dictionary mapping agent names to responses
        """
        responses = {}

        for agent_name in agents:
            if agent_name in self.agents:
                try:
                    response = self.agents[agent_name].process(query, context)
                    responses[agent_name] = response
                except Exception as e:
                    self.logger.error(f"Error processing with {agent_name}: {str(e)}")
                    responses[agent_name] = AgentResponse(
                        content=f"Error: {str(e)}",
                        agent_name=agent_name,
                        metadata={"error": True}
                    )

        return responses

    def synthesize_multi_agent_response(
        self,
        query: str,
        agent_names: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get responses from multiple agents and synthesize into one answer.

        Args:
            query: User query
            agent_names: List of agents to consult
            context: Optional context

        Returns:
            Synthesized response
        """
        # Get responses from all agents
        responses = self.process_multi_agent(query, agent_names, context)

        # Convert to simple dict for synthesis
        response_dict = {
            name: resp.content for name, resp in responses.items()
        }

        # Use supervisor to synthesize
        synthesis_context = {
            "responses": response_dict,
            "query": query
        }

        synthesis = self.agents["supervisor"].process(
            f"Synthesize these responses into a cohesive answer:\n\n{json.dumps(response_dict, indent=2)}",
            synthesis_context
        )

        return synthesis.content

    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all agents and system"""
        return {
            "agents": {
                name: agent.get_status()
                for name, agent in self.agents.items()
            },
            "knowledge_base_size": {
                "conversations": len(self.knowledge_base["conversations"]),
                "insights": len(self.knowledge_base["insights"]),
                "decisions": len(self.knowledge_base["decisions"])
            },
            "system_info": {
                "streaming_enabled": ENABLE_STREAMING,
                "models": AGENT_MODELS
            },
            "timestamp": datetime.now().isoformat()
        }

    def reset_all_conversations(self):
        """Reset conversation history for all agents"""
        for agent in self.agents.values():
            agent.reset_conversation()
        self.logger.info("All agent conversations reset")

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get a specific agent by name"""
        return self.agents.get(agent_name)

    # Document Processing Methods

    def process_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Process documents and add to system context.

        Args:
            file_paths: List of file paths to process

        Returns:
            Dictionary with processing results and statistics
        """
        self.logger.info(f"Processing {len(file_paths)} documents...")

        results = self.document_processor.process_multiple_files(file_paths)

        # Add document context to knowledge base
        doc_context = self.document_processor.get_combined_context(max_chars=50000)
        if doc_context:
            self.knowledge_base["document_context"] = doc_context

        successful = sum(1 for doc in results if doc.success)
        failed = len(results) - successful

        return {
            "processed": len(results),
            "successful": successful,
            "failed": failed,
            "documents": [
                {
                    "filename": doc.file_name,
                    "success": doc.success,
                    "error": doc.error,
                    "processing_time": doc.processing_time
                }
                for doc in results
            ],
            "context_available": len(doc_context) > 0,
            "statistics": self.document_processor.get_statistics()
        }

    def process_query_with_documents(
        self,
        query: str,
        include_document_context: bool = True
    ) -> AgentResponse:
        """
        Process query with document context included.

        Args:
            query: User query
            include_document_context: Whether to include processed documents in context

        Returns:
            AgentResponse with document-aware answer
        """
        context = {}

        if include_document_context:
            doc_context = self.document_processor.get_combined_context(max_chars=10000)
            if doc_context:
                context["document_context"] = doc_context
                self.logger.info("Including document context in query")

        return self.process_query(query, context)

    def search_documents(self, query: str) -> List[Dict[str, Any]]:
        """
        Search processed documents for query.

        Args:
            query: Search query

        Returns:
            List of matching documents with excerpts
        """
        return self.document_processor.search_documents(query)

    def get_document_statistics(self) -> Dict[str, Any]:
        """Get document processing statistics"""
        return self.document_processor.get_statistics()

    def clear_document_context(self):
        """Clear all processed documents from context"""
        self.document_processor.clear_context()
        if "document_context" in self.knowledge_base:
            del self.knowledge_base["document_context"]
        self.logger.info("Document context cleared")
