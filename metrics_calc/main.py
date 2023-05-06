import sys
import json
import sqlite3
import click
from ranx import Qrels, Run, evaluate

sys.path.append("../gen_query_red_made")
from utils import logger, DB_PATH


# python metrics_calc/main.py eval QRELS test_exp
@click.command()
@click.argument("qrels_table")
@click.argument("exp_name")
def eval(qrels_table, exp_name):
    logger.debug(f"Start evaluate with params: {qrels_table, exp_name}")

    experiments_runs_path = f"experiments_runs/{exp_name}_run.jsonl"

    with open(experiments_runs_path) as json_run:
        run_dict = json.load(json_run)

    logger.debug(f"RUN dict length: {len(run_dict)}")

    conn = sqlite3.connect(DB_PATH)
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

    experiments_results_path = f"metrics_calc/results.jsonl"
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
