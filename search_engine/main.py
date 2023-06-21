import sys
import os
import sqlite3
import click
import json
from src.sparse_retriever.sparse_retriever import SparseRetriever as SearchEngine

from config.utils import logger, VOLUME_PATH, DB_NAME_MSMARCO, DB_NAME_VK


# python search_engine/main.py start-run QUERIES test_exp
@click.command()
@click.argument("db_name")
@click.argument("queries_table")
@click.argument("exp_name")
@click.option("--b", default=0.75)
@click.option("--k", default=1.2)
@click.option("--cutoff", default=100)
def start_run(db_name, queries_table, exp_name, b, k, cutoff):
    if db_name != DB_NAME_VK and db_name != DB_NAME_MSMARCO:
        logger.error(f"Wrong DB name: {db_name} (available: {DB_NAME_VK, DB_NAME_MSMARCO})")

    db_path = os.path.join(VOLUME_PATH, f'{db_name}.db')

    logger.info(
        f"Start handling queries with params: \n"
        f"db_name: {db_name} \n"
        f"db_path: {db_path} \n"
        f"queries_table: {queries_table}, \n"
        f"exp_name: {exp_name}, \n"
        f"b: {b}, \n"
        f"k: {k}, \n"
        f"cutoff: {cutoff}"
    )

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    query = f"SELECT * FROM {queries_table}"
    se = SearchEngine.load(f"{exp_name}_index")
    se.set_hyperparams(b=b, k=k)

    experiments_runs_path = f"experiments_runs/{exp_name}_run.jsonl"

    run_dict = {}
    answers_deficit_count = 0
    query_count = 0
    for q in c.execute(query):
        q_primary_id, q_id, q_text = q
        query_result = se.search(q_text, cutoff=100)

        run_dict[q_id] = {}

        for qr in query_result:
            run_dict[q_id][qr["id"]] = str(qr["score"])

        if len(run_dict[q_id]) < 100:
            answers_deficit_count += 1
        query_count += 1

    logger.debug(f"{answers_deficit_count}/{query_count} dont have 100 answers")
    logger.debug(f"Saving experiments data to: {experiments_runs_path}")

    os.makedirs(os.path.dirname(experiments_runs_path), exist_ok=True)
    with open(experiments_runs_path, "w") as run_f:
        json.dump(run_dict, run_f)


# python search_engine/main.py index JOINED test_exp
@click.command()
@click.argument("db_name")
@click.argument("joined_table_name")
@click.argument("exp_name")
@click.option("--row_limit", default=False)
def index(db_name, joined_table_name, exp_name, row_limit):
    if db_name != DB_NAME_VK and db_name != DB_NAME_MSMARCO:
        logger.error(f"Wrong DB name: {db_name} (available: {DB_NAME_VK, DB_NAME_MSMARCO})")

    db_path = os.path.join(VOLUME_PATH, f'{db_name}.db')

    logger.info(f"Start indexing documents with params: {db_name, joined_table_name, row_limit}")

    try:
        row_limit = int(row_limit)
    except TypeError:
        logger.error(
            f"Incorrect type of row_limit argument: must be integer, received: {row_limit, type(row_limit)}"
        )
        exit(1)

    docs_generator = SearchEngine.collection_generator_from_db(
        sql_db_path=db_path, table_name=joined_table_name, row_limit=row_limit
    )

    se = SearchEngine(f"{exp_name}_index").index(docs_generator)


@click.group()
def entry_point():
    pass


entry_point.add_command(start_run)
entry_point.add_command(index)


if __name__ == "__main__":
    entry_point()
