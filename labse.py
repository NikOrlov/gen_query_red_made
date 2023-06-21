import os
import sys
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from iterator import DBIterator
import pandas as pd
import numpy as np
import json
import pickle
from config.utils import logger

MODEL_NAME = 'sentence-transformers/LaBSE'
EMBEDDINGS_PATH = 'labse_embeddings'
EMB_SIZE = 768
MODEL = SentenceTransformer(MODEL_NAME)
BATCH_SIZE = 512
TOP_K = 100
EXPERIMENTS_RUNS_PATH = 'experiments_runs'
QUERY_ITEM_PATH = 'labse_embeddings/msmarco/msmarco_queries_mean_data_'


class Item:
    def __init__(self, embeddings, ids):
        assert len(embeddings) == len(ids)
        assert embeddings is not None
        assert ids is not None
        self.embeddings = embeddings
        self.ids = ids

    def __getitem__(self, item):
        doc_arg = np.where(self.ids == item)[0][0]
        return self.embeddings[doc_arg]

    def __eq__(self, other):
        if np.array_equal(self.ids, other.ids):
            if np.array_equal(self.embeddings, other.embeddings):
                return True
            else:
                print('Equal ids, but embeddings are different')
                return False

        else:
            sorted_args_self = np.argsort(self.ids)
            sorted_args_other = np.argsort(other.ids)
            if np.array_equal(self.ids[sorted_args_self], other.ids[sorted_args_other]):
                if np.array_equal(self.embeddings[sorted_args_self], other.embeddings[sorted_args_other]):
                    print('Equal, but shuffled ids and embeddings')
                    return True
                else:
                    print('Shuffled ids, but embeddings are different')
                    return False

    def __str__(self):
        return f"Item with embeddings ({self.embeddings.shape}) and ids ({self.ids.shape})"


