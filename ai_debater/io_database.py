
import sqlite3 
import pandas as pd

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
            *
        FROM 'fact_discourse'
        WHERE
            TRUE
            AND discourse_id = '{}'
        """.format(discourse_id)
        return pd.read_sql(sql_statement, self.connection)

    def load_enriched_judgements(self):
        dim_judgements = None
        if 'dim_judgements' in self.table_names.tbl_name.values:
            sql_statement = \
            """
            SELECT
                judg.*,
                model_infos.model_entity
            FROM 'dim_judgements' AS judg
            LEFT JOIN 'model_infos' as model_infos
                ON judg.model_id_judging = model_infos.model_id
            """
            dim_judgements = pd.read_sql(sql_statement, self.connection)
        return dim_judgements