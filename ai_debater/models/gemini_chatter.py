from typing import Dict, List, Union
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import Content, Part
from datetime import datetime
from ai_debater.models.abstractai_chatter import BaseAiChatter
import os 

class GeminiChatter(BaseAiChatter):
    def __init__(self, api_key: str = None):
        vertexai.init(
            project=os.environ.get('project_id'),
            location='europe-west3')
        self.model = "gemini-pro"
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
        self._client = GenerativeModel(self.model)

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
        if messages: # Because Gemini require alternance user - system
            insert_system_ok = messages[0]["role"] == "user"
        else:
            insert_system_ok = False
        if insert_system_ok:
            messages.insert(0, {"role": "model", "content": "Ok I understood my role"})
        messages.insert(0, {"role": "user", "content": self.init_prompt})
        messages = [Content(role="user" if val["role"]=="user" else "model",
                            parts=[Part.from_text(val["content"])]) 
                            for val in messages]
        chat_completion = self._client.generate_content(messages)
        if chat_completion.candidates:
            if chat_completion.candidates[0].content.parts:
                return chat_completion.candidates[0].content.parts[0].text
        return ''