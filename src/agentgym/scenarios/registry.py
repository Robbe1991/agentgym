"""Scenario registry for dynamic scenario loading.

This module provides a registry system for discovering and loading training scenarios.
The registry allows scenarios to be loaded by name and provides metadata about available scenarios.
"""

from typing import Any

from agentgym.scenarios.base import Scenario


class ScenarioNotFoundError(Exception):
    """Raised when a requested scenario is not found in the registry.

    Attributes:
        scenario_name: The name of the scenario that was not found.
        available_scenarios: List of available scenario names.
    """

    def __init__(self, scenario_name: str, available_scenarios: list[str]):
        """Initialize error with scenario name and available scenarios.

        Args:
            scenario_name: The name of the scenario that was not found.
            available_scenarios: List of available scenario names.
        """
        self.scenario_name = scenario_name
        self.available_scenarios = available_scenarios

        available_str = (
            ", ".join(available_scenarios) if available_scenarios else "none"
        )
        super().__init__(
            f"Scenario '{scenario_name}' not found. "
            f"Available scenarios: {available_str}"
        )


class ScenarioRegistry:
    """Registry for managing and loading training scenarios.

    The registry maintains a dictionary of built-in scenarios and provides
    methods for loading scenarios by name and listing available scenarios.

    This allows the Trainer to dynamically load scenarios without hard-coding
    imports, making it easy to add new scenarios.

    Example:
        >>> # Load a scenario by name
        >>> scenario = ScenarioRegistry.load("customer_support")  # doctest: +SKIP
        >>> print(scenario.name)  # doctest: +SKIP
        customer_support

        >>> # List all available scenarios
        >>> scenarios = ScenarioRegistry.list()  # doctest: +SKIP
        >>> for s in scenarios:  # doctest: +SKIP
        ...     print(f"{s['name']}: {s['description']}")

    Note:
        Built-in scenarios will be added as they are implemented:
        - Issue #6: CustomerSupportScenario
        - Future: CodeReviewScenario, DataAnalysisScenario, etc.
    """

    # Built-in scenarios mapping (name -> scenario class)
    # This will be populated as scenarios are implemented
    BUILT_IN: dict[str, type[Scenario]] = {}
    _built_ins_loaded: bool = False

    # Lazy import to avoid circular dependencies
    @classmethod
    def _ensure_built_in_loaded(cls) -> None:
        """Load built-in scenarios if not already loaded."""
        if not cls._built_ins_loaded:
            from agentgym.scenarios.customer_support import CustomerSupportScenario

            cls.BUILT_IN["customer_support"] = CustomerSupportScenario
            cls._built_ins_loaded = True

    @classmethod
    def load(cls, scenario_name: str) -> Scenario:
        """Load a scenario by name.

        Args:
            scenario_name: Name of the scenario to load (e.g., "customer_support").

        Returns:
            Instantiated scenario object.

        Raises:
            ScenarioNotFoundError: If scenario_name is not in the registry.

        Example:
            >>> scenario = ScenarioRegistry.load("customer_support")  # doctest: +SKIP
            >>> env = scenario.create_environment()  # doctest: +SKIP
        """
        cls._ensure_built_in_loaded()

        if scenario_name not in cls.BUILT_IN:
            available = list(cls.BUILT_IN.keys())
            raise ScenarioNotFoundError(scenario_name, available)

        scenario_class = cls.BUILT_IN[scenario_name]
        return scenario_class()

    @classmethod
    def list(cls) -> list[dict[str, Any]]:
        """List all available scenarios with their metadata.

        Returns:
            List of dictionaries containing scenario metadata:
            - name: Scenario identifier
            - description: Human-readable description
            - difficulty: Difficulty level ("beginner", "intermediate", "advanced")

        Example:
            >>> scenarios = ScenarioRegistry.list()  # doctest: +SKIP
            >>> for scenario in scenarios:  # doctest: +SKIP
            ...     print(f"{scenario['name']} ({scenario['difficulty']})")
            customer_support (beginner)
        """
        cls._ensure_built_in_loaded()

        return [
            {
                "name": name,
                "description": scenario_class.description,
                "difficulty": scenario_class.difficulty,
            }
            for name, scenario_class in cls.BUILT_IN.items()
        ]

    @classmethod
    def register(cls, name: str, scenario_class: type[Scenario]) -> None:
        """Register a new scenario with the registry.

        This allows custom scenarios to be added to the registry at runtime.

        Args:
            name: Unique identifier for the scenario.
            scenario_class: Scenario class (must inherit from Scenario ABC).

        Raises:
            ValueError: If name is already registered or scenario_class is invalid.

        Example:
            >>> class MyScenario(Scenario):  # doctest: +SKIP
            ...     name = "my_scenario"
            ...     description = "Custom scenario"
            ...     difficulty = "beginner"
            ...     # ... implement abstract methods

            >>> ScenarioRegistry.register("my_scenario", MyScenario)  # doctest: +SKIP
            >>> scenario = ScenarioRegistry.load("my_scenario")  # doctest: +SKIP
        """
        if name in cls.BUILT_IN:
            raise ValueError(
                f"Scenario '{name}' is already registered. "
                f"Use a different name or unregister the existing scenario first."
            )

        # Verify it's a Scenario subclass
        if not issubclass(scenario_class, Scenario):
            raise ValueError(
                f"scenario_class must be a subclass of Scenario, "
                f"got {type(scenario_class).__name__}"
            )

        cls.BUILT_IN[name] = scenario_class

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a scenario is registered.

        Args:
            name: Scenario name to check.

        Returns:
            True if scenario is registered, False otherwise.

        Example:
            >>> if ScenarioRegistry.is_registered("customer_support"):  # doctest: +SKIP
            ...     scenario = ScenarioRegistry.load("customer_support")
        """
        return name in cls.BUILT_IN

    @classmethod
    def unregister(cls, name: str) -> None:
        """Unregister a scenario from the registry.

        Args:
            name: Name of scenario to remove.

        Raises:
            ScenarioNotFoundError: If scenario is not registered.

        Example:
            >>> ScenarioRegistry.unregister("my_scenario")  # doctest: +SKIP
        """
        if name not in cls.BUILT_IN:
            available = list(cls.BUILT_IN.keys())
            raise ScenarioNotFoundError(name, available)

        del cls.BUILT_IN[name]

    @classmethod
    def clear(cls) -> None:
        """Clear all registered scenarios.

        Warning:
            This removes ALL scenarios including built-ins.
            Primarily useful for testing.

        Example:
            >>> ScenarioRegistry.clear()  # doctest: +SKIP
            >>> assert len(ScenarioRegistry.list()) == 0  # doctest: +SKIP
        """
        cls.BUILT_IN.clear()
        cls._built_ins_loaded = False
