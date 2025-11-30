import streamlit as st
import uuid
import sys
import os

# Add project root to path so 'src' module can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.store.base import GetOp
try:
    from src.graph import app as graph_app
    from src.repositories.outfit_repository import OutfitRepository
    from src.memory.firestore_store import FirestoreStore
except ImportError:
    # Fallback for when running directly inside src/
    from graph import app as graph_app
    from repositories.outfit_repository import OutfitRepository
    from memory.firestore_store import FirestoreStore

st.set_page_config(page_title="ALI Agent v2", layout="wide")

# Initialize Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.summary = "" # Context Compression
    
    # Initialize Core Services
    st.session_state.repo = OutfitRepository()
    st.session_state.store = FirestoreStore()
    
    # Fetch OOTD
    st.session_state.current_ootd = st.session_state.repo.get_outfit_by_date()
    
    # Load User Memory (Persistent)
    st.session_state.user_id = "default_user"
    user_mem = st.session_state.store.batch([
        GetOp(namespace=("users",), key=st.session_state.user_id)
    ])
    # (Simplified loading)

st.title("ALI Agent v2")
st.markdown("### Your Personal AI Stylist")

# Sidebar: Controls & Context
with st.sidebar:
    st.header("User Identity")
    # User ID Input
    new_user_id = st.text_input("User ID", value=st.session_state.user_id)
    if new_user_id != st.session_state.user_id:
        st.session_state.user_id = new_user_id
        # CRITICAL: Clear ALL user-specific state to prevent leaks
        st.session_state.messages = [] 
        st.session_state.summary = "" 
        if "weather_cache" in st.session_state:
            del st.session_state.weather_cache
        if "last_route" in st.session_state:
            del st.session_state.last_route
        if "last_city" in st.session_state:
            del st.session_state.last_city
            
        # Reset Location Widget
        st.session_state["user_city"] = "New York"
        
        # Reload User Memory
        user_mem = st.session_state.store.batch([
            GetOp(namespace=("users",), key=st.session_state.user_id)
        ])
        # Update summary if memory exists
        if user_mem and user_mem[0]:
            st.session_state.summary = user_mem[0].value.get("summary", "")
        
        st.rerun()
        
    st.header("Outfit Context")
    # OOTD Date Selection
    import datetime
    selected_date = st.date_input("OOTD Date", value=datetime.date.today())
    
    # Fetch OOTD on date change
    if "last_selected_date" not in st.session_state or st.session_state.last_selected_date != selected_date:
        st.session_state.last_selected_date = selected_date
        date_str = selected_date.strftime("%Y-%m-%d")
        with st.spinner(f"Fetching OOTD for {date_str}..."):
            st.session_state.current_ootd = st.session_state.repo.get_outfit_by_date(date_str)
            
    # Display Current OOTD (Simplified)
    if st.session_state.current_ootd:
        st.success(f"OOTD Loaded: {st.session_state.current_ootd.get('date', 'Unknown')}")
        st.image(st.session_state.current_ootd.get('image_url'), caption=st.session_state.current_ootd.get('description'))
    else:
        st.warning("No OOTD found for this date.")

    st.header("Environment")
    # Use key to allow programmatic reset
    city = st.text_input("Location", value="New York", key="user_city")
    
    # Fetch Weather
    if "weather_cache" not in st.session_state or st.session_state.get("last_city") != city:
        with st.spinner(f"Fetching weather for {city}..."):
            from src.services.weather_service import WeatherService
            st.session_state.weather_cache = WeatherService.get_current_weather(city)
            st.session_state.last_city = city
            
    if "error" not in st.session_state.weather_cache:
        w = st.session_state.weather_cache
        st.info(f"{w['temperature']}, {w['conditions']}")
    else:
        st.error("Could not fetch weather.")

    st.divider()
    
    # Context Debugger (Collapsible)
    with st.expander("🛠️ Context Debugger"):
        st.subheader("Compression")
        if st.session_state.summary:
            st.info(st.session_state.summary)
        else:
            st.caption("No summary generated yet (starts after 10 messages).")
        
        st.subheader("Selection (Current OOTD)")
        if st.session_state.current_ootd:
            st.json(st.session_state.current_ootd)
        else:
            st.write("No OOTD available")
            
        st.subheader("Trimming")
        st.write(f"Message Count: {len(st.session_state.messages)}")

    st.divider()
    st.subheader("🤖 Agent Activity")
    if "last_route" in st.session_state and st.session_state.last_route:
        for step in st.session_state.last_route:
            st.code(f"→ {step}")
    else:
        st.caption("No activity yet.")

# Chat Interface
for msg in st.session_state.messages:
    with st.chat_message(msg.type):
        st.write(msg.content)

if prompt := st.chat_input("Ask ALI..."):
    # Add user message
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.write(prompt)
        
    # Run Graph
    inputs = {
        "messages": st.session_state.messages,
        "user_id": st.session_state.user_id,
        "current_ootd": st.session_state.current_ootd,
        "weather_data": st.session_state.get("weather_cache", {"temperature": "Unknown", "conditions": "Unknown"}),
        "summary": st.session_state.summary
    }
    
    with st.spinner("ALI is thinking..."):
        # We stream the output to get the final state
        final_state = None
        route = []
        for output in graph_app.stream(inputs):
            for key, value in output.items():
                route.append(key)
                # Update local state with intermediate results if needed
                if "summary" in value:
                    st.session_state.summary = value["summary"]
                
                # Capture new messages from agents
                # CRITICAL: Only capture messages from the 'orchestrator' node.
                # Subagent messages are internal signals for the orchestrator to compose.
                # We don't want to show raw "FINAL_ANSWER" or "QUESTION" to the user.
                if key == "orchestrator" and "messages" in value:
                    new_msgs = value["messages"]
                    if isinstance(new_msgs, list):
                        st.session_state.messages.extend(new_msgs)
                    elif isinstance(new_msgs, (HumanMessage, AIMessage)):
                        st.session_state.messages.append(new_msgs)
                        
            final_state = value # Keep last state
        
        st.session_state.last_route = route


    # Display Agent Response
    st.rerun()
