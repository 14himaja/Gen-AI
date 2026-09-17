from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
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


# Create graph
graph = StateGraph(ChatState)


# Add chatbot node
graph.add_node("chatbot", chatbot)


# Connect nodes
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)


# Compile graph
app = graph.compile()


# Run chatbot
while True:

    user_input = input("You: ")

    # Stop the chatbot
    if user_input.lower() in ["exit", "quit"]:
        break

    # Invoke the graph
    result = app.invoke({
        "messages": [
            ("user", user_input)
        ]
    })

    # Print AI response
    print("AI:", result["messages"][-1].content)