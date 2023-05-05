All commands must be executed in the project directory (``gen_query_red_made``):

### 1. Create container:
``docker build -t db_red .``

### 2. Run container and upload data:
``docker run -it -v /path_to_project/gen_query_red_made/volume:/volume -v /path_to_project/gen_query_red_made/data:/data db_red ./db_init.sh``

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

![alt text](https://user-images.githubusercontent.com/21123064/234050815-045b2d36-a2fb-44f9-b004-3ee72e37040f.png)


### Pipeline v0.1: Documents indexing and metrics calculation

#### Step 1
The first step of the pipeline is document indexing and
**search engine** service can help us with this.
To start indexing documents, you must be in the root directory of the project.

Command format:

``python search_engine/main.py <COMMAND> <TABLE_NAME> <EXPERIMENT_NAME>``

First argument can be one of two commands: **index** and **start-run**. <br/>
In first step case we should use **index** command.

Second argument is table name of sqlite database. This table should contain:
TODO: write column names

Third argument is name of experiment. **Attention**: you should use this name in all other steps.


Test example: 

``python search_engine/main.py index JOINED test_exp``

#### Step 2

Next step is **make a run**:
We should create a .jsonl file that will contain work result of search engine: 
top-100 best search engine answers on each query.


Command format is the same as in the previous step.

Now In first argument you should use another command: **start-run**

In second argument you should specify name of table containing queries.

In last argument you should use experiment name from step 1.

Test example:

``python search_engine/main.py start-run QUERIES test_exp``

3. Last step is metrics calculation


Command format:
``python search_engine/main.py <COMMAND> <TABLE_NAME> <EXPERIMENT_NAME>``

COMMAND = eval <br>
TABLE_NAME = table with queries relationships <br>
EXPERIMENT_NAME = like in previous steps

Test example:
``python metrics_calc/main.py eval QRELS test_exp``

You will see results of experiment in folder: experiments_runs/<experiment_name>





