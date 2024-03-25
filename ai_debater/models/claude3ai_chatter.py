from typing import Dict, List, Union
import anthropic
from datetime import datetime
import os
from ai_debater.models.abstractai_chatter import BaseAiChatter

class Claude3AiChatter(BaseAiChatter):
    def __init__(self, api_key: str):
        self._client = anthropic.Anthropic(api_key = api_key)
        self.model = 'claude-3-opus-20240229'
        self._timestamp = datetime.now()
        
    @property
    def model_entity(self) -> str:
        return self.__class__.__name__+'|'+self._model

    @property
    def model(self) -> str:
        return self._model
    @model.setter
    def model(self, model):
        self._model = model

    @property
    def metainfo(self) -> Dict[str, Union[str, float]]:
        return {
            "model_class": self.__class__.__name__,
            "model":self.model,
            "model_entity":self.model_entity,
            "creation_date":self._timestamp
        }


    def answer(self, messages: List[Dict[str,str]] = []) -> str:
        messages = messages.copy()
        if not len(messages):
            messages = [dict(role='user',
                             content='Please fullfill your role')]
        # We need to replace all role: systems -> assistant:
        messages_claud = []
        for m in messages:
            role = m["role"]
            if role == "system":
                m["role"] = "assistant"
            messages_claud.append(m)
        chat_completion = self._client.messages.create(
            system = self.init_prompt,
            max_tokens = 2000,
            model=self._model,
            messages=messages_claud)
        if chat_completion.content:
            return chat_completion.content[0].text
        return ''