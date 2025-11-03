"""Example usage of LangChain adapter with real LLM integration.

This example demonstrates how to:
1. Create a LangChain adapter with different LLM providers
2. Wrap trained models as LangChain agents
3. Run agents with real LLMs (requires API keys)
4. Use mock mode for testing without API keys

Prerequisites:
- For OpenAI: pip install langchain-openai + OPENAI_API_KEY environment variable
- For Anthropic: pip install langchain-anthropic + ANTHROPIC_API_KEY environment variable
- For testing: No requirements (uses mock mode automatically)
"""

import os

from agentgym.integrations.langchain import LangChainAdapter

# Example 1: Mock Mode (no API keys required)
print("=" * 60)
print("Example 1: Mock Mode")
print("=" * 60)

# Create adapter in mock mode
adapter = LangChainAdapter(mock_mode=True)
print(f"Mock mode: {adapter.mock_mode}")

# Wrap a trained model
trained_model = "./models/customer_support_ep100"
agent = adapter.wrap_agent(trained_model)

print(f"Agent type: {agent['type']}")
print(f"Model path: {agent['model']}")
print(f"Mock agent: {agent.get('_mock', False)}")

# Validate the agent
is_valid = adapter.validate_agent(agent)
print(f"Agent valid: {is_valid}")

# Create environment
env = adapter.create_environment(agent)
print(f"Environment type: {env['type']}")

print()


# Example 2: Auto-detection (automatically uses mock mode if no API keys)
print("=" * 60)
print("Example 2: Auto-detection")
print("=" * 60)

# Create adapter without specifying mock mode
# Will automatically enable mock mode if no API keys found
adapter_auto = LangChainAdapter(llm_provider="openai")
print(f"LLM provider: {adapter_auto.llm_provider}")
print(f"Auto-detected mock mode: {adapter_auto.mock_mode}")

print()


# Example 3: Real OpenAI Integration (requires OPENAI_API_KEY)
print("=" * 60)
print("Example 3: Real OpenAI Integration")
print("=" * 60)

if os.getenv("OPENAI_API_KEY"):
    print("OpenAI API key found!")

    # Create adapter with OpenAI
    adapter_openai = LangChainAdapter(
        llm_provider="openai",
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        verbose=True,
    )

    print(f"Mock mode: {adapter_openai.mock_mode}")
    print(f"Model: {adapter_openai.model_name}")

    # Create a simple tool
    from langchain.tools import Tool

    def search_tool(query: str) -> str:
        """Mock search tool."""
        return f"Search results for: {query}"

    tools = [
        Tool(
            name="search",
            func=search_tool,
            description="Search for information",
        )
    ]

    # Wrap trained model with tools
    agent = adapter_openai.wrap_agent(trained_model, tools=tools)

    # Run the agent (this will make real API calls)
    # Uncomment to test:
    # result = adapter_openai.run_agent(agent, "What is the weather today?")
    # print(f"Agent response: {result['output']}")

    print("Agent created successfully!")
    print(f"Agent has {len(adapter_openai.extract_tools(agent))} tools")
else:
    print("No OpenAI API key found. Set OPENAI_API_KEY to test real integration.")

print()


# Example 4: Real Anthropic Integration (requires ANTHROPIC_API_KEY)
print("=" * 60)
print("Example 4: Real Anthropic Integration")
print("=" * 60)

if os.getenv("ANTHROPIC_API_KEY"):
    print("Anthropic API key found!")

    # Create adapter with Anthropic
    adapter_anthropic = LangChainAdapter(
        llm_provider="anthropic",
        model_name="claude-3-sonnet-20240229",
        temperature=0.7,
        verbose=True,
    )

    print(f"Mock mode: {adapter_anthropic.mock_mode}")
    print(f"Model: {adapter_anthropic.model_name}")

    # Wrap trained model
    agent = adapter_anthropic.wrap_agent(trained_model)

    # Run the agent (this will make real API calls)
    # Uncomment to test:
    # result = adapter_anthropic.run_agent(agent, "Summarize this for me")
    # print(f"Agent response: {result['output']}")

    print("Agent created successfully!")
else:
    print("No Anthropic API key found. Set ANTHROPIC_API_KEY to test real integration.")

print()


# Example 5: Using Different Agent Types
print("=" * 60)
print("Example 5: Different Agent Types")
print("=" * 60)

adapter = LangChainAdapter(mock_mode=True)

# Zero-shot ReAct (default)
agent1 = adapter.wrap_agent(trained_model, agent_type="zero-shot-react-description")
print(f"Agent 1 type: {agent1['executor']['agent_type']}")

# Conversational ReAct
agent2 = adapter.wrap_agent(
    trained_model, agent_type="conversational-react-description"
)
print(f"Agent 2 type: {agent2['executor']['agent_type']}")

# Self-ask with search
agent3 = adapter.wrap_agent(trained_model, agent_type="self-ask-with-search")
print(f"Agent 3 type: {agent3['executor']['agent_type']}")

print()


# Example 6: Custom Memory
print("=" * 60)
print("Example 6: Custom Memory")
print("=" * 60)

adapter = LangChainAdapter(mock_mode=True)

# Wrap agent with custom memory object
custom_memory = {"history": [], "max_length": 10}
agent = adapter.wrap_agent(trained_model, memory=custom_memory)

print(f"Agent has custom memory: {agent['memory'] == custom_memory}")
print(f"Memory config: {agent['memory']}")

print()


# Example 7: Framework Info
print("=" * 60)
print("Example 7: Framework Info")
print("=" * 60)

adapter = LangChainAdapter(mock_mode=True)

info = adapter.get_framework_info()
print(f"Framework: {info['name']}")
print(f"Adapter class: {info['adapter_class']}")
print(f"Available methods: {', '.join(info['methods'])}")

print()


# Example 8: Error Handling
print("=" * 60)
print("Example 8: Error Handling")
print("=" * 60)

# Try to run agent in mock mode (will raise error)
adapter = LangChainAdapter(mock_mode=True)
agent = adapter.wrap_agent(trained_model)

try:
    adapter.run_agent(agent, "test input")
except ValueError as e:
    print(f"Expected error: {e}")

# Try to create LLM with unknown provider
adapter_bad = LangChainAdapter(llm_provider="unknown", mock_mode=False)
adapter_bad.mock_mode = False  # Force real mode

try:
    adapter_bad._create_llm()
except ValueError as e:
    print(f"Expected error: {e}")

print()


print("=" * 60)
print("All examples completed!")
print("=" * 60)
