from typing import Optional, Union
from dataclasses import dataclass, field
import xmltodict

import pandas as pd

from abc import ABC, abstractmethod

def xml_is_valid(xml: str) -> bool:
    try:
        _ = xmltodict.parse(xml)
    except xmltodict.expat.ExpatError:
        return False
    return True

@dataclass
class CoStar(ABC):
    context: Optional[str] = field(default=None, init=False)
    objective: Optional[str] = field(default=None, init=False)
    style: Optional[str] = field(default=None, init=False)
    tone: Optional[str] = field(default=None, init=False)
    audience: Optional[str] = field(default=None, init=False)
    response_format: Optional[str] = field(default=None, init=False)
    input_format: Optional[str] = field(default=None, init=False)
    
    def generate_prompt(self) -> str:
        costar = {  "Context": self.context,
                    "Objective": self.objective,
                    "Style": self.style,
                    "Tone": self.tone,
                    "Audience": self.audience,
                    "Response format": self.response_format,
                    "Input format": self.input_format
                  }

        context = "#########\n"
        for key, value in costar.items():
            context+=f"# {key} #{value}\n"
        context+="#########\n"
        return context
    
    def wrap_xmlresponse(self, response: str) -> str:
        return f"""<?xml version="1.0"?><data>{response}</data>"""
    
    def response_is_valid(self, response: str) -> bool:
        try:
            self.response2output(response)
        except Exception:
            return False
        return True

    @abstractmethod
    def response2output(self, response: str) -> Optional[Union[pd.DataFrame, pd.Series, str]]: ...


@dataclass
class TopicCreatorContext(CoStar):
    context = \
"""
Within the domain of academic, professional, or recreational debate settings where individuals are tasked with selecting topics for debates. 
This could include debate clubs, educational institutions, public forums, or online debating communities.
"""
    objective = \
"""
Your objective is to choose engaging, relevant, and thought-provoking topics that encourage critical thinking, stimulate discussion, and foster a productive exchange of ideas among participants. 
The aim is to inspire lively debates that explore various perspectives on important issues.
"""
    style = \
"""
Write in an informative and persuasive style, resembling guidelines or recommendations for selecting debate topics. 
Ensure clarity and coherence in presenting the rationale behind topic selection, catering to individuals seeking guidance on how to choose suitable debate topics effectively.
"""
    tone = \
"""
Maintain a professional and inclusive tone throughout. 
Encourage creativity and diversity in topic selection, fostering an atmosphere of open-mindedness and inclusivity.
""",
    audience = \
"""
The target audience includes debate organizers, educators, students, professionals, and anyone interested in selecting topics for debates. 
Assume a readership with varying levels of experience in debate and a desire to choose topics that inspire meaningful discourse and intellectual engagement.
"""
    response_format = \
"""
10 different topics formated as:
<Topic><Subject></Subject><Rational></Rational></Topic>
...
<Topic><Subject></Subject><Rational></Rational></Topic>
"""
    
    def response2output(self, response: str) -> Optional[Union[pd.DataFrame, pd.Series, str]]:
        data = xmltodict.parse(self.wrap_xmlresponse(response))
        df = pd.DataFrame(data['data']).Topic.apply(pd.Series)
        df.index.name = 'ith_topic'
        return df

@dataclass
class DebaterContext(CoStar):
    context = \
"""
The context is within a formal or informal debate setting where individuals participate in structured discussions to argue for or against topic.
"""
    objective = \
"""
Your objective is to take the opposite stance than your opponent compelling arguments, engage in persuasive discourse, and effectively refute opposing viewpoints to advance your position on the debate topic.
You target flaws in the opponent answers, provide novel arguments, or any other tactic in order to win the debate
"""
    style = \
"""
Write in a persuasive and articulate style to communicate ideas persuasively and convincingly.
Engage with the other participants
"""
    tone = \
"""
Maintain a confident and respectful tone throughout, demonstrating professionalism and civility
"""
    audience = \
"""
The target audience includes fellow debaters, judges, moderators, spectators, and anyone participating in or observing the debate.
Assume a diverse audience with varying levels of knowledge and interest in the topic, seeking to be informed, entertained, or persuaded by the arguments presented.
"""
    response_format = \
"""
A one paragraph argument
"""
    def response2output(self, response: str) -> Optional[Union[pd.DataFrame, pd.Series, str]]:
        if len(response):
            return response
        raise NameError("Response is empty")


@dataclass
class JudgesContext(CoStar):
    context = \
"""
Within the realm of academic or competitive debating, judges play a crucial role in evaluating and determining the outcome of debates.
This could include debate competitions, academic debate clubs, or formal debating events.
"""
    objective = \
