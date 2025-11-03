"""Tests for CrewAI adapter implementation.

This test suite covers:
- Mock agent creation
- Real agent creation (if CrewAI available)
- Tool/agent extraction
- Environment creation
- Agent validation
- Configuration handling
- Error handling
"""

import os
from unittest.mock import Mock, patch

import pytest

from agentgym.integrations.crewai import CrewAIAdapter


# Mock classes for testing when CrewAI is not available
class MockCrewAIAgent:
    """Mock CrewAI Agent for testing."""

    def __init__(
        self,
        role="Assistant",
        goal="Accomplish tasks",
        backstory="Helpful agent",
        tools=None,
        llm=None,
        verbose=False,
        allow_delegation=False,
    ):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.llm = llm
        self.verbose = verbose
        self.allow_delegation = allow_delegation


class MockCrewAICrew:
    """Mock CrewAI Crew for testing."""

    def __init__(self, agents=None, tasks=None, process="sequential", verbose=False):
        self.agents = agents or []
        self.tasks = tasks or []
        self.process = process
        self.verbose = verbose

    def kickoff(self, **kwargs):
        return "Mock crew result"


class MockTask:
    """Mock CrewAI Task for testing."""

    def __init__(self, description="", agent=None, expected_output=""):
        self.description = description
        self.agent = agent
        self.expected_output = expected_output


# Fixtures
@pytest.fixture
def mock_adapter():
    """Create adapter in mock mode."""
    return CrewAIAdapter(mock_mode=True)


@pytest.fixture
def mock_openai_adapter():
    """Create adapter configured for OpenAI (but in mock mode)."""
    return CrewAIAdapter(llm_provider="openai", mock_mode=True)


@pytest.fixture
def trained_model():
    """Sample trained model path."""
    return "./models/agent_ep100"


# Test initialization
class TestInitialization:
    def test_init_defaults(self):
        adapter = CrewAIAdapter()
        assert adapter.framework_name == "crewai"
        assert adapter.llm_provider == "mock"
        assert adapter.mock_mode is True  # No CrewAI available in test
        assert adapter.process == "sequential"
        assert adapter.verbose is False

    def test_init_with_openai(self):
        adapter = CrewAIAdapter(llm_provider="openai", model_name="gpt-4")
        assert adapter.llm_provider == "openai"
        assert adapter.model_name == "gpt-4"
        assert adapter.mock_mode is True  # No API key

    def test_init_with_anthropic(self):
        adapter = CrewAIAdapter(
            llm_provider="anthropic",
            model_name="claude-3-sonnet-20240229",
            temperature=0.5,
        )
        assert adapter.llm_provider == "anthropic"
        assert adapter.model_name == "claude-3-sonnet-20240229"
        assert adapter.temperature == 0.5

    def test_init_with_custom_process(self):
        adapter = CrewAIAdapter(process="hierarchical")
        assert adapter.process == "hierarchical"

    def test_init_with_verbose(self):
        adapter = CrewAIAdapter(verbose=True)
        assert adapter.verbose is True

    def test_auto_detect_mock_mode_no_openai_key(self):
        with patch.dict(os.environ, {}, clear=True):
            adapter = CrewAIAdapter(llm_provider="openai")
            assert adapter.mock_mode is True

    def test_auto_detect_mock_mode_no_anthropic_key(self):
        with patch.dict(os.environ, {}, clear=True):
            adapter = CrewAIAdapter(llm_provider="anthropic")
            assert adapter.mock_mode is True


