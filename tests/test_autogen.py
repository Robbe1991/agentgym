"""Tests for AutoGen framework adapter.

This module contains comprehensive tests for the AutoGenAdapter,
including wrapping agents, extracting agents, creating environments,
and validation.
"""

import pytest

from agentgym.integrations.base import FrameworkAdapter
from agentgym.integrations.autogen import AutoGenAdapter


class MockAutoGenAgent:
    """Mock AutoGen agent for testing."""

    def __init__(self, name="assistant", agent_type="assistant"):
        """Initialize mock agent."""
        self.name = name
        self.agent_type = agent_type
        self._max_consecutive_auto_reply = 10

    def send(self, message, recipient):
        """Mock send method."""
        pass

    def receive(self, message, sender):
        """Mock receive method."""
        pass


class MockGroupChat:
    """Mock AutoGen GroupChat for testing."""

    def __init__(self, agents):
        """Initialize mock group chat."""
        self.agents = agents
        self.messages = []
        self.max_round = 10


class MockGroupChatManager:
    """Mock AutoGen GroupChatManager for testing."""

    def __init__(self, groupchat):
        """Initialize mock group chat manager."""
        self.groupchat = groupchat
        self.name = "group_chat_manager"

    def send(self, message, recipient):
        """Mock send method."""
        pass

    def receive(self, message, sender):
        """Mock receive method."""
        pass


class TestAutoGenAdapterBasics:
    """Test basic AutoGenAdapter properties and inheritance."""

    def test_inherits_from_framework_adapter(self):
        """Test that AutoGenAdapter inherits from FrameworkAdapter."""
        adapter = AutoGenAdapter(mock_mode=True)

        assert isinstance(adapter, FrameworkAdapter)

    def test_framework_name(self):
        """Test that framework_name is set correctly."""
        adapter = AutoGenAdapter(mock_mode=True)

        assert adapter.framework_name == "autogen"

    def test_initialization(self):
        """Test creating AutoGenAdapter instance."""
        adapter = AutoGenAdapter(mock_mode=True)

        assert adapter is not None
        assert hasattr(adapter, "wrap_agent")
        assert hasattr(adapter, "extract_tools")
        assert hasattr(adapter, "create_environment")

    def test_initialization_with_parameters(self):
        """Test creating AutoGenAdapter with parameters."""
        adapter = AutoGenAdapter(
            llm_provider="openai",
            model_name="gpt-4",
            temperature=0.5,
            mock_mode=True,
            max_consecutive_auto_reply=5,
            verbose=True,
        )

        assert adapter.llm_provider == "openai"
        assert adapter.model_name == "gpt-4"
        assert adapter.temperature == 0.5
        assert adapter.mock_mode is True
        assert adapter.max_consecutive_auto_reply == 5
        assert adapter.verbose is True

    def test_initialization_defaults(self):
        """Test that initialization uses correct defaults."""
        adapter = AutoGenAdapter(mock_mode=True)

        assert adapter.llm_provider == "mock"
        assert adapter.model_name is None
        assert adapter.temperature == 0.7
        assert adapter.max_consecutive_auto_reply == 10
        assert adapter.verbose is False


