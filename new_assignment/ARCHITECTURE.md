# Architecture Documentation - TreadWise ReAct Agent

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    TreadWise ReAct Agent System                  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
        ┌───────▼──────┐  ┌─────▼─────┐  ┌──────▼──────┐
        │   Personas   │  │   Tools   │  │  LangGraph  │
        │   (3 types)  │  │ (4 funcs) │  │ State Graph │
        └──────────────┘  └───────────┘  └─────────────┘
```

## ReAct Loop Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         ReAct Flow Diagram                            │
└──────────────────────────────────────────────────────────────────────┘

    User Input
       │
       │
       ▼
┌─────────────┐
│   REASON    │ ◄──────────────────┐
│   (Node)    │                    │
│             │                    │
│ - Add sys   │                    │
│   prompt    │                    │
│ - Call LLM  │                    │
│ - Track     │                    │
│   iteration │                    │
└──────┬──────┘                    │
       │                            │
       │ [Conditional Edge]         │
       │                            │
       ▼                            │
   Tool calls?                      │
       │                            │
   ┌───┴────┐                       │
   │        │                       │
  Yes      No                       │
   │        │                       │
   │        └───────────────┐       │
   │                        │       │
   ▼                        ▼       │
┌─────────────┐      ┌──────────┐  │
│    TOOLS    │      │   END    │  │
│   (Node)    │      └──────────┘  │
│             │                     │
│ - Execute   │                     │
│   tool      │                     │
│ - Return    │                     │
│   result    │                     │
└──────┬──────┘                     │
       │                            │
       │ [Edge]                     │
       │                            │
       └────────────────────────────┘

       Loop continues until:
       - No tool calls (return answer)
       - Max iterations reached (5)
```

## State Management

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # ↑ Accumulates messages using + operator

    thoughts: list[str]
    # ↑ Debug trail of reasoning steps

    iterations: int
    # ↑ Counter to prevent infinite loops
```

### State Flow Example

```
Initial State:
{
    "messages": [HumanMessage("I need tires")],
    "thoughts": [],
    "iterations": 0
}

After Reason Node:
{
    "messages": [
        HumanMessage("I need tires"),
        AIMessage(content="...", tool_calls=[...])
    ],
    "thoughts": ["Iteration 1: Reasoning about user query"],
    "iterations": 1
}

After Tools Node:
{
    "messages": [
        HumanMessage("I need tires"),
        AIMessage(content="...", tool_calls=[...]),
        ToolMessage(content="Recommendation: EcoGlide...")
    ],
    "thoughts": ["Iteration 1: Reasoning about user query"],
    "iterations": 1
}

After Second Reason:
{
    "messages": [
        HumanMessage("I need tires"),
        AIMessage(content="...", tool_calls=[...]),
        ToolMessage(content="Recommendation: EcoGlide..."),
        AIMessage(content="Based on... I recommend EcoGlide!")
    ],
    "thoughts": [
        "Iteration 1: Reasoning about user query",
        "Iteration 2: Reasoning about user query"
    ],
    "iterations": 2
}
```

## Component Architecture

### 1. Persona Layer

```
┌───────────────────────────────────────────────────────────┐
│                     Persona Prompts                        │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Friendly        │  │ Technical    │  │ Cautious     │ │
│  │ Advisor         │  │ Expert       │  │ Helper       │ │
│  │                 │  │              │  │              │ │
│  │ • Warm          │  │ • Precise    │  │ • Careful    │ │
│  │ • Enthusiastic  │  │ • Detailed   │  │ • Thorough   │ │
│  │ • Conversational│  │ • Data-driven│  │ • Risk-aware │ │
│  └─────────────────┘  └──────────────┘  └──────────────┘ │
│                                                            │
│  All personas share same tools, differ in:                │
│  - Tone of voice                                          │
│  - Level of detail                                        │
│  - Decision-making style                                  │
└───────────────────────────────────────────────────────────┘
```

### 2. Tool Layer

```
┌────────────────────────────────────────────────────────────────┐
│                         Tool Suite                              │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  record_customer_interest(email, name, message)                │
│  ├─ Logs to: customer_leads.jsonl                              │
│  ├─ Use case: Lead generation                                  │
│  └─ Return: Confirmation message                               │
│                                                                 │
│  record_feedback(question)                                     │
│  ├─ Logs to: feedback_log.jsonl                                │
│  ├─ Use case: Unknown questions                                │
│  └─ Return: "Logged for review"                                │
│                                                                 │
│  get_tire_recommendation(vehicle_type, usage)                  │
│  ├─ Data: Static recommendation map                            │
│  ├─ Use case: Product suggestions                              │
│  └─ Return: Tire model + description                           │
│                                                                 │
│  check_service_availability(location, service_type)            │
│  ├─ Data: Simulated coverage map                               │
│  ├─ Use case: Service inquiries                                │
│  └─ Return: Availability status                                │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 3. LLM Configuration Layer