"""
Your task is to provide fair and impartial judgment in debates, evaluating the arguments presented by debaters based on criteria:
* Reasoning and evidence:
    - How well has the motion been defined?
    - Have the arguments been clearly and logically constructed?
    - Have appropriate examples and evidence been used?
    - Is everything said relevant to the motion?
    - Are the speakers guilty of any logical fallacies?
* Listening and response:
    - How effective and thorough is rebuttal of previous speakers?
    - Are points of information precise, concise, timely, focused and relevant?
    - Has the point of clash been identified and used effectively?
* Organisation and prioritisation:
    - Are there the right number of arguments?
    - Are they organised effectively, with the strongest coming first?
    - Are the arguments divided effectively between speakers?
    - Is time used effectively.
* Expression and delivery:
    - Do they sound as if they care about what they are saying?
    - Do they (where appropriate) use humour effectively?
* Team work and roles:
    - Do the speakers support to and refer to each other?
    - Do they avoid contradicting or repeating each other?
"""
    style = \
"""
Write in a formal and authoritative style, resembling guidelines or instructions for judges in a debate setting.
Ensure clarity and precision in outlining evaluation criteria and procedures, catering to judges seeking guidance on how to assess debates effectively.
"""
    tone = \
"""
Maintain a professional and objective tone throughout, emphasizing the importance of fairness, impartiality, and adherence to debate rules.
Offer guidance and insights in a respectful manner, fostering an atmosphere of integrity and credibility in the judging process.
"""
    audience = \
"""
The target audience includes judges participating in debate competitions, academic debate coaches, and individuals involved in organizing or overseeing debate events.
Assume a readership with a background in debate or a keen interest in developing their skills in evaluating and adjudicating debates.
"""
    input_format = \
"""
<Discourse>
<Argument><Number></Number><Team_ID></Team_ID><Text></Text></Argument>
<Argument><Number></Number><Team_ID></Team_ID><Text></Text></Argument>
...
<Argument><Number></Number><Team_ID></Team_ID><Text></Text></Argument>
</Discourse>
"""
    response_format = \
"""
<ReasoningAndEvidence>
<Team><Team_ID></Team_ID><Score max_score="100"></Score><Rational></Rational></Team>
<Team><Team_ID></Team_ID><Score max_score="100"></Score><Rational></Rational></Team>
</ReasoningAndEvidence>
<ListeningAndResponse>
<Team><Team_ID></Team_ID><Score max_score="100"></Score><Rational></Rational></Team>
<Team><Team_ID></Team_ID><Score max_score="100"></Score><Rational></Rational></Team>
</ListeningAndResponse>
<OrganisationAndPrioritisation>
<Team><Team_ID></Team_ID><Score max_score="100"></Score><Rational></Rational></Team>
<Team><Team_ID></Team_ID><Score max_score="100"></Score><Rational></Rational></Team>
</OrganisationAndPrioritisation>
<ExpressionAndDelivery>
<Team><Team_ID></Team_ID><Score max_score="100"></Score><Rational></Rational></Team>
<Team><Team_ID></Team_ID><Score max_score="100"></Score><Rational></Rational></Team>
</ExpressionAndDelivery>
<TeamworkAndRoles>
<Team><Team_ID></Team_ID><Score max_score="100"></Score><Rational></Rational></Team>
<Team><Team_ID></Team_ID><Score max_score="100"></Score><Rational></Rational></Team>
</TeamworkAndRoles>
"""
    def response2output(self, response: str) -> Optional[Union[pd.DataFrame, pd.Series, str]]:
        data = xmltodict.parse(self.wrap_xmlresponse(response))['data']
        df = pd.DataFrame(data).loc['Team'].explode().apply(pd.Series)
        df['Score'] = df.Score.apply(lambda x: float(x['#text'])/float(x['@max_score']))
        df.index.name = 'Categories'
        return df

@dataclass
class PublicContext(CoStar):
    context = \
"""
The context is within a debate setting where individuals serve as audience members or spectators, observing and listening to the arguments presented by debaters on a specific topic.
This could include academic debates, public forums, political debates, or online debate platforms.
""" 
    objective = \
"""
Your objective is to evaluate which judge judgment is most appropriate.
""" 
    input_format = \
    JudgesContext().input_format + \
"""
<Verdict>
<Judgement_ID></Judgement_ID>
""" \
    + JudgesContext().response_format + \
"""
</Verdict>
<Verdict>
...
</Verdict>
""" 
    response_format = \
"""
<Judgement_ID></Judgement_ID>
"""
    def response2output(self, response: str) -> Optional[Union[pd.DataFrame, pd.Series, str]]:
        data = xmltodict.parse(self.wrap_xmlresponse(response))['data']
        df = pd.Series(data)
        df = pd.Series(data=df.loc["Judgement_ID"], index=["Judgement_ID"])
        return df