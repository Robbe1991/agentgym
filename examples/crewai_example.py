"""Example usage of CrewAI adapter with real LLM integration.

This example demonstrates how to:
1. Create a CrewAI adapter with different agent types
2. Wrap trained models as CrewAI agents
3. Create multi-agent crews
4. Use mock mode for testing without API keys

Prerequisites:
- For OpenAI: pip install crewai langchain-openai + OPENAI_API_KEY environment variable
- For Anthropic: pip install crewai langchain-anthropic + ANTHROPIC_API_KEY environment variable
- For testing: No requirements (uses mock mode automatically)
"""

import os

from agentgym.integrations.crewai import CrewAIAdapter

# Example 1: Mock Mode (no API keys required)
print("=" * 60)
print("Example 1: Mock Mode - Single Agent")
print("=" * 60)

# Create adapter in mock mode
adapter = CrewAIAdapter(mock_mode=True)
print(f"Mock mode: {adapter.mock_mode}")

# Wrap a trained model as researcher agent
trained_model = "./models/researcher_ep100"
agent = adapter.wrap_agent(
    trained_model,
    role="Researcher",
    goal="Find and analyze relevant information",
    backstory="Expert researcher with 10 years of experience in AI",
)

print(f"Agent type: {agent['type']}")
print(f"Agent role: {agent['role']}")
print(f"Agent goal: {agent['goal']}")
print(f"Mock agent: {agent.get('_mock', False)}")

# Validate the agent
is_valid = adapter.validate_agent(agent)
print(f"Agent valid: {is_valid}")

# Create environment
env = adapter.create_environment(agent)
print(f"Environment type: {env['type']}")
print(f"Number of agents: {len(env['tools'])}")

print()


# Example 2: Multi-Agent Crew (Mock Mode)
print("=" * 60)
print("Example 2: Multi-Agent Crew")
print("=" * 60)

adapter = CrewAIAdapter(mock_mode=True, verbose=True)

# Create multiple agents with different roles
researcher = adapter.wrap_agent(
    "model1",
    role="Researcher",
    goal="Research and gather information on AI topics",
    backstory="PhD in Computer Science with focus on AI research",
    tools=[{"name": "search", "description": "Search the web"}],
)

analyst = adapter.wrap_agent(
    "model2",
    role="Data Analyst",
    goal="Analyze data and identify patterns",
    backstory="Expert data analyst with 15 years experience",
    tools=[{"name": "calculator", "description": "Perform calculations"}],
)

writer = adapter.wrap_agent(
    "model3",
    role="Technical Writer",
    goal="Write clear and engaging technical content",
    backstory="Professional technical writer published in top journals",
)

# Create crew with multiple agents
crew_model = {
    "agents": [researcher, analyst, writer],
    "tasks": [
        {"description": "Research AI safety topics", "agent": researcher},
        {"description": "Analyze research findings", "agent": analyst},
        {"description": "Write comprehensive report", "agent": writer},
    ],
}

crew = adapter.wrap_agent(crew_model, agent_type="crew")

print(f"Crew type: {crew['agent_type']}")
print(f"Number of agents in crew: {len(crew['model']['agents'])}")

# Extract all agents
agents = adapter.extract_tools(crew)
print(f"Extracted agents: {len(agents)}")
for i, agent in enumerate(agents, 1):
    print(f"  Agent {i}: {agent['role']}")

# Create environment for crew
env = adapter.create_environment(crew)
print(f"Environment has {len(env['tools'])} agents")
print(f"Config: {env['config']}")

print()


# Example 3: Agent with Delegation
print("=" * 60)
print("Example 3: Agent with Delegation")
print("=" * 60)

adapter = CrewAIAdapter(mock_mode=True)

# Create manager agent that can delegate tasks
manager = adapter.wrap_agent(
    "manager_model",
    role="Project Manager",
    goal="Coordinate team and ensure project success",
    backstory="Experienced project manager with strong leadership skills",
    allow_delegation=True,
)

print(f"Agent role: {manager['role']}")
print(f"Can delegate: {manager['allow_delegation']}")

env = adapter.create_environment(manager)
print(f"Delegation enabled: {env['config']['allow_delegation']}")

print()


# Example 4: Hierarchical Process
print("=" * 60)
print("Example 4: Hierarchical Process")
print("=" * 60)

# Create adapter with hierarchical process
adapter_hierarchical = CrewAIAdapter(mock_mode=True, process="hierarchical")

crew_model_h = {
    "agents": [
        adapter_hierarchical.wrap_agent("m1", role="Researcher"),
        adapter_hierarchical.wrap_agent("m2", role="Analyst"),
    ],
    "tasks": [
        {"description": "Research topic"},
        {"description": "Analyze findings"},
    ],
}

crew_h = adapter_hierarchical.wrap_agent(crew_model_h, agent_type="crew")

env_h = adapter_hierarchical.create_environment(crew_h)
print(f"Process type: {env_h['config']['process']}")

print()


# Example 5: Auto-detection (automatically uses mock mode if no API keys)
print("=" * 60)
print("Example 5: Auto-detection")
print("=" * 60)

# Create adapter without specifying mock mode
# Will automatically enable mock mode if no API keys found
adapter_auto = CrewAIAdapter(llm_provider="openai")
print(f"LLM provider: {adapter_auto.llm_provider}")
print(f"Auto-detected mock mode: {adapter_auto.mock_mode}")

print()


# Example 6: Real OpenAI Integration (requires OPENAI_API_KEY)
print("=" * 60)
print("Example 6: Real OpenAI Integration")
print("=" * 60)

