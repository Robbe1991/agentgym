"""Example usage of AutoGen adapter with real LLM integration.

This example demonstrates how to:
1. Create an AutoGen adapter with different agent types
2. Wrap trained models as AutoGen agents
3. Create multi-agent group chats
4. Use mock mode for testing without API keys

Prerequisites:
- For OpenAI: pip install pyautogen[openai] + OPENAI_API_KEY environment variable
- For testing: No requirements (uses mock mode automatically)
"""

import os

from agentgym.integrations.autogen import AutoGenAdapter

# Example 1: Mock Mode (no API keys required)
print("=" * 60)
print("Example 1: Mock Mode - Single Assistant Agent")
print("=" * 60)

# Create adapter in mock mode
adapter = AutoGenAdapter(mock_mode=True)
print(f"Mock mode: {adapter.mock_mode}")

# Wrap a trained model as assistant agent
trained_model = "./models/customer_support_ep100"
agent = adapter.wrap_agent(trained_model, agent_type="assistant")

print(f"Agent type: {agent['type']}")
print(f"Agent model: {agent['agent_type']}")
print(f"Mock agent: {agent.get('_mock', False)}")

# Validate the agent
is_valid = adapter.validate_agent(agent)
print(f"Agent valid: {is_valid}")

# Create environment
env = adapter.create_environment(agent)
print(f"Environment type: {env['type']}")
print(f"Number of agents: {len(env['agents'])}")

print()


# Example 2: Multi-Agent System (Mock Mode)
print("=" * 60)
print("Example 2: Multi-Agent Group Chat")
print("=" * 60)

adapter = AutoGenAdapter(mock_mode=True, max_consecutive_auto_reply=5)

# Create multiple agents
assistant = adapter.wrap_agent(
    "model1",
    agent_type="assistant",
    system_message="You are a helpful coding assistant"
)

user_proxy = adapter.wrap_agent(
    "model2",
    agent_type="user_proxy",
    code_execution=True,
    system_message="You execute code and provide feedback"
)

# Create group chat with multiple agents
group_chat = adapter.wrap_agent(
    "group_model",
    agent_type="group_chat",
    agents=[assistant, user_proxy]
)

print(f"Group chat type: {group_chat['agent_type']}")
print(f"Number of agents in group: {len(group_chat['agents'])}")

# Extract all agents
agents = adapter.extract_tools(group_chat)
print(f"Extracted agents: {len(agents)}")

# Create environment for group chat
env = adapter.create_environment(group_chat)
print(f"Environment has {len(env['agents'])} agents")
print(f"Config: {env['config']}")

print()


# Example 3: Auto-detection (automatically uses mock mode if no API keys)
print("=" * 60)
print("Example 3: Auto-detection")
print("=" * 60)

# Create adapter without specifying mock mode
# Will automatically enable mock mode if no API keys found
adapter_auto = AutoGenAdapter(llm_provider="openai")
print(f"LLM provider: {adapter_auto.llm_provider}")
print(f"Auto-detected mock mode: {adapter_auto.mock_mode}")

print()


# Example 4: Real OpenAI Integration (requires OPENAI_API_KEY)
print("=" * 60)
print("Example 4: Real OpenAI Integration")
print("=" * 60)

if os.getenv("OPENAI_API_KEY"):
    print("OpenAI API key found!")

    # Create adapter with OpenAI
    adapter_openai = AutoGenAdapter(
        llm_provider="openai",
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        max_consecutive_auto_reply=10,
        verbose=True,
    )

    print(f"Mock mode: {adapter_openai.mock_mode}")
    print(f"Model: {adapter_openai.model_name}")

    # Create assistant agent
    assistant = adapter_openai.wrap_agent(
        trained_model,
        agent_type="assistant",
        system_message="You are a helpful AI assistant"
    )

    # Create user proxy agent
    user_proxy = adapter_openai.wrap_agent(
        trained_model,
        agent_type="user_proxy",
        code_execution=False
    )

    # Run conversation (this will make real API calls)
    # Uncomment to test:
    # result = adapter_openai.run_agent(
    #     assistant,
    #     "What is the weather today?",
    #     recipient=user_proxy
    # )
    # print(f"Conversation messages: {len(result['messages'])}")

    print("Agents created successfully!")
else:
    print("No OpenAI API key found. Set OPENAI_API_KEY to test real integration.")

print()


# Example 5: Code Execution Agent
print("=" * 60)
print("Example 5: Code Execution Agent")
print("=" * 60)

adapter = AutoGenAdapter(mock_mode=True)

# Create user proxy with code execution enabled
code_agent = adapter.wrap_agent(
    "code_model",
    agent_type="user_proxy",
    code_execution=True,
    system_message="You can execute Python code"
)

print(f"Agent type: {code_agent['agent_type']}")
print(f"Code execution enabled: {code_agent['code_execution']}")

print()


# Example 6: Framework Info
print("=" * 60)
print("Example 6: Framework Info")
print("=" * 60)

adapter = AutoGenAdapter(mock_mode=True)

info = adapter.get_framework_info()
print(f"Framework: {info['name']}")
print(f"Adapter class: {info['adapter_class']}")
print(f"Available methods: {', '.join(info['methods'])}")

print()


# Example 7: Different Max Auto-Reply Settings
print("=" * 60)
print("Example 7: Different Max Auto-Reply Settings")
print("=" * 60)

for max_replies in [5, 10, 20]:
    adapter = AutoGenAdapter(
        mock_mode=True,
        max_consecutive_auto_reply=max_replies
    )
    agent = adapter.wrap_agent("model")

    print(f"Max consecutive auto-reply set to {max_replies}: "
          f"{agent['config']['max_consecutive_auto_reply']}")

print()


# Example 8: Error Handling
print("=" * 60)
print("Example 8: Error Handling")
print("=" * 60)

# Try to run agent in mock mode (will raise error)
adapter = AutoGenAdapter(mock_mode=True)
agent = adapter.wrap_agent(trained_model)

try:
    adapter.run_agent(agent, "test message")
except ValueError as e:
    print(f"Expected error: {e}")

# Try to create LLM config with unknown provider
adapter_bad = AutoGenAdapter(llm_provider="unknown", mock_mode=False)
adapter_bad.mock_mode = False  # Force real mode

try:
    adapter_bad._create_llm_config()
except ValueError as e:
    print(f"Expected error: {e}")

print()


print("=" * 60)
print("All examples completed!")
print("=" * 60)