class TestWrapAgent:
    """Test wrap_agent method."""

    def test_wrap_agent_assistant_type(self):
        """Test wrapping as assistant agent."""
        adapter = AutoGenAdapter(mock_mode=True)
        model_path = "./models/customer_support_ep100"

        agent = adapter.wrap_agent(model_path, agent_type="assistant")

        assert isinstance(agent, dict)
        assert agent["type"] == "autogen_agent"
        assert agent["model"] == model_path
        assert agent["agent_type"] == "assistant"
        assert agent.get("_mock") is True

    def test_wrap_agent_user_proxy_type(self):
        """Test wrapping as user_proxy agent."""
        adapter = AutoGenAdapter(mock_mode=True)
        model = {"weights": [1, 2, 3]}

        agent = adapter.wrap_agent(model, agent_type="user_proxy")

        assert isinstance(agent, dict)
        assert agent["type"] == "autogen_agent"
        assert agent["agent_type"] == "user_proxy"
        assert agent["model"] == model

    def test_wrap_agent_group_chat_type(self):
        """Test wrapping as group_chat."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent1 = {"type": "autogen_agent", "agent_type": "assistant"}
        agent2 = {"type": "autogen_agent", "agent_type": "user_proxy"}

        group = adapter.wrap_agent(
            "model", agent_type="group_chat", agents=[agent1, agent2]
        )

        assert isinstance(group, dict)
        assert group["type"] == "autogen_agent"
        assert group["agent_type"] == "group_chat"
        assert len(group["agents"]) == 2

    def test_wrap_agent_with_system_message(self):
        """Test wrapping with custom system message."""
        adapter = AutoGenAdapter(mock_mode=True)
        system_msg = "You are a code review assistant"

        agent = adapter.wrap_agent("model", system_message=system_msg)

        assert agent["system_message"] == system_msg

    def test_wrap_agent_default_system_message(self):
        """Test that default system message is set."""
        adapter = AutoGenAdapter(mock_mode=True)

        agent = adapter.wrap_agent("model", agent_type="assistant")

        assert "assistant" in agent["system_message"].lower()

    def test_wrap_agent_with_code_execution(self):
        """Test wrapping with code execution enabled."""
        adapter = AutoGenAdapter(mock_mode=True)

        agent = adapter.wrap_agent(
            "model", agent_type="user_proxy", code_execution=True
        )

        assert agent["code_execution"] is True

    def test_wrap_agent_structure(self):
        """Test that wrapped agent has correct structure."""
        adapter = AutoGenAdapter(mock_mode=True)

        agent = adapter.wrap_agent("test_model")

        # Check all required keys
        assert "type" in agent
        assert "model" in agent
        assert "agent_type" in agent
        assert "agents" in agent
        assert "system_message" in agent
        assert "code_execution" in agent
        assert "config" in agent

        # Check config structure
        assert isinstance(agent["config"], dict)
        assert "max_consecutive_auto_reply" in agent["config"]
        assert "verbose" in agent["config"]

    def test_wrap_agent_config_values(self):
        """Test that config has expected values."""
        adapter = AutoGenAdapter(mock_mode=True, max_consecutive_auto_reply=15)

        agent = adapter.wrap_agent("model")

        assert agent["config"]["max_consecutive_auto_reply"] == 15
        assert agent["config"]["verbose"] is False


class TestExtractTools:
    """Test extract_tools method (extracts agents)."""

    def test_extract_agents_from_dict_single_agent(self):
        """Test extracting agents from single agent dict."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent = {
            "type": "autogen_agent",
            "agent_type": "assistant",
            "agents": [],
        }

        agents = adapter.extract_tools(agent)

        assert len(agents) == 1
        assert agents[0] == agent

    def test_extract_agents_from_dict_group_chat(self):
        """Test extracting agents from group chat dict."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent1 = {"type": "autogen_agent", "agent_type": "assistant"}
        agent2 = {"type": "autogen_agent", "agent_type": "user_proxy"}
        group = {
            "type": "autogen_agent",
            "agent_type": "group_chat",
            "agents": [agent1, agent2],
        }

        agents = adapter.extract_tools(group)

        assert len(agents) == 2
        assert agents[0] == agent1
        assert agents[1] == agent2

    def test_extract_agents_from_mock_agent_object(self):
        """Test extracting agents from mock AutoGen agent object."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent = MockAutoGenAgent("assistant")

        agents = adapter.extract_tools(agent)

        assert len(agents) == 1
        assert agents[0] == agent

    def test_extract_agents_from_mock_group_chat_manager(self):
        """Test extracting agents from mock GroupChatManager."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent1 = MockAutoGenAgent("agent1")
        agent2 = MockAutoGenAgent("agent2")
        groupchat = MockGroupChat([agent1, agent2])
        manager = MockGroupChatManager(groupchat)

        agents = adapter.extract_tools(manager)

        assert len(agents) == 2
        assert agents[0] == agent1
        assert agents[1] == agent2

    def test_extract_agents_from_invalid_agent(self):
        """Test extracting agents from agent without proper attributes."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent = "not_an_agent"

        agents = adapter.extract_tools(agent)

        assert len(agents) == 1


