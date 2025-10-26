"""
TreadWise ReAct Agent - Gradio App
Standalone deployment script for the multi-persona ReAct agent

Student: Mounir Khalil
ID: 202100437
Course: EECE798S Agentic Systems
"""

import os
import json
from datetime import datetime
from typing import TypedDict, Annotated, Sequence, Literal
import operator
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import gradio as gr

# Load environment variables
load_dotenv()

# Load business summary
with open('me/Business_summary.txt', 'r') as f:
    business_summary = f.read()

# ============================================================================
# TOOLS
# ============================================================================

@tool
def record_customer_interest(email: str, name: str, message: str) -> str:
    """
    Record customer interest by logging their contact information and message.
    Use this when a customer wants to schedule service, get a quote, or learn more.

    Args:
        email: Customer's email address
        name: Customer's name
        message: Customer's inquiry or request

    Returns:
        Confirmation message
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lead_entry = {
        "timestamp": timestamp,
        "name": name,
        "email": email,
        "message": message
    }

    with open('customer_leads.jsonl', 'a') as f:
        f.write(json.dumps(lead_entry) + '\n')

    print(f"\n{'='*60}")
    print("NEW CUSTOMER LEAD RECORDED")
    print(f"{'='*60}")
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Message: {message}")
    print(f"{'='*60}\n")

    return f"Successfully recorded contact information for {name} ({email}). Our team will follow up shortly."


@tool
def record_feedback(question: str) -> str:
    """
    Record questions you cannot answer for team review.
    Use this when asked about topics outside your knowledge base.

    Args:
        question: The question you cannot answer

    Returns:
        Confirmation message
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    feedback_entry = {
        "timestamp": timestamp,
        "question": question
    }

    with open('feedback_log.jsonl', 'a') as f:
        f.write(json.dumps(feedback_entry) + '\n')

    print(f"\n{'='*60}")
    print("FEEDBACK LOGGED")
    print(f"{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}\n")

    return "Question logged for team review."


@tool
def get_tire_recommendation(vehicle_type: str, usage: str) -> str:
    """
    Get tire recommendations based on vehicle type and usage pattern.

    Args:
        vehicle_type: Type of vehicle (sedan, suv, truck, commercial)
        usage: Usage pattern (daily_commute, highway, off_road, mixed, heavy_duty)

    Returns:
        Tire recommendations
    """
    recommendations = {
        ("sedan", "daily_commute"): "EcoGlide All-Season - Optimized for fuel efficiency and comfort",
        ("sedan", "highway"): "TourMax Highway - Long tread life and quiet ride",
        ("suv", "mixed"): "TrailBlazer A/T - Versatile for road and light off-road",
        ("suv", "off_road"): "MudWarrior M/T - Aggressive tread for serious terrain",
        ("truck", "heavy_duty"): "LoadMaster Commercial - High load capacity and durability",
        ("commercial", "heavy_duty"): "FleetPro LT - Designed for commercial vehicle fleets with Smart Tread™ compatibility"
    }

    key = (vehicle_type.lower(), usage.lower())
    recommendation = recommendations.get(key, "Contact us for personalized tire recommendations based on your specific needs")

    return f"Recommendation: {recommendation}"


@tool
def check_service_availability(location: str, service_type: str) -> str:
    """
    Check if a service is available in a specific location.

    Args:
        location: City or region name
        service_type: Type of service (mobile_installation, smart_tread, fleet_management)

    Returns:
        Availability information
    """
    major_cities = ["new york", "los angeles", "chicago", "houston", "phoenix", "philadelphia"]

    location_lower = location.lower()
    is_major_city = any(city in location_lower for city in major_cities)

    if service_type == "mobile_installation":
        if is_major_city:
            return f"Mobile installation is available in {location} with same-day service options!"
        else:
            return f"Mobile installation coverage in {location} - please provide your zip code for specific availability."
    elif service_type == "smart_tread":
        return f"Smart Tread™ IoT monitoring is available nationwide, including {location}."
    elif service_type == "fleet_management":
        return f"Fleet management services are available in {location}. We work with fleets of all sizes."

    return "Please specify service type: mobile_installation, smart_tread, or fleet_management"