# Test wrap_agent
class TestWrapAgent:
    def test_wrap_agent_basic(self, mock_adapter, trained_model):
        agent = mock_adapter.wrap_agent(trained_model)

        assert agent["type"] == "crewai_agent"
        assert agent["model"] == trained_model
        assert agent["agent_type"] == "agent"
        assert agent["role"] == "Assistant"
        assert agent.get("_mock") is True

    def test_wrap_agent_with_role(self, mock_adapter, trained_model):
        agent = mock_adapter.wrap_agent(trained_model, role="Researcher")

        assert agent["role"] == "Researcher"
        assert "Researcher" in agent["goal"]
        assert "Researcher" in agent["backstory"]

    def test_wrap_agent_with_goal_and_backstory(self, mock_adapter, trained_model):
        agent = mock_adapter.wrap_agent(
            trained_model,
            role="Writer",
            goal="Write engaging content",
            backstory="Professional writer with 10 years experience",
        )

        assert agent["role"] == "Writer"
        assert agent["goal"] == "Write engaging content"
        assert agent["backstory"] == "Professional writer with 10 years experience"

    def test_wrap_agent_with_tools(self, mock_adapter, trained_model):
        tools = [{"name": "search"}, {"name": "calculator"}]
        agent = mock_adapter.wrap_agent(trained_model, tools=tools)

        assert len(agent["tools"]) == 2
        assert agent["tools"] == tools

    def test_wrap_agent_with_delegation(self, mock_adapter, trained_model):
        agent = mock_adapter.wrap_agent(trained_model, allow_delegation=True)

        assert agent["allow_delegation"] is True

    def test_wrap_agent_crew_type(self, mock_adapter):
        # For crew type, pass dict with agents
        crew_model = {
            "agents": [{"role": "Researcher"}, {"role": "Writer"}],
            "tasks": [{"description": "Research topic"}, {"description": "Write report"}],
        }

        crew = mock_adapter.wrap_agent(crew_model, agent_type="crew")

        assert crew["type"] == "crewai_agent"
        assert crew["agent_type"] == "crew"
        assert crew["model"] == crew_model

    def test_wrap_agent_invalid_type(self, mock_adapter, trained_model):
        with pytest.raises(ValueError, match="Unknown agent_type"):
            mock_adapter.wrap_agent(trained_model, agent_type="invalid")

    def test_wrap_agent_stores_config(self, mock_adapter, trained_model):
        adapter = CrewAIAdapter(mock_mode=True, verbose=True, process="hierarchical")
        agent = adapter.wrap_agent(trained_model)

        assert agent["config"]["verbose"] is True
        assert agent["config"]["process"] == "hierarchical"


# Test extract_tools
class TestExtractTools:
    def test_extract_tools_from_mock_agent(self, mock_adapter, trained_model):
        tools = [{"name": "search"}, {"name": "calculator"}]
        agent = mock_adapter.wrap_agent(trained_model, tools=tools)

        extracted = mock_adapter.extract_tools(agent)

        assert len(extracted) == 2
        assert extracted == tools

    def test_extract_tools_from_mock_agent_no_tools(self, mock_adapter, trained_model):
        agent = mock_adapter.wrap_agent(trained_model)

        extracted = mock_adapter.extract_tools(agent)

        assert extracted == []

    def test_extract_agents_from_mock_crew(self, mock_adapter):
        crew_model = {
            "agents": [{"role": "Researcher"}, {"role": "Writer"}],
            "tasks": [],
        }
        crew = mock_adapter.wrap_agent(crew_model, agent_type="crew")

        agents = mock_adapter.extract_tools(crew)

        assert len(agents) == 2
        assert agents[0]["role"] == "Researcher"
        assert agents[1]["role"] == "Writer"

    def test_extract_tools_from_real_agent_mock(self, mock_adapter):
        # Mock a real CrewAI agent
        mock_agent = MockCrewAIAgent(tools=[{"name": "tool1"}])

        tools = mock_adapter.extract_tools(mock_agent)

        assert len(tools) == 1

    def test_extract_agents_from_real_crew_mock(self, mock_adapter):
        # Mock a real CrewAI crew
        mock_crew = MockCrewAICrew(agents=[{"role": "Agent1"}, {"role": "Agent2"}])

        agents = mock_adapter.extract_tools(mock_crew)

        assert len(agents) == 2

    def test_extract_tools_invalid_agent(self, mock_adapter):
        result = mock_adapter.extract_tools("not an agent")
        assert result == []


