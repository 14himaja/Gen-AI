from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field


# Load environment variables
load_dotenv()


# Create the LLM
model = ChatOpenAI(model='gpt-4o-mini')


# Schema for sentiment
class SentimentSchema(BaseModel):

    sentiment: Literal["positive", "negative"] = Field(
        description='Sentiment of the review'
    )


# Schema for diagnosing negative reviews
class DiagnosisSchema(BaseModel):

    issue_type: Literal[
        "UX", "Performance", "Bug", "Support", "Other"
    ] = Field(
        description='The category of issue mentioned in the review'
    )

    tone: Literal[
        "angry", "frustrated", "disappointed", "calm"
    ] = Field(
        description='The emotional tone expressed by the user'
    )

    urgency: Literal[
        "low", "medium", "high"
    ] = Field(
        description='How urgent or critical the issue appears to be'
    )


# Create structured-output models
structured_model = model.with_structured_output(SentimentSchema)
structured_model2 = model.with_structured_output(DiagnosisSchema)


# Define graph state
class ReviewState(TypedDict):

    review: str
    sentiment: Literal["positive", "negative"]
    diagnosis: dict
    response: str


# Find sentiment of review
def find_sentiment(state: ReviewState):

    prompt = f"""
    For the following review find out the sentiment:

    {state["review"]}
    """

    sentiment = structured_model.invoke(prompt).sentiment

    return {
        'sentiment': sentiment
    }


# Decide which path to take
def check_sentiment(
    state: ReviewState
) -> Literal["positive_response", "run_diagnosis"]:

    if state['sentiment'] == 'positive':
        return 'positive_response'
    else:
        return 'run_diagnosis'


# Generate response for positive review
def positive_response(state: ReviewState):

    prompt = f"""
    Write a warm thank-you message in response to this review:

    "{state['review']}"

    Also, kindly ask the user to leave feedback on our website.
    """

    response = model.invoke(prompt).content

    return {
        'response': response
    }


# Diagnose negative review
def run_diagnosis(state: ReviewState):

    prompt = f"""
    Diagnose this negative review:

    {state['review']}

    Return issue_type, tone, and urgency.
    """

    response = structured_model2.invoke(prompt)

    return {
        'diagnosis': response.model_dump()
    }


# Generate response for negative review
def negative_response(state: ReviewState):

    diagnosis = state['diagnosis']

    prompt = f"""
    You are a support assistant.

    The user had a '{diagnosis['issue_type']}' issue,
    sounded '{diagnosis['tone']}',
    and marked urgency as '{diagnosis['urgency']}'

    Write an empathetic, helpful resolution message.
    """

    response = model.invoke(prompt).content

    return {
        'response': response
    }


# Create the graph
graph = StateGraph(ReviewState)


# Add nodes
graph.add_node('find_sentiment', find_sentiment)
graph.add_node('positive_response', positive_response)
graph.add_node('run_diagnosis', run_diagnosis)
graph.add_node('negative_response', negative_response)


# Start with sentiment analysis
graph.add_edge(START, 'find_sentiment')


# Route based on sentiment
graph.add_conditional_edges(
    'find_sentiment',
    check_sentiment
)
# Positive path
graph.add_edge('positive_response',END)
# Negative path
graph.add_edge('run_diagnosis','negative_response')
graph.add_edge('negative_response',END)
# Compile the workflow
workflow = graph.compile()