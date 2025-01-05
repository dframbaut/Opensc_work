import os
import pandas as pd
from data_contract import compare_columns
from datetime import datetime

# Function to read CSV files
def read_csv_file(file_path):
    try:
        df = pd.read_csv(file_path, sep='|')
        if df.empty and df.columns.size == 0:
            return 'empty'
        return df
    except pd.errors.EmptyDataError:
        return 'empty'
    except Exception as e:
        print(f'Could not process file {file_path}: {e}')
        return None

# Function to read xlsx files
def read_excel_file(file_path):
    try:
        df = pd.read_excel(file_path)
        if df.empty and df.columns.size == 0:
            return 'empty'
        return df
    except pd.errors.EmptyDataError:
        return 'empty'
    except Exception as e:
        print(f'Could not process file {file_path}: {e}')
        return None


# Function to list folders
def list_folders(parent_path):
    folders = sorted([name for name in os.listdir(parent_path) if os.path.isdir(os.path.join(parent_path, name))], reverse=True)
    if not folders:
        print("No folders found in the specified path.")
        return []
    print("\nFound folders:")
    for i, folder in enumerate(folders, 1):
        print(f"{i}. {folder}")
    return folders

# Function to select a folder
def select_folder(parent_path, selection, folders):
    # If the selection is a number
    if selection.isdigit():
        index = int(selection) - 1
        if 0 <= index < len(folders):
            return os.path.join(parent_path, folders[index])
        else:
            print("Invalid selection.")
            exit()
    # If the selection is a folder name
    elif selection in folders:
        return os.path.join(parent_path, selection)
    else:
        print("Invalid selection.")
        exit()

# Function to retrieve file records in order (with two columns)
def get_records_data(folder_path, prefixes):
    current_date = datetime.now().strftime('%y%m%d')
    records_data = []

    for prefix in prefixes:
        subfolder_path = os.path.join(folder_path, prefix)
        if not os.path.isdir(subfolder_path):
            records_data.append(['subfolder missing', prefix])
            continue

        xlsx_files = sorted([
            file for file in os.listdir(subfolder_path) 
            if file.endswith('.xlsx') and current_date in file
        ])

        for file in xlsx_files:
            full_path = os.path.join(subfolder_path, file)
            df = read_excel_file(full_path)

            if df is not None:
                if isinstance(df, str) and df == 'empty':
                    records_data.append(['empty file', os.path.join(prefix, file)])
                else:
                    num_records = len(df)
                    records_data.append([num_records, os.path.join(prefix, file)])
            else:
                records_data.append(['error reading file', os.path.join(prefix, file)])
    return records_data

# Function to retrieve files with column mismatches, returning a matrix with three columns
def compare_columns(file_name, expected_columns, actual_columns):
    return set(expected_columns) == set(actual_columns)

def get_mismatch_files(folder_path, expected_columns, prefixes):
    current_date = datetime.now().strftime('%y%m%d')
    mismatch_files = []

    for prefix in prefixes:
        subfolder_path = os.path.join(folder_path, prefix)
        if not os.path.isdir(subfolder_path):
            mismatch_files.append([f'{prefix}/', 'subfolder missing', []])
            continue

        xlsx_files = sorted([
            file for file in os.listdir(subfolder_path) 
            if file.endswith('.xlsx') and current_date in file
        ])

        for file in xlsx_files:
            if file.startswith(prefix):
                full_path = os.path.join(subfolder_path, file)
                df = read_excel_file(full_path)

                if df is not None and isinstance(df, pd.DataFrame):
                    actual_columns = df.columns.tolist()
                    table_name = file.split('-')[1] if '-' in file else None

                    if table_name and table_name in expected_columns:
                        expected_cols = expected_columns[table_name]
                        columns_match = compare_columns(file, expected_cols, actual_columns)

                        if not columns_match:
                            mismatch_files.append([os.path.join(prefix, file), expected_cols, actual_columns])
                else:
                    mismatch_files.append([os.path.join(prefix, file), 'error reading file', []])

    return mismatch_files


# Function to retrieve valid files (with at least one record)
def get_valid_files(folder_path, prefixes):
    current_date = datetime.now().strftime('%y%m%d')
    valid_files = []
    for prefix in prefixes:
        subfolder_path = os.path.join(folder_path, prefix)
        if not os.path.isdir(subfolder_path):
            valid_files.append((f'{prefix}/', 'subfolder missing'))
            continue

        xlsx_files = sorted([
            file for file in os.listdir(subfolder_path)
            if file.endswith('.xlsx') and current_date in file
        ])

        for file in xlsx_files:
            full_path = os.path.join(subfolder_path, file)
            df = read_excel_file(full_path)
            if isinstance(df, pd.DataFrame) and len(df) > 0:
                valid_files.append((os.path.join(prefix, file), df))
    return valid_files

# Function to check for missing expected files using prefixes and suffixes
def check_expected_files(folder_path, expected_files, prefixes):
    current_date = datetime.now().strftime('%y%m%d')
    missing_files = []
    if len(prefixes) != len(expected_files):
        raise ValueError("La cantidad de 'prefixes' y 'expected_files' debe ser igual.")

    for count, prefix in enumerate(prefixes):
        subfolder_path = os.path.join(folder_path, prefix)
    
        if not os.path.isdir(subfolder_path):
            print(f"La subcarpeta '{prefix}' no existe. Se marcarán los archivos como faltantes.")
            missing_files.append(f"{prefix}/{expected_files[count]}_{current_date}.xlsx")
            continue

        existing_files = [file for file in os.listdir(subfolder_path) if file.endswith('.xlsx')]
        expected_pattern = f"{expected_files[count]}_{current_date}"
        if not any(expected_pattern in file for file in existing_files):
            missing_files.append(f"{prefix}/{expected_files[count]}_{current_date}.xlsx")

    return missing_files