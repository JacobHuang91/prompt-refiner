"""
LangChain Agent - With Context and Message History

This example demonstrates how to build an agent with LangChain, including:
- RAG context (retrieved documents)
- Message history (conversation state)
- Tool calling (function execution)

LangChain provides:
- Automatic tool schema generation with @tool decorator
- Built-in message history management
- Unified interface across different LLMs
- Rich ecosystem of integrations

Run: python examples/agents/langchain_agent.py
"""

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from shared_data import CONTEXT_DOCUMENTS, MESSAGE_HISTORY, QUERY, SYSTEM_PROMPT, search_books

# Load environment variables
load_dotenv()


@tool
def search_books_tool(query: str) -> dict:
    """Search for books by query.

    Args:
        query: Search query for finding books

    Returns:
        Dictionary containing search results
    """
    # Use shared search_books function
    return search_books(query)


def main():
    """Run the LangChain agent example with context and history."""
    print("=" * 80)
    print("LangChain Agent - Context and Message History")
    print("=" * 80)
    print()

    # RAG Context - retrieved documents (from shared_data)
    # Strip HTML tags for cleaner output
    from prompt_refiner import StripHTML
    strip_html = StripHTML()
    cleaned_docs = [strip_html.refine(doc) for doc in CONTEXT_DOCUMENTS]

    # Format context
    context_text = "\n".join(f"- {doc}" for doc in cleaned_docs)

    # Message history - previous conversation (from shared_data)
    # Convert dict format to LangChain message objects
    message_history = [
        HumanMessage(content=MESSAGE_HISTORY[0]["content"]),
        AIMessage(content=MESSAGE_HISTORY[1]["content"]),
        HumanMessage(content=MESSAGE_HISTORY[2]["content"]),
        AIMessage(content=MESSAGE_HISTORY[3]["content"]),
    ]

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Define tools
    tools = [search_books_tool]

    # Create prompt template with placeholders for:
    # - System message with context
    # - Message history
    # - Current user input
    # - Agent scratchpad (for tool calling)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""{SYSTEM_PROMPT}

Context:
{{context}}

Use this context when making recommendations.""",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # Create agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    # Create agent executor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    print("Structure:")
    print("  • Context: In system message via prompt template")
    print("  • History: Via chat_history placeholder")
    print("  • Tools: Auto-generated schemas with @tool decorator")
    print("  • Current query: Via input variable")
    print()
    print("Running agent...")
    print()

    # Run agent with context and history (using shared QUERY)
    result = agent_executor.invoke(
        {
            "context": context_text,
            "chat_history": message_history,
            "input": QUERY,
        }
    )

    print()
    print("=" * 80)
    print("Final Response:")
    print("=" * 80)
    print(result["output"])
    print()

    # Demonstrate how to continue the conversation
    print()
    print("=" * 80)
    print("Continuing the conversation...")
    print("=" * 80)
    print()

    # Add the previous exchange to history
    updated_history = message_history + [
        HumanMessage(content=QUERY),
        AIMessage(content=result["output"]),
    ]

    # Continue with updated history
    result2 = agent_executor.invoke(
        {
            "context": context_text,
            "chat_history": updated_history,
            "input": "Which one is best for complete beginners?",
        }
    )

    print()
    print("=" * 80)
    print("Follow-up Response:")
    print("=" * 80)
    print(result2["output"])
    print()

    print("=" * 80)
    print("Summary:")
    print("=" * 80)
    print()
    print("LangChain Features Used:")
    print("  • ChatPromptTemplate: Structured prompt with variables")
    print("  • MessagesPlaceholder: Flexible message history injection")
    print("  • @tool decorator: Automatic schema generation")
    print("  • AgentExecutor: Manages tool calling loop")
    print("  • ChatOpenAI: OpenAI integration")
    print()
    print("Advantages:")
    print("  ✅ Unified interface across different LLMs")
    print("  ✅ Rich ecosystem (memory, retrievers, chains)")
    print("  ✅ Easy prompt templating")
    print("  ✅ Built-in conversation management")
    print()
    print("Considerations:")
    print("  ⚠️  Abstraction layer adds complexity")
    print("  ⚠️  Framework-specific patterns to learn")
    print("  ⚠️  May need to understand internals for debugging")
    print("=" * 80)


if __name__ == "__main__":
    main()
