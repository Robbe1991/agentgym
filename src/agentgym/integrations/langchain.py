"""LangChain framework adapter with real integration.

This module provides integration with LangChain agents, enabling:
- Converting trained models to LangChain AgentExecutor instances
- Extracting tools from LangChain agents
- Creating training environments from existing LangChain agents

Supports both mock mode (for testing) and real mode (with LLM API keys).

Example:
    >>> from agentgym.integrations.langchain import LangChainAdapter
    >>> adapter = LangChainAdapter()
    >>>
    >>> # Wrap a trained model as a LangChain agent
    >>> agent = adapter.wrap_agent(trained_model)
    >>>
    >>> # Extract tools from existing LangChain agent
    >>> tools = adapter.extract_tools(agent)
    >>>
    >>> # Create training environment
    >>> env = adapter.create_environment(agent)
"""

import os
from typing import Any, Optional

from agentgym.integrations.base import FrameworkAdapter

# Try to import LangChain - graceful degradation if not available
try:
    from langchain.agents import AgentExecutor, AgentType, initialize_agent
    from langchain.memory import ConversationBufferMemory
    from langchain.tools import BaseTool, Tool

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    AgentExecutor = None
    BaseTool = None
    Tool = None

# Try to import LLM providers
try:
    from langchain_openai import ChatOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    ChatOpenAI = None

try:
    from langchain_anthropic import ChatAnthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    ChatAnthropic = None


