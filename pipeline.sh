#!/bin/bash
project_dir=$( pwd )
db_name=$1
joined_table=$2

experiment_name="${db_name}_${joined_table}_exp"
docker run --rm --name search_engine -e TZ=Europe/Moscow -v $project_dir/volume/:/volume -v $project_dir/logs/:/search_engine/logs -v $project_dir/experiments_runs/:/search_engine/experiments_runs -v $project_dir/search_engine/retriv_storage/:/search_engine/search_engine/retriv_storage/ search_engine:0.3 index $db_name $joined_table $experiment_name
docker run --rm --name search_engine -e TZ=Europe/Moscow -v $project_dir/volume/:/volume -v $project_dir/logs/:/search_engine/logs -v $project_dir/experiments_runs/:/search_engine/experiments_runs -v $project_dir/search_engine/retriv_storage/:/search_engine/search_engine/retriv_storage/ search_engine:0.3 start-run $db_name queries $experiment_name
docker run --rm --name metrics_calc -e TZ=Europe/Moscow -v $project_dir/logs:/metrics_calc/logs -v $project_dir/volume/:/volume -v $project_dir/experiments_runs/:/metrics_calc/experiments_runs -v $project_dir/metrics_calc/results/:/metrics_calc/results metrics_calc:0.3 eval $db_name qrels $experiment_name