# Test create_environment
class TestCreateEnvironment:
    def test_create_environment_from_mock_agent(self, mock_adapter, trained_model):
        agent = mock_adapter.wrap_agent(
            trained_model,
            role="Researcher",
            goal="Research topics",
            backstory="Expert researcher",
        )

        env = mock_adapter.create_environment(agent)

        assert env["type"] == "crewai"
        assert env["agent"] == agent
        assert env["config"]["agent_type"] == "agent"
        assert env["config"]["role"] == "Researcher"
        assert env["config"]["goal"] == "Research topics"
        assert env["config"]["backstory"] == "Expert researcher"

    def test_create_environment_from_mock_crew(self, mock_adapter):
        crew_model = {
            "agents": [{"role": "Agent1"}, {"role": "Agent2"}],
            "tasks": [{"description": "Task1"}],
        }
        crew = mock_adapter.wrap_agent(crew_model, agent_type="crew")

        env = mock_adapter.create_environment(crew)

        assert env["type"] == "crewai"
        assert env["config"]["agent_type"] == "crew"
        assert len(env["tools"]) == 2  # 2 agents

    def test_create_environment_from_real_agent_mock(self, mock_adapter):
        mock_agent = MockCrewAIAgent(
            role="Analyst",
            goal="Analyze data",
            backstory="Data analyst",
            allow_delegation=True,
            verbose=True,
        )

        env = mock_adapter.create_environment(mock_agent)

        assert env["type"] == "crewai"
        assert env["config"]["agent_type"] == "agent"
        assert env["config"]["role"] == "Analyst"
        assert env["config"]["allow_delegation"] is True
        assert env["config"]["verbose"] is True

    def test_create_environment_from_real_crew_mock(self, mock_adapter):
        mock_crew = MockCrewAICrew(
            agents=[MockCrewAIAgent(), MockCrewAIAgent()],
            tasks=[MockTask(), MockTask(), MockTask()],
            process="hierarchical",
            verbose=True,
        )

        env = mock_adapter.create_environment(mock_crew)

        assert env["type"] == "crewai"
        assert env["config"]["agent_type"] == "crew"
        assert env["config"]["num_agents"] == 2
        assert env["config"]["num_tasks"] == 3
        assert env["config"]["process"] == "hierarchical"

    def test_create_environment_extracts_tools(self, mock_adapter, trained_model):
        tools = [{"name": "tool1"}, {"name": "tool2"}]
        agent = mock_adapter.wrap_agent(trained_model, tools=tools)

        env = mock_adapter.create_environment(agent)

        assert len(env["tools"]) == 2


# Test validate_agent
class TestValidateAgent:
    def test_validate_mock_agent(self, mock_adapter, trained_model):
        agent = mock_adapter.wrap_agent(trained_model)

        assert mock_adapter.validate_agent(agent) is True

    def test_validate_mock_crew(self, mock_adapter):
        crew_model = {"agents": [], "tasks": []}
        crew = mock_adapter.wrap_agent(crew_model, agent_type="crew")

        assert mock_adapter.validate_agent(crew) is True

    def test_validate_real_agent_mock(self, mock_adapter):
        mock_agent = MockCrewAIAgent()

        assert mock_adapter.validate_agent(mock_agent) is True

    def test_validate_real_crew_mock(self, mock_adapter):
        mock_crew = MockCrewAICrew()

        assert mock_adapter.validate_agent(mock_crew) is True

    def test_validate_invalid_dict(self, mock_adapter):
        invalid = {"type": "not_crewai"}

        assert mock_adapter.validate_agent(invalid) is False

    def test_validate_invalid_object(self, mock_adapter):
        assert mock_adapter.validate_agent("not an agent") is False
        assert mock_adapter.validate_agent(123) is False
        assert mock_adapter.validate_agent(None) is False


# Test run_agent
class TestRunAgent:
    def test_run_agent_raises_in_mock_mode(self, mock_adapter, trained_model):
        agent = mock_adapter.wrap_agent(trained_model)

        with pytest.raises(ValueError, match="Cannot run agent in mock mode"):
            mock_adapter.run_agent(agent, "Test task")

    def test_run_agent_with_dict_raises(self, mock_adapter, trained_model):
        agent = mock_adapter.wrap_agent(trained_model)

        with pytest.raises(ValueError, match="Cannot run agent in mock mode"):
            mock_adapter.run_agent(agent, "Test task")


