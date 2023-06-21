#!/bin/bash
project_dir=$( pwd )
docker run --rm --name search_engine -e TZ=Europe/Moscow -v $project_dir/volume/:/volume -v $project_dir/logs/:/search_engine/logs -v $project_dir/experiments_runs/:/search_engine/experiments_runs -v $project_dir/search_engine/retriv_storage/:/search_engine/search_engine/retriv_storage/ search_engine:0.3 $1 $2 $3 $4 $5