```
┌─────────────────────────────────────────────────────┐
│              LLM Configuration Options               │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Model Selection:                                   │
│  ┌──────────────┬──────────┬──────────┬──────────┐ │
│  │ GPT-3.5      │ GPT-4o   │ GPT-4o   │ Future   │ │
│  │ Turbo        │ mini     │          │ models   │ │
│  │              │          │          │          │ │
│  │ Fastest      │ Balanced │ Best     │ ...      │ │
│  │ Cheapest     │ *OPTIMAL*│ Reasoning│          │ │
│  └──────────────┴──────────┴──────────┴──────────┘ │
│                                                      │
│  Temperature:                                        │
│  [0.0]────────[0.7]────────[1.0]                    │
│   │            │            │                        │
│   Deterministic Balanced   Creative                 │
│   Robotic      *OPTIMAL*   Unpredictable            │
│                                                      │
│  Max Tokens:                                         │
│  500 tokens (default) - balances completeness       │
│  and cost                                            │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## Data Flow

### Complete Request Flow

```
1. User sends message via Gradio
   │
   ▼
2. Chat history converted to LangChain messages
   [HumanMessage, AIMessage, HumanMessage, ...]
   │
   ▼
3. Initial state created
   {messages: [...], thoughts: [], iterations: 0}
   │
   ▼
4. LangGraph workflow invoked
   │
   ├─► REASON node
   │   ├─ Add SystemMessage with persona prompt
   │   ├─ Call LLM with tools
   │   ├─ Increment iteration counter
   │   └─ Return updated state
   │
   ├─► CONDITIONAL EDGE
   │   └─ Tool calls present?
   │       ├─ Yes → Go to TOOLS node
   │       └─ No  → Go to END
   │
   ├─► TOOLS node (if tool calls)
   │   ├─ Execute each tool
   │   ├─ Create ToolMessage with results
   │   └─ Return to REASON node
   │
   └─► Loop until no tool calls or max iterations
   │
   ▼
5. Extract final AIMessage content
   │
   ▼
6. Return to Gradio interface
   │
   ▼
7. Display to user
```

## Example Execution Trace

### Scenario: Tire Recommendation Query

```
USER: "I need tires for my SUV for highway and occasional off-road"

─────────────────────────────────────────────────────────────

[Iteration 1 - REASON]
State: {iterations: 0, messages: [HumanMessage(...)]}
↓
SystemMessage injected with Friendly Advisor prompt
↓
LLM called with tools
↓
Response: AIMessage with tool_call(
    name="get_tire_recommendation",
    args={vehicle_type: "suv", usage: "mixed"}
)
↓
State: {iterations: 1, messages: [..., AIMessage]}

─────────────────────────────────────────────────────────────

[Conditional Edge]
Tool calls present? → YES
Route to: TOOLS

─────────────────────────────────────────────────────────────

[TOOLS Node]
Execute: get_tire_recommendation("suv", "mixed")
↓
Result: "Recommendation: TrailBlazer A/T - Versatile for
         road and light off-road"
↓
Create: ToolMessage(content="Recommendation: TrailBlazer...")
↓
State: {iterations: 1, messages: [..., ToolMessage]}

─────────────────────────────────────────────────────────────

[Edge back to REASON]

─────────────────────────────────────────────────────────────

[Iteration 2 - REASON]
State: {iterations: 1, messages: [..., ToolMessage]}
↓
LLM called with updated context
↓
Response: AIMessage(
    content="Perfect! I'd recommend the TrailBlazer A/T tires
             for your SUV. They're versatile and handle both
             highway and light off-road beautifully. Would you
             like to schedule a mobile installation?"
)
↓
State: {iterations: 2, messages: [..., AIMessage]}

─────────────────────────────────────────────────────────────

[Conditional Edge]
Tool calls present? → NO
Route to: END

