"""
Base Agent class for OpenAI-powered multi-agent warehouse management system.

This module provides the foundation for all specialized agents using the latest
OpenAI SDK features including function calling, streaming, and structured outputs.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable, Generator
from openai import OpenAI
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import json


class AgentConfig(BaseModel):
    """Configuration for an agent"""
    name: str
    model: str = "gpt-4o"  # Default to GPT-4o for best performance
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = False


class Message(BaseModel):
    """Structured message for agent communication"""
    role: str = Field(..., description="Message role: system, user, assistant, or function")
    content: str = Field(..., description="Message content")
    name: Optional[str] = Field(None, description="Name of function or agent")
    function_call: Optional[Dict[str, Any]] = Field(None, description="Function call data")


class AgentResponse(BaseModel):
    """Structured response from an agent"""
    content: str = Field(..., description="Response content")
    agent_name: str = Field(..., description="Name of the responding agent")
    function_calls: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class BaseAgent(ABC):
    """
    Base class for all OpenAI-powered warehouse agents.

    Features:
    - OpenAI SDK integration with streaming support
    - Function calling for tool use
    - Structured outputs with Pydantic
    - Conversation history management
    - Agent handoffs and collaboration
    """

    def __init__(self, config: AgentConfig, api_key: str, tools: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize base agent with OpenAI client and configuration.

        Args:
            config: Agent configuration
            api_key: OpenAI API key
            tools: Optional list of function definitions for tool calling
        """
        self.config = config
        self.client = OpenAI(api_key=api_key)
        self.tools = tools or []

        # Agent state
        self.state = {
            "queries_processed": 0,
            "documents_processed": 0,
            "last_activity": None,
            "insights": [],
            "total_tokens_used": 0
        }

        # Conversation history
        self.conversation_history: List[Dict[str, Any]] = []

        # Setup logging
        self.logger = logging.getLogger(f"agent.{config.name}")

        # System prompt - to be defined by subclasses
        self.system_prompt = self._get_system_prompt()

    @abstractmethod
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def _get_tools(self) -> List[Dict[str, Any]]:
        """
        Get the function definitions (tools) for this agent.
        Must be implemented by subclasses.
        """
        pass

    def process(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Process input using OpenAI chat completion with function calling.

        Args:
            input_data: User input to process
            context: Optional context dictionary

        Returns:
            AgentResponse with the result
        """
        try:
            # Build messages
            messages = self._build_messages(input_data, context)

            # Get tools for this request
            tools = self._get_tools() if self._get_tools() else None

            # Make API call
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                tools=tools,
                tool_choice="auto" if tools else None
            )

            # Extract response
            message = response.choices[0].message

            # Handle function calls
            function_calls = []
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Execute the function
                    result = self._execute_function(function_name, function_args)
                    function_calls.append({
                        "function": function_name,
                        "arguments": function_args,
                        "result": result
                    })

                    # Add function result to conversation
                    messages.append({
                        "role": "function",
                        "name": function_name,
                        "content": json.dumps(result)
                    })

                # Get final response after function execution
                final_response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )

                content = final_response.choices[0].message.content
                self.state["total_tokens_used"] += final_response.usage.total_tokens
            else:
                content = message.content or ""
                self.state["total_tokens_used"] += response.usage.total_tokens

            # Update state
            self.state["queries_processed"] += 1
            self.state["last_activity"] = datetime.now().isoformat()

            # Store in conversation history
            self.conversation_history.append({
                "user": input_data,
                "assistant": content,
                "timestamp": datetime.now().isoformat()
            })

            return AgentResponse(
                content=content,
                agent_name=self.config.name,
                function_calls=function_calls,
                metadata={
                    "tokens_used": response.usage.total_tokens,
                    "model": self.config.model
                }
            )

        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}")
            return AgentResponse(
                content=f"Error: {str(e)}",
                agent_name=self.config.name,
                metadata={"error": True}
            )

    def process_stream(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        """
        Process input with streaming response.

        Args:
            input_data: User input to process
            context: Optional context dictionary

        Yields:
            Response chunks as they arrive
        """
        try:
            messages = self._build_messages(input_data, context)

            stream = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                stream=True
            )

            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content

            # Update state after streaming completes
            self.state["queries_processed"] += 1
            self.state["last_activity"] = datetime.now().isoformat()

            self.conversation_history.append({
                "user": input_data,
                "assistant": full_response,
                "timestamp": datetime.now().isoformat()
            })

        except Exception as e:
            self.logger.error(f"Error in streaming: {str(e)}")
            yield f"Error: {str(e)}"

    def _build_messages(self, input_data: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """
        Build message list for OpenAI API call.

        Args:
            input_data: User input
            context: Optional context

        Returns:
            List of message dictionaries
        """
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add relevant conversation history (last 5 exchanges)
        for exchange in self.conversation_history[-5:]:
            messages.append({"role": "user", "content": exchange["user"]})
            messages.append({"role": "assistant", "content": exchange["assistant"]})

        # Add context if provided
        if context:
            context_str = f"\nContext: {json.dumps(context, indent=2)}"
            input_data = input_data + context_str

        # Add current input
        messages.append({"role": "user", "content": input_data})

        return messages

    def _execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a function call.
        Must be implemented or overridden by subclasses.

        Args:
            function_name: Name of the function to execute
            arguments: Function arguments

        Returns:
            Function result
        """
        self.logger.warning(f"Function {function_name} called but not implemented")
        return {"error": f"Function {function_name} not implemented"}

    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the agent"""
        return self.state.copy()

    def get_status(self) -> str:
        """Get a human-readable status string"""
        return (
            f"Active - Processed: {self.state['queries_processed']} queries, "
            f"{self.state['documents_processed']} documents, "
            f"Tokens used: {self.state['total_tokens_used']}, "
            f"Insights: {len(self.state['insights'])}"
        )

    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
        self.logger.info(f"Conversation history reset for {self.config.name}")

    def handoff_to(self, target_agent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare handoff to another agent.

        Args:
            target_agent: Name of the target agent
            context: Context to pass to the target agent

        Returns:
            Handoff data
        """
        return {
            "source_agent": self.config.name,
            "target_agent": target_agent,
            "context": context,
            "conversation_summary": self._summarize_conversation(),
            "timestamp": datetime.now().isoformat()
        }

    def _summarize_conversation(self) -> str:
        """
        Create a summary of the recent conversation.

        Returns:
            Summary string
        """
        if not self.conversation_history:
            return "No conversation history"

        recent = self.conversation_history[-3:]
        summary = "Recent conversation:\n"
        for exchange in recent:
            summary += f"User: {exchange['user'][:100]}...\n"
            summary += f"Assistant: {exchange['assistant'][:100]}...\n"

        return summary
