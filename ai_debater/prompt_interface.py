from typing import List, Dict,Tuple
import numpy as np

def topic2message(topic) -> Dict[str, str]:
    return {"role": "user", 
            "content": f"Subject: {str(topic['Subject'])}; Rational:{str(topic['Rational'])}"}

def discourse2messages(discourse: List[str], for_opponent: bool = False) -> List[str]:
    messages = []
    modulo = 0 if for_opponent else 1
    if for_opponent:
        messages.append({"role": "system", "content": "Ok, I understood"})
    for iii, d in enumerate(discourse):
        role = "user" if (iii%2)==modulo else "system"
        messages.append({"role": role, "content": d})
    return messages

def discourse2input(discourse) -> Dict[str,str]:
    assert discourse.discourse_id.unique().shape[0]==1, 'Too many discourses'
    message = "<Discourse>\n"
    for _, row in discourse.sort_values(by='ith_argument').iterrows():
        message += "<Argument>"
        message += f"<Number>{row.ith_argument}</Number>"
        message += f"<Team_ID>{row.model_speaking}</Team_ID>"
        message += f"<Text>{row.Argument}</Text>"
        message +="</Argument>\n"
    message += "</Discourse>\n"
    return {"role": "user", 
            "content": message}

def judgement_and_discourse2input(discourse_id, result_manager) -> Tuple[Dict[str, str], List[str]]:
    judgements = result_manager.load_judgements()
    judges = judgements.judge_entity.unique()
    selection = judgements.loc[judgements.discourse_id==discourse_id]
    assert np.all(judges == selection.judge_entity.unique()), "Problem with the judges"
    judgement_ids = selection.judgement_id.unique()
    discourse = result_manager.load_discourse(discourse_id)
    text = discourse2input(discourse)['content']
    for judgement_id in judgement_ids:
        selection = selection.loc[selection.judgement_id == selection.judgement_id.iloc[0]]
        text += "<Verdict>"
        text += f"<Judgement_ID>{judgement_id}</Judgement_ID>"
        for cat, row in selection.loc[:,["Categories","Team_ID","Score", "Rational"]].groupby("Categories"):
            text += f"<{cat}>"
            text += "<Team>"
            for team, score in row.groupby("Team_ID"):
                text += f"<Team_ID>{team}</Team_ID>"
                for key in ["Score", "Rational"]:
                    val = score.loc[:,key].values
                    if len(val)!=1:
                        raise NameError("Too many values")
                    val = val[0]
                    text += f"<{key}>{val}</{key}>"
            text += "</Team>"
            text += f"</{cat}>\n"
        text += "</Verdict>"
    return {"role": "user", 
            "content": text}, judgement_ids
