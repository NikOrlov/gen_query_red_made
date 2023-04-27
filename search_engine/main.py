from src.sparse_retriever.sparse_retriever import SparseRetriever as SearchEngine
import sqlite3
import click
from ranx import evaluate

sql_db_path = '../volume/db/project.db'


@click.command()
@click.argument('exp_name')
@click.argument('queries_table')
@click.option('--cutoff', default=100)
def start_run(exp_name, queries_table, cutoff):
    click.echo(f'Start handle of queries with params: {exp_name, queries_table, cutoff}')
    conn = sqlite3.connect(sql_db_path)
    c = conn.cursor()
    query = f'SELECT * FROM {queries_table}'
    row_count = 0
    row_limit = 10
    # 1. Создать jsonl файл по директории с учетом exp_name
    # 2. Записывать в файл построчно новый словарь
    # with open(f'../experiments_runs/run_of_{exp_name}')
    #     for q in c.execute(query):
    #         print(f'Query: {q}')
    #         se = SearchEngine.load("new_index")
    #         q_primary_id, q_id, q_text = q
    #         query_result = se.search(q_text)
    #         print(f'Test query result: {query_result}')
    #         new_result = {q_id: query_result}
    #
    #         row_count += 1
    #         if row_count >= row_limit:
    #             break

# python main.py index queries_table_1 qrels_table_1 DOCS
@click.command()
@click.argument('queries_table')
@click.argument('qrels_table')
@click.argument('docs_table')
@click.option('--row_limit', default=10)
def index(queries_table, qrels_table, docs_table, row_limit):
    click.echo(f'Start index with params: {qrels_table, queries_table, docs_table, row_limit}')

    docs_generator = SearchEngine.collection_generator_from_db(sql_db_path=sql_db_path,
                                                               table_name=docs_table,
                                                               row_limit=row_limit)
    se = SearchEngine("new_index").index(docs_generator)
    query = "simple_text"
    cutoff = 100
    # cutoff == 100 because main metric is MRR@100
    query_result = se.search(query=query, return_docs=False, cutoff=cutoff)
    print('Test search result: \n', query_result)


@click.group()
def entry_point():
    pass


entry_point.add_command(start_run)
entry_point.add_command(index)


if __name__ == '__main__':
    entry_point()
