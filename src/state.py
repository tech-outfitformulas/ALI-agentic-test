from typing import TypedDict, List, Dict, Optional, Any, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """Isolated state for a specific agent."""
    messages: Annotated[List[BaseMessage], add_messages]
    context: Dict[str, Any]

class SessionState(TypedDict):
    """Global session state."""
    messages: Annotated[List[BaseMessage], add_messages]
    user_id: str
    current_ootd: Optional[Dict[str, Any]]
    weather_data: Optional[Dict[str, Any]]
    summary: str # For context compression
    agent_states: Dict[str, AgentState] # For state isolation
    next_agent: Optional[str]