# Test _create_llm
class TestCreateLLM:
    def test_create_llm_mock_mode(self, mock_adapter):
        llm = mock_adapter._create_llm()
        assert llm is None

    def test_create_llm_openai_not_available(self):
        adapter = CrewAIAdapter(llm_provider="openai", mock_mode=False)
        # Manually override mock_mode since it's forced to True in __init__
        adapter.mock_mode = False

        with patch("agentgym.integrations.crewai.OPENAI_AVAILABLE", False):
            with pytest.raises(ValueError, match="OpenAI not available"):
                adapter._create_llm()

    def test_create_llm_anthropic_not_available(self):
        adapter = CrewAIAdapter(llm_provider="anthropic", mock_mode=False)
        # Manually override mock_mode since it's forced to True in __init__
        adapter.mock_mode = False

        with patch("agentgym.integrations.crewai.ANTHROPIC_AVAILABLE", False):
            with pytest.raises(ValueError, match="Anthropic not available"):
                adapter._create_llm()

    def test_create_llm_unknown_provider(self):
        adapter = CrewAIAdapter(llm_provider="unknown", mock_mode=False)
        # Manually override mock_mode since it's forced to True in __init__
        adapter.mock_mode = False

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            adapter._create_llm()

    def test_create_llm_mock_provider(self):
        adapter = CrewAIAdapter(llm_provider="mock", mock_mode=False)
        llm = adapter._create_llm()
        assert llm is None


# Test framework_name
class TestFrameworkName:
    def test_framework_name(self, mock_adapter):
        assert mock_adapter.framework_name == "crewai"

    def test_get_framework_info(self, mock_adapter):
        info = mock_adapter.get_framework_info()

        assert info["name"] == "crewai"
        assert info["adapter_class"] == "CrewAIAdapter"
        assert "wrap_agent" in info["methods"]
        assert "extract_tools" in info["methods"]
        assert "create_environment" in info["methods"]


# Integration tests
class TestIntegration:
    def test_full_workflow_single_agent(self, mock_adapter, trained_model):
        """Test complete workflow with single agent."""
        # 1. Wrap agent
        agent = mock_adapter.wrap_agent(
            trained_model,
            role="Researcher",
            goal="Research AI topics",
            backstory="Expert AI researcher",
            tools=[{"name": "search"}],
        )

        # 2. Validate agent
        assert mock_adapter.validate_agent(agent)

        # 3. Extract tools
        tools = mock_adapter.extract_tools(agent)
        assert len(tools) == 1

        # 4. Create environment
        env = mock_adapter.create_environment(agent)
        assert env["type"] == "crewai"
        assert env["config"]["role"] == "Researcher"

    def test_full_workflow_crew(self, mock_adapter, trained_model):
        """Test complete workflow with crew."""
        # 1. Create agents
        researcher = mock_adapter.wrap_agent(
            trained_model,
            role="Researcher",
            goal="Research topics",
        )

        writer = mock_adapter.wrap_agent(
            trained_model,
            role="Writer",
            goal="Write content",
        )

        # 2. Create crew
        crew_model = {
            "agents": [researcher, writer],
            "tasks": [
                {"description": "Research AI"},
                {"description": "Write article"},
            ],
        }

        crew = mock_adapter.wrap_agent(crew_model, agent_type="crew")

        # 3. Validate crew
        assert mock_adapter.validate_agent(crew)

        # 4. Extract agents
        agents = mock_adapter.extract_tools(crew)
        assert len(agents) == 2

        # 5. Create environment
        env = mock_adapter.create_environment(crew)
        assert env["type"] == "crewai"
        assert env["config"]["agent_type"] == "crew"

    def test_agent_with_delegation(self, mock_adapter, trained_model):
        """Test agent with delegation enabled."""
        agent = mock_adapter.wrap_agent(
            trained_model,
            role="Manager",
            goal="Manage team",
            allow_delegation=True,
        )

        assert agent["allow_delegation"] is True

        env = mock_adapter.create_environment(agent)
        assert env["config"]["allow_delegation"] is True

    def test_hierarchical_process(self):
        """Test crew with hierarchical process."""
        adapter = CrewAIAdapter(mock_mode=True, process="hierarchical")

        crew_model = {"agents": [{"role": "Agent1"}], "tasks": [{"description": "Task1"}]}

        crew = adapter.wrap_agent(crew_model, agent_type="crew")

        env = adapter.create_environment(crew)
        assert env["config"]["process"] == "hierarchical"

    def test_multiple_tools(self, mock_adapter, trained_model):
        """Test agent with multiple tools."""
        tools = [
            {"name": "search", "description": "Search the web"},
            {"name": "calculator", "description": "Calculate numbers"},
            {"name": "file_reader", "description": "Read files"},
        ]

        agent = mock_adapter.wrap_agent(trained_model, tools=tools)

        extracted_tools = mock_adapter.extract_tools(agent)
        assert len(extracted_tools) == 3

        env = mock_adapter.create_environment(agent)
        assert len(env["tools"]) == 3


