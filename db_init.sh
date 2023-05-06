#!/bin/sh
mkdir /volume/db
sqlite3 /volume/db/project.db << EOF
.read /init.sql
.separator \t
.import /data/docs.tsv docs
.import /data/qrels.tsv qrels
.import /data/queries.tsv queries
EOF