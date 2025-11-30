from typing import Dict, Any
from langchain_core.messages import SystemMessage, AIMessage
from ..state import SessionState
from .base import BaseAgent

class SubAgent(BaseAgent):
    def invoke(self, state: SessionState) -> Dict[str, Any]:
        # Selective Context Passing
        context_str = self._build_context(state)
        
        messages = state["messages"]
        # We might want to filter messages too (Trimming/Isolation)
        # For now, pass full history + specific context
        
        chain = self.get_chain()
        response = chain.invoke({
            "messages": messages + [SystemMessage(content=context_str)]
        })
        
        # Return the response to be routed back to orchestrator? 
        # Or just update state?
        # The orchestrator expects <agent_response> in the next turn if we loop back.
        # But usually subagents provide the answer.
        
        return {"messages": [AIMessage(content=response.content)]}

    def _build_context(self, state: SessionState) -> str:
        raise NotImplementedError

class OccasionAgent(SubAgent):
    def __init__(self):
        super().__init__("occasion_formality", "1_occasion_formality.txt")

    def _build_context(self, state: SessionState) -> str:
        # Select: user_message, current_outfit, user_memory
        # Exclude: weather_data
        user_msg = state["messages"][-1].content
        ootd = state.get("current_ootd")
        ootd_str = str(ootd) if ootd else "Not available"
        
        return f"""
<inputs_you_receive>
<user_latest_message>
{user_msg}
</user_latest_message>

<current_outfit_for_reference>
{ootd_str}
</current_outfit_for_reference>

</user_memory>
</inputs_you_receive>

<required_context>
- MUST have: user_latest_message
- OPTIONAL: current_outfit_for_reference, user_memory, conversation_so_far
- NEVER need: weather_data (unless specifically asked about rain/snow impact on formality)
</required_context>

<conversation_state>
- Track: [occasion, dress_code, jeans_policy]
- Don't re-ask: Check state before asking questions
- Summarize: After completing, summarize the flow for future reference
</conversation_state>
"""

class ItemStylingAgent(SubAgent):
    def __init__(self):
        super().__init__("item_styling", "2_item_styling.txt")

    def _build_context(self, state: SessionState) -> str:
        # Select: user_message, current_outfit, user_memory
        user_msg = state["messages"][-1].content
        ootd = state.get("current_ootd")
        ootd_str = str(ootd) if ootd else "Not available"
        
        return f"""
<inputs_you_receive>
<user_latest_message>
{user_msg}
</user_latest_message>

<current_outfit_for_reference>
{ootd_str}
</current_outfit_for_reference>

</user_memory>
</inputs_you_receive>

<required_context>
- MUST have: user_latest_message
- OPTIONAL: current_outfit_for_reference, user_memory
- NEVER need: weather_data, conversation_so_far (usually single turn)
</required_context>
"""

class ColorAgent(SubAgent):
    def __init__(self):
        super().__init__("color_intelligence", "3_color_intelligence.txt")

    def _build_context(self, state: SessionState) -> str:
        # Select: user_message, current_outfit, user_memory (palette)
        # Exclude: weather
        user_msg = state["messages"][-1].content
        ootd = state.get("current_ootd")
        ootd_str = str(ootd) if ootd else "Not available"
        
        return f"""
<inputs_you_receive>
<user_latest_message>
{user_msg}
</user_latest_message>

<current_outfit_for_reference>
{ootd_str}
</current_outfit_for_reference>

</user_memory>
</inputs_you_receive>

<required_context>
- MUST have: user_latest_message
- OPTIONAL: current_outfit_for_reference, user_memory (seasonal palette)
- NEVER need: weather_data, conversation_so_far
</required_context>
"""

class TemperatureAgent(SubAgent):
    def __init__(self):
        super().__init__("temperature", "4_temperature.txt")

    def _build_context(self, state: SessionState) -> str:
        # Select: user_message, weather_data, current_outfit
        # Exclude: user_memory (palette)
        user_msg = state["messages"][-1].content
        ootd = state.get("current_ootd")
        ootd_str = str(ootd) if ootd else "Not available"
        weather = state.get("weather_data")
        weather_str = str(weather) if weather else "Not available"
        
        return f"""
<inputs_you_receive>
<user_latest_message>
{user_msg}
</user_latest_message>

<weather_data>
{weather_str}
</weather_data>

<current_outfit_for_reference>
{ootd_str}
</current_outfit_for_reference>
</inputs_you_receive>

<required_context>
- MUST have: user_latest_message, weather_data
- OPTIONAL: current_outfit_for_reference
- NEVER need: user_memory (seasonal palette), conversation_so_far (usually single turn)
</required_context>
"""
