from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from ..config import PROMPTS_DIR, LLM_MODEL, OPENAI_API_KEY

class BaseAgent:
    def __init__(self, name: str, prompt_file: str):
        self.name = name
        self.prompt_path = PROMPTS_DIR / prompt_file
        self.llm = ChatOpenAI(model=LLM_MODEL, api_key=OPENAI_API_KEY, temperature=0.7)
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> ChatPromptTemplate:
        with open(self.prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])

    def get_chain(self):
        return self.prompt_template | self.llm
