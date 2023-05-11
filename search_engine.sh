#!/bin/bash
project_dir=$( pwd )
#docker build search_engine/ -t search_engine:0.2
docker run --rm --name search_engine -v $project_dir/volume/:/volume -v $project_dir/experiments_runs/:/search_engine/experiments_runs -v $project_dir/search_engine/retriv_storage/:/search_engine/search_engine/retriv_storage/ search_engine:0.2 $1 $2 $3 $4 $5