# Collect all tools
tools = [record_customer_interest, record_feedback, get_tire_recommendation, check_service_availability]

# ============================================================================
# PERSONAS
# ============================================================================

PERSONA_PROMPTS = {
    "friendly_advisor": f"""
You are a warm and enthusiastic customer service advisor for TreadWise Tire Co.

BUSINESS CONTEXT:
{business_summary}

YOUR PERSONALITY:
- Warm, friendly, and personable - you make customers feel valued
- Enthusiastic about TreadWise's mission and innovations
- Build rapport by relating to customer needs and concerns
- Use conversational language
- Focus on benefits and customer experience

YOUR APPROACH:
- Start with a friendly greeting
- Ask clarifying questions to understand customer needs
- Share relevant success stories and customer benefits
- Proactively offer to help with next steps
- End conversations warmly

AVAILABLE TOOLS:
- record_customer_interest: Collect contact info when customers want to learn more
- record_feedback: Log questions you can't answer
- get_tire_recommendation: Suggest tires based on vehicle and usage
- check_service_availability: Check if services are available in customer's area

Remember: You're building relationships, not just answering questions!
""",

    "technical_expert": f"""
You are a highly knowledgeable technical expert for TreadWise Tire Co.

BUSINESS CONTEXT:
{business_summary}

YOUR PERSONALITY:
- Precise, accurate, and detail-oriented
- Data-driven and specification-focused
- Professional and authoritative
- Cite specific features, numbers, and technical details
- Prefer clarity over friendliness

YOUR APPROACH:
- Provide exact specifications and technical details
- Explain the "how" and "why" behind features
- Reference IoT sensors, pressure monitoring, predictive analytics
- Discuss engineering aspects of tire design
- Be thorough and comprehensive

AVAILABLE TOOLS:
- record_customer_interest: Collect contact info when customers want to learn more
- record_feedback: Log questions you can't answer
- get_tire_recommendation: Suggest tires based on vehicle and usage
- check_service_availability: Check if services are available in customer's area

Remember: Accuracy and technical depth are your strengths!
""",

    "cautious_helper": f"""
You are a careful and thorough advisor for TreadWise Tire Co.

BUSINESS CONTEXT:
{business_summary}

YOUR PERSONALITY:
- Cautious and risk-aware
- Thorough in gathering information before making suggestions
- Conservative with promises
- Emphasize safety and compliance
- Set realistic expectations

YOUR APPROACH:
- Ask many clarifying questions before recommending
- Emphasize safety features and proper tire maintenance
- Mention potential limitations or considerations
- Suggest customers verify details with specialists
- Always confirm understanding before proceeding

AVAILABLE TOOLS:
- record_customer_interest: Collect contact info when customers want to learn more
- record_feedback: Log questions you can't answer
- get_tire_recommendation: Suggest tires based on vehicle and usage
- check_service_availability: Check if services are available in customer's area

Remember: Better to ask twice than assume once!
"""
}

# ============================================================================
# REACT AGENT
# ============================================================================

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    thoughts: list[str]
    iterations: int


def create_react_agent(persona_name: str, model_name: str = "gpt-4o-mini", temperature: float = 0.7, max_tokens: int = 500):
    """
    Create a ReAct agent with specified persona and LLM configuration.
    """
    llm = ChatOpenAI(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=os.getenv('OPENAI_API_KEY')
    )

    llm_with_tools = llm.bind_tools(tools)
    system_prompt = PERSONA_PROMPTS[persona_name]

    def reason(state: AgentState) -> AgentState:
        """Agent reasons about what to do next."""
        messages = state["messages"]

        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=system_prompt)] + list(messages)

        response = llm_with_tools.invoke(messages)

        thought = f"Iteration {state['iterations'] + 1}: Reasoning about user query"
        thoughts = state.get("thoughts", []) + [thought]

        return {
            "messages": [response],
            "thoughts": thoughts,
            "iterations": state["iterations"] + 1
        }

    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """Decide whether to use tools or end."""
        messages = state["messages"]
        last_message = messages[-1]

        # Max iterations safeguard
        if state["iterations"] >= 5:
            return "end"

        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"

        return "end"

    workflow = StateGraph(AgentState)
    workflow.add_node("reason", reason)
    workflow.add_node("tools", ToolNode(tools))
    workflow.set_entry_point("reason")
    workflow.add_conditional_edges(
        "reason",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    workflow.add_edge("tools", "reason")

    return workflow.compile()


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

# Cache agents
agents_cache = {}

def get_agent(persona, temperature):
    """Get or create an agent with specified config."""
    key = f"{persona}_{temperature}"
    if key not in agents_cache:
        agents_cache[key] = create_react_agent(persona, temperature=float(temperature))
    return agents_cache[key]

def chat_with_persona(message, history, persona, temperature):
    """Handle chat with selected persona."""
    try:
        agent = get_agent(persona, temperature)

        # Build message history
        messages = []
        for h in history:
            messages.append(HumanMessage(content=h[0]))
            messages.append(AIMessage(content=h[1]))
        messages.append(HumanMessage(content=message))

        # Run agent
        result = agent.invoke({
            "messages": messages,
            "thoughts": [],
            "iterations": 0
        })

        response = result["messages"][-1].content
        return response

    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="TreadWise ReAct Agent", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # TreadWise Tire Co. - Multi-Persona ReAct Agent

    **Student:** Mounir Khalil | **ID:** 202100437 | **Course:** EECE798S Agentic Systems

    Test different agent personas and configurations! Each persona has a unique approach to customer service.
    """)

    with gr.Row():
        with gr.Column(scale=1):
            persona_select = gr.Dropdown(
                choices=[
                    ("Friendly Advisor (Warm & Enthusiastic)", "friendly_advisor"),
                    ("Technical Expert (Precise & Detailed)", "technical_expert"),
                    ("Cautious Helper (Thorough & Safety-Focused)", "cautious_helper")
                ],
                value="friendly_advisor",
                label="Select Agent Persona",
                info="Choose the personality style for the agent"
            )
            temperature_slider = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                value=0.7,
                step=0.1,
                label="Temperature",
                info="Higher = more creative, Lower = more consistent"
            )

            gr.Markdown("""
            ### About the Personas:

            **Friendly Advisor:** Best for general customer service, warm and engaging

            **Technical Expert:** Best for detailed technical questions, precise and thorough

            **Cautious Helper:** Best for safety concerns, careful and conservative
            """)

        with gr.Column(scale=2):
            chatbot = gr.Chatbot(height=500, label="TreadWise Assistant")
            msg = gr.Textbox(
                label="Your Message",
                placeholder="Ask about TreadWise services, tire recommendations, or anything else!",
                lines=2
            )

            with gr.Row():
                submit = gr.Button("Send", variant="primary")
                clear = gr.Button("Clear Chat")

    gr.Examples(
        examples=[
            "What makes TreadWise different from other tire companies?",
            "I need tires for my SUV for mixed highway and off-road use",
            "Is mobile installation available in Chicago?",
            "Tell me about the Smart Tread platform and how it works",
            "I'm interested in fleet management. I'm John at john@example.com"
        ],
        inputs=msg,
        label="Example Questions"
    )

    def respond(message, chat_history, persona, temperature):
        bot_message = chat_with_persona(message, chat_history, persona, temperature)
        chat_history.append((message, bot_message))
        return "", chat_history

    submit.click(respond, [msg, chatbot, persona_select, temperature_slider], [msg, chatbot])
    msg.submit(respond, [msg, chatbot, persona_select, temperature_slider], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    print("Starting TreadWise ReAct Agent...")
    print("Make sure you have set OPENAI_API_KEY in your .env file")
    demo.launch(share=True, server_name="0.0.0.0", server_port=7860)
