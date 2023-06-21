import sys
import re
from typing import List
from tqdm import tqdm
from transformers import pipeline
import torch
from query_generator import QueryGenerator
from iterator import DBIterator


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class HuggingFaceWrapper:
    def __init__(self, nlp_model, name, max_seq_len=1024, num_return_sequences=1, prefix=None):
        self.model = nlp_model
        self.name = name
        self.max_seq_len = max_seq_len
        self.num_return_sequences = num_return_sequences
        self.prefix = '' if prefix is None else prefix

    def __call__(self, text_list: List[str]) -> List[str]:
        # total_summary = []
        # for text in text_list:
        #     print(f'{len(text)}:')
        #     text_summary = []
        #     for sub_text in chunks(text.split(), self.max_seq_len):
        #         print(f'\t{len(sub_text)}')
        #         sub_text_summary = self.model(self.prefix + ' '.join(sub_text))
        #
        #         joined_query = ' '.join([q['summary_text'] for q in sub_text_summary])
        #         text_summary.append(joined_query)
        #
        #     total_summary.append(' '.join(text_summary))
        # return total_summary

        summary_text = self.model([self.prefix + t[:self.max_seq_len] for t in text_list])
        res = []

        for queries in summary_text:
            joined_query = ' '.join([q['summary_text'] for q in queries])
            res.append(joined_query)
        return res


NUM_WORKERS = 4
DEVICE = 1 if torch.cuda.is_available() else -1
DB_PATH = 'volume/db/msmarco.db'
MIN_LEN = 5
MAX_LEN = 30
NUM_RETURN_SEQ = 30
TOP_P = 0.95
DO_SAMPLE = True
SPLIT_SEQ_LEN = 320

ARGS = {'min_len': MIN_LEN, 'max_len': MAX_LEN, 'num_gen': NUM_RETURN_SEQ, 'seq_len': SPLIT_SEQ_LEN}
ARGS_STR = '_'.join([f'{k}_{v}' for k, v in ARGS.items()])


if __name__ == "__main__":
    # model_name = sys.argv[1]
    # bs = int(sys.argv[2])
    # info = sys.argv[3]

    model_name = 'doc2query/msmarco-t5-base-v1'
    bs = 8
    info = ''

    summarizer = pipeline("summarization",
                          model=model_name,
                          num_workers=NUM_WORKERS,
                          batch_size=bs,
                          device=DEVICE,
                          min_length=MIN_LEN,
                          max_length=MAX_LEN,
                          do_sample=DO_SAMPLE,
                          top_p=TOP_P,
                          num_return_sequences=NUM_RETURN_SEQ)
    # summarizer.seq_len = SEQ_LEN
    model = HuggingFaceWrapper(summarizer, model_name, SPLIT_SEQ_LEN, NUM_RETURN_SEQ)

    experiment_name = re.sub('[^0-9a-zA-Z]', '_', model.name) + f'__{ARGS_STR}_{info}'

    experiment = QueryGenerator(model, experiment_name, db_path=DB_PATH)

    db_iterator = DBIterator('DOCS', batch_size=bs, db_path=DB_PATH)
    for batch_data in tqdm(db_iterator):
        experiment.generate_query(batch_data)
