from typing import Dict, List, Union
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from datetime import datetime
from ai_debater.models.abstractai_chatter import BaseAiChatter


class MistralAIChatter(BaseAiChatter):
    def __init__(self, api_key: str):
        self._client = MistralClient(api_key=api_key)
        self.model = "mistral-large-latest"
        self._timestamp = datetime.now()
        
    @property
    def model_entity(self) -> str:
        return self.__class__.__name__+'|'+self.model
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
        messages.insert(0, {"role": "user", "content": self.init_prompt})
        messages = [ChatMessage(**m) for m in messages]
        chat_completion = self._client.chat(
            model=self._model,
            messages=messages)
        if chat_completion.choices:
            return chat_completion.choices[0].message.content
        return ''