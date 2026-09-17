from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from pydantic import BaseModel, Field
import operator
# Load environment variables
load_dotenv()

# Create LLM
model = ChatOpenAI(model='gpt-4o-mini')

# Define structured output format
class EvaluationSchema(BaseModel):
    feedback: str = Field( description='Detailed feedback for the essay')
    score: int = Field(description='Score out of 10',ge=0,le=10)

# Make LLM return structured output
structured_model = model.with_structured_output(EvaluationSchema)

# Sample essay
essay = """India in the Age of AI

As the world enters a transformative era defined by artificial intelligence (AI),
India stands at a critical juncture — one where it can either emerge as a global
leader in AI innovation or risk falling behind in the technology race.

India's strengths in the AI domain are rooted in its vast pool of skilled engineers,
a thriving IT industry, and a growing startup ecosystem.

However, the path to AI-led growth is riddled with challenges.
Chief among them is the digital divide.

Another pressing concern is data privacy and ethics.

To harness AI responsibly, India must adopt a multi-stakeholder approach involving
the government, academia, industry, and civil society.

In conclusion, India in the age of AI is a story in the making — one of opportunity,
responsibility, and transformation."""

# Define graph state
class UPSCState(TypedDict):
    essay: str
    language_feedback: str
    analysis_feedback: str
    clarity_feedback: str
    overall_feedback: str
    # Collect scores from parallel nodes
    individual_scores: Annotated[list[int], operator.add]
    avg_score: float

# Evaluate language
def evaluate_language(state: UPSCState):
    prompt = f"""
    Evaluate the language quality of the following essay
    and provide a feedback and assign a score out of 10.
    {state["essay"]}
    """
    output = structured_model.invoke(prompt)
    return {
        'language_feedback': output.feedback,
        'individual_scores': [output.score]
    }
# Evaluate depth of analysis
def evaluate_analysis(state: UPSCState):
    prompt = f"""
    Evaluate the depth of analysis of the following essay
    and provide a feedback and assign a score out of 10.

    {state["essay"]}
    """

    output = structured_model.invoke(prompt)

    return {
        'analysis_feedback': output.feedback,
        'individual_scores': [output.score]
    }


# Evaluate clarity of thought
def evaluate_thought(state: UPSCState):

    prompt = f"""
    Evaluate the clarity of thought of the following essay
    and provide a feedback and assign a score out of 10.

    {state["essay"]}
    """

    output = structured_model.invoke(prompt)

    return {
        'clarity_feedback': output.feedback,
        'individual_scores': [output.score]
    }


# Create final evaluation
def final_evaluation(state: UPSCState):

    # Combine all feedback
    prompt = f"""
    Based on the following feedbacks create a summarized feedback.

    Language feedback:
    {state["language_feedback"]}

    Depth of analysis feedback:
    {state["analysis_feedback"]}

    Clarity of thought feedback:
    {state["clarity_feedback"]}
    """

    overall_feedback = model.invoke(prompt).content

    # Calculate average score
    avg_score = (
        sum(state['individual_scores'])
        / len(state['individual_scores'])
    )

    return {
        'overall_feedback': overall_feedback,
        'avg_score': avg_score
    }

# Create graph
graph = StateGraph(UPSCState)

# Add nodes
graph.add_node('evaluate_language', evaluate_language)
graph.add_node('evaluate_analysis', evaluate_analysis)
graph.add_node('evaluate_thought', evaluate_thought)
graph.add_node('final_evaluation', final_evaluation)

# Start three evaluations in parallel
graph.add_edge(START, 'evaluate_language')
graph.add_edge(START, 'evaluate_analysis')
graph.add_edge(START, 'evaluate_thought')

# Send all evaluations to final node
graph.add_edge('evaluate_language','final_evaluation')
graph.add_edge('evaluate_analysis','final_evaluation')
graph.add_edge('evaluate_thought','final_evaluation')
# End workflow
graph.add_edge('final_evaluation', END)
# Compile graph
workflow = graph.compile()
# Initial state
initial_state = {
    'essay': essay,
    'language_feedback': '',
    'analysis_feedback': '',
    'clarity_feedback': '',
    'overall_feedback': '',
    'individual_scores': [],
    'avg_score': 0
}
# Run workflow
final_state = workflow.invoke(initial_state)
# Print result
print(final_state)