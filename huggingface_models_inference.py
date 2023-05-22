import sys
import re
from tqdm import tqdm
from transformers import pipeline
import torch
from query_generator import QueryGenerator
from iterator import DBIterator


class HuggingFaceWrapper:
    def __init__(self, nlp_model, max_seq_len=1024):
        self.model = nlp_model
        self.max_seq_len = max_seq_len

    def __call__(self, text):
        summary_text = self.model([t[:self.max_seq_len] for t in text])
        return [s['summary_text'] for s in summary_text]


# BS = 4
# SEQ_LEN = 4096
NUM_WORKERS = 4
DEVICE = 1 if torch.cuda.is_available() else -1
DB_PATH = 'volume/db/project.db'


if __name__ == "__main__":
    MODEL_NAME = sys.argv[1]
    SEQ_LEN = int(sys.argv[2])
    BS = int(sys.argv[3])
    # MODEL_NAME = "facebook/bart-large-cnn"
    # MODEL_NAME = "Einmalumdiewelt/T5-Base_GNAD"
    EXPERIMENT_NAME = re.sub('[^0-9a-zA-Z]', '_', MODEL_NAME)

    summarizer = pipeline("summarization",
                          model=MODEL_NAME,
                          num_workers=NUM_WORKERS,
                          batch_size=BS,
                          device=DEVICE)
    summarizer.seq_len = SEQ_LEN
    model = HuggingFaceWrapper(summarizer, SEQ_LEN)

    experiment = QueryGenerator(model, EXPERIMENT_NAME, db_path=DB_PATH)

    db_iterator = DBIterator('DOCS', batch_size=BS, db_path=DB_PATH)
    for batch_data in tqdm(db_iterator):
        experiment.generate_query(batch_data)
