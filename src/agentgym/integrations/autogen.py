"""AutoGen framework adapter with real integration.

This module provides integration with Microsoft AutoGen framework, enabling:
- Converting trained models to AutoGen agent instances
- Extracting agents and tools from AutoGen systems
- Creating training environments from existing AutoGen setups
- Supporting multi-agent conversations

Supports both mock mode (for testing) and real mode (with LLM API keys).

Example:
    >>> from agentgym.integrations.autogen import AutoGenAdapter
    >>> adapter = AutoGenAdapter()
    >>>
    >>> # Wrap a trained model as an AutoGen agent
    >>> agent = adapter.wrap_agent(trained_model)
    >>>
    >>> # Extract agents from existing AutoGen setup
    >>> agents = adapter.extract_tools(agent)
    >>>
    >>> # Create training environment
    >>> env = adapter.create_environment(agent)
"""

import os
from typing import Any, Optional

from agentgym.integrations.base import FrameworkAdapter

# Try to import AutoGen - graceful degradation if not available
try:
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    from autogen import config_list_from_json

    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    AssistantAgent = None
    UserProxyAgent = None
    GroupChat = None
    GroupChatManager = None

# Try to import LLM providers
try:
    from autogen import oai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    oai = None


class AutoGenAdapter(FrameworkAdapter):
    """Adapter for integrating with Microsoft AutoGen framework.

    This adapter enables AgentGym to work with AutoGen multi-agent systems by
    providing methods to convert between AgentGym's training format and AutoGen's
    agent conversation format.

    Supports both mock mode (testing without API keys) and real mode (with LLMs).

    AutoGen is a framework for building multi-agent applications with:
    - AssistantAgent: AI agents with LLM backing
    - UserProxyAgent: Human proxy or code executor agents
    - GroupChat: Multi-agent conversations
    - GroupChatManager: Orchestrates group conversations

    Attributes:
        framework_name: Always "autogen" for this adapter.
        llm_provider: LLM provider to use ("openai" or "mock")
        model_name: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
        temperature: Temperature for LLM generation
        mock_mode: If True, use mock implementation
        max_consecutive_auto_reply: Max auto-replies for agents

    Example:
        >>> # With OpenAI
        >>> adapter = AutoGenAdapter(llm_provider="openai", model_name="gpt-4")
        >>> agent = adapter.wrap_agent(trained_model)
        >>>
        >>> # Mock mode (for testing)
        >>> adapter = AutoGenAdapter(mock_mode=True)
        >>> agent = adapter.wrap_agent(trained_model)
    """

    framework_name: str = "autogen"

    def __init__(
        self,
        llm_provider: str = "mock",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        mock_mode: bool = False,
        max_consecutive_auto_reply: int = 10,
        verbose: bool = False,
    ):
        """Initialize AutoGen adapter.

        Args:
            llm_provider: LLM provider ("openai", "mock")
            model_name: Model name (default: gpt-3.5-turbo for OpenAI)
            temperature: Temperature for generation (0-1)
            mock_mode: Force mock mode even if API keys available
            max_consecutive_auto_reply: Max auto-replies (default: 10)
            verbose: Enable verbose logging
        """
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.temperature = temperature
        self.mock_mode = mock_mode or not AUTOGEN_AVAILABLE
        self.max_consecutive_auto_reply = max_consecutive_auto_reply
        self.verbose = verbose

        # Auto-detect mock mode if no API keys
        if llm_provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            self.mock_mode = True

    def _create_llm_config(self) -> dict[str, Any]:
        """Create LLM configuration for AutoGen.

        Returns:
            LLM configuration dict or None if mock mode

        Raises:
            ValueError: If provider not supported or API key missing
        """
        if self.mock_mode:
            return {}

        if self.llm_provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ValueError(
                    "OpenAI not available. Install: pip install pyautogen[openai]"
                )

            model = self.model_name or "gpt-3.5-turbo"

            # Create config list
            config_list = [
                {
                    "model": model,
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "temperature": self.temperature,
                }
            ]

            return {
                "config_list": config_list,
                "temperature": self.temperature,
            }

        elif self.llm_provider == "mock":
            return {}

        else:
            raise ValueError(
                f"Unknown LLM provider: {self.llm_provider}. "
                f"Supported: openai, mock"
            )

    def wrap_agent(
        self,
        trained_model: Any,
        agent_type: str = "assistant",
        agents: Optional[list[Any]] = None,
        system_message: Optional[str] = None,
        code_execution: bool = False,
    ) -> Any:
        """Wrap a trained model as an AutoGen agent or multi-agent system.

        Creates a real AutoGen agent if API keys available, otherwise mock.

        Args:
            trained_model: Path to trained model or model object from AgentGym.
                Can be:
                - str: Path to saved model (e.g., "./models/agent_ep100")
                - dict: Model configuration/weights
                - Any: Model object from training
            agent_type: Type of agent ("assistant", "user_proxy", "group_chat")
            agents: List of agents for group chat (only for agent_type="group_chat")
            system_message: System message for the agent
            code_execution: Enable code execution (for user_proxy agents)

        Returns:
            - If real mode: AutoGen Agent instance (AssistantAgent, UserProxyAgent, or GroupChatManager)
            - If mock mode: Dict representing agent structure

        Raises:
            ValueError: If trained_model is invalid or API keys missing in real mode

        Example:
            >>> adapter = AutoGenAdapter(llm_provider="openai")
            >>> assistant = adapter.wrap_agent(trained_model, agent_type="assistant")
            >>> user_proxy = adapter.wrap_agent(trained_model, agent_type="user_proxy")
            >>> group = adapter.wrap_agent(trained_model, agent_type="group_chat",
            ...                            agents=[assistant, user_proxy])
        """
        agents = agents or []

        # Mock mode: Return dict representation
        if self.mock_mode:
            return {
                "type": "autogen_agent",
                "model": trained_model,
                "agent_type": agent_type,
                "agents": agents,
                "system_message": system_message
                or f"You are a helpful {agent_type} agent.",
                "code_execution": code_execution,
                "config": {
                    "max_consecutive_auto_reply": self.max_consecutive_auto_reply,
                    "verbose": self.verbose,
                },
                "_mock": True,  # Flag for testing
            }

        # Real mode: Create AutoGen agents
        llm_config = self._create_llm_config()

        if agent_type == "assistant":
            # Create AssistantAgent
            agent = AssistantAgent(
                name="assistant",
                llm_config=llm_config,
                system_message=system_message or "You are a helpful AI assistant.",
                max_consecutive_auto_reply=self.max_consecutive_auto_reply,
            )

        elif agent_type == "user_proxy":
            # Create UserProxyAgent
            agent = UserProxyAgent(
                name="user_proxy",
                llm_config=llm_config if code_execution else False,
                system_message=system_message or "You are a helpful user proxy.",
                max_consecutive_auto_reply=self.max_consecutive_auto_reply,
                code_execution_config=(
                    {"work_dir": "coding", "use_docker": False}
                    if code_execution
                    else False
                ),
                human_input_mode="NEVER",  # Autonomous for training
            )

        elif agent_type == "group_chat":
            # Create GroupChat with multiple agents
            if not agents:
                raise ValueError(
                    "group_chat requires at least one agent in 'agents' list"
                )

            groupchat = GroupChat(
                agents=agents,
                messages=[],
                max_round=self.max_consecutive_auto_reply,
            )

            agent = GroupChatManager(
                groupchat=groupchat,
                llm_config=llm_config,
            )

        else:
            raise ValueError(
                f"Unknown agent_type: {agent_type}. "
                f"Supported: assistant, user_proxy, group_chat"
            )

        # Store trained model reference for later use
        agent._agentgym_model = trained_model

        return agent

    def extract_tools(self, agent: Any) -> list[Any]:
        """Extract agents/tools from an AutoGen multi-agent system.

        Args:
            agent: AutoGen agent, GroupChatManager, or dict representation

        Returns:
            List of agents in the system (for GroupChat) or single agent as list

        Example:
            >>> agents = adapter.extract_tools(group_chat_manager)
            >>> for agent in agents:
            ...     print(agent.name if hasattr(agent, 'name') else agent['agent_type'])
        """
        # Dict format (mock mode)
        if isinstance(agent, dict):
            agents = agent.get("agents", [])
            if agents:
                return agents
            # Single agent - return as list
            return [agent]

        # GroupChatManager (real or mock)
        if hasattr(agent, "groupchat"):
            return agent.groupchat.agents

        # Single agent - return as list
        return [agent]

    def create_environment(self, agent: Any) -> dict[str, Any]:
        """Create a training environment from an AutoGen agent system.

        Args:
            agent: AutoGen agent, GroupChatManager, or dict representation

        Returns:
            Environment dictionary compatible with Scenario.create_environment()

        Example:
            >>> env = adapter.create_environment(agent)
            >>> print(env["type"])  # "autogen"
            >>> print(len(env["agents"]))  # Number of agents
        """
        agents = self.extract_tools(agent)

        # Extract configuration
        config = {}

        if isinstance(agent, dict):
            # Mock mode
            config = agent.get("config", {})
            config["agent_type"] = agent.get("agent_type", "unknown")
        elif hasattr(agent, "groupchat"):
            # GroupChatManager (real or mock)
            config = {
                "agent_type": "group_chat",
                "max_round": getattr(agent.groupchat, "max_round", 10),
                "num_agents": len(agents),
            }
        elif hasattr(agent, "_max_consecutive_auto_reply"):
            # Single AutoGen agent (real or mock)
            # Determine agent type - safely handle when AssistantAgent is None
            if AUTOGEN_AVAILABLE and isinstance(agent, AssistantAgent):
                agent_type = "assistant"
            elif hasattr(agent, "agent_type"):
                agent_type = agent.agent_type
            else:
                agent_type = "user_proxy"

            config = {
                "agent_type": agent_type,
                "max_consecutive_auto_reply": agent._max_consecutive_auto_reply,
            }

        return {
            "type": "autogen",
            "agent": agent,
            "agents": agents,
            "config": config,
        }

    def validate_agent(self, agent: Any) -> bool:
        """Validate that an agent is compatible with AutoGen.

        Args:
            agent: Agent object to validate

        Returns:
            True if agent is valid AutoGen agent, False otherwise

        Example:
            >>> if adapter.validate_agent(agent):
            ...     env = adapter.create_environment(agent)
        """
        # Dict with correct type (mock mode)
        if isinstance(agent, dict):
            return agent.get("type") == "autogen_agent"

        # Real AutoGen agents
        if AUTOGEN_AVAILABLE:
            if isinstance(agent, (AssistantAgent, UserProxyAgent, GroupChatManager)):
                return True

        # Object with AutoGen-like attributes
        if hasattr(agent, "send") and hasattr(agent, "receive"):
            return True

        return False

    def run_agent(
        self, agent: Any, message: str, recipient: Optional[Any] = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Run the AutoGen agent with given message.

        Convenience method for executing agent conversations.

        Args:
            agent: AutoGen agent or GroupChatManager
            message: Input message for the agent
            recipient: Recipient agent (for direct conversations)
            **kwargs: Additional arguments to pass to agent

        Returns:
            Dict with "messages" key containing conversation history

        Raises:
            ValueError: If mock mode or agent invalid

        Example:
            >>> result = adapter.run_agent(assistant, "What is 2+2?", recipient=user_proxy)
            >>> print(result["messages"])
        """
        if isinstance(agent, dict) or not AUTOGEN_AVAILABLE:
            raise ValueError("Cannot run agent in mock mode. Set up real LLM provider.")

        # For GroupChatManager, initiate chat
        if hasattr(agent, "groupchat"):
            # Get first agent from group chat to initiate
            first_agent = agent.groupchat.agents[0]
            chat_result = first_agent.initiate_chat(agent, message=message, **kwargs)
            return {"messages": chat_result.chat_history}

        # For direct agent conversation
        if recipient is None:
            raise ValueError("recipient is required for direct agent conversations")

        chat_result = agent.initiate_chat(recipient, message=message, **kwargs)
        return {"messages": chat_result.chat_history}
