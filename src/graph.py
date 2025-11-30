from typing import Literal
from langgraph.graph import StateGraph, END
from .state import SessionState
from .agents.orchestrator import Orchestrator
from .agents.subagents import OccasionAgent, ItemStylingAgent, ColorAgent, TemperatureAgent
from .memory.firestore_store import FirestoreStore

# Initialize Agents
orchestrator = Orchestrator()
occasion_agent = OccasionAgent()
item_agent = ItemStylingAgent()
color_agent = ColorAgent()
temp_agent = TemperatureAgent()

# Initialize Store
store = FirestoreStore()

def orchestrator_node(state: SessionState):
    # If we are returning from a subagent, the last message is the agent response.
    # The orchestrator logic in `invoke` handles context building.
    # We just call invoke.
    result = orchestrator.invoke(state)
    
    # Persistence: Save summary if updated
    if "summary" in result and result["summary"]:
        # We need the user_id to save to the right key. 
        # It's in the state!
        user_id = state["user_id"]
        
        # Save to Firestore
        store.put(
            namespace=("users",),
            key=user_id,
            value={"summary": result["summary"]}
        )
        
    return result

def occasion_node(state: SessionState):
    return occasion_agent.invoke(state)

def item_node(state: SessionState):
    return item_agent.invoke(state)

def color_node(state: SessionState):
    return color_agent.invoke(state)

def temp_node(state: SessionState):
    return temp_agent.invoke(state)

def router(state: SessionState) -> Literal["occasion_formality", "item_styling", "color_intelligence", "temperature", "end"]:
    # The orchestrator sets 'next_agent' in the state update
    return state.get("next_agent", "end")

# Build Graph
workflow = StateGraph(SessionState)

workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("occasion_formality", occasion_node)
workflow.add_node("item_styling", item_node)
workflow.add_node("color_intelligence", color_node)
workflow.add_node("temperature", temp_node)

workflow.set_entry_point("orchestrator")

workflow.add_conditional_edges(
    "orchestrator",
    router,
    {
        "occasion_formality": "occasion_formality",
        "item_styling": "item_styling",
        "color_intelligence": "color_intelligence",
        "temperature": "temperature",
        "end": END
    }
)

# Subagents return to orchestrator to compose final response
workflow.add_edge("occasion_formality", "orchestrator")
workflow.add_edge("item_styling", "orchestrator")
workflow.add_edge("color_intelligence", "orchestrator")
workflow.add_edge("temperature", "orchestrator")

app = workflow.compile()
