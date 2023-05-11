import sys
import sqlite3
import pandas as pd
from config.utils import DB_PATH, EXPERIMENT_INIT, logger
from iterator import DBIterator


class QueryGenerator:
    def __init__(self, model, experiment_name, db_path=DB_PATH):
        logger.info(f"Starting {experiment_name} experiment!")
        self.model = model
        self.connection = sqlite3.connect(db_path)
        self.experiment_name = experiment_name
        self.table_queries = f"QUERIES_{experiment_name}"
        self.table_qrels = f"QRELS_{experiment_name}"
        self.joined_view = f"JOINED_{experiment_name}"
        self.init_experiment()

    def init_experiment(self):
        logger.info(f"Initializing DB experiments: "
                    f"creating {self.table_queries}, {self.table_qrels}, {self.joined_view}")
        self.connection.executescript(
            EXPERIMENT_INIT.format(
                TABLE_QUERIES=self.table_queries,
                TABLE_QRELS=self.table_qrels,
                JOINED_VIEW=self.joined_view,
            )
        )

    def generate_query(self, batch, write=True):
        """
        :param batch: DOCS table content: List of (id, doc_d, data)
        :param write: write generated queries to db or not (write by default)
        :return: List of generated queries: 1 query for 1 doc

        For each document model generates only ONE string:
        1 string = 1 query
        1 string = multiple queries concatenated in one string with ';' separator
        """
        # TODO Discuss:
        #  1 doc = 1 "string" format
        #  is it necessary to return generated_qs

        df_batch = pd.DataFrame(batch, columns=["id", "doc_id", "data"])
        df_batch["query_id"] = df_batch["doc_id"]
        documents = df_batch["data"]

        if self.model:
            generated_qs = self.model(documents)
        else:
            generated_qs = [""] * len(documents)

        assert len(generated_qs) == len(documents)

        if write:
            self.write_to_db(generated_qs, df_batch)
        return generated_qs

    def write_to_db(self, generated_queries, df_batch):
        logger.debug(f"Writing generated queries ({len(df_batch)} samples) "
                     f"to DB (tables: {self.table_queries}, {self.table_qrels})")

        queries_to_db = df_batch[["id", "query_id"]].copy()
        queries_to_db["data"] = generated_queries
        queries_to_db["data"] = queries_to_db["data"].astype("string")
        queries_to_db.to_sql(
            self.table_queries, self.connection, if_exists="append", index=False
        )

        qrels_to_db = df_batch[["id", "query_id", "doc_id"]].copy()
        qrels_to_db.to_sql(
            self.table_qrels, self.connection, if_exists="append", index=False
        )


if __name__ == "__main__":
    experiment = sys.argv[1]
    docs_table = "DOCS"
    dummy_model = None
    q_generator = QueryGenerator(dummy_model, experiment)
    test_iterator = DBIterator(docs_table, batch_size=1024)
    for batch_data in test_iterator:
        q_generator.generate_query(batch_data)