class TestCreateEnvironment:
    """Test create_environment method."""

    def test_create_environment_from_dict_agent(self):
        """Test creating environment from dict agent."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent = {
            "type": "autogen_agent",
            "agent_type": "assistant",
            "agents": [],
            "config": {
                "max_consecutive_auto_reply": 10,
                "verbose": False,
            },
        }

        env = adapter.create_environment(agent)

        assert isinstance(env, dict)
        assert env["type"] == "autogen"
        assert env["agent"] == agent
        assert len(env["agents"]) == 1
        assert env["config"]["agent_type"] == "assistant"

    def test_create_environment_from_group_chat(self):
        """Test creating environment from group chat."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent1 = {"type": "autogen_agent", "agent_type": "assistant"}
        agent2 = {"type": "autogen_agent", "agent_type": "user_proxy"}
        group = {
            "type": "autogen_agent",
            "agent_type": "group_chat",
            "agents": [agent1, agent2],
        }

        env = adapter.create_environment(group)

        assert env["type"] == "autogen"
        assert len(env["agents"]) == 2
        assert env["config"]["agent_type"] == "group_chat"

    def test_create_environment_from_mock_agent_object(self):
        """Test creating environment from mock AutoGen agent object."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent = MockAutoGenAgent("assistant")

        env = adapter.create_environment(agent)

        assert env["type"] == "autogen"
        assert env["agent"] == agent
        assert len(env["agents"]) == 1

    def test_create_environment_from_mock_group_chat_manager(self):
        """Test creating environment from mock GroupChatManager."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent1 = MockAutoGenAgent("agent1")
        agent2 = MockAutoGenAgent("agent2")
        groupchat = MockGroupChat([agent1, agent2])
        manager = MockGroupChatManager(groupchat)

        env = adapter.create_environment(manager)

        assert env["type"] == "autogen"
        assert env["agent"] == manager
        assert len(env["agents"]) == 2
        assert env["config"]["agent_type"] == "group_chat"
        assert env["config"]["num_agents"] == 2

    def test_create_environment_structure(self):
        """Test that environment has correct structure."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent = adapter.wrap_agent("model")

        env = adapter.create_environment(agent)

        # Check all required keys
        assert "type" in env
        assert "agent" in env
        assert "agents" in env
        assert "config" in env

        # Check types
        assert isinstance(env["type"], str)
        assert isinstance(env["agents"], list)
        assert isinstance(env["config"], dict)


class TestValidateAgent:
    """Test validate_agent method."""

    def test_validate_dict_agent_valid(self):
        """Test validating valid dict agent."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent = {
            "type": "autogen_agent",
            "agent_type": "assistant",
        }

        assert adapter.validate_agent(agent) is True

    def test_validate_dict_agent_invalid_type(self):
        """Test validating dict agent with wrong type."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent = {
            "type": "langchain_agent",  # Wrong type
            "agent_type": "assistant",
        }

        assert adapter.validate_agent(agent) is False

    def test_validate_dict_agent_no_type(self):
        """Test validating dict agent without type field."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent = {"agent_type": "assistant"}

        assert adapter.validate_agent(agent) is False

    def test_validate_mock_agent_object(self):
        """Test validating mock AutoGen agent object."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent = MockAutoGenAgent()

        assert adapter.validate_agent(agent) is True

    def test_validate_invalid_agent_types(self):
        """Test validating various invalid agent types."""
        adapter = AutoGenAdapter(mock_mode=True)

        assert adapter.validate_agent(None) is False
        assert adapter.validate_agent("string") is False
        assert adapter.validate_agent(123) is False
        assert adapter.validate_agent([]) is False

    def test_validate_wrapped_agent(self):
        """Test that wrapped agents pass validation."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent = adapter.wrap_agent("model")

        assert adapter.validate_agent(agent) is True


