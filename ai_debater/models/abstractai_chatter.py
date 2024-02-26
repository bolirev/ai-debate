from typing import Dict, List
from abc import ABC, abstractmethod, abstractproperty
import uuid
from ai_debater.prompt_engineering import CoStar

import string
def base_n(num,b=None,numerals=string.digits+string.ascii_letters):
    if b is None:
        b = len(numerals)
    return ((num == 0) and numerals[0]) \
        or (base_n(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

class BaseAiChatter(ABC):
    def generate_init_prompt(self, costar: CoStar) -> None:
        self.init_prompt = costar.generate_prompt()
    def model_id(self) -> str:
        if not hasattr(self, '_model_id'):
            longuuid = str(uuid.uuid4())
            uuid_int = int(f"{longuuid.replace('-','')}", base=16)
            self._model_id = base_n(uuid_int)
        return self._model_id
    
    @abstractmethod
    def __init__(self, api_key: str): ...
    @abstractmethod
    def answer(self, messages: List[str]): ...
    @abstractproperty
    def model_parameters(self) -> Dict[str, str]: ...