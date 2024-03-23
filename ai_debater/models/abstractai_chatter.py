from typing import Dict, List
from abc import ABC, abstractmethod, abstractproperty
import uuid
from ai_debater.prompt_engineering import CoStar
from typing import Optional, Union
import pandas as pd

import string
def base_n(num,b=None,numerals=string.digits+string.ascii_letters):
    if b is None:
        b = len(numerals)
    return ((num == 0) and numerals[0]) \
        or (base_n(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

class BaseAiChatter(ABC):

    def initialise(self, costar: CoStar, max_attempt=10) -> None:
        self.init_prompt = costar.generate_prompt()
        self._costar = costar
        self._max_attempt = max_attempt

    def model_id(self) -> str:
        if not hasattr(self, '_model_id'):
            longuuid = str(uuid.uuid4())
            uuid_int = int(f"{longuuid.replace('-','')}", base=16)
            self._model_id = base_n(uuid_int)
        return self._model_id
    
    def answer_until_valid(self, messages: List[Dict[str,str]]) -> Optional[Union[pd.DataFrame, pd.Series, str]]:
        if not hasattr(self, '_costar'):
            raise NameError('Please initialise with costar')
        attempt_i = 0
        while attempt_i < self._max_attempt:
            answer = self.answer(messages)
            if self._costar.response_is_valid(answer):                  
                return self._costar.response2output(answer)
        return None

    @abstractmethod
    def __init__(self, api_key: str): ...
    @abstractmethod
    def answer(self, messages: List[Dict[str,str]]) -> str: ...
    @abstractproperty
    def metainfo(self) -> Dict[str, str]: ...
    @abstractproperty
    def model_entity(self) -> str: ...