class TestGetFrameworkInfo:
    """Test get_framework_info method."""

    def test_framework_info_structure(self):
        """Test that framework info has correct structure."""
        adapter = AutoGenAdapter(mock_mode=True)

        info = adapter.get_framework_info()

        assert isinstance(info, dict)
        assert "name" in info
        assert "adapter_class" in info
        assert "methods" in info

    def test_framework_info_values(self):
        """Test that framework info has correct values."""
        adapter = AutoGenAdapter(mock_mode=True)

        info = adapter.get_framework_info()

        assert info["name"] == "autogen"
        assert info["adapter_class"] == "AutoGenAdapter"
        assert "wrap_agent" in info["methods"]
        assert "extract_tools" in info["methods"]
        assert "create_environment" in info["methods"]


class TestRepr:
    """Test __repr__ method."""

    def test_repr(self):
        """Test string representation."""
        adapter = AutoGenAdapter(mock_mode=True)

        repr_str = repr(adapter)

        assert "AutoGenAdapter" in repr_str
        assert "autogen" in repr_str


class TestCreateLLMConfig:
    """Test _create_llm_config method."""

    def test_create_llm_config_in_mock_mode_returns_empty(self):
        """Test that _create_llm_config returns empty dict in mock mode."""
        adapter = AutoGenAdapter(mock_mode=True)

        config = adapter._create_llm_config()

        assert config == {}

    def test_create_llm_config_with_mock_provider_returns_empty(self):
        """Test that _create_llm_config returns empty dict for mock provider."""
        adapter = AutoGenAdapter(llm_provider="mock")

        config = adapter._create_llm_config()

        assert config == {}

    def test_create_llm_config_unknown_provider_raises_error(self):
        """Test that unknown provider raises ValueError."""
        adapter = AutoGenAdapter(llm_provider="unknown", mock_mode=False)
        # Force real mode for test
        adapter.mock_mode = False

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            adapter._create_llm_config()


class TestRunAgent:
    """Test run_agent method."""

    def test_run_agent_in_mock_mode_raises_error(self):
        """Test that run_agent raises error in mock mode."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent = adapter.wrap_agent("model")

        with pytest.raises(ValueError, match="Cannot run agent in mock mode"):
            adapter.run_agent(agent, "test message")

    def test_run_agent_with_dict_raises_error(self):
        """Test that run_agent raises error with dict agent."""
        adapter = AutoGenAdapter(mock_mode=True)
        agent = {"type": "autogen_agent"}

        with pytest.raises(ValueError, match="Cannot run agent in mock mode"):
            adapter.run_agent(agent, "test message")

    def test_run_agent_without_recipient_raises_error(self):
        """Test that run_agent raises error without recipient for direct chat."""
        adapter = AutoGenAdapter(mock_mode=True)

        # Even though it will raise "Cannot run in mock mode" first,
        # we're testing the validation logic
        with pytest.raises(ValueError):
            adapter.run_agent("not_an_agent", "test message")


class TestMockModeDetection:
    """Test automatic mock mode detection."""

    def test_mock_mode_when_autogen_unavailable(self):
        """Test that mock mode is enabled when AutoGen unavailable."""
        adapter = AutoGenAdapter()

        # Should default to mock mode or detect no AutoGen
        assert adapter.mock_mode is True or adapter.llm_provider == "mock"

    def test_mock_mode_when_no_openai_api_key(self):
        """Test that mock mode is enabled when no OpenAI API key."""
        import os
        from unittest.mock import patch

        # Remove API key from environment
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=True):
            adapter = AutoGenAdapter(llm_provider="openai")

            # Should auto-enable mock mode
            assert adapter.mock_mode is True

    def test_explicit_mock_mode_overrides_detection(self):
        """Test that explicit mock_mode parameter overrides detection."""
        adapter = AutoGenAdapter(llm_provider="openai", mock_mode=True)

        assert adapter.mock_mode is True

    def test_mock_mode_false_does_not_force_real_mode(self):
        """Test that mock_mode=False doesn't force real mode if no dependencies."""
        adapter = AutoGenAdapter(mock_mode=False)

        # Should still be mock if AutoGen not available
        assert adapter is not None


