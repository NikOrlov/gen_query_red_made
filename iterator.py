import sys
import random
import sqlite3
from utils import DB_PATH

from query_generator import QueryGenerator


class DBIterator:
    def __init__(self, table, batch_size=1, shuffle=False, db_path=DB_PATH):
        self.con = sqlite3.connect(db_path)
        self.table = table
        self.shuffle = shuffle
        self.batch_size = batch_size
        self.cursor = self.con.cursor()
        self.min, self.max = self.cursor.execute(
            f"select min(id), max(id) from {table}"
        ).fetchall()[0]

    def __iter__(self):
        self.curr_id = self.min
        self.ids = list(range(self.min, self.max + 1))
        if self.shuffle:
            random.shuffle(self.ids)
        return self

    def make_request(self, start_pos, end_pos):
        sample_ids = tuple(self.ids[start_pos: end_pos + 1])
        if len(sample_ids) != 1:
            sql = "SELECT * FROM {} WHERE ID IN {}".format(self.table, sample_ids)
        else:
            sql = "SELECT * FROM {} WHERE ID = {}".format(self.table, sample_ids[0])
        data = self.cursor.execute(sql).fetchall()
        assert (
            len(data) == end_pos - start_pos + 1
        ), f"{len(data)} != {end_pos} - {start_pos} + 1"
        return data

    def __next__(self):
        if self.curr_id > self.max:
            raise StopIteration
        start_pos = self.curr_id
        end_pos = min(start_pos + self.batch_size - 1, self.max)
        data = self.make_request(start_pos, end_pos)
        self.curr_id += self.batch_size
        return data


if __name__ == "__main__":
    # table_name = 'docs'
    table_name = sys.argv[1]
    bs = int(sys.argv[2])
    shuffle_data = True if sys.argv[3] == 'True' else False
    q_generator = QueryGenerator('Dummy_Model', 'DEV_MODEL_0')
    test_iterator = DBIterator(table_name, bs, shuffle_data)
    for batch in test_iterator:
        q_generator.generate_query(batch)
        # break
