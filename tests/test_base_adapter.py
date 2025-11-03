"""Tests for base framework adapter.

This module contains comprehensive tests for the FrameworkAdapter ABC,
including abstract method enforcement and default implementations.
"""

import pytest

from agentgym.integrations.base import FrameworkAdapter


class ConcreteAdapter(FrameworkAdapter):
    """Concrete adapter for testing base class."""

    framework_name = "test_framework"

    def wrap_agent(self, trained_model):
        """Wrap trained model."""
        return {"agent": trained_model, "framework": "test"}

    def extract_tools(self, agent):
        """Extract tools from agent."""
        return agent.get("tools", [])

    def create_environment(self, agent):
        """Create environment from agent."""
        return {
            "type": "test_environment",
            "agent": agent,
            "tools": self.extract_tools(agent),
        }


class MinimalAdapter(FrameworkAdapter):
    """Minimal adapter with only required methods."""

    framework_name = "minimal"

    def wrap_agent(self, trained_model):
        return trained_model

    def extract_tools(self, agent):
        return []

    def create_environment(self, agent):
        return {}


class TestFrameworkAdapterAbstractMethods:
    """Test abstract method enforcement."""

    def test_cannot_instantiate_abstract_adapter(self):
        """Test that FrameworkAdapter ABC cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            FrameworkAdapter()  # type: ignore

    def test_must_implement_wrap_agent(self):
        """Test that wrap_agent must be implemented."""

        class IncompleteAdapter1(FrameworkAdapter):
            framework_name = "incomplete"

            def extract_tools(self, agent):
                return []

            def create_environment(self, agent):
                return {}

        with pytest.raises(TypeError):
            IncompleteAdapter1()  # type: ignore

    def test_must_implement_extract_tools(self):
        """Test that extract_tools must be implemented."""

        class IncompleteAdapter2(FrameworkAdapter):
            framework_name = "incomplete"

            def wrap_agent(self, trained_model):
                return trained_model

            def create_environment(self, agent):
                return {}

        with pytest.raises(TypeError):
            IncompleteAdapter2()  # type: ignore

    def test_must_implement_create_environment(self):
        """Test that create_environment must be implemented."""

        class IncompleteAdapter3(FrameworkAdapter):
            framework_name = "incomplete"

            def wrap_agent(self, trained_model):
                return trained_model

            def extract_tools(self, agent):
                return []

        with pytest.raises(TypeError):
            IncompleteAdapter3()  # type: ignore


class TestConcreteAdapter:
    """Test concrete adapter implementations."""

    def test_initialization(self):
        """Test creating concrete adapter."""
        adapter = ConcreteAdapter()

        assert adapter.framework_name == "test_framework"

    def test_wrap_agent(self):
        """Test wrapping trained model as agent."""
        adapter = ConcreteAdapter()
        trained_model = {"model": "trained", "weights": [1, 2, 3]}

        agent = adapter.wrap_agent(trained_model)

        assert isinstance(agent, dict)
        assert agent["agent"] == trained_model
        assert agent["framework"] == "test"

    def test_extract_tools_with_tools(self):
        """Test extracting tools from agent with tools."""
        adapter = ConcreteAdapter()
        agent = {"tools": ["search", "calculator", "weather"]}

        tools = adapter.extract_tools(agent)

        assert tools == ["search", "calculator", "weather"]

    def test_extract_tools_without_tools(self):
        """Test extracting tools from agent without tools."""
        adapter = ConcreteAdapter()
        agent = {"name": "test_agent"}

        tools = adapter.extract_tools(agent)

        assert tools == []

    def test_create_environment(self):
        """Test creating environment from agent."""
        adapter = ConcreteAdapter()
        agent = {"name": "test_agent", "tools": ["search"]}

        env = adapter.create_environment(agent)

        assert env["type"] == "test_environment"
        assert env["agent"] == agent
        assert env["tools"] == ["search"]

    def test_create_environment_without_tools(self):
        """Test creating environment from agent without tools."""
        adapter = ConcreteAdapter()
        agent = {"name": "test_agent"}

        env = adapter.create_environment(agent)

        assert env["type"] == "test_environment"
        assert env["agent"] == agent
        assert env["tools"] == []


class TestDefaultMethods:
    """Test default method implementations."""

    def test_validate_agent_default_true(self):
        """Test that default validate_agent returns True."""
        adapter = ConcreteAdapter()

        assert adapter.validate_agent({"any": "agent"}) is True
        assert adapter.validate_agent(None) is True
        assert adapter.validate_agent("string") is True

    def test_get_framework_info(self):
        """Test getting framework information."""
        adapter = ConcreteAdapter()

        info = adapter.get_framework_info()

        assert info["name"] == "test_framework"
        assert info["adapter_class"] == "ConcreteAdapter"
        assert "wrap_agent" in info["methods"]
        assert "extract_tools" in info["methods"]
        assert "create_environment" in info["methods"]

    def test_repr(self):
        """Test __repr__ method."""
        adapter = ConcreteAdapter()

        repr_str = repr(adapter)

        assert "ConcreteAdapter" in repr_str
        assert "test_framework" in repr_str


class TestMinimalAdapter:
    """Test minimal adapter implementation."""

    def test_minimal_adapter_works(self):
        """Test that minimal implementation satisfies interface."""
        adapter = MinimalAdapter()

        assert adapter.framework_name == "minimal"

        # Should be able to call all required methods
        agent = adapter.wrap_agent("model")
        assert agent == "model"

        tools = adapter.extract_tools(agent)
        assert tools == []

        env = adapter.create_environment(agent)
        assert env == {}


class TestAdapterWithCustomValidation:
    """Test adapter with custom validation logic."""

    def test_custom_validation(self):
        """Test adapter with overridden validate_agent."""

        class ValidatingAdapter(ConcreteAdapter):
            def validate_agent(self, agent):
                """Only accept dict agents with 'name' key."""
                return isinstance(agent, dict) and "name" in agent

        adapter = ValidatingAdapter()

        # Valid agent
        assert adapter.validate_agent({"name": "test"}) is True

        # Invalid agents
        assert adapter.validate_agent({}) is False
        assert adapter.validate_agent("string") is False
        assert adapter.validate_agent(None) is False


class TestAdapterIntegration:
    """Integration tests for adapter usage."""

    def test_complete_workflow(self):
        """Test complete workflow: wrap, extract, create environment."""
        adapter = ConcreteAdapter()

        # 1. Wrap a trained model
        trained_model = {"model": "customer_support", "weights": [1, 2, 3]}
        agent = adapter.wrap_agent(trained_model)

        assert agent is not None
        assert "agent" in agent

        # 2. Add tools to agent
        agent["tools"] = ["search_kb", "update_ticket"]

        # 3. Extract tools
        tools = adapter.extract_tools(agent)
        assert len(tools) == 2

        # 4. Create environment
        env = adapter.create_environment(agent)
        assert env["type"] == "test_environment"
        assert env["tools"] == tools

    def test_multiple_adapters_independent(self):
        """Test that multiple adapters are independent."""
        adapter1 = ConcreteAdapter()
        adapter2 = MinimalAdapter()

        assert adapter1.framework_name != adapter2.framework_name

        model = {"weights": [1, 2, 3]}
        agent1 = adapter1.wrap_agent(model)
        agent2 = adapter2.wrap_agent(model)

        # Different adapters produce different results
        assert agent1 != agent2

    def test_adapter_reusability(self):
        """Test that adapter can be reused for multiple agents."""
        adapter = ConcreteAdapter()

        # Wrap multiple models
        model1 = {"id": 1}
        model2 = {"id": 2}
        model3 = {"id": 3}

        agent1 = adapter.wrap_agent(model1)
        agent2 = adapter.wrap_agent(model2)
        agent3 = adapter.wrap_agent(model3)

        assert agent1["agent"]["id"] == 1
        assert agent2["agent"]["id"] == 2
        assert agent3["agent"]["id"] == 3


class TestFrameworkInfo:
    """Test framework information methods."""

    def test_framework_info_different_adapters(self):
        """Test that different adapters report different info."""
        adapter1 = ConcreteAdapter()
        adapter2 = MinimalAdapter()

        info1 = adapter1.get_framework_info()
        info2 = adapter2.get_framework_info()

        assert info1["name"] != info2["name"]
        assert info1["adapter_class"] != info2["adapter_class"]

    def test_framework_info_structure(self):
        """Test that framework info has expected structure."""
        adapter = ConcreteAdapter()
        info = adapter.get_framework_info()

        # Required keys
        assert "name" in info
        assert "adapter_class" in info
        assert "methods" in info

        # Types
        assert isinstance(info["name"], str)
        assert isinstance(info["adapter_class"], str)
        assert isinstance(info["methods"], list)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_wrap_agent_with_none(self):
        """Test wrapping None as trained model."""
        adapter = ConcreteAdapter()

        agent = adapter.wrap_agent(None)

        assert agent is not None
        assert agent["agent"] is None

    def test_extract_tools_from_invalid_agent(self):
        """Test extracting tools from dict agent without tools key."""
        adapter = ConcreteAdapter()

        # Dict without tools key
        tools = adapter.extract_tools({})
        assert tools == []

        # Dict with None tools
        tools = adapter.extract_tools({"tools": None})
        assert tools is None

        # Dict with empty tools
        tools = adapter.extract_tools({"tools": []})
        assert tools == []

    def test_create_environment_with_minimal_agent(self):
        """Test creating environment with minimal agent data."""
        adapter = ConcreteAdapter()

        env = adapter.create_environment({})

        assert isinstance(env, dict)
        assert "type" in env
        assert "agent" in env

    def test_repr_with_different_names(self):
        """Test repr with different framework names."""
        adapter1 = ConcreteAdapter()
        adapter2 = MinimalAdapter()

        repr1 = repr(adapter1)
        repr2 = repr(adapter2)

        assert "test_framework" in repr1
        assert "minimal" in repr2
        assert repr1 != repr2
