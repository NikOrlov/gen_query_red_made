from ranx import Qrels, Run, evaluate
import sqlite3
import click
import json


sql_db_path = 'volume/db/project.db'


# python metrics_calc/main.py eval QRELS test_exp
@click.command()
@click.argument('qrels_table')
@click.argument('exp_name')
def eval(qrels_table, exp_name):
    click.echo(f'Start evaluate with params: {qrels_table, exp_name}')

    experiments_runs_path = f'experiments_runs/{exp_name}_run.jsonl'

    with open(experiments_runs_path) as json_run:
        run_dict = json.load(json_run)

    print('RUN DICT LEN')
    print(len(run_dict))

    conn = sqlite3.connect(sql_db_path)
    c = conn.cursor()
    query = f'SELECT * FROM {qrels_table}'
    qrels_dict = {}
    for q in c.execute(query):
        q_id, query_id, doc_id = q
        qrels_dict[f'{query_id}'] = {doc_id: 1}

    print('QRELS DICT LEN')
    print(len(qrels_dict))

    run = Run(run_dict)
    qrels = Qrels(qrels_dict)

    score = evaluate(qrels, run, "mrr@100")

    print(f'SCORE: {score}')

    experiments_results_path = f'metrics_calc/results.jsonl'

    with open(experiments_results_path, 'a+') as results_f:
        new_row = {exp_name: score}
        json.dump(new_row, results_f)


@click.group()
def entry_point():
    pass


entry_point.add_command(eval)


if __name__ == '__main__':
    entry_point()
