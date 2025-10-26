# TreadWise Tire Co. - ReAct Agent with Multiple Personas

**Student:** Mounir Khalil
**ID:** 202100437
**Course:** EECE798S Agentic Systems - Chapter 4 Assignment

## Overview

This project implements a **ReAct-style agent** using **LangGraph** for TreadWise Tire Co., featuring:
- Custom ReAct loop (Thought → Action → Observation → Answer)
- Multiple agent personas with distinct personalities
- Comprehensive experimentation with different LLM configurations
- Tool-calling capabilities for real business scenarios
- Systematic evaluation and comparison framework

## Project Structure

```
new_assignment/
├── me/
│   ├── About_business.pdf       # Detailed business profile
│   └── Business_summary.txt     # Business summary
├── ReAct_Agent.ipynb           # Main implementation notebook
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── REFLECTION.md               # Detailed reflection and analysis
├── experiment_results.csv      # Experimental results
├── sample_conversations.txt    # Example conversations
├── customer_leads.jsonl        # Collected leads
└── feedback_log.jsonl          # Feedback log
```

## Use Case

**TreadWise Tire Co.** is a modern tire company combining:
- Smart Tread™ IoT platform for tire monitoring
- Mobile installation services
- Circular economy sustainability model
- Fleet management solutions

The ReAct agent helps customers by:
- Answering questions about services
- Providing tire recommendations
- Checking service availability
- Collecting customer leads
- Logging feedback for improvement

## ReAct Loop Implementation

Our custom ReAct loop follows this pattern:

```
1. THOUGHT: Agent reasons about the user's query
2. ACTION: Agent decides to use a tool or provide answer
3. OBSERVATION: Tool execution results are observed
4. ANSWER: Agent formulates final response
```

This is implemented using **LangGraph's state machine**:
- **Nodes**: `reason` (thinking), `tools` (action execution)
- **Edges**: Conditional routing based on tool calls
- **State**: Tracks messages, thoughts, and iteration count

## Agent Personas

### 1. Friendly Advisor
- **Tone:** Warm, enthusiastic, personable
- **Approach:** Relationship-focused, conversational
- **Best for:** General customer interactions
- **Characteristics:** Uses friendly language, builds rapport, proactive

### 2. Technical Expert
- **Tone:** Precise, authoritative, detail-oriented
- **Approach:** Data-driven, specification-focused
- **Best for:** Technical inquiries
- **Characteristics:** Cites specs, explains mechanisms, comprehensive

### 3. Cautious Helper
- **Tone:** Careful, thorough, conservative
- **Approach:** Risk-aware, safety-focused
- **Best for:** Safety-critical scenarios
- **Characteristics:** Asks clarifying questions, sets realistic expectations

## Tools Available

The agent has access to 4 custom tools:

1. **`record_customer_interest`** - Collect customer contact info
   - Parameters: `name`, `email`, `message`
   - Use case: Lead generation

2. **`record_feedback`** - Log unanswered questions
   - Parameters: `question`
   - Use case: Knowledge base improvement

3. **`get_tire_recommendation`** - Suggest tires
   - Parameters: `vehicle_type`, `usage`
   - Use case: Product recommendations

4. **`check_service_availability`** - Check location coverage
   - Parameters: `location`, `service_type`
   - Use case: Service inquiries

## Experiments Conducted

We tested combinations of:

### Personas (3 types)
- Friendly Advisor
- Technical Expert
- Cautious Helper

### LLM Configurations
- **Models:** GPT-3.5-turbo, GPT-4o-mini, GPT-4o
- **Temperature:** 0.0, 0.5, 0.7, 1.0
- **Max tokens:** 500

### Test Scenarios (5 categories)
1. Information queries
2. Recommendation requests
3. Service inquiries
4. Lead collection
5. Unknown questions

**Total tests:** 40+ configurations × 5 scenarios = 200+ tests

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_key_here
   ```

## Usage

### Option 1: Run the Jupyter Notebook

```bash
jupyter notebook ReAct_Agent.ipynb
```

The notebook includes:
- Complete implementation
- Experimental framework
- Analysis and visualization
- Interactive Gradio demo
- Reflection and insights

### Option 2: Test Individual Personas

```python
from ReAct_Agent import create_react_agent
from langchain_core.messages import HumanMessage

