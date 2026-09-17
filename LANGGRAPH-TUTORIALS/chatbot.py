from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
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

    # Send messages to LLM
    response = llm.invoke(state["messages"])

    return {
        "messages": [response]
    }


# Create graph
graph = StateGraph(ChatState)


# Add chatbot node
graph.add_node("chatbot", chatbot)


# Connect START → chatbot → END
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)


# Compile graph
chatbot_graph = graph.compile()


# User message
input_message = HumanMessage(
    content="Hello, tell me about LangGraph."
)


# Run chatbot
result = chatbot_graph.invoke({
    "messages": [input_message]
})


# Print AI response
print(result["messages"][-1].content)