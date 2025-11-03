"""LangChain framework adapter.

This module provides integration with LangChain agents, enabling:
- Converting trained models to LangChain AgentExecutor instances
- Extracting tools from LangChain agents
- Creating training environments from existing LangChain agents

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

from typing import Any

from agentgym.integrations.base import FrameworkAdapter


class LangChainAdapter(FrameworkAdapter):
    """Adapter for integrating with LangChain framework.

    This adapter enables AgentGym to work with LangChain agents by providing
    methods to convert between AgentGym's training format and LangChain's
    AgentExecutor format.

    LangChain is a popular framework for building LLM applications with:
    - AgentExecutor: Main agent runtime
    - Tools: Functions the agent can call
    - Chains: Sequences of operations
    - Memory: Conversation history

    Attributes:
        framework_name: Always "langchain" for this adapter.

    Example:
        >>> adapter = LangChainAdapter()  # doctest: +SKIP
        >>>
        >>> # Wrap trained model
        >>> model_path = "./models/customer_support_ep100"  # doctest: +SKIP
        >>> agent = adapter.wrap_agent(model_path)  # doctest: +SKIP
        >>>
        >>> # Extract tools
        >>> tools = adapter.extract_tools(agent)  # doctest: +SKIP
        >>> print([tool.name for tool in tools])  # doctest: +SKIP
        ['search', 'calculator']
        >>>
        >>> # Create environment for training
        >>> env = adapter.create_environment(agent)  # doctest: +SKIP
    """

    framework_name: str = "langchain"

    def wrap_agent(self, trained_model: Any) -> dict[str, Any]:
        """Wrap a trained model as a LangChain-compatible agent.

        This method converts an AgentGym trained model into a structure
        compatible with LangChain's AgentExecutor. In the current
        implementation, this creates a mock structure suitable for testing.

        In a full implementation, this would:
        1. Load the trained model weights
        2. Create a LangChain LLM with the model
        3. Initialize tools based on the training scenario
        4. Build an AgentExecutor with the LLM and tools

        Args:
            trained_model: Path to trained model or model object from AgentGym.
                Can be:
                - str: Path to saved model (e.g., "./models/agent_ep100")
                - dict: Model configuration/weights
                - Any: Model object from training

        Returns:
            Dictionary representing a LangChain agent with structure:
            {
                "type": "langchain_agent",
                "model": trained_model,
                "tools": list,
                "memory": dict,
                "executor": dict (AgentExecutor-like structure)
            }

        Raises:
            ValueError: If trained_model is invalid or incompatible.

        Example:
            >>> adapter = LangChainAdapter()  # doctest: +SKIP
            >>> agent = adapter.wrap_agent("./models/support_agent")  # doctest: +SKIP
            >>> print(agent["type"])  # doctest: +SKIP
            langchain_agent
        """
        # Mock implementation for Week 1
        # Full implementation in Week 2-3 will integrate with actual LangChain
        return {
            "type": "langchain_agent",
            "model": trained_model,
            "tools": [],
            "memory": {},
            "executor": {
                "agent_type": "zero-shot-react-description",
                "verbose": False,
            },
        }

    def extract_tools(self, agent: Any) -> list[Any]:
        """Extract tools from a LangChain agent.

        This method extracts the list of tools available to a LangChain agent.
        LangChain tools have a standard structure with name, description,
        and a function to call.

        Args:
            agent: LangChain agent (typically AgentExecutor) or dict representation.
                Expected to have one of:
                - agent.tools: List of LangChain Tool objects
                - agent["tools"]: List of tools in dict format

        Returns:
            List of tools. Each tool may be:
            - LangChain Tool object (in full implementation)
            - Dict with tool information (in mock implementation)
            Empty list if agent has no tools.

        Raises:
            ValueError: If agent format is invalid or unsupported.

        Example:
            >>> adapter = LangChainAdapter()  # doctest: +SKIP
            >>> agent = get_langchain_agent()  # doctest: +SKIP
            >>> tools = adapter.extract_tools(agent)  # doctest: +SKIP
            >>> for tool in tools:  # doctest: +SKIP
            ...     print(f"{tool.name}: {tool.description}")
            search: Search the web
            calculator: Perform calculations
        """
        # Support both dict and object formats
        if isinstance(agent, dict):
            return agent.get("tools", [])

        # For LangChain AgentExecutor objects (future implementation)
        if hasattr(agent, "tools"):
            return agent.tools

        return []

    def create_environment(self, agent: Any) -> dict[str, Any]:
        """Create a training environment from a LangChain agent.

        This method creates an environment dictionary suitable for AgentGym
        training based on an existing LangChain agent. The environment includes
        the agent's tools, configuration, and metadata needed for training.

        Args:
            agent: LangChain agent (AgentExecutor) or dict representation.

        Returns:
            Environment dictionary compatible with Scenario.create_environment():
            {
                "type": "langchain",
                "agent": agent,
                "tools": list of tools,
                "config": {
                    "agent_type": str,
                    "verbose": bool,
                    ...
                }
            }

        Raises:
            ValueError: If agent is invalid or incompatible.

        Example:
            >>> adapter = LangChainAdapter()  # doctest: +SKIP
            >>> agent = get_langchain_agent()  # doctest: +SKIP
            >>> env = adapter.create_environment(agent)  # doctest: +SKIP
            >>> print(env["type"])  # doctest: +SKIP
            langchain
            >>> print(len(env["tools"]))  # doctest: +SKIP
            5
        """
        tools = self.extract_tools(agent)

        # Extract configuration from agent
        config = {}
        if isinstance(agent, dict):
            config = agent.get("executor", {})
        elif hasattr(agent, "agent"):
            # LangChain AgentExecutor has .agent attribute
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

        This method checks if an agent object is a valid LangChain agent
        or dict representation. Overrides the base class to add framework-
        specific validation.

        Args:
            agent: Agent object to validate.

        Returns:
            True if agent is a valid LangChain agent, False otherwise.

        Example:
            >>> adapter = LangChainAdapter()  # doctest: +SKIP
            >>> agent = adapter.wrap_agent(trained_model)  # doctest: +SKIP
            >>> if adapter.validate_agent(agent):  # doctest: +SKIP
            ...     env = adapter.create_environment(agent)
        """
        # Accept dict with "type" = "langchain_agent"
        if isinstance(agent, dict):
            return agent.get("type") == "langchain_agent"

        # Accept LangChain AgentExecutor objects (future)
        # Check for common LangChain agent attributes
        if hasattr(agent, "agent") and hasattr(agent, "tools"):
            return True

        return False