if os.getenv("OPENAI_API_KEY"):
    print("OpenAI API key found!")

    # Create adapter with OpenAI
    adapter_openai = CrewAIAdapter(
        llm_provider="openai",
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        verbose=True,
    )

    print(f"Mock mode: {adapter_openai.mock_mode}")
    print(f"Model: {adapter_openai.model_name}")

    # Create researcher agent
    researcher = adapter_openai.wrap_agent(
        trained_model,
        role="AI Researcher",
        goal="Research cutting-edge AI topics",
        backstory="PhD researcher specializing in machine learning",
    )

    # Create analyst agent
    analyst = adapter_openai.wrap_agent(
        trained_model,
        role="Data Analyst",
        goal="Analyze research data",
        backstory="Expert analyst with strong statistical background",
    )

    # Create crew with both agents
    crew_model_real = {
        "agents": [researcher, analyst],
        "tasks": [
            {"description": "Research latest AI developments"},
            {"description": "Analyze impact and trends"},
        ],
    }

    crew_real = adapter_openai.wrap_agent(crew_model_real, agent_type="crew")

    # Run the crew (this will make real API calls)
    # Uncomment to test:
    # result = adapter_openai.run_agent(crew_real, "Research AI safety")
    # print(f"Result: {result['output']}")

    print("Crew created successfully!")
else:
    print("No OpenAI API key found. Set OPENAI_API_KEY to test real integration.")

print()


# Example 7: Real Anthropic Integration (requires ANTHROPIC_API_KEY)
print("=" * 60)
print("Example 7: Real Anthropic Integration")
print("=" * 60)

if os.getenv("ANTHROPIC_API_KEY"):
    print("Anthropic API key found!")

    # Create adapter with Anthropic
    adapter_anthropic = CrewAIAdapter(
        llm_provider="anthropic",
        model_name="claude-3-sonnet-20240229",
        temperature=0.7,
    )

    print(f"Mock mode: {adapter_anthropic.mock_mode}")
    print(f"Model: {adapter_anthropic.model_name}")

    # Create agent
    agent = adapter_anthropic.wrap_agent(
        trained_model,
        role="Research Assistant",
        goal="Assist with research tasks",
    )

    print("Agent created successfully!")
else:
    print("No Anthropic API key found. Set ANTHROPIC_API_KEY to test real integration.")

print()


# Example 8: Agent with Tools
print("=" * 60)
print("Example 8: Agent with Tools")
print("=" * 60)

adapter = CrewAIAdapter(mock_mode=True)

# Create agent with multiple tools
tools = [
    {"name": "search", "description": "Search the web"},
    {"name": "calculator", "description": "Perform calculations"},
    {"name": "file_reader", "description": "Read files"},
]

agent_with_tools = adapter.wrap_agent(
    "model_with_tools",
    role="Data Scientist",
    goal="Analyze data and provide insights",
    tools=tools,
)

print(f"Agent role: {agent_with_tools['role']}")
print(f"Number of tools: {len(agent_with_tools['tools'])}")
for tool in agent_with_tools['tools']:
    print(f"  - {tool['name']}: {tool['description']}")

extracted_tools = adapter.extract_tools(agent_with_tools)
print(f"Extracted tools: {len(extracted_tools)}")

print()


# Example 9: Framework Info
print("=" * 60)
print("Example 9: Framework Info")
print("=" * 60)

adapter = CrewAIAdapter(mock_mode=True)

info = adapter.get_framework_info()
print(f"Framework: {info['name']}")
print(f"Adapter class: {info['adapter_class']}")
print(f"Available methods: {', '.join(info['methods'])}")

print()


# Example 10: Error Handling
print("=" * 60)
print("Example 10: Error Handling")
print("=" * 60)

# Try to run agent in mock mode (will raise error)
adapter = CrewAIAdapter(mock_mode=True)
agent = adapter.wrap_agent(trained_model, role="Assistant")

try:
    adapter.run_agent(agent, "test task")
except ValueError as e:
    print(f"Expected error: {e}")

# Try to create crew without agents
try:
    adapter.wrap_agent("model", agent_type="crew")
except ValueError as e:
    print(f"Expected error: {e}")

# Try invalid agent type
try:
    adapter.wrap_agent("model", agent_type="invalid")
except ValueError as e:
    print(f"Expected error: {e}")

print()


# Example 11: Large Crew
print("=" * 60)
print("Example 11: Large Multi-Agent Crew")
print("=" * 60)

adapter = CrewAIAdapter(mock_mode=True)

# Create a large crew with specialized agents
agents = [
    adapter.wrap_agent(f"m{i}", role=role, goal=f"Perform {role} tasks")
    for i, role in enumerate(
        [
            "Researcher",
            "Data Analyst",
            "Writer",
            "Editor",
            "Quality Assurance",
        ]
    )
]

crew_model_large = {
    "agents": agents,
    "tasks": [
        {"description": "Research topic"},
        {"description": "Analyze data"},
        {"description": "Write report"},
        {"description": "Edit content"},
        {"description": "Quality check"},
    ],
}

large_crew = adapter.wrap_agent(crew_model_large, agent_type="crew")

print(f"Large crew created with {len(large_crew['model']['agents'])} agents")
print(f"Number of tasks: {len(large_crew['model']['tasks'])}")

env = adapter.create_environment(large_crew)
print(f"Environment config:")
print(f"  Agent type: {env['config']['agent_type']}")
print(f"  Process: {env['config']['process']}")

print()


print("=" * 60)
print("All examples completed!")
print("=" * 60)
