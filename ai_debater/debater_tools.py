import pandas as pd
from ai_debater.models.abstractai_chatter import BaseAiChatter
from ai_debater.prompt_interface import topic2message
from ai_debater.prompt_interface import discourse2messages

def run_debate(topic: pd.Series, 
               prop: BaseAiChatter, oppo: BaseAiChatter,
               connection,
               n_round=4):
    assert "topic_id" in topic.index, "topic must have a unique id"
    topic_message = topic2message(topic)
    current_topic_id = topic.topic_id
    discourse_id = current_topic_id+':'+prop.model_id()+'-vs-'+oppo.model_id()
    discourse = []
    for _ in range(n_round):
        for is_opponent, model_speaking in zip([False, True], [prop, oppo]):
            messages = [topic_message]
            messages.extend(discourse2messages(discourse, for_opponent=is_opponent))
            discourse.append(model_speaking.answer_until_valid(messages))
    fact_discourse = pd.DataFrame(discourse, columns=['Argument'])
    fact_discourse['ith_argument'] = fact_discourse.index
    fact_discourse['discourse_id'] = discourse_id
    fact_discourse['argument_id']  =discourse_id + fact_discourse['ith_argument'].astype(str)
    fact_discourse['model_speaking'] = None
    fact_discourse.loc[fact_discourse.index%2 == 0 ,'model_speaking'] = prop.model_id()
    fact_discourse.loc[fact_discourse.index%2 == 1 ,'model_speaking'] = oppo.model_id()

    dim_discourse = pd.Series(dict(discourse_id=discourse_id,
                                    model_proposing = prop.model_id(),
                                    model_opposing = oppo.model_id(),
                                    topic_id = current_topic_id))
    dim_discourse.to_frame().transpose().to_sql("dim_discourse", connection, if_exists='append')
    fact_discourse.to_sql("fact_discourse", connection, if_exists='append')