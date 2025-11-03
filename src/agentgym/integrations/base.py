"""Base framework adapter interface.

This module provides the abstract base class for framework integrations,
defining the interface that all framework adapters (LangChain, AutoGen, CrewAI)
must implement.
"""

from abc import ABC, abstractmethod
from typing import Any


class FrameworkAdapter(ABC):
    """Abstract base class for framework adapters.

    Framework adapters enable AgentGym to work with different agent frameworks
    (LangChain, AutoGen, CrewAI) by providing a common interface for:
    - Converting trained models to framework-specific agents
    - Extracting tools from existing framework agents
    - Creating training environments from agents

    Subclasses must implement all abstract methods to support their specific
    framework.

    Attributes:
        framework_name: Name of the framework this adapter supports.

    Example:
        >>> class MyFrameworkAdapter(FrameworkAdapter):  # doctest: +SKIP
        ...     framework_name = "my_framework"
        ...
        ...     def wrap_agent(self, trained_model):
        ...         # Convert trained model to MyFramework agent
        ...         return MyFrameworkAgent(trained_model)
        ...
        ...     def extract_tools(self, agent):
        ...         # Extract tools from MyFramework agent
        ...         return agent.tools
        ...
        ...     def create_environment(self, agent):
        ...         # Create training environment
        ...         return {"type": "my_framework", "agent": agent}
    """

    framework_name: str = "base"

    @abstractmethod
    def wrap_agent(self, trained_model: Any) -> Any:
        """Wrap a trained model as a framework-specific agent.

        This method converts an AgentGym trained model into an agent
        compatible with the target framework (e.g., LangChain AgentExecutor,
        AutoGen ConversableAgent).

        Args:
            trained_model: Trained model from AgentGym (typically a path
                to saved model weights or a model object).

        Returns:
            Framework-specific agent object ready for deployment.

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
            ValueError: If trained_model is invalid or incompatible.

        Example:
            >>> adapter = MyFrameworkAdapter()  # doctest: +SKIP
            >>> model_path = "./models/customer_support_ep100"  # doctest: +SKIP
            >>> agent = adapter.wrap_agent(model_path)  # doctest: +SKIP
            >>> # agent is now a MyFramework-compatible agent
        """
        pass

    @abstractmethod
    def extract_tools(self, agent: Any) -> list[Any]:
        """Extract tools from a framework agent.

        This method extracts the list of tools/functions available to an
        agent in the target framework. This is useful for:
        - Analyzing existing agents
        - Migrating agents between frameworks
        - Creating training scenarios based on existing agents

        Args:
            agent: Framework-specific agent object.

        Returns:
            List of tool objects from the framework.

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
            ValueError: If agent is invalid or has no tools.

        Example:
            >>> adapter = MyFrameworkAdapter()  # doctest: +SKIP
            >>> agent = get_existing_agent()  # doctest: +SKIP
            >>> tools = adapter.extract_tools(agent)  # doctest: +SKIP
            >>> print([tool.name for tool in tools])  # doctest: +SKIP
            ['search', 'calculator', 'weather']
        """
        pass

    @abstractmethod
    def create_environment(self, agent: Any) -> dict[str, Any]:
        """Create a training environment from a framework agent.

        This method creates an environment dict suitable for AgentGym training
        based on an existing framework agent. The environment should include:
        - Agent reference
        - Available tools/actions
        - State/action space definitions
        - Any framework-specific configuration

        Args:
            agent: Framework-specific agent object.

        Returns:
            Environment dictionary compatible with Scenario.create_environment().

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
            ValueError: If agent is invalid or incompatible.

        Example:
            >>> adapter = MyFrameworkAdapter()  # doctest: +SKIP
            >>> agent = get_existing_agent()  # doctest: +SKIP
            >>> env = adapter.create_environment(agent)  # doctest: +SKIP
            >>> print(env.keys())  # doctest: +SKIP
            dict_keys(['type', 'agent', 'tools', 'config'])
        """
        pass

    def validate_agent(self, agent: Any) -> bool:
        """Validate that an agent is compatible with this adapter.

        Default implementation returns True. Subclasses can override to add
        framework-specific validation logic.

        Args:
            agent: Agent object to validate.

        Returns:
            True if agent is valid for this framework, False otherwise.

        Example:
            >>> adapter = MyFrameworkAdapter()  # doctest: +SKIP
            >>> agent = get_agent()  # doctest: +SKIP
            >>> if adapter.validate_agent(agent):  # doctest: +SKIP
            ...     env = adapter.create_environment(agent)
        """
        return True

    def get_framework_info(self) -> dict[str, Any]:
        """Get information about the framework this adapter supports.

        Returns:
            Dictionary containing framework metadata:
            - name: Framework name
            - adapter_class: This adapter's class name
            - methods: List of available methods

        Example:
            >>> adapter = MyFrameworkAdapter()  # doctest: +SKIP
            >>> info = adapter.get_framework_info()  # doctest: +SKIP
            >>> print(info["name"])  # doctest: +SKIP
            my_framework
        """
        return {
            "name": self.framework_name,
            "adapter_class": self.__class__.__name__,
            "methods": ["wrap_agent", "extract_tools", "create_environment"],
        }

    def __repr__(self) -> str:
        """String representation of the adapter.

        Returns:
            String showing adapter class and framework name.

        Example:
            >>> adapter = MyFrameworkAdapter()  # doctest: +SKIP
            >>> print(repr(adapter))  # doctest: +SKIP
            MyFrameworkAdapter(framework='my_framework')
        """
        return f"{self.__class__.__name__}(framework='{self.framework_name}')"