─────────────────────────────────────────────────────────────

[END]
Return final state
↓
Extract: result["messages"][-1].content
↓
Response to user: "Perfect! I'd recommend the TrailBlazer..."
```

## Failure Handling

### Max Iterations Safeguard

```python
def should_continue(state: AgentState) -> Literal["tools", "end"]:
    if state["iterations"] >= 5:
        return "end"  # Prevent infinite loops
    # ...
```

### Tool Error Handling

```python
@tool
def get_tire_recommendation(vehicle_type: str, usage: str) -> str:
    # Validate parameters
    if vehicle_type not in VALID_TYPES:
        return "Please specify: sedan, suv, truck, or commercial"
    # ...
```

### LLM Error Handling

```python
def chat_with_persona(...):
    try:
        result = agent.invoke(...)
        return result["messages"][-1].content
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"
```

## Performance Characteristics

### Latency Breakdown

```
Total Response Time: ~2.3 seconds (average)

├─ LLM API call #1 (Reasoning):     1.2s
├─ Tool execution:                  0.1s
├─ LLM API call #2 (Final answer):  0.8s
└─ Overhead (state management):     0.2s
```

### Token Usage

```
Average tokens per request:

Input tokens:
├─ System prompt: ~400 tokens
├─ User message: ~20-100 tokens
├─ Tool descriptions: ~200 tokens
└─ Total input: ~620-700 tokens

Output tokens:
├─ Tool calls: ~50 tokens
├─ Final response: ~150-300 tokens
└─ Total output: ~200-350 tokens

Cost per request (GPT-4o-mini):
~$0.01 per complete interaction
```

## Scalability Considerations

### Current Limitations

1. **Stateless conversations**
   - Each request starts fresh
   - No memory across sessions

2. **Synchronous execution**
   - Blocks until complete
   - No parallel tool calls

3. **Local tool execution**
   - Tools run in same process
   - Not distributed

### Production Improvements

```
┌──────────────────────────────────────────────────────┐
│         Production Architecture (Future)              │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────┐    ┌──────────┐    ┌─────────────┐    │
│  │  Redis  │    │ LangGraph│    │   Vector    │    │
│  │  Cache  │◄───┤  Server  │───►│  Database   │    │
│  └─────────┘    └──────────┘    │  (ChromaDB) │    │
│                      │           └─────────────┘    │
│                      │                               │
│                      ▼                               │
│               ┌────────────┐                         │
│               │Tool Service│                         │
│               │  (FastAPI) │                         │
│               └────────────┘                         │
│                                                       │
└──────────────────────────────────────────────────────┘
```

## Testing Architecture

### Experiment Framework

```
┌──────────────────────────────────────────────────────┐
│              Experiment Configuration                 │
├──────────────────────────────────────────────────────┤
│                                                       │
│  3 Personas × 3 Temps × 3 Models = 27 configs       │
│  + 13 Additional variations                           │
│  = 40 Total configurations                            │
│                                                       │
│  Each tested against 5 scenarios:                    │
│  1. Information query                                 │
│  2. Recommendation request                            │
│  3. Service inquiry                                   │
│  4. Lead collection                                   │
│  5. Unknown question                                  │
│                                                       │
│  Total: 40 × 5 = 200 test cases                      │
│                                                       │
│  Results logged to CSV with:                          │
│  - Response time                                      │
│  - Response length                                    │
│  - Tools used                                         │
│  - Iteration count                                    │
│  - Success/failure                                    │
│                                                       │
└──────────────────────────────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────┐
│         Technology Stack                 │
├─────────────────────────────────────────┤
│                                          │
│  Orchestration:  LangGraph              │
│  LLM Provider:   OpenAI (GPT-4o family) │
│  UI Framework:   Gradio                 │
│  Language:       Python 3.11+           │
│  State:          TypedDict + Annotated  │
│  Tools:          LangChain @tool        │
│  Viz:            Matplotlib + Seaborn   │
│  Data:           Pandas (CSV export)    │
│                                          │
└─────────────────────────────────────────┘
```

---

**This architecture enables:**
- ✅ Transparent ReAct reasoning
- ✅ Flexible persona switching
- ✅ Robust tool execution
- ✅ Comprehensive testing
- ✅ Easy debugging
- ✅ Production scalability path

---

**Student:** Mounir Khalil | **ID:** 202100437
