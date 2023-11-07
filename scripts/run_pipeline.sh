#!/bin/bash

# You can run this script from the command line using:
# ./run_pipeline.sh <start_date> <end_date> <raw_data_file> <processed_data_file> <model_file> <test_data_file> <predictions_file>
# For example:
# ./run_pipeline.sh 2020-01-01 2020-01-31 data/raw_data.csv data/processed_data.csv models/model.pkl data/test_data.csv predictions/predictions.json

# Get command line arguments
start_date="$1"
end_date="$2"
raw_data_file="$3"
processed_data_file="$4"
model_file="$5"
test_data_file="$6"
predictions_file="$7"

# Run data_ingestion.py
echo "Starting data ingestion..."
python src/data_ingestion.py --start_date="$start_date" --end_date="$end_date" --output_file="$raw_data_file"

# Run data_processing.py
echo "Starting data processing..."
python src/data_processing.py --input_file="$raw_data_file" --output_file="$processed_data_file"

# Run model_training.py
echo "Starting model training..."
python src/model_training.py --input_file="$processed_data_file" --model_file="$model_file"

# Run model_prediction.py
echo "Starting prediction..."
python src/model_prediction.py --input_file="$test_data_file" --model_file="$model_file" --output_file="$predictions_file"

echo "Pipeline completed."
