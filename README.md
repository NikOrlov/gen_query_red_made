All commands must be executed in the project directory (``gen_query_red_made``):
### 0. Download data:
- download **docs.tsv** from [Google drive (5 gb)](https://drive.google.com/file/d/11axOQXZe-sTrjrlRpFhy1KLMRp8535E3/view?usp=share_link)
- replace current dummy file ``data/docs.tsv``

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

![alt text](https://user-images.githubusercontent.com/21123064/235137898-f2208f31-f9fc-46e3-b3c3-aadc46639c13.png)