# Test error handling
class TestErrorHandling:
    def test_wrap_agent_crew_without_agents(self, mock_adapter, trained_model):
        """Test that crew type requires agents."""
        with pytest.raises(ValueError, match="must be dict with 'agents' key"):
            mock_adapter.wrap_agent(trained_model, agent_type="crew")

    def test_invalid_agent_type(self, mock_adapter, trained_model):
        """Test invalid agent_type."""
        with pytest.raises(ValueError, match="Unknown agent_type"):
            mock_adapter.wrap_agent(trained_model, agent_type="invalid_type")

    def test_unknown_llm_provider(self):
        """Test unknown LLM provider."""
        adapter = CrewAIAdapter(llm_provider="unknown_provider", mock_mode=False)
        # Manually override mock_mode since it's forced to True in __init__
        adapter.mock_mode = False

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            adapter._create_llm()


# Test configuration preservation
class TestConfigurationPreservation:
    def test_temperature_preserved(self):
        adapter = CrewAIAdapter(temperature=0.5)
        assert adapter.temperature == 0.5

    def test_model_name_preserved(self):
        adapter = CrewAIAdapter(model_name="gpt-4")
        assert adapter.model_name == "gpt-4"

    def test_verbose_preserved(self):
        adapter = CrewAIAdapter(verbose=True)
        agent = adapter.wrap_agent("model", role="Agent")
        assert agent["config"]["verbose"] is True

    def test_process_preserved(self):
        adapter = CrewAIAdapter(process="hierarchical")
        agent = adapter.wrap_agent("model", role="Agent")
        assert agent["config"]["process"] == "hierarchical"


# Test different LLM providers
class TestLLMProviders:
    def test_openai_provider(self):
        adapter = CrewAIAdapter(llm_provider="openai", model_name="gpt-4")
        assert adapter.llm_provider == "openai"
        assert adapter.model_name == "gpt-4"

    def test_anthropic_provider(self):
        adapter = CrewAIAdapter(
            llm_provider="anthropic", model_name="claude-3-sonnet-20240229"
        )
        assert adapter.llm_provider == "anthropic"
        assert adapter.model_name == "claude-3-sonnet-20240229"

    def test_mock_provider(self):
        adapter = CrewAIAdapter(llm_provider="mock")
        assert adapter.llm_provider == "mock"
        assert adapter.mock_mode is True


# Test edge cases
class TestEdgeCases:
    def test_empty_tools_list(self, mock_adapter, trained_model):
        agent = mock_adapter.wrap_agent(trained_model, tools=[])
        tools = mock_adapter.extract_tools(agent)
        assert tools == []

    def test_none_goal_and_backstory(self, mock_adapter, trained_model):
        """Test that None goal and backstory get defaults."""
        agent = mock_adapter.wrap_agent(
            trained_model, role="TestRole", goal=None, backstory=None
        )
        assert "TestRole" in agent["goal"]
        assert "TestRole" in agent["backstory"]

    def test_extract_tools_from_non_dict_non_object(self, mock_adapter):
        result = mock_adapter.extract_tools(None)
        assert result == []

    def test_validate_with_object_without_attributes(self, mock_adapter):
        class EmptyObject:
            pass

        obj = EmptyObject()
        assert mock_adapter.validate_agent(obj) is False
