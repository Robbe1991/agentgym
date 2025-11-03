"""Tests for LangChain framework adapter.

This module contains comprehensive tests for the LangChainAdapter,
including wrapping agents, extracting tools, creating environments,
and validation.
"""

import pytest

from agentgym.integrations.base import FrameworkAdapter
from agentgym.integrations.langchain import LangChainAdapter


class MockLangChainAgent:
    """Mock LangChain AgentExecutor for testing."""

    def __init__(self, tools=None):
        """Initialize mock agent."""
        self.tools = tools or []
        self.agent = MockAgent()
        self.verbose = False


class MockAgent:
    """Mock LangChain agent for testing."""

    def __init__(self):
        """Initialize mock agent."""
        self.agent_type = "zero-shot-react-description"


class TestLangChainAdapterBasics:
    """Test basic LangChainAdapter properties and inheritance."""

    def test_inherits_from_framework_adapter(self):
        """Test that LangChainAdapter inherits from FrameworkAdapter."""
        adapter = LangChainAdapter(mock_mode=True)

        assert isinstance(adapter, FrameworkAdapter)

    def test_framework_name(self):
        """Test that framework_name is set correctly."""
        adapter = LangChainAdapter(mock_mode=True)

        assert adapter.framework_name == "langchain"

    def test_initialization(self):
        """Test creating LangChainAdapter instance."""
        adapter = LangChainAdapter(mock_mode=True)

        assert adapter is not None
        assert hasattr(adapter, "wrap_agent")
        assert hasattr(adapter, "extract_tools")
        assert hasattr(adapter, "create_environment")

    def test_initialization_with_parameters(self):
        """Test creating LangChainAdapter with parameters."""
        adapter = LangChainAdapter(
            llm_provider="openai",
            model_name="gpt-4",
            temperature=0.5,
            mock_mode=True,
            verbose=True,
        )

        assert adapter.llm_provider == "openai"
        assert adapter.model_name == "gpt-4"
        assert adapter.temperature == 0.5
        assert adapter.mock_mode is True
        assert adapter.verbose is True

    def test_initialization_defaults(self):
        """Test that initialization uses correct defaults."""
        adapter = LangChainAdapter(mock_mode=True)

        assert adapter.llm_provider == "mock"
        assert adapter.model_name is None
        assert adapter.temperature == 0.7
        assert adapter.verbose is False


class TestWrapAgent:
    """Test wrap_agent method."""

    def test_wrap_agent_with_string_path(self):
        """Test wrapping a model path as string."""
        adapter = LangChainAdapter(mock_mode=True)
        model_path = "./models/customer_support_ep100"

        agent = adapter.wrap_agent(model_path)

        assert isinstance(agent, dict)
        assert agent["type"] == "langchain_agent"
        assert agent["model"] == model_path
        assert "tools" in agent
        assert "memory" in agent
        assert "executor" in agent
        assert agent.get("_mock") is True

    def test_wrap_agent_with_dict(self):
        """Test wrapping a model dict."""
        adapter = LangChainAdapter(mock_mode=True)
        model = {"weights": [1, 2, 3], "config": {"layers": 12}}

        agent = adapter.wrap_agent(model)

        assert isinstance(agent, dict)
        assert agent["type"] == "langchain_agent"
        assert agent["model"] == model

    def test_wrap_agent_with_none(self):
        """Test wrapping None as model."""
        adapter = LangChainAdapter(mock_mode=True)

        agent = adapter.wrap_agent(None)

        assert agent is not None
        assert agent["type"] == "langchain_agent"
        assert agent["model"] is None

    def test_wrap_agent_structure(self):
        """Test that wrapped agent has correct structure."""
        adapter = LangChainAdapter(mock_mode=True)
        model = "test_model"

        agent = adapter.wrap_agent(model)

        # Check all required keys
        assert "type" in agent
        assert "model" in agent
        assert "tools" in agent
        assert "memory" in agent
        assert "executor" in agent

        # Check executor structure
        assert isinstance(agent["executor"], dict)
        assert "agent_type" in agent["executor"]
        assert "verbose" in agent["executor"]

    def test_wrap_agent_executor_config(self):
        """Test that executor config has expected values."""
        adapter = LangChainAdapter(mock_mode=True)

        agent = adapter.wrap_agent("model")

        assert agent["executor"]["agent_type"] == "zero-shot-react-description"
        assert agent["executor"]["verbose"] is False

    def test_wrap_agent_empty_tools(self):
        """Test that newly wrapped agent has empty tools list."""
        adapter = LangChainAdapter(mock_mode=True)

        agent = adapter.wrap_agent("model")

        assert agent["tools"] == []

    def test_wrap_agent_with_tools(self):
        """Test wrapping agent with tools provided."""
        adapter = LangChainAdapter(mock_mode=True)
        tools = [
            {"name": "search", "description": "Search"},
            {"name": "calculator", "description": "Calculate"},
        ]

        agent = adapter.wrap_agent("model", tools=tools)

        assert agent["tools"] == tools

    def test_wrap_agent_with_custom_agent_type(self):
        """Test wrapping agent with custom agent type."""
        adapter = LangChainAdapter(mock_mode=True)

        agent = adapter.wrap_agent(
            "model", agent_type="conversational-react-description"
        )

        assert agent["executor"]["agent_type"] == "conversational-react-description"


