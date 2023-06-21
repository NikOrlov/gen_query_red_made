#!/bin/bash
project_dir=$( pwd )
docker run --rm --name metrics_calc -e TZ=Europe/Moscow -v $project_dir/logs:/metrics_calc/logs -v $project_dir/volume/:/volume -v $project_dir/experiments_runs/:/metrics_calc/experiments_runs -v $project_dir/metrics_calc/results/:/metrics_calc/results metrics_calc:0.3 eval qrels "$1"