class LaBSERanker:
    def __init__(self, db, table, emb_columns, id_column='doc_id', regime='merged', experiment_info=None,
                 table_type='joined', batch_size=BATCH_SIZE):
        self.db = db
        self.db_path = os.path.join('volume/db', f'{db}.db')
        self.table = table
        self.emb_columns = emb_columns
        self.id_column = id_column
        self.regime = regime
        self.experiment_info = experiment_info if experiment_info is not None else ''
        self.experiment_name = f'{db}_{table}_{regime}_{"_".join(emb_columns)}_{self.experiment_info}'
        self.table_type = table_type
        self.batch_size = batch_size
        self.model = MODEL
        self.embeddings = None
        self.ids = None
        logger.info(f'Start LaBSERanker ({self.experiment_name})')
        logger.info(f'Parameters: db={db}, '
                    f'table={table}, '
                    f'emb_columns={emb_columns}, '
                    f'id_column={id_column}, '
                    f'regime={regime}, '
                    f'experiment_info={experiment_info}, '
                    f'table_type={table_type}, '
                    f'batch_size={batch_size}')

    def process_table(self, emb_columns):
        logger.debug(f'Processing {self.table}-table, columns: {emb_columns}')
        db_iterator = DBIterator(self.table,
                                 batch_size=self.batch_size,
                                 shuffle=False,
                                 db_path=self.db_path)

        queries_columns = ["id", "query_id", "data"]
        docs_columns = ["id", "doc_id", "data"]
        joined_columns = ["id", "query_id", "query_data", "doc_id", "doc_data"]

        column_types = {'queries': queries_columns,
                        'docs': docs_columns,
                        'joined': joined_columns}

        select_columns = column_types[self.table_type]

        embs, ids = [], []
        for batch in tqdm(db_iterator):
            df_batch = pd.DataFrame(batch, columns=select_columns)

            batch_ids = df_batch[self.id_column].dropna()
            assert len(batch_ids.unique()) == len(batch_ids)
            batch_ids = batch_ids.values.tolist()

            df_batch_filtered = df_batch[emb_columns]
            model_batch = pd.Series(df_batch_filtered.fillna('').values.tolist()).str.join(' ').values.tolist()
            model_emb = self.model.encode(model_batch)

            assert len(batch_ids) == len(model_emb)
            embs.extend(model_emb)
            ids.extend(batch_ids)
        logger.debug(f'Table processed, embeddings len: {len(embs)}, ids: {len(ids)}')

        assert len(embs) == len(ids)
        return np.array(embs), np.array(ids)

    def build_doc_embeddings(self):
        logger.debug(f"Building doc-embeddings for {self.table}")
        if len(self.emb_columns) == 1 or self.regime == 'merged':
            self.embeddings, self.ids = self.process_table(self.emb_columns[0])
            assert self.embeddings.shape[1] == EMB_SIZE, f'{self.embeddings.shape[1]} != {EMB_SIZE}'
        else:
            storage_emb = []
            storage_ids = []
            for column in self.emb_columns:
                embs, ids = self.process_table([column])
                storage_emb.append(embs)
                storage_ids.append(ids)

            self.ids = storage_ids[0]
            for ids in storage_ids[1:]:
                assert np.array_equal(self.ids, ids)

            if self.regime == 'concat':
                self.embeddings = np.concatenate(storage_emb, axis=1)
                assert self.embeddings.shape[1] == EMB_SIZE * len(
                    self.emb_columns), f'{self.embeddings.shape[1]} != {EMB_SIZE * len(self.emb_columns)}'

            elif self.regime == 'mean':
                self.embeddings = np.mean(storage_emb, axis=0)
                assert self.embeddings.shape[1] == EMB_SIZE, f'{self.embeddings.shape[1]} != {EMB_SIZE}'

            else:
                raise NotImplementedError
            assert len(self.embeddings) == len(self.ids)

        logger.debug(f'Embeddings shape: {self.embeddings.shape}, ids: {self.ids.shape}')

    def export(self):
        logger.debug("Exporting documents embeddings")
        if self.embeddings is None or self.ids is None:
            logger.warning(f'No embeddings or no ids for {self.table}')
            return

        dump_dir_path = os.path.join(EMBEDDINGS_PATH, self.db)
        os.makedirs(dump_dir_path, exist_ok=True)

        with open(os.path.join(dump_dir_path, self.experiment_name), 'wb') as file:
            exported_item = Item(self.embeddings, self.ids)
            pickle.dump(exported_item, file, protocol=4)
            # logger.debug(f'Exported embeddings (shape: {self.embeddings.shape}), ids (shape: {self.ids.shape})')
            logger.debug(exported_item)

    def rank(self, query_features_path, k=TOP_K):
        logger.debug("Start ranking documents")
        if self.embeddings is None or self.ids is None:
            logger.warning(f'No embeddings or no ids for {self.table}')
            return
        with open(query_features_path, 'rb') as file:
            query_item = pickle.load(file)

        run_dict = {}
        for query_id, query_emb in zip(query_item.ids, query_item.embeddings):
            dists = query_emb @ self.embeddings.T
            most_similar_args = np.argsort(dists)[::-1][:k]
            # top_docs = self.ids[most_similar_args]
            run_dict[str(query_id)] = {str(self.ids[arg_id]): str(dists[arg_id]) for arg_id in most_similar_args}
        assert len(run_dict) == len(query_item.ids)

        with open(os.path.join(EXPERIMENTS_RUNS_PATH, f'labse_{self.experiment_name}_run.jsonl'), 'w') as outfile:
            json.dump(run_dict, outfile)


def build_queries_embeddings(db):
    exp_query = LaBSERanker(db=db,
                            table="queries",
                            emb_columns=["data"],
                            regime="mean",
                            id_column='query_id',
                            experiment_info="",
                            table_type='queries')
    exp_query.build_doc_embeddings()
    exp_query.export()


def run_experiment(joined_table, db='msmarco'):
    query_emb_path = f'labse_embeddings/{db}/{db}_queries_mean_data_'
    if not os.path.exists(query_emb_path):
        exp_query = LaBSERanker(db=db,
                                table="queries",
                                emb_columns=["data"],
                                regime="mean",
                                id_column='query_id',
                                experiment_info="",
                                table_type='queries')
        exp_query.build_doc_embeddings()
        exp_query.export()

    exp_joined_merged = LaBSERanker(db=db,
                                    table=joined_table,
                                    emb_columns=["query_data", "doc_data"],
                                    regime="merged",
                                    experiment_info="",
                                    table_type='joined')
    exp_joined_merged.build_doc_embeddings()
    # exp_joined_merged.export()
    exp_joined_merged.rank(query_emb_path)
    run_name = f'labse_{exp_joined_merged.experiment_name}'
    return run_name


if __name__ == "__main__":
    db = sys.argv[1]
    joined_view = sys.argv[2]
    experiment_name = run_experiment(joined_view, db)
    logger.info(f'Run completed: {experiment_name}')