class LangChainAdapter(FrameworkAdapter):
    """Adapter for integrating with LangChain framework.

    This adapter enables AgentGym to work with LangChain agents by providing
    methods to convert between AgentGym's training format and LangChain's
    AgentExecutor format.

    Supports both mock mode (testing without API keys) and real mode (with LLMs).

    LangChain is a popular framework for building LLM applications with:
    - AgentExecutor: Main agent runtime
    - Tools: Functions the agent can call
    - Chains: Sequences of operations
    - Memory: Conversation history

    Attributes:
        framework_name: Always "langchain" for this adapter.
        llm_provider: LLM provider to use ("openai", "anthropic", or "mock")
        model_name: Model name (e.g., "gpt-4", "claude-3-sonnet")
        temperature: Temperature for LLM generation
        mock_mode: If True, use mock implementation

    Example:
        >>> # With OpenAI
        >>> adapter = LangChainAdapter(llm_provider="openai", model_name="gpt-4")
        >>> agent = adapter.wrap_agent(trained_model, tools=[search_tool])
        >>>
        >>> # Mock mode (for testing)
        >>> adapter = LangChainAdapter(mock_mode=True)
        >>> agent = adapter.wrap_agent(trained_model)
    """

    framework_name: str = "langchain"

    def __init__(
        self,
        llm_provider: str = "mock",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        mock_mode: bool = False,
        verbose: bool = False,
    ):
        """Initialize LangChain adapter.

        Args:
            llm_provider: LLM provider ("openai", "anthropic", "mock")
            model_name: Model name (default: gpt-3.5-turbo for OpenAI,
                       claude-3-sonnet for Anthropic)
            temperature: Temperature for generation (0-1)
            mock_mode: Force mock mode even if API keys available
            verbose: Enable verbose logging
        """
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.temperature = temperature
        self.mock_mode = mock_mode or not LANGCHAIN_AVAILABLE
        self.verbose = verbose

        # Auto-detect mock mode if no API keys
        if llm_provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            self.mock_mode = True
        elif llm_provider == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
            self.mock_mode = True

    def _create_llm(self) -> Any:
        """Create LLM instance based on provider.

        Returns:
            LLM instance or None if mock mode

        Raises:
            ValueError: If provider not supported or API key missing
        """
        if self.mock_mode:
            return None

        if self.llm_provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ValueError(
                    "OpenAI not available. Install: pip install langchain-openai"
                )
            model = self.model_name or "gpt-3.5-turbo"
            return ChatOpenAI(model=model, temperature=self.temperature)

        elif self.llm_provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ValueError(
                    "Anthropic not available. Install: pip install langchain-anthropic"
                )
            model = self.model_name or "claude-3-sonnet-20240229"
            return ChatAnthropic(model=model, temperature=self.temperature)

        elif self.llm_provider == "mock":
            return None

        else:
            raise ValueError(
                f"Unknown LLM provider: {self.llm_provider}. "
                f"Supported: openai, anthropic, mock"
            )

    def wrap_agent(
        self,
        trained_model: Any,
        tools: Optional[list[Any]] = None,
        agent_type: str = "zero-shot-react-description",
        memory: Optional[Any] = None,
    ) -> Any:
        """Wrap a trained model as a LangChain agent.

        Creates a real AgentExecutor if API keys available, otherwise mock.

        Args:
            trained_model: Path to trained model or model object from AgentGym.
                Can be:
                - str: Path to saved model (e.g., "./models/agent_ep100")
                - dict: Model configuration/weights
                - Any: Model object from training
            tools: List of LangChain Tool objects to give the agent
            agent_type: Type of agent ("zero-shot-react-description",
                       "conversational-react-description", etc.)
            memory: Memory instance (default: ConversationBufferMemory)

        Returns:
            - If real mode: LangChain AgentExecutor instance
            - If mock mode: Dict representing agent structure

        Raises:
            ValueError: If trained_model is invalid or API keys missing in real mode

        Example:
            >>> from langchain.tools import Tool
            >>> search_tool = Tool(
            ...     name="search",
            ...     func=lambda x: f"Results for: {x}",
            ...     description="Search for information"
            ... )
            >>> adapter = LangChainAdapter(llm_provider="openai")
            >>> agent = adapter.wrap_agent(trained_model, tools=[search_tool])
        """
        tools = tools or []

        # Mock mode: Return dict representation
        if self.mock_mode:
            return {
                "type": "langchain_agent",
                "model": trained_model,
                "tools": tools,
                "memory": memory or {},
                "executor": {
                    "agent_type": agent_type,
                    "verbose": self.verbose,
                },
                "_mock": True,  # Flag for testing
            }

        # Real mode: Create AgentExecutor
        llm = self._create_llm()

        # Create memory if not provided
        if memory is None:
            memory = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )

        # Map agent_type string to AgentType enum
        agent_type_map = {
            "zero-shot-react-description": AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            "conversational-react-description": AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            "react-docstore": AgentType.REACT_DOCSTORE,
            "self-ask-with-search": AgentType.SELF_ASK_WITH_SEARCH,
            "openai-functions": AgentType.OPENAI_FUNCTIONS,
            "structured-chat-zero-shot-react-description": AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        }

        agent_type_enum = agent_type_map.get(
            agent_type, AgentType.ZERO_SHOT_REACT_DESCRIPTION
        )

        # Create AgentExecutor
        agent_executor = initialize_agent(
            tools=tools,
            llm=llm,
            agent=agent_type_enum,
            memory=memory,
            verbose=self.verbose,
            handle_parsing_errors=True,
        )

        # Store trained model reference for later use
        agent_executor._agentgym_model = trained_model

        return agent_executor

    def extract_tools(self, agent: Any) -> list[Any]:
        """Extract tools from a LangChain agent.

        Args:
            agent: LangChain AgentExecutor or dict representation

        Returns:
            List of LangChain Tool objects or dicts

        Example:
            >>> tools = adapter.extract_tools(agent)
            >>> for tool in tools:
            ...     print(tool.name if hasattr(tool, 'name') else tool['name'])
        """
        # Dict format (mock mode)
        if isinstance(agent, dict):
            return agent.get("tools", [])

        # Real AgentExecutor
        if LANGCHAIN_AVAILABLE and isinstance(agent, AgentExecutor):
            return agent.tools

        # Object with tools attribute
        if hasattr(agent, "tools"):
            return agent.tools

        return []

    def create_environment(self, agent: Any) -> dict[str, Any]:
        """Create a training environment from a LangChain agent.

        Args:
            agent: LangChain AgentExecutor or dict representation

        Returns:
            Environment dictionary compatible with Scenario.create_environment()

        Example:
            >>> env = adapter.create_environment(agent)
            >>> print(env["type"])  # "langchain"
            >>> print(len(env["tools"]))  # Number of tools
        """
        tools = self.extract_tools(agent)

        # Extract configuration
        config = {}

        if isinstance(agent, dict):
            # Mock mode
            config = agent.get("executor", {})
        elif LANGCHAIN_AVAILABLE and isinstance(agent, AgentExecutor):
            # Real AgentExecutor
            config = {
                "agent_type": (
                    getattr(agent.agent, "agent_type", "unknown")
                    if hasattr(agent, "agent")
                    else "unknown"
                ),
                "verbose": getattr(agent, "verbose", False),
                "handle_parsing_errors": getattr(agent, "handle_parsing_errors", True),
            }
        elif hasattr(agent, "agent"):
            # Other object with agent attribute
            config = {
                "agent_type": getattr(agent.agent, "agent_type", "unknown"),
                "verbose": getattr(agent, "verbose", False),
            }

        return {
            "type": "langchain",
            "agent": agent,
            "tools": tools,
            "config": config,
        }

    def validate_agent(self, agent: Any) -> bool:
        """Validate that an agent is compatible with LangChain.

        Args:
            agent: Agent object to validate

        Returns:
            True if agent is valid LangChain agent, False otherwise

        Example:
            >>> if adapter.validate_agent(agent):
            ...     env = adapter.create_environment(agent)
        """
        # Dict with correct type (mock mode)
        if isinstance(agent, dict):
            return agent.get("type") == "langchain_agent"

        # Real AgentExecutor
        if LANGCHAIN_AVAILABLE and isinstance(agent, AgentExecutor):
            return True

        # Object with agent and tools attributes
        if hasattr(agent, "agent") and hasattr(agent, "tools"):
            return True

        return False

    def run_agent(self, agent: Any, input_text: str, **kwargs: Any) -> dict[str, Any]:
        """Run the agent with given input.

        Convenience method for executing agent with input.

        Args:
            agent: LangChain AgentExecutor or dict
            input_text: Input text for the agent
            **kwargs: Additional arguments to pass to agent

        Returns:
            Dict with "output" key containing agent response

        Raises:
            ValueError: If mock mode or agent invalid

        Example:
            >>> result = adapter.run_agent(agent, "What is 2+2?")
            >>> print(result["output"])
        """
        if isinstance(agent, dict) or not LANGCHAIN_AVAILABLE:
            raise ValueError("Cannot run agent in mock mode. Set up real LLM provider.")

        if isinstance(agent, AgentExecutor):
            result = agent.invoke({"input": input_text}, **kwargs)
            return {"output": result.get("output", "")}

        raise ValueError(f"Invalid agent type: {type(agent)}")
