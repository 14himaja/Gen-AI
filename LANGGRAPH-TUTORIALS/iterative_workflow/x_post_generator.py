from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create LLM
model = ChatOpenAI(model='gpt-4o-mini')

# Define state
class PostState(TypedDict):

    topic: str
    post: str

# Generate X post
def generate_post(state: PostState):

    prompt = f"""
    Write a short and engaging X post about:

    {state['topic']}

    Keep it concise and interesting.
    """
    response = model.invoke(prompt)

    return {
        'post': response.content
    }

# Create graph
graph = StateGraph(PostState)

# Add node
graph.add_node('generate_post', generate_post)

# Connect nodes
graph.add_edge(START, 'generate_post')
graph.add_edge('generate_post', END)

# Compile graph
workflow = graph.compile()

# Input
initial_state = {'topic': 'Artificial Intelligence'}

# Run workflow
final_state = workflow.invoke(initial_state)

# Print generated post
print(final_state['post'])