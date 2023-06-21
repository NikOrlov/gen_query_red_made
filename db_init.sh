#!/bin/sh
mkdir -p volume/db

sqlite3 volume/db/"$1".db << EOF
.read init.sql
.separator \t
.import data/$1/docs.tsv docs
.import data/$1/qrels.tsv qrels
.import data/$1/queries.tsv queries
EOF