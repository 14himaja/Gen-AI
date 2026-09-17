from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv
# Load environment variables
load_dotenv()
# Create LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Define chatbot state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Chatbot node
def chatbot(state: ChatState):
    # Get response from LLM
    response = llm.invoke(state["messages"])
    return {
        "messages": [response]
    }

# Human approval node
def human_review(state: ChatState):
    # Pause and ask human for approval
    decision = interrupt(
        "Do you want to continue? Type yes or no."
    )
    return {
        "messages": [
            HumanMessage(content=f"Human decision: {decision}")
        ]
    }

# Create graph
graph = StateGraph(ChatState)

# Add nodes
graph.add_node("chatbot", chatbot)
graph.add_node("human_review", human_review)

# Connect nodes
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", "human_review")
graph.add_edge("human_review", END)

# Create memory/checkpointer
memory = MemorySaver()

# Compile graph
app = graph.compile(checkpointer=memory)

# Thread configuration
config = {
    "configurable": {
        "thread_id": "1"
    }
}

# Initial message
input_message = {
    "messages": [
        HumanMessage(content="Tell me a joke.")
    ]
}

# Run until human interaction
result = app.invoke( input_message,config=config)
print(result)
# Resume after human decision
decision = input("Enter your decision: ")
result = app.invoke(Command(resume=decision),config=config)
# Print final result
print(result["messages"][-1].content)