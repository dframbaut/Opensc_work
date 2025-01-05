# data_contract.py
import json

def load_table_definitions(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)
    return data

def extract_expected_columns(json_data):
    tables_columns = {}
    # Extract the datasets from the JSON body
    datasets = json_data.get('body', {}).get('datasets', [])
    
    for dataset in datasets:
        # Iterate through each table in the dataset
        for table in dataset.get('tables', []):
            table_name = table.get('name')
            # Extract the column names for the current table
            columns = [col.get('name') for col in table.get('columns', [])]
            tables_columns[table_name] = columns
    return tables_columns

def compare_columns(file_name, expected_columns, actual_columns):
    # Compare sets of expected and actual columns
    if set(expected_columns) == set(actual_columns):
        return True
    else:
        return False