# Create agent
agent = create_react_agent("friendly_advisor", temperature=0.7)

# Test
result = agent.invoke({
    "messages": [HumanMessage(content="Tell me about Smart Tread")],
    "thoughts": [],
    "iterations": 0
})

print(result["messages"][-1].content)
```

## Key Findings

### Best Performing Configuration
- **Persona:** Friendly Advisor
- **Model:** GPT-4o-mini (cost-effective)
- **Temperature:** 0.7
- **Technique:** System prompt with clear tool descriptions

### Persona Performance
1. **Friendly Advisor:** Most natural for customer service
2. **Technical Expert:** Best for detailed technical questions
3. **Cautious Helper:** Ideal for safety-critical scenarios

### Temperature Impact
- **0.0-0.3:** Too robotic, lacks personality
- **0.6-0.8:** Optimal balance (recommended)
- **0.9-1.0:** Too creative, inconsistent

### Tool Usage
- All personas successfully used tools
- Tool selection accuracy: ~85%
- Average iterations: 2-3 per query

## Evaluation Metrics

We measured:
- **Response time** (seconds)
- **Response length** (characters)
- **Tool accuracy** (correct tool selection)
- **Iteration count** (ReAct loops)
- **Success rate** (% of successful completions)

Results are visualized in the notebook with:
- Bar charts comparing personas
- Temperature impact graphs
- Tool usage statistics
- Response time distributions

## Challenges & Solutions

### Challenge 1: State Management in LangGraph
**Solution:** Carefully designed state schema with clear transitions

### Challenge 2: Preventing Infinite Loops
**Solution:** Added iteration tracking and maximum iteration limits

### Challenge 3: Consistent Persona Behavior
**Solution:** Detailed system prompts with personality guidelines

### Challenge 4: Tool Parameter Extraction
**Solution:** Clear tool schemas with detailed parameter descriptions

### Challenge 5: Cost Management
**Solution:** Used GPT-4o-mini for bulk testing, GPT-4o for validation

## Production Recommendations

For deploying TreadWise chatbot in production:

1. **Default Persona:** Friendly Advisor
2. **Model:** GPT-4o-mini (upgrade to GPT-4o for complex cases)
3. **Temperature:** 0.7
4. **Enhancements:**
   - Add conversation memory
   - Implement persona switching based on query type
   - Include user feedback collection
   - Monitor tool usage for knowledge base improvements

## Assignment Requirements Checklist

- [x] Use-case defined (TreadWise Tire Co. customer service)
- [x] ReAct loop manually implemented with LangGraph
- [x] System prompt with tool descriptions
- [x] Logic to detect and execute tool calls
- [x] Response parsing and loop continuation
- [x] At least 2 agent personas tested (3 implemented)
- [x] Prompt engineering experiments (default, varying temperatures)
- [x] LLM configuration variations (temperature, model type)
- [x] Experiment logging and comparison
- [x] Reflection on persona effectiveness
- [x] Reflection on optimal configuration
- [x] Analysis of reasoning and tool usage
- [x] Documentation of implementation challenges
- [x] Comprehensive write-up and code documentation

## Framework Choice Justification

**Why LangGraph?**

1. **Explicit Control:** State machine model gives precise control over ReAct flow
2. **Transparency:** Easy to visualize and debug Thought → Action → Observation steps
3. **Flexibility:** Can customize each node's behavior independently
4. **Production-Ready:** Battle-tested framework with good documentation
5. **Integration:** Seamless integration with LangChain tools

Alternatives considered:
- **CrewAI:** Better for multi-agent collaboration (not needed here)
- **Autogen:** Better for dialogue-based reasoning (our use case is simpler)

## Future Enhancements

1. **Hybrid Personas:** Dynamically switch personas based on query type
2. **Memory Integration:** Add conversation history across sessions
3. **RAG Enhancement:** Integrate vector database for knowledge retrieval
4. **Multi-language:** Support multiple languages
5. **Voice Interface:** Add speech-to-text for phone support
6. **Analytics Dashboard:** Track conversation metrics and improve over time

## References

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

## Author

**Mounir Khalil**
Student ID: 202100437
American University of Beirut
EECE798S Agentic Systems - Chapter 4 Assignment
Fall 2025-2026

## License

Educational project for EECE798S course.
