
import sqlite3 
import pandas as pd
import numpy as np
from io import BytesIO

def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = BytesIO(text)
    out.seek(0)
    return np.load(out, allow_pickle=True)

# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, adapt_array)

# Converts TEXT to np.array when selecting
sqlite3.register_converter("array", convert_array)


class IODataBase():
    def __init__(self, db_name = 'results/dataset.db'):
        self.connection = sqlite3.connect(db_name)


    @property
    def connection(self):
        return self._cnx
    @connection.setter
    def connection(self, cnx):
        self._cnx = cnx

    @property
    def table_names(self):
        tables_names = pd.read_sql(
            "SELECT tbl_name FROM sqlite_master WHERE type='table'",
            self.connection)
        return tables_names
    
    def table2pandas(self, table_name, condition="True"):
        sql_statement = \
        f"""
        SELECT * FROM '{table_name}'
        WHERE {condition}
        """
        return pd.read_sql(sql_statement, self.connection)

    def load_topics(self):
        existing_topics = None
        if 'topics' in self.table_names.tbl_name.values:
            sql_statement = \
            """
            SELECT
                topics.model_id,
                topics.ith_topic,
                topics.topic_id,
                topics.Subject,
                topics.Rational,
                model_infos.model_entity
            FROM 'topics' as topics
            LEFT JOIN 'model_infos' as model_infos
                USING (model_id)
            """
            existing_topics = pd.read_sql(sql_statement, self.connection)
        return existing_topics
    
    def load_competitions(self):
        existing_competitions = None
        if 'dim_discourse' in self.table_names.tbl_name.values:
            sql_statement = \
            """
            SELECT
                discourse.discourse_id AS discourse_id,
                discourse.topic_id,
                discourse.model_proposing,
                discourse.model_opposing,
                model_infos_oppo.model_entity AS model_opposing_entity,
                model_infos_prop.model_entity AS model_proposing_entity
            FROM 'dim_discourse' AS discourse
            LEFT JOIN 'model_infos' as model_infos_oppo
                ON discourse.model_opposing = model_infos_oppo.model_id
            LEFT JOIN 'model_infos' as model_infos_prop
                ON discourse.model_proposing = model_infos_prop.model_id
            """
            existing_competitions = pd.read_sql(sql_statement, self.connection)
        return existing_competitions
    
    def load_discourse(self, discourse_id) -> pd.DataFrame:
        assert 'dim_discourse' in self.table_names.tbl_name.values
        sql_statement = \
        """
        SELECT
            fact.*,
            model.model_entity AS model_speaking_entity
        FROM 'fact_discourse' AS fact
        LEFT JOIN 'model_infos' AS model
            ON fact.model_speaking = model.model_id
        WHERE
            TRUE
            AND discourse_id = "{}"
        """.format(discourse_id)
        return pd.read_sql(sql_statement, self.connection)

    def load_enriched_judgements(self):
        dim_judgements = None
        if 'dim_judgements' in self.table_names.tbl_name.values:
            sql_statement = \
            """
            SELECT
                judg.judgement_id,
                judg.discourse_id,
                judg.model_id_judging,
                model_infos.model_entity AS judge_model_entity
            FROM 'dim_judgements' AS judg
            LEFT JOIN 'model_infos' as model_infos
                ON judg.model_id_judging = model_infos.model_id
            """
            dim_judgements = pd.read_sql(sql_statement, self.connection)
        return dim_judgements

    def load_enriched_public(self):
        dim_public = None
        if 'dim_public' in self.table_names.tbl_name.values:
            sql_statement = \
            """
            SELECT
                public.discourse_id,
                model_infos.model_entity AS public_model_entity
            FROM 'dim_public' AS public
            LEFT JOIN 'model_infos' as model_infos
                ON public.public_model_id = model_infos.model_id
            """
            dim_public = pd.read_sql(sql_statement, self.connection)
        return dim_public

    def load_judgements_for_analyses(self):
        sql_statement = \
        """
        WITH enriched_judegement AS (
            SELECT
                fact.Categories,
                fact.Score,
                dim.discourse_id AS discourse_id,
                judge.model_entity AS judge_entity,
                team.model_entity AS team_entity,
                team.model_id AS team_id,
                dim_discourse.model_proposing AS team_proposing_id,
                dim_discourse.model_opposing AS team_opposing_id,
                topic_creator.model_entity AS topic_creator_entity,
                opposing.model_entity AS opposing_entity,
                proposing.model_entity AS proposing_entity
            FROM 'fact_judgements' AS fact
            LEFT JOIN 'dim_judgements' as dim
                USING (judgement_id)
            LEFT JOIN 'model_infos' as judge
                ON dim.model_id_judging = judge.model_id
            LEFT JOIN 'model_infos' AS team
                ON fact.Team_ID = team.model_id
            LEFT JOIN 'dim_discourse' AS dim_discourse
                ON dim.discourse_id = dim_discourse.discourse_id
            LEFT JOIN 'topics' AS topics
                ON topics.topic_id = dim_discourse.topic_id
            LEFT JOIN 'model_infos' AS topic_creator
                ON topics.model_id = topic_creator.model_id
            LEFT JOIN 'model_infos' AS proposing
                ON dim_discourse.model_proposing = proposing.model_id
            LEFT JOIN 'model_infos' AS opposing
                ON dim_discourse.model_opposing = opposing.model_id
        ),

        minmax_judges AS (
            SELECT
                judge_entity,
                Categories,
                MIN(Score) AS min_score,
                MAX(Score) AS max_score
            FROM enriched_judegement
            GROUP BY
                judge_entity,
                Categories
        ),

        normalised_score AS (
            SELECT
                src.*,
                (src.Score-mm.min_score)/(mm.max_score - mm.min_score) AS Normalised_score
            FROM enriched_judegement AS src
            LEFT JOIN minmax_judges AS mm
                USING ( judge_entity, Categories)
        )

        SELECT * FROM normalised_score
        """
        return pd.read_sql(sql_statement, self.connection)

    def load_votes_for_analyses(self):
        sql_statement = """
        SELECT
            fact_public.Judgement_ID AS voted_for_judgement_id,
            public.discourse_id,
            public.judgement_ids,
            model_infos.model_entity AS public_model_entity,
            model_judgement.model_entity AS voted_for_judgement_model_entity
        FROM 'dim_public' AS public
        LEFT JOIN 'fact_public' AS fact_public
            ON fact_public.public_voting_id = public.public_voting_id
        LEFT JOIN 'model_infos' as model_infos
            ON public.public_model_id = model_infos.model_id
        LEFT JOIN 'dim_judgements' AS judg
            ON fact_public.Judgement_ID = judg.judgement_id
        LEFT JOIN 'model_infos' as model_judgement
            ON judg.model_id_judging = model_judgement.model_id
        """
        public_voting = pd.read_sql(sql_statement, self.connection)
        public_voting.judgement_ids = public_voting.judgement_ids.apply(convert_array)
        public_voting.loc[public_voting.voted_for_judgement_model_entity.isna(), 
            "voted_for_judgement_model_entity"] = "Failed to vote"
        def voted_for(x):
            if x.voted_for_judgement_model_entity == 'Failed to vote':
                return x.voted_for_judgement_model_entity
            voted_for_ith = (x.voted_for_judgement_id==x.judgement_ids).argmax()
            nth = {
                0: "first",
                1: "second",
                2: "third",
                3: "fourth"
            }
            ith = nth[voted_for_ith]
            return f'{ith}_judgement'
        public_voting['voted_for'] = public_voting.apply(voted_for, axis=1)
        return public_voting
    
    def load_judgements(self):
        judgements = None
        if 'fact_judgements' in self.table_names.tbl_name.values:
            sql_statement = \
            """
            SELECT
                fact.Categories,
                fact.Team_ID,
                fact.Score,
                fact.Rational,
                dim.judgement_id,
                dim.discourse_id,
                dim.model_id_judging,
                model_infos.model_entity AS judge_entity,
                team.model_entity AS team_entity
            FROM 'fact_judgements' AS fact
            LEFT JOIN 'dim_judgements' as dim
                USING (judgement_id)
            LEFT JOIN 'model_infos' as model_infos
                ON dim.model_id_judging = model_infos.model_id
            LEFT JOIN 'model_infos' AS team
                ON fact.Team_ID = team.model_id
            """
            judgements = pd.read_sql(sql_statement, self.connection)
        return judgements