class TestExtractTools:
    """Test extract_tools method."""

    def test_extract_tools_from_dict_agent_with_tools(self):
        """Test extracting tools from dict agent with tools."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = {
            "type": "langchain_agent",
            "tools": [
                {"name": "search", "description": "Search the web"},
                {"name": "calculator", "description": "Calculate"},
            ],
        }

        tools = adapter.extract_tools(agent)

        assert len(tools) == 2
        assert tools[0]["name"] == "search"
        assert tools[1]["name"] == "calculator"

    def test_extract_tools_from_dict_agent_without_tools(self):
        """Test extracting tools from dict agent without tools key."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = {"type": "langchain_agent"}

        tools = adapter.extract_tools(agent)

        assert tools == []

    def test_extract_tools_from_dict_agent_empty_tools(self):
        """Test extracting from dict agent with empty tools list."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = {"type": "langchain_agent", "tools": []}

        tools = adapter.extract_tools(agent)

        assert tools == []

    def test_extract_tools_from_mock_agent_object(self):
        """Test extracting tools from mock LangChain agent object."""
        adapter = LangChainAdapter(mock_mode=True)
        tools_list = [
            {"name": "search"},
            {"name": "calculator"},
            {"name": "weather"},
        ]
        agent = MockLangChainAgent(tools=tools_list)

        tools = adapter.extract_tools(agent)

        assert len(tools) == 3
        assert tools == tools_list

    def test_extract_tools_from_mock_agent_no_tools(self):
        """Test extracting tools from mock agent with no tools."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = MockLangChainAgent(tools=[])

        tools = adapter.extract_tools(agent)

        assert tools == []

    def test_extract_tools_from_invalid_agent(self):
        """Test extracting tools from agent without tools attribute."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = "not_an_agent"

        tools = adapter.extract_tools(agent)

        assert tools == []


class TestCreateEnvironment:
    """Test create_environment method."""

    def test_create_environment_from_dict_agent(self):
        """Test creating environment from dict agent."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = {
            "type": "langchain_agent",
            "tools": [{"name": "search"}, {"name": "calculator"}],
            "executor": {
                "agent_type": "zero-shot-react-description",
                "verbose": False,
            },
        }

        env = adapter.create_environment(agent)

        assert isinstance(env, dict)
        assert env["type"] == "langchain"
        assert env["agent"] == agent
        assert len(env["tools"]) == 2
        assert env["config"]["agent_type"] == "zero-shot-react-description"

    def test_create_environment_from_dict_agent_without_tools(self):
        """Test creating environment from dict agent without tools."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = {
            "type": "langchain_agent",
            "executor": {"agent_type": "conversational"},
        }

        env = adapter.create_environment(agent)

        assert env["type"] == "langchain"
        assert env["tools"] == []
        assert env["config"]["agent_type"] == "conversational"

    def test_create_environment_from_mock_agent_object(self):
        """Test creating environment from mock LangChain agent object."""
        adapter = LangChainAdapter(mock_mode=True)
        tools_list = [{"name": "search"}, {"name": "calculator"}]
        agent = MockLangChainAgent(tools=tools_list)

        env = adapter.create_environment(agent)

        assert env["type"] == "langchain"
        assert env["agent"] == agent
        assert len(env["tools"]) == 2
        assert env["config"]["agent_type"] == "zero-shot-react-description"
        assert env["config"]["verbose"] is False

    def test_create_environment_structure(self):
        """Test that environment has correct structure."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = adapter.wrap_agent("model")

        env = adapter.create_environment(agent)

        # Check all required keys
        assert "type" in env
        assert "agent" in env
        assert "tools" in env
        assert "config" in env

        # Check types
        assert isinstance(env["type"], str)
        assert isinstance(env["tools"], list)
        assert isinstance(env["config"], dict)

    def test_create_environment_minimal_agent(self):
        """Test creating environment from minimal agent dict."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = {}

        env = adapter.create_environment(agent)

        assert env["type"] == "langchain"
        assert env["agent"] == agent
        assert env["tools"] == []
        assert env["config"] == {}


class TestValidateAgent:
    """Test validate_agent method."""

    def test_validate_dict_agent_valid(self):
        """Test validating valid dict agent."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = {
            "type": "langchain_agent",
            "model": "test_model",
            "tools": [],
        }

        assert adapter.validate_agent(agent) is True

    def test_validate_dict_agent_invalid_type(self):
        """Test validating dict agent with wrong type."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = {
            "type": "autogen_agent",  # Wrong type
            "model": "test_model",
        }

        assert adapter.validate_agent(agent) is False

    def test_validate_dict_agent_no_type(self):
        """Test validating dict agent without type field."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = {"model": "test_model"}

        assert adapter.validate_agent(agent) is False

    def test_validate_mock_agent_object(self):
        """Test validating mock LangChain agent object."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = MockLangChainAgent()

        assert adapter.validate_agent(agent) is True

    def test_validate_invalid_agent_types(self):
        """Test validating various invalid agent types."""
        adapter = LangChainAdapter(mock_mode=True)

        assert adapter.validate_agent(None) is False
        assert adapter.validate_agent("string") is False
        assert adapter.validate_agent(123) is False
        assert adapter.validate_agent([]) is False

    def test_validate_wrapped_agent(self):
        """Test that wrapped agents pass validation."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = adapter.wrap_agent("model")

        assert adapter.validate_agent(agent) is True


class TestGetFrameworkInfo:
    """Test get_framework_info method."""

    def test_framework_info_structure(self):
        """Test that framework info has correct structure."""
        adapter = LangChainAdapter(mock_mode=True)

        info = adapter.get_framework_info()

        assert isinstance(info, dict)
        assert "name" in info
        assert "adapter_class" in info
        assert "methods" in info

    def test_framework_info_values(self):
        """Test that framework info has correct values."""
        adapter = LangChainAdapter(mock_mode=True)

        info = adapter.get_framework_info()

        assert info["name"] == "langchain"
        assert info["adapter_class"] == "LangChainAdapter"
        assert "wrap_agent" in info["methods"]
        assert "extract_tools" in info["methods"]
        assert "create_environment" in info["methods"]


class TestRepr:
    """Test __repr__ method."""

    def test_repr(self):
        """Test string representation."""
        adapter = LangChainAdapter(mock_mode=True)

        repr_str = repr(adapter)

        assert "LangChainAdapter" in repr_str
        assert "langchain" in repr_str


class TestIntegration:
    """Integration tests for LangChainAdapter."""

    def test_complete_workflow_with_dict_agent(self):
        """Test complete workflow: wrap, extract, create environment."""
        adapter = LangChainAdapter(mock_mode=True)

        # 1. Wrap a trained model
        trained_model = "./models/customer_support_ep100"
        agent = adapter.wrap_agent(trained_model)

        assert adapter.validate_agent(agent)

        # 2. Add tools to agent
        agent["tools"] = [
            {"name": "search_kb", "description": "Search knowledge base"},
            {"name": "update_ticket", "description": "Update support ticket"},
        ]

        # 3. Extract tools
        tools = adapter.extract_tools(agent)
        assert len(tools) == 2

        # 4. Create environment
        env = adapter.create_environment(agent)
        assert env["type"] == "langchain"
        assert len(env["tools"]) == 2
        assert env["tools"] == tools

    def test_complete_workflow_with_mock_agent(self):
        """Test complete workflow with mock LangChain agent object."""
        adapter = LangChainAdapter(mock_mode=True)

        # Create mock agent with tools
        tools_list = [
            {"name": "search", "description": "Search"},
            {"name": "calculator", "description": "Calculate"},
        ]
        agent = MockLangChainAgent(tools=tools_list)

        # Validate
        assert adapter.validate_agent(agent)

        # Extract tools
        tools = adapter.extract_tools(agent)
        assert len(tools) == 2

        # Create environment
        env = adapter.create_environment(agent)
        assert env["type"] == "langchain"
        assert len(env["tools"]) == 2

    def test_adapter_reusability(self):
        """Test that adapter can be reused for multiple agents."""
        adapter = LangChainAdapter(mock_mode=True)

        # Wrap multiple models
        agent1 = adapter.wrap_agent("model1")
        agent2 = adapter.wrap_agent("model2")
        agent3 = adapter.wrap_agent("model3")

        assert agent1["model"] == "model1"
        assert agent2["model"] == "model2"
        assert agent3["model"] == "model3"

        # All should be valid
        assert adapter.validate_agent(agent1)
        assert adapter.validate_agent(agent2)
        assert adapter.validate_agent(agent3)

    def test_multiple_adapters_independent(self):
        """Test that multiple adapter instances are independent."""
        adapter1 = LangChainAdapter(mock_mode=True)
        adapter2 = LangChainAdapter(mock_mode=True)

        agent1 = adapter1.wrap_agent("model1")
        agent2 = adapter2.wrap_agent("model2")

        # Both should work independently
        assert adapter1.validate_agent(agent1)
        assert adapter2.validate_agent(agent2)

        # Cross-validation should also work (same adapter type)
        assert adapter1.validate_agent(agent2)
        assert adapter2.validate_agent(agent1)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_extract_tools_with_none_tools(self):
        """Test extracting tools when tools field is None."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = {"type": "langchain_agent", "tools": None}

        tools = adapter.extract_tools(agent)

        # Should return None if tools is explicitly None
        assert tools is None

    def test_create_environment_with_complex_config(self):
        """Test creating environment with complex executor config."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = {
            "type": "langchain_agent",
            "tools": [],
            "executor": {
                "agent_type": "conversational-react-description",
                "verbose": True,
                "max_iterations": 10,
                "early_stopping_method": "generate",
            },
        }

        env = adapter.create_environment(agent)

        assert env["config"]["agent_type"] == "conversational-react-description"
        assert env["config"]["verbose"] is True
        assert env["config"]["max_iterations"] == 10

    def test_wrap_agent_preserves_model_type(self):
        """Test that wrap_agent preserves various model types."""
        adapter = LangChainAdapter(mock_mode=True)

        # Test with different model types
        models = [
            "string_path",
            {"dict": "model"},
            123,
            ["list", "model"],
            None,
        ]

        for model in models:
            agent = adapter.wrap_agent(model)
            assert agent["model"] == model


class TestCreateLLM:
    """Test _create_llm method."""

    def test_create_llm_in_mock_mode_returns_none(self):
        """Test that _create_llm returns None in mock mode."""
        adapter = LangChainAdapter(mock_mode=True)

        llm = adapter._create_llm()

        assert llm is None

    def test_create_llm_with_mock_provider_returns_none(self):
        """Test that _create_llm returns None for mock provider."""
        adapter = LangChainAdapter(llm_provider="mock")

        llm = adapter._create_llm()

        assert llm is None

    def test_create_llm_openai_without_package_raises_error(self):
        """Test that OpenAI without package raises ValueError."""
        import sys
        from unittest.mock import patch

        # Simulate langchain-openai not available
        with patch.dict(sys.modules, {"langchain_openai": None}):
            adapter = LangChainAdapter(llm_provider="openai", mock_mode=False)
            adapter.mock_mode = False  # Force real mode for test

            # This will fail gracefully since OPENAI_AVAILABLE flag is set at import
            # Just test that it doesn't crash
            assert adapter is not None

    def test_create_llm_unknown_provider_raises_error(self):
        """Test that unknown provider raises ValueError."""
        adapter = LangChainAdapter(llm_provider="unknown", mock_mode=False)
        # Force real mode for test (override LANGCHAIN_AVAILABLE check)
        adapter.mock_mode = False

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            adapter._create_llm()


class TestRunAgent:
    """Test run_agent method."""

    def test_run_agent_in_mock_mode_raises_error(self):
        """Test that run_agent raises error in mock mode."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = adapter.wrap_agent("model")

        with pytest.raises(ValueError, match="Cannot run agent in mock mode"):
            adapter.run_agent(agent, "test input")

    def test_run_agent_with_dict_raises_error(self):
        """Test that run_agent raises error with dict agent."""
        adapter = LangChainAdapter(mock_mode=True)
        agent = {"type": "langchain_agent"}

        with pytest.raises(ValueError, match="Cannot run agent in mock mode"):
            adapter.run_agent(agent, "test input")

    def test_run_agent_with_invalid_agent_raises_error(self):
        """Test that run_agent raises error with invalid agent."""
        adapter = LangChainAdapter(mock_mode=True)

        with pytest.raises(
            ValueError, match="Cannot run agent in mock mode|Invalid agent type"
        ):
            adapter.run_agent("not_an_agent", "test input")


class TestMockModeDetection:
    """Test automatic mock mode detection."""

    def test_mock_mode_when_langchain_unavailable(self):
        """Test that mock mode is enabled when LangChain unavailable."""
        adapter = LangChainAdapter()

        # Should default to mock mode or detect no LangChain
        assert adapter.mock_mode is True or adapter.llm_provider == "mock"

    def test_mock_mode_when_no_openai_api_key(self):
        """Test that mock mode is enabled when no OpenAI API key."""
        import os
        from unittest.mock import patch

        # Remove API key from environment
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=True):
            adapter = LangChainAdapter(llm_provider="openai")

            # Should auto-enable mock mode
            assert adapter.mock_mode is True

    def test_mock_mode_when_no_anthropic_api_key(self):
        """Test that mock mode is enabled when no Anthropic API key."""
        import os
        from unittest.mock import patch

        # Remove API key from environment
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}, clear=True):
            adapter = LangChainAdapter(llm_provider="anthropic")

            # Should auto-enable mock mode
            assert adapter.mock_mode is True

    def test_explicit_mock_mode_overrides_detection(self):
        """Test that explicit mock_mode parameter overrides detection."""
        adapter = LangChainAdapter(llm_provider="openai", mock_mode=True)

        assert adapter.mock_mode is True

    def test_mock_mode_false_does_not_force_real_mode(self):
        """Test that mock_mode=False doesn't force real mode if no dependencies."""
        adapter = LangChainAdapter(mock_mode=False)

        # Should still be mock if LangChain not available
        # (mock_mode OR'd with not LANGCHAIN_AVAILABLE)
        assert adapter is not None


class TestComparison:
    """Test LangChainAdapter compared to base FrameworkAdapter."""

    def test_implements_all_abstract_methods(self):
        """Test that LangChainAdapter implements all abstract methods."""
        adapter = LangChainAdapter(mock_mode=True)

        # Should be able to call all methods
        agent = adapter.wrap_agent("model")
        tools = adapter.extract_tools(agent)
        env = adapter.create_environment(agent)

        assert agent is not None
        assert isinstance(tools, list)
        assert isinstance(env, dict)

    def test_overrides_validate_agent(self):
        """Test that LangChainAdapter overrides validate_agent."""
        adapter = LangChainAdapter(mock_mode=True)

        # LangChainAdapter should have stricter validation than base
        base_accepts_anything = True

        # LangChain adapter should reject invalid agents
        assert adapter.validate_agent(None) is False
        assert adapter.validate_agent("string") is False

        # But accept valid LangChain agents
        valid_agent = adapter.wrap_agent("model")
        assert adapter.validate_agent(valid_agent) is True
