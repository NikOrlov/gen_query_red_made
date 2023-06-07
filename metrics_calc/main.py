import sys
import os
import json
import sqlite3
import click
from ranx import Qrels, Run, evaluate

from config.utils import logger, VOLUME_PATH, DB_NAME_MSMARCO, DB_NAME_VK


# python metrics_calc/main.py eval QRELS test_exp
@click.command()
@click.argument("db_name")
@click.argument("qrels_table")
@click.argument("exp_name")
def eval(db_name, qrels_table, exp_name):
    if db_name != DB_NAME_VK and db_name != DB_NAME_MSMARCO:
        logger.error(f"Wrong DB name: {db_name} (available: {DB_NAME_VK, DB_NAME_MSMARCO})")
    db_path = os.path.join(VOLUME_PATH, f'{db_name}.db')

    logger.debug(f"Start evaluate with params: {db_name, qrels_table, exp_name}")

    experiments_runs_path = f"experiments_runs/{exp_name}_run.jsonl"

    with open(experiments_runs_path) as json_run:
        run_dict = json.load(json_run)

    logger.debug(f"RUN dict length: {len(run_dict)}")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    query = f"SELECT * FROM {qrels_table}"
    qrels_dict = {}
    for q in c.execute(query):
        q_id, query_id, doc_id = q
        qrels_dict[f"{query_id}"] = {doc_id: 1}

    logger.debug(f"QRELS dict length: {len(qrels_dict)}")

    run = Run(run_dict)
    qrels = Qrels(qrels_dict)

    score = evaluate(qrels, run, "mrr@100")

    logger.info(f"Score MRR@100: {score}")

    experiments_results_path = f"results/results.jsonl"
    logger.info(f"Save experiments result to: metrics_calc/results.jsonl")

    with open(experiments_results_path, "a+") as results_f:
        new_row = {exp_name: score}
        json.dump(new_row, results_f)


@click.group()
def entry_point():
    pass


entry_point.add_command(eval)


if __name__ == "__main__":
    entry_point()
