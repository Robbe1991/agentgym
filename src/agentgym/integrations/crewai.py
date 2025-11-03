"""CrewAI framework adapter with real integration.

This module provides integration with CrewAI framework, enabling:
- Converting trained models to CrewAI agent instances
- Extracting agents and tasks from CrewAI systems
- Creating training environments from existing CrewAI setups
- Supporting multi-agent role-based collaboration

Supports both mock mode (for testing) and real mode (with LLM API keys).

Example:
    >>> from agentgym.integrations.crewai import CrewAIAdapter
    >>> adapter = CrewAIAdapter()
    >>>
    >>> # Wrap a trained model as a CrewAI agent
    >>> agent = adapter.wrap_agent(trained_model, role="Researcher")
    >>>
    >>> # Extract agents from existing CrewAI setup
    >>> agents = adapter.extract_tools(crew)
    >>>
    >>> # Create training environment
    >>> env = adapter.create_environment(crew)
"""

import os
from typing import Any, Optional

from agentgym.integrations.base import FrameworkAdapter

# Try to import CrewAI - graceful degradation if not available
try:
    from crewai import Agent, Task, Crew, Process

    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    Agent = None
    Task = None
    Crew = None
    Process = None

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


class CrewAIAdapter(FrameworkAdapter):
    """Adapter for integrating with CrewAI framework.

    This adapter enables AgentGym to work with CrewAI multi-agent systems by
    providing methods to convert between AgentGym's training format and CrewAI's
    role-based agent collaboration format.

    Supports both mock mode (testing without API keys) and real mode (with LLMs).

    CrewAI is a framework for building role-based autonomous AI agents with:
    - Agent: Role-based agents with specific goals and backstories
    - Task: Work items with descriptions and expected outputs
    - Crew: Team of agents working together
    - Process: Sequential or hierarchical task execution

    Attributes:
        framework_name: Always "crewai" for this adapter.
        llm_provider: LLM provider to use ("openai", "anthropic", or "mock")
        model_name: Model name (e.g., "gpt-4", "claude-3-sonnet")
        temperature: Temperature for LLM generation
        mock_mode: If True, use mock implementation
        process: Process type ("sequential" or "hierarchical")

    Example:
        >>> # With OpenAI
        >>> adapter = CrewAIAdapter(llm_provider="openai", model_name="gpt-4")
        >>> agent = adapter.wrap_agent(trained_model, role="Researcher")
        >>>
        >>> # Mock mode (for testing)
        >>> adapter = CrewAIAdapter(mock_mode=True)
        >>> agent = adapter.wrap_agent(trained_model, role="Analyst")
    """

    framework_name: str = "crewai"

    def __init__(
        self,
        llm_provider: str = "mock",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        mock_mode: bool = False,
        process: str = "sequential",
        verbose: bool = False,
    ):
        """Initialize CrewAI adapter.

        Args:
            llm_provider: LLM provider ("openai", "anthropic", "mock")
            model_name: Model name (default: gpt-3.5-turbo for OpenAI,
                       claude-3-sonnet for Anthropic)
            temperature: Temperature for generation (0-1)
            mock_mode: Force mock mode even if API keys available
            process: Process type ("sequential" or "hierarchical")
            verbose: Enable verbose logging
        """
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.temperature = temperature
        self.mock_mode = mock_mode or not CREWAI_AVAILABLE
        self.process = process
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
        role: str = "Assistant",
        goal: Optional[str] = None,
        backstory: Optional[str] = None,
        tools: Optional[list[Any]] = None,
        allow_delegation: bool = False,
        agent_type: str = "agent",
    ) -> Any:
        """Wrap a trained model as a CrewAI agent or crew.

        Creates a real CrewAI agent if API keys available, otherwise mock.

        Args:
            trained_model: Path to trained model or model object from AgentGym.
                Can be:
                - str: Path to saved model (e.g., "./models/agent_ep100")
                - dict: Model configuration/weights
                - Any: Model object from training
            role: Role of the agent (e.g., "Researcher", "Writer")
            goal: Goal of the agent (what they aim to achieve)
            backstory: Backstory providing context for the agent
            tools: List of tools the agent can use
            allow_delegation: Whether agent can delegate tasks
            agent_type: Type ("agent" or "crew")

        Returns:
            - If real mode: CrewAI Agent or Crew instance
            - If mock mode: Dict representing agent/crew structure

        Raises:
            ValueError: If trained_model is invalid or API keys missing in real mode

        Example:
            >>> adapter = CrewAIAdapter(llm_provider="openai")
            >>> researcher = adapter.wrap_agent(
            ...     trained_model,
            ...     role="Researcher",
            ...     goal="Find and analyze information",
            ...     backstory="Expert researcher with 10 years experience"
            ... )
        """
        tools = tools or []

        # Validate agent_type first
        if agent_type not in ("agent", "crew"):
            raise ValueError(
                f"Unknown agent_type: {agent_type}. Supported: agent, crew"
            )

        # For crew type, validate trained_model structure
        if agent_type == "crew":
            if not isinstance(trained_model, dict) or "agents" not in trained_model:
                raise ValueError(
                    "For agent_type='crew', trained_model must be dict with 'agents' key"
                )

        # Default goal and backstory if not provided
        if goal is None:
            goal = f"Accomplish tasks as a {role}"
        if backstory is None:
            backstory = f"You are a skilled {role} agent"

        # Mock mode: Return dict representation
        if self.mock_mode:
            return {
                "type": "crewai_agent",
                "model": trained_model,
                "agent_type": agent_type,
                "role": role,
                "goal": goal,
                "backstory": backstory,
                "tools": tools,
                "allow_delegation": allow_delegation,
                "config": {
                    "verbose": self.verbose,
                    "process": self.process,
                },
                "_mock": True,  # Flag for testing
            }

        # Real mode: Create CrewAI agent
        llm = self._create_llm()

        if agent_type == "agent":
            agent = Agent(
                role=role,
                goal=goal,
                backstory=backstory,
                tools=tools,
                llm=llm,
                verbose=self.verbose,
                allow_delegation=allow_delegation,
            )

            # Store trained model reference for later use
            agent._agentgym_model = trained_model

            return agent

        elif agent_type == "crew":
            # Extract agents and tasks from trained_model
            agents = trained_model.get("agents", [])
            tasks = trained_model.get("tasks", [])

            # Map process string to Process enum
            process_map = {
                "sequential": Process.sequential,
                "hierarchical": Process.hierarchical,
            }
            process_enum = process_map.get(self.process, Process.sequential)

            crew = Crew(
                agents=agents,
                tasks=tasks,
                process=process_enum,
                verbose=self.verbose,
            )

            crew._agentgym_model = trained_model
            return crew

    def extract_tools(self, agent: Any) -> list[Any]:
        """Extract tools/agents from a CrewAI agent or crew.

        Args:
            agent: CrewAI Agent, Crew, or dict representation

        Returns:
            List of tools (for Agent) or agents (for Crew)

        Example:
            >>> tools = adapter.extract_tools(agent)
            >>> for tool in tools:
            ...     print(tool.name if hasattr(tool, 'name') else tool)
        """
        # Dict format (mock mode)
        if isinstance(agent, dict):
            agent_type = agent.get("agent_type", "agent")
            if agent_type == "crew":
                # For crew, return agents
                model = agent.get("model", {})
                if isinstance(model, dict):
                    return model.get("agents", [])
            # For agent, return tools
            return agent.get("tools", [])

        # Real CrewAI Crew
        if hasattr(agent, "agents"):
            return agent.agents

        # Real CrewAI Agent
        if hasattr(agent, "tools"):
            return agent.tools

        return []

    def create_environment(self, agent: Any) -> dict[str, Any]:
        """Create a training environment from a CrewAI agent or crew.

        Args:
            agent: CrewAI Agent, Crew, or dict representation

        Returns:
            Environment dictionary compatible with Scenario.create_environment()

        Example:
            >>> env = adapter.create_environment(agent)
            >>> print(env["type"])  # "crewai"
            >>> print(env["config"]["role"])  # Agent role
        """
        tools = self.extract_tools(agent)

        # Extract configuration
        config = {}

        if isinstance(agent, dict):
            # Mock mode
            config = {
                "agent_type": agent.get("agent_type", "agent"),
                "role": agent.get("role", "Unknown"),
                "goal": agent.get("goal", ""),
                "backstory": agent.get("backstory", ""),
                "allow_delegation": agent.get("allow_delegation", False),
                "verbose": agent.get("config", {}).get("verbose", False),
                "process": agent.get("config", {}).get("process", "sequential"),
            }
        elif hasattr(agent, "agents"):
            # CrewAI Crew
            config = {
                "agent_type": "crew",
                "num_agents": len(agent.agents),
                "num_tasks": len(getattr(agent, "tasks", [])),
                "process": getattr(agent, "process", "sequential"),
                "verbose": getattr(agent, "verbose", False),
            }
        elif hasattr(agent, "role"):
            # CrewAI Agent
            config = {
                "agent_type": "agent",
                "role": agent.role,
                "goal": getattr(agent, "goal", ""),
                "backstory": getattr(agent, "backstory", ""),
                "allow_delegation": getattr(agent, "allow_delegation", False),
                "verbose": getattr(agent, "verbose", False),
            }

        return {
            "type": "crewai",
            "agent": agent,
            "tools": tools,
            "config": config,
        }

    def validate_agent(self, agent: Any) -> bool:
        """Validate that an agent is compatible with CrewAI.

        Args:
            agent: Agent object to validate

        Returns:
            True if agent is valid CrewAI agent, False otherwise

        Example:
            >>> if adapter.validate_agent(agent):
            ...     env = adapter.create_environment(agent)
        """
        # Dict with correct type (mock mode)
        if isinstance(agent, dict):
            return agent.get("type") == "crewai_agent"

        # Real CrewAI agents
        if CREWAI_AVAILABLE:
            if isinstance(agent, (Agent, Crew)):
                return True

        # Object with CrewAI-like attributes
        if hasattr(agent, "role") and hasattr(agent, "goal"):
            return True

        # Crew-like object
        if hasattr(agent, "agents") and hasattr(agent, "tasks"):
            return True

        return False

    def run_agent(
        self, agent: Any, task: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Run the CrewAI agent or crew with given task.

        Convenience method for executing agent tasks.

        Args:
            agent: CrewAI Agent or Crew
            task: Task description for the agent
            **kwargs: Additional arguments to pass to agent

        Returns:
            Dict with "output" key containing agent response

        Raises:
            ValueError: If mock mode or agent invalid

        Example:
            >>> result = adapter.run_agent(agent, "Research the topic of AI safety")
            >>> print(result["output"])
        """
        if isinstance(agent, dict) or not CREWAI_AVAILABLE:
            raise ValueError("Cannot run agent in mock mode. Set up real LLM provider.")

        # For Crew
        if hasattr(agent, "kickoff"):
            result = agent.kickoff(**kwargs)
            return {"output": str(result)}

        # For single Agent - need to create a task and crew
        if hasattr(agent, "role"):
            # Create a task for the agent
            task_obj = Task(
                description=task,
                agent=agent,
                expected_output="Completed task output"
            )

            # Create a crew with this single agent and task
            crew = Crew(
                agents=[agent],
                tasks=[task_obj],
                verbose=self.verbose,
            )

            result = crew.kickoff(**kwargs)
            return {"output": str(result)}

        raise ValueError(f"Invalid agent type: {type(agent)}")