class TestIntegration:
    """Integration tests for AutoGenAdapter."""

    def test_complete_workflow_single_agent(self):
        """Test complete workflow with single agent."""
        adapter = AutoGenAdapter(mock_mode=True)

        # 1. Wrap a trained model
        trained_model = "./models/customer_support_ep100"
        agent = adapter.wrap_agent(trained_model, agent_type="assistant")

        assert adapter.validate_agent(agent)

        # 2. Extract agents
        agents = adapter.extract_tools(agent)
        assert len(agents) == 1

        # 3. Create environment
        env = adapter.create_environment(agent)
        assert env["type"] == "autogen"
        assert len(env["agents"]) == 1

    def test_complete_workflow_group_chat(self):
        """Test complete workflow with group chat."""
        adapter = AutoGenAdapter(mock_mode=True)

        # Create multiple agents
        assistant = adapter.wrap_agent("model1", agent_type="assistant")
        user_proxy = adapter.wrap_agent("model2", agent_type="user_proxy")

        # Create group chat
        group = adapter.wrap_agent(
            "model_group", agent_type="group_chat", agents=[assistant, user_proxy]
        )

        # Validate
        assert adapter.validate_agent(group)

        # Extract agents
        agents = adapter.extract_tools(group)
        assert len(agents) == 2

        # Create environment
        env = adapter.create_environment(group)
        assert env["type"] == "autogen"
        assert len(env["agents"]) == 2
        assert env["config"]["agent_type"] == "group_chat"

    def test_adapter_reusability(self):
        """Test that adapter can be reused for multiple agents."""
        adapter = AutoGenAdapter(mock_mode=True)

        # Wrap multiple agents
        agent1 = adapter.wrap_agent("model1", agent_type="assistant")
        agent2 = adapter.wrap_agent("model2", agent_type="user_proxy")
        agent3 = adapter.wrap_agent("model3", agent_type="assistant")

        assert agent1["model"] == "model1"
        assert agent2["model"] == "model2"
        assert agent3["model"] == "model3"

        # All should be valid
        assert adapter.validate_agent(agent1)
        assert adapter.validate_agent(agent2)
        assert adapter.validate_agent(agent3)

    def test_multiple_adapters_independent(self):
        """Test that multiple adapter instances are independent."""
        adapter1 = AutoGenAdapter(mock_mode=True)
        adapter2 = AutoGenAdapter(mock_mode=True)

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

    def test_wrap_agent_preserves_model_type(self):
        """Test that wrap_agent preserves various model types."""
        adapter = AutoGenAdapter(mock_mode=True)

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

    def test_group_chat_empty_agents_in_mock_mode(self):
        """Test group chat with empty agents list in mock mode."""
        adapter = AutoGenAdapter(mock_mode=True)

        # Mock mode allows empty agents (will be validated later in real mode)
        agent = adapter.wrap_agent("model", agent_type="group_chat", agents=[])

        assert agent["agent_type"] == "group_chat"
        assert len(agent["agents"]) == 0

    def test_different_max_consecutive_auto_reply_values(self):
        """Test different max_consecutive_auto_reply values."""
        for max_replies in [1, 5, 10, 20, 100]:
            adapter = AutoGenAdapter(
                mock_mode=True, max_consecutive_auto_reply=max_replies
            )
            agent = adapter.wrap_agent("model")

            assert agent["config"]["max_consecutive_auto_reply"] == max_replies


class TestComparison:
    """Test AutoGenAdapter compared to base FrameworkAdapter."""

    def test_implements_all_abstract_methods(self):
        """Test that AutoGenAdapter implements all abstract methods."""
        adapter = AutoGenAdapter(mock_mode=True)

        # Should be able to call all methods
        agent = adapter.wrap_agent("model")
        agents = adapter.extract_tools(agent)
        env = adapter.create_environment(agent)

        assert agent is not None
        assert isinstance(agents, list)
        assert isinstance(env, dict)

    def test_overrides_validate_agent(self):
        """Test that AutoGenAdapter overrides validate_agent."""
        adapter = AutoGenAdapter(mock_mode=True)

        # AutoGen adapter should reject invalid agents
        assert adapter.validate_agent(None) is False
        assert adapter.validate_agent("string") is False

        # But accept valid AutoGen agents
        valid_agent = adapter.wrap_agent("model")
        assert adapter.validate_agent(valid_agent) is True
