import re
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

patterns = "[A-Za-z0-9!#$%&'()*+,./:;<=>?@[\]^_`{|}~—\"\-]+"
stopwords_ru = stopwords.words("russian")
import tqdm
import subprocess
from config.utils import DB_PATH
from transformers import T5Tokenizer, T5ForConditionalGeneration
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from query_generator import QueryGenerator
from iterator import DBIterator


class NLPModel():
    def __init__(self, model, tokenizer, min_length, max_length, num_first_tokens):
        self.model = model
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.min_length = min_length
        self.num_first_tokens = num_first_tokens

    def __call__(self, list_docs):
        splitted_tokens = [txt.split()[:self.num_first_tokens] for txt in list_docs]
        splitted_tokens = [[tok for tok in tokens if tok not in stopwords_ru and tok not in patterns] for tokens in splitted_tokens]
        texts = [' '.join(tokens) for tokens in splitted_tokens]
        texts = [WHITESPACE_HANDLER(text) for text in texts]
        token_batch = self.tokenizer(texts, truncation=True, padding="max_length",
                                    max_length=400,# self.max_length,
                                     return_tensors="pt").to(DEVICE)
        summ1 = self.model.generate(**token_batch,
                                    min_length=self.min_length,
                                   max_length=self.max_length,
                                    do_sample=True,
                                    num_return_sequences=30,
                                    top_p = 0.95)
        decoded_summ1 = self.tokenizer.batch_decode(summ1,# max_length=self.max_length,
                                                   #num_beams=3,
                                                   skip_special_tokens=True)
        result = []
        for i in range(0, len(decoded_summ1), 30):
            decode = decoded_summ1[i:i + 30]
            result.append(decode)
        return result


if __name__ == '__main__':
    model_list_names = ['/home/tatiana/MADE/Project/VK_Dataset/rut5-base-finetuned-rut5-2-epchs/checkpoint-40000']
    WHITESPACE_HANDLER = lambda k: re.sub('\s+', ' ', re.sub('\n+', ' ', k.strip()))
    BS = 2
    DEVICE = "cuda"
    NUM_BEAMS = 3
    min_length_list = [15, 30, 45, 60, 100, 120]
    max_length_list = [30, 45, 60, 100, 120]
    for i, model_name in enumerate(model_list_names):
        model = T5ForConditionalGeneration.from_pretrained(model_name)
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        model.to(DEVICE)
        model.eval()
        exps = []
        for min_len in min_length_list:
            for max_len in max_length_list:
                if max_len > min_len:
                    experiment_str = '_' + str(min_len) + '_' + str(max_len)
                    EXPERIMENT_NAME = model_name.split('/')[-1] + experiment_str + '30_queries_top_p'
                    experiment_nm = re.sub('[^0-9a-zA-Z]', '_', EXPERIMENT_NAME)
                    nlp_model = NLPModel(model, tokenizer, min_len, max_len, 100)
                    experiment = QueryGenerator(nlp_model, experiment_nm, db_path=DB_PATH)
                    db_iterator = DBIterator('DOCS', batch_size=BS, db_path=DB_PATH)
                    exps.append(experiment_nm)
                    for batch_data in db_iterator:
                        experiment.generate_query(batch_data)
    print(exps)
