import sys
import sqlite3
import click
import json
from src.sparse_retriever.sparse_retriever import SparseRetriever as SearchEngine

sys.path.append("../gen_query_red_made")
from utils import logger, DB_PATH


# python search_engine/main.py start-run QUERIES test_exp
@click.command()
@click.argument("queries_table")
@click.argument("exp_name")
@click.option("--cutoff", default=100)
def start_run(queries_table, exp_name, cutoff):
    logger.info(
        f"Start handling queries with params: {exp_name, queries_table, cutoff}"
    )

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = f"SELECT * FROM {queries_table}"
    se = SearchEngine.load(f"{exp_name}_index")

    experiments_runs_path = f"experiments_runs/{exp_name}_run.jsonl"

    run_dict = {}
    for q in c.execute(query):
        q_primary_id, q_id, q_text = q
        query_result = se.search(q_text, cutoff=100)

        run_dict[q_id] = {}

        for qr in query_result:
            run_dict[q_id][qr["id"]] = str(qr["score"])

    logger.debug(f"Saving experiments data to: {experiments_runs_path}")

    with open(experiments_runs_path, "w") as run_f:
        json.dump(run_dict, run_f)


# python search_engine/main.py index JOINED test_exp
@click.command()
@click.argument("joined_table_name")
@click.argument("exp_name")
@click.option("--row_limit", default=False)
def index(joined_table_name, exp_name, row_limit):
    logger.info(f"Start indexing documents with params: {joined_table_name, row_limit}")

    try:
        row_limit = int(row_limit)
    except TypeError:
        logger.error(
            f"Incorrect type of row_limit argument: must be integer, received: {row_limit, type(row_limit)}"
        )
        exit(1)

    docs_generator = SearchEngine.collection_generator_from_db(
        sql_db_path=DB_PATH, table_name=joined_table_name, row_limit=row_limit
    )

    se = SearchEngine(f"{exp_name}_index").index(docs_generator)


@click.group()
def entry_point():
    pass


entry_point.add_command(start_run)
entry_point.add_command(index)


if __name__ == "__main__":
    entry_point()
