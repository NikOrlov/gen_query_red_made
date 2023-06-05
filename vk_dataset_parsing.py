import sys
import csv
import os
import string
import random


def write_queries_file(dataset_file_path, dataset_filename):
    query_to_id = {}
    query_id = 0
    id_q = 0
    with open(os.path.join(dataset_file_path, dataset_filename), 'r') as f:
        csv_reader = csv.reader(f, delimiter='\t')
        for line in csv_reader:
            if len(line) == 7:  # Line CHECK
                label, query, _, _, _, data, _ = line
                if query not in query_to_id:
                    query_to_id[query] = query_id  # нам еще не попадался такой запрос
                    query = query.translate(str.maketrans('', '', string.punctuation)).lower()
                    with open(os.path.join(dataset_file_path, 'queries.tsv'), 'a', newline='') as new_file:
                        writer = csv.writer(new_file, delimiter='\t', lineterminator='\n')
                        writer.writerow([id_q, query_id, query])
                    id_q += 1
                    query_id += 1
    print('Unique queries found:', len(query_to_id.values()))
    print('queries file was written')
    return query_to_id


def write_docs_file(dataset_file_path, dataset_filename, query_to_id, return_dicts=True):
    doc_to_id = {}
    doc_num = 0
    doc_str = 'D'
    id_d, id = -1, 0
    with open(os.path.join(dataset_file_path, dataset_filename), 'r') as f:
        csv_reader = csv.reader(f, delimiter='\t')
        for line in csv_reader:
            id_d += 1
            doc_id = doc_str + str(doc_num)  # формируем название документа наподобие предыдущего датасета
            if len(line) == 7:  # Line CHECK
                label, query, _, _, _, data, _ = line
                data = data.translate(str.maketrans('', '', string.punctuation)).lower()
                data_short = ' '.join(data.lower().split()[:400])  # столько символов нам хватит, чтобы составить дикт
                if data_short not in doc_to_id:
                    doc_to_id[data_short] = doc_id
                    with open(os.path.join(dataset_file_path, 'docs.tsv'), 'a', newline='') as new_file:
                        writer = csv.writer(new_file, delimiter='\t', lineterminator='\n')
                        writer.writerow([id_d, doc_id, data])  # пишем текст полного документа
                    doc_num += 1
                if label == '3':  # хоть мы могли этот документ уже встречать, мы все равно запишем его отношение
                    query_id = query_to_id[query]
                    doc_id = doc_to_id[data_short]
                    with open(os.path.join(dataset_file_path, 'qrels.tsv'), 'a', newline='') as new_file:
                        writer = csv.writer(new_file, delimiter='\t', lineterminator='\n')
                        writer.writerow([id, query_id, doc_id])
                    id += 1
    print('Unique docs found:', len(doc_to_id.values()))
    print('Qrels number written:', id)
    print('qrels, docs files were written')


def dev_qrels_write(qrels_file_path, qrels_filename, dev_size):
    dev_docs_selected = set()
    dev_queries_selected = set()
    sampled_qrels_id = random.sample(range(0, 190000), dev_size + 2000)
    with open(os.path.join(qrels_file_path, qrels_filename), 'r') as f:
        csv_reader = csv.reader(f, delimiter='\t')
        for line in csv_reader:
            id, query_id, doc_id = line
            if query_id not in dev_queries_selected and int(id) in sampled_qrels_id:
                dev_queries_selected.add(query_id)
                dev_docs_selected.add(doc_id)
                with open(os.path.join(qrels_file_path, 'dev_qrels.tsv'), 'a', newline='') as new_file:
                    writer = csv.writer(new_file, delimiter='\t', lineterminator='\n')
                    writer.writerow([id, query_id, doc_id])
            if len(dev_queries_selected) >= dev_size:
                      break
    print(len(dev_queries_selected), 'qrels selected and written to dev_qrels.tsv')
    print(len(dev_docs_selected), 'docs selected')
    return dev_queries_selected, dev_docs_selected


def dev_docs_write(docs_file_path, docs_filename, dev_docs_selected):
    with open(os.path.join(docs_file_path, docs_filename), 'r') as f:
        csv_reader = csv.reader(f, delimiter='\t')
        for line in csv_reader:
            id_d, doc_id, data = line
            if doc_id in dev_docs_selected:
                with open(os.path.join(docs_file_path, 'dev_docs.tsv'), 'a', newline='') as new_file:
                    writer = csv.writer(new_file, delimiter='\t', lineterminator='\n')
                    writer.writerow([id_d, doc_id, data])


def dev_queries_write(queries_file_path, queries_filename, dev_queries_selected):
    with open(os.path.join(queries_file_path, queries_filename), 'r') as f:
        csv_reader = csv.reader(f, delimiter='\t')
        for line in csv_reader:
            id_q, query_id, query = line
            if query_id in dev_queries_selected:
                with open(os.path.join(queries_file_path, 'dev_queries.tsv'), 'a', newline='') as new_file:
                    writer = csv.writer(new_file, delimiter='\t', lineterminator='\n')
                    writer.writerow([id_q, query_id, query])


if __name__ == '__main__':
    csv.field_size_limit(sys.maxsize)
    DATASET_FILEPATH = '/home/tatiana/MADE/Project/VK_Dataset'
    DATASET_FILENAME = 'assessors_train_l_q_u_t_m_b_ql.tsv'
    QRELS_FILEPATH = DATASET_FILEPATH
    DOCS_FILEPATH = DATASET_FILEPATH
    QUERIES_FILEPATH = DATASET_FILEPATH
    DEV_SIZE = 5200

    query_to_id = write_queries_file(DATASET_FILEPATH, DATASET_FILENAME)
    write_docs_file(DATASET_FILEPATH, DATASET_FILENAME, query_to_id)
    # Тут генерится рандомная выборка для dev датасета, лучше он будет зафиксирован, поэтому код закоммичен
    # зафиксируем дев выборку - скачаем ее лучше из репа
    # dev_queries_selected, dev_docs_selected = dev_qrels_write(QRELS_FILEPATH, 'qrels.tsv', DEV_SIZE)
    # dev_docs_write(DOCS_FILEPATH, 'docs.tsv', dev_docs_selected)
    # dev_queries_write(DATASET_FILEPATH, 'queries.tsv', dev_queries_selected)

