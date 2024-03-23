from typing import List, Dict

def topic2message(topic) -> Dict[str, str]:
    return {"role": "user", 
            "content": f"Subject: {str(topic['Subject'])}; Rational:{str(topic['Rational'])}"}

def discourse2messages(discourse: List[str], for_opponent: bool = False) -> List[str]:
    messages = []
    modulo = 0 if for_opponent else 1
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