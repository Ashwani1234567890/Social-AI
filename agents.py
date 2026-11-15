import os
import json
from typing import TypedDict
from pydantic import BaseModel
from dotenv import load_dotenv
from google.genai import Client
from langgraph.graph import StateGraph,START,END

load_dotenv()

API_KEY=os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Api key invalid")

client=Client(api_key=API_KEY) 

MODEL='gemini-3.8-flash'

def ask_ai(prompt):
    if client is None:
        raise ValueError('add Gemini api key ')

    response=client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text


class SocialPost(BaseModel):
    platform:str
    title:str
    hooks:str
    caption:str
    hashtags:list[str]
    cta:str

class PostBundle(BaseModel):
    posts:list[SocialPost]


class AgentState(TypedDict):
    business:str
    industry:str
    platform:str
    topic:str
    number_of_posts:str

    research:str
    posts:list[dict]
    quality_report:str

def research_agent(state:AgentState):
    prompt=f'''
        You are a social media research agent

        Business:{state['business']}
        Industry: {state['industry']}
        Topic: {state['topic']}
        Platform: {state['platform']}

        Identify:
        1. Relevant audience interests.
        2. Five content angles.
        3. Common audience problems.
        4. Useful educational content ideas.

        Do not invent statistics or claim you performed live research.
        Return a concise research report.
        '''

    result=ask_ai(prompt)

    return {'response':result}

def content_agent(state:AgentState):
    prompt=f'''
        You are an expert social media content creator.

    Business: {state['business']}
    Industry: {state['industry']}
    Platform: {state['platform']}
    Topic: {state['topic']}

    Research:
    {state['research']}

    Generate exactly {state['number_of_posts']} different posts.

    Requirements:
    - Interesting hooks.
    - Engaging captions.
    - Relevant hashtags.
    - Strong calls to action.
    - No fake statistics.
    - Adapt content to the selected platform.

    Return the required structured output.
    '''

    response=client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type":"json",
            "response_schema":PostBundle
        }
    )

    if response.text is None:
        raise ValueError("Gemini returned an empty response")

    bundle=PostBundle.model_validate_json(response.text)

    return {
        'posts':[
            post.model_dump()
            for post in bundle.posts
        ]
    }

def quality_agent(state:AgentState):
    prompt = f"""
    You are a social media quality control agent.

    Business: {state['business']}
    Platform: {state['platform']}

    Review these posts:
    {json.dumps(state['posts'], indent=2)}

    Check:
    1. Grammar.
    2. Brand relevance.
    3. Engagement potential.
    4. Repeated content.
    5. Unsupported claims.
    6. Platform suitability.

    Give each post a score out of 100.
    Identify problems and suggest improvements.

    Do not claim that a post is factually verified
    unless evidence is supplied.

    Return a readable report.
    """

    result=ask_ai(prompt)
    return {'quality_report':result}


builder=StateGraph(AgentState)
builder.add_node("research",research_agent)
builder.add_node('content',content_agent)
builder.add_node('quality',quality_agent)

builder.add_edge(START,"research")
builder.add_edge("research","content")
builder.add_edge("content","quality")
builder.add_edge("quality",END)

social_media_graph=builder.compile()


def run_social_media_agents(
        business,
        industry,
        platform,
        topic,
        number_of_posts
):

    intial_state:AgentState={
        "business":business,
        "industry":industry,
        "platform":platform,
        "topic":topic,
        'number_of_posts':number_of_posts,
        'research':"",
        'posts':[],
        'quality_report':""
    }

    return social_media_graph.invoke(intial_state)