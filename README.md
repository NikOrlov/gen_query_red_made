All commands must be executed in the project directory (``gen_query_red_made``):
### 0. Download extended docs and VK data (optional)
By default DB contains docs, only represented in qrels (5185 docs), in case if you want to test pipeline on large amount of docs, you can download larger data.tsv file: 

- download and extract data-file from [Google drive (5 gb, 400k docs)](https://drive.google.com/file/d/1rF6nZE-z32lR2A-AS1gVZUL4mDKP-C4O/view?usp=sharing) 
- replace existing: ``mv docs_400k.tsv data/msmarco/docs.tsv``
<br><br>

To perform operations with VK dataset:
- download vk-dataset files ``docs.tsv``, ``queries.tsv``, ``qrels.tsv``
- create directory ``data/vk``
- move downloaded files to ``data/vk/*``


### 1. Create virtual environment:
```
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

### 2. Create DB (``db_name`` = ``vk`` or ``msmarco``):
```
docker build -t db_red .
docker run -it -v /path_to_project/gen_query_red_made/volume:/volume -v /path_to_project/gen_query_red_made/data:/data db_red ./db_init.sh <DB_NAME>
```
- DB_NAME - msmarco/vk <br>

Test example (creating ``msmarco.db`` and ``vk.db``):
```
docker run -it -v $(pwd)/volume:/volume -v $(pwd)/data:/data db_red ./db_init.sh msmarco
docker run -it -v $(pwd)/volume:/volume -v $(pwd)/data:/data db_red ./db_init.sh vk
```

### Run experiment

Build docker image for indexing documents and performing searching: <br>
``docker build search_engine/ -t search_engine:0.3``

Build docker image for metrics calculation: <br>
``docker build metrics_calc/ -t metrics_calc:0.3``

Run experiment: <br>
``./pipeline.sh <DB_NAME> <DATA_TABLE>``

- DB_NAME - msmarco/vk <br>
- DATA_TABLE - DOCS/JOINED <br>

Test example (run experiment on ``joined`` table in ``vk`` DB):
```
./pipeline.sh vk joined
```


### 3. Iterator usage:
``python iterator.py table_name batch_size shuffle``

- table_name - string
- batch_size - number
- shuffle - True/False

Example (get ``shuffled`` data from table/view ``joined`` with ``batch_size=16``):

``python iterator.py joined 16 True``


Iterator's response:
```
[
  [(row_1),(row_2),(row_3)...(row_BS)],
  .....,
  [(row_k1),(row_k2),(row_k3)...(row_kBS)]
]
```


### DB setup:
1. Run container:

``docker run -it -v /path_to_project/gen_query_red_made/volume:/volume -v /path_to_project/gen_query_red_made/data:/data <image_name>``

2. Open **sqlite** (type command in docker container console):

``sqlite3 volume/db/project.db``

3. Write SQL-queries (pay attention to ``;``):

``select count(*) from qrels;``

### DB schema:
(foreign keys removed due to the missing docs.data)

![alt text](https://user-images.githubusercontent.com/21123064/235138482-c678a431-a8aa-43fa-bb46-568509893351.png)

### Pipeline v0.2: Documents indexing and metrics calculation

#### Step 1
The first step of the pipeline is document indexing and
**search engine** service can help us with this. <br>
Build docker image (from root) <br>
``docker build search_engine/ -t search_engine:0.2``

Then use search_engine.sh to interact with service:

Command format:
``./search_engine.sh <COMMAND> <SQL TABLE> <EXPERIMENT NAME>``

```COMMAND``` - index/start-run <br>
```SQL TABLE``` - DOCS/JOINED <br>
```EXPERIMENT``` - any string u want <br>

Command example:
``./search_engine.sh index DOCS no_queries_test ``

First argument can be one of two commands: **index** and **start-run**. <br/>
In first step case we should use **index** command.

Second argument is table name of sqlite database. This table should contain:
TODO: write column names

Third argument is name of experiment. **Attention**: you should use this name in all other steps.


#### Step 2

Next step is **make a run**:
We should create a .jsonl file that will contain work result of search engine: 
top-100 best search engine answers on each query.

Command format: <br>
``./search_engine.sh <COMMAND> <SQL TABLE> <EXPERIMENT NAME> <--b> <--k>``

COMMAND - start-run <br>
b - bm25 coefficient <br>
k - bm25 coefficient

Now In first argument you should use another command: **start-run**

Test example:

``./search_engine.sh start-run QUERIES no_queries_test --b=0.4 --k=0.9``

#### Step 3
Last step is metrics calculation.

First we should build docker of metrics_calc service: <br>
``docker build metrics_calc/ -t metrics_calc:0.1``

Command format: <br>
``./metrics_calc.sh <COMMAND> <TABLE_NAME> <EXPERIMENT_NAME>``

COMMAND = eval <br>
TABLE_NAME = table with queries relationships <br>
EXPERIMENT_NAME = like in previous steps

Test example: <br>
``./metrics_calc.sh eval QRELS no_queries_test``

You will see results of experiment in folder: experiments_runs/<experiment_name>
