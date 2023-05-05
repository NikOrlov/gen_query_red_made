from src.sparse_retriever.sparse_retriever import SparseRetriever as SearchEngine
import sqlite3
import click
import json

sql_db_path = 'volume/db/project.db'


# python search_engine/main.py start-run QUERIES test_exp
@click.command()
@click.argument('queries_table')
@click.argument('exp_name')
@click.option('--cutoff', default=100)
def start_run(queries_table, exp_name, cutoff):
    click.echo(f'Start handle of queries with params: {exp_name, queries_table, cutoff}')
    conn = sqlite3.connect(sql_db_path)
    c = conn.cursor()
    query = f'SELECT * FROM {queries_table}'
    se = SearchEngine.load(f"{exp_name}_index")

    experiments_runs_path = f'experiments_runs/{exp_name}_run.jsonl'

    run_dict = {}
    for q in c.execute(query):
        q_primary_id, q_id, q_text = q
        query_result = se.search(q_text, cutoff=100)

        run_dict[q_id] = {}

        for qr in query_result:
            run_dict[q_id][qr['id']] = str(qr['score'])

    with open(experiments_runs_path, 'w') as run_f:
        json.dump(run_dict, run_f)


# python search_engine/main.py index JOINED test_exp
@click.command()
@click.argument('joined_table_name')
@click.argument('exp_name')
@click.option('--row_limit', default=False)
def index(joined_table_name, exp_name, row_limit):
    click.echo(f'Start index with params: {joined_table_name, row_limit}')

    try:
        row_limit = int(row_limit)
    except TypeError:
        print('Incorrect type of row_limit argument')
        exit(1)

    docs_generator = SearchEngine.collection_generator_from_db(sql_db_path=sql_db_path,
                                                               table_name=joined_table_name,
                                                               row_limit=row_limit)

    se = SearchEngine(f'{exp_name}_index').index(docs_generator)
    query = "simple_text"

    # cutoff == 100 because main metric is MRR@100
    cutoff = 100
    query_result = se.search(query=query, return_docs=False, cutoff=cutoff)
    print(f'Len of test query result: {len(query_result)}')


@click.group()
def entry_point():
    pass


entry_point.add_command(start_run)
entry_point.add_command(index)


if __name__ == '__main__':
    entry_point()
