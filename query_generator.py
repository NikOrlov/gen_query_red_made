import sqlite3
import pandas as pd
from utils import DB_PATH


class QueryGenerator():
    def __init__(self, model, experiment_name, db_path=DB_PATH):
        self.model = model
        self.connection = sqlite3.connect(db_path)
        self.experiment_name = experiment_name
        self.table_queries = 'QUERIES_' + experiment_name
        self.table_qrels = 'QRELS_' + experiment_name
        self.joined_view = 'JOINED_' + experiment_name
        self.init_experiment()


    def init_experiment(self):
        self.connection.execute(('drop table if exists {table};'.format(table=self.table_queries)))
        self.connection.execute(('drop table if exists {table};'.format(table=self.table_qrels)))
        # self.connection.execute(('drop view if exists {table};'.format(table=self.joined_view)))
        create_table = 'create table {table}({field_1} {type_1} primary key, {field_2} {type_2}, {field_3} {type_3});'
        create_index = 'create {option} index {ind}_{i}_id on {table}({field});'
        self.connection.execute(create_table.format(table=self.table_queries, field_1='id', type_1='number', field_2='query_id', type_2='number', field_3='data', type_3='text'))
        self.connection.execute(create_table.format(table=self.table_qrels, field_1='id', type_1='number', field_2='query_id', type_2='number', field_3='doc_id', type_3='number'))
        self.connection.execute(create_index.format(option='unique', ind=self.table_queries, i='1', table=self.table_queries, field='query_id'))
        self.connection.execute(create_index.format(option='', ind=self.table_qrels, i='1', table=self.table_qrels, field='query_id'))
        self.connection.execute(create_index.format(option='', ind=self.table_qrels, i='2', table=self.table_qrels, field='doc_id'))


    def init_view(self):
        self.connection.execute(('drop view if exists {table};'.format(table=self.joined_view)))
        self.connection.execute(("""
        CREATE VIEW {view} AS SELECT QR.ID ID, Q.QUERY_ID, Q.DATA QUERY_DATA, D.DOC_ID, D.DATA DOC_DATA FROM {qrels} QR
        LEFT JOIN DOCS D ON QR.DOC_ID = D.DOC_ID
        LEFT JOIN {queries} Q ON QR.QUERY_ID = Q.QUERY_ID;""".format(view=self.joined_view, queries=self.table_queries, qrels=self.table_qrels)))


    def generate_query(self, batch, write=True):
        df_batch = pd.DataFrame(batch)
        if df_batch.shape[1] == 5:
            df_batch.rename(columns={0: 'id', 1: 'query_id', 2: 'query', 3: 'doc_id', 4: 'data'}, inplace=True)
        elif df_batch.shape[1] == 3:
            df_batch.rename(columns={0: 'id', 1: 'doc_id', 2: 'data'}, inplace=True)
        documents = df_batch['data']
        generated_qs = []
        if 'query' in df_batch.columns:
            queries = df_batch['query']
            for doc, query in zip(documents, queries):
                generated_qs.append(query)
        else:
            pass
        if write:
            self.write_to_db(generated_qs, df_batch)
            self.init_view()
        return generated_qs

    def write_to_db(self, generated_queries, df_batch):
        queries_to_db = df_batch[['id', 'query_id']].copy()
        queries_to_db['data'] = generated_queries
        queries_to_db['data'] = queries_to_db['data'].astype('string')
        queries_to_db.to_sql(self.table_queries, self.connection, if_exists='append', index=False)
        qrels_to_db = df_batch[['id', 'query_id', 'doc_id']].copy()
        qrels_to_db.to_sql(self.table_qrels, self.connection, if_exists='append', index=False)
