from typing import Dict, List, Union
from openai import OpenAI
import os
from ai_debater.models.abstractai_chatter import BaseAiChatter

class OpenAIChatter(BaseAiChatter):
    def __init__(self, api_key: str):
        self._client = OpenAI(api_key = api_key)
        self.model = 'gpt-4'
        self.temperature = 1.0
        
    @property
    def model(self) -> str:
        return self._model
    @model.setter
    def model(self, model):
        self._model = model

    @property
    def temperature(self) -> float:
        return self._temperature
    @temperature.setter
    def temperature(self, temperature: float):
        self._temperature = temperature

    @property
    def model_parameters(self) -> Dict[str, Union[str, float]]:
        return {
            "model-class": self.__class__.__name__,
            "temperature": self.temperature,
            "model":self.model
        }


    def answer(self, messages: List[str] = []) -> str:
        messages = messages.copy()
        messages.insert(0, {"role": "user", "content": self.init_prompt})
        chat_completion = self._client.chat.completions.create(
            model=self._model, 
            temperature = self._temperature,
            messages=messages)
        return chat_completion.choices[0].message.content