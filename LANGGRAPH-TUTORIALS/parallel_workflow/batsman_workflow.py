from langgraph.graph import StateGraph, START, END
from typing import TypedDict


# Define the state
class BatsmanState(TypedDict):

    runs: int
    balls: int
    fours: int
    sixes: int

    sr: float
    bpb: float
    boundary_percent: float
    summary: str


# Calculate strike rate
def calculate_sr(state: BatsmanState):

    sr = (state['runs'] / state['balls']) * 100

    return {'sr': sr}


# Calculate balls per boundary
def calculate_bpb(state: BatsmanState):

    bpb = state['balls'] / (state['fours'] + state['sixes'])

    return {'bpb': bpb}


# Calculate boundary percentage
def calculate_boundary_percent(state: BatsmanState):

    boundary_percent = (
        ((state['fours'] * 4) + (state['sixes'] * 6))
        / state['runs']
    ) * 100

    return {'boundary_percent': boundary_percent}


# Create final summary
def summary(state: BatsmanState):

    summary = f"""
Strike Rate - {state['sr']}

Balls per boundary - {state['bpb']}

Boundary percent - {state['boundary_percent']}
"""

    return {'summary': summary}


# Create the graph
graph = StateGraph(BatsmanState)


# Add nodes
graph.add_node('calculate_sr', calculate_sr)
graph.add_node('calculate_bpb', calculate_bpb)
graph.add_node('calculate_boundary_percent', calculate_boundary_percent)
graph.add_node('summary', summary)


# Connect START to calculation nodes
graph.add_edge(START, 'calculate_sr')
graph.add_edge(START, 'calculate_bpb')
graph.add_edge(START, 'calculate_boundary_percent')


# Connect calculation nodes to summary
graph.add_edge('calculate_sr', 'summary')
graph.add_edge('calculate_bpb', 'summary')
graph.add_edge('calculate_boundary_percent', 'summary')


# End the workflow
graph.add_edge('summary', END)


# Compile the graph
workflow = graph.compile()


# Input data
initial_state = {
    'runs': 100,
    'balls': 80,
    'fours': 10,
    'sixes': 5
}


# Run the workflow
final_state = workflow.invoke(initial_state)

print(final_state)