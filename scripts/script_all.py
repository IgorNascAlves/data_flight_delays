import os
import zipfile
import shutil
import pandas as pd
from tqdm import tqdm


def unzip_all_files(folder_path, output_folder):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith('.zip'):
            folder_name = os.path.splitext(filename)[0]
            extract_folder = os.path.join(output_folder, folder_name)
            os.makedirs(extract_folder, exist_ok=True)

            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)

            print(f"Unzipped {filename} to {extract_folder}")


def rename_and_move_files_in_directory(directory, new_path):
    # Get a list of all subdirectories in the directory
    subdirectories = [subdir for subdir in os.listdir(directory) if os.path.isdir(os.path.join(directory, subdir))]

    for subdir in subdirectories:
        subdir_path = os.path.join(directory, subdir)
        rename_and_move_files(subdir_path, new_path)


def rename_and_move_files(directory, new_path):
    # Create the new folder if it doesn't exist
    os.makedirs(new_path, exist_ok=True)

    # Get a list of all files in the directory
    files = os.listdir(directory)

    for filename in files:
        filepath = os.path.join(directory, filename)

        # Check if the current item is a file
        if os.path.isfile(filepath):
            # Get the current file extension
            file_extension = os.path.splitext(filename)[1]

            # Concatenate folder name and current file name
            new_filename = os.path.basename(directory) + '_' + filename

            # Create the new file path with the renamed file
            new_filepath = os.path.join(new_path, new_filename)

            # Copy the file to the new path with the renamed file
            shutil.copy(filepath, new_filepath)
            print(f"Copied {filename} to {new_filepath}")


def concat_csv_files(directory):
    # Get a list of all CSV files in the directory
    files = [file for file in os.listdir(directory) if file.endswith('.csv')]

    # Initialize an empty DataFrame to store the concatenated data
    concatenated_data = pd.DataFrame()

    # Concatenate the CSV files
    for i, file in enumerate(files):
        filepath = os.path.join(directory, file)
        data = pd.read_csv(filepath)
        concatenated_data = pd.concat([concatenated_data, data], ignore_index=True)
        print(f"Concatenating file {i + 1}/{len(files)}: {file}")

    return concatenated_data


def analyze_concatenated_data(concatenated_data):
    # Print the number of rows and columns
    num_rows, num_cols = concatenated_data.shape
    print(f"Number of rows: {num_rows}")
    print(f"Number of columns: {num_cols}")

    # Print the column names
    column_names = concatenated_data.columns.tolist()
    print("Column names:")
    for column in column_names:
        print(column)

    # Analyze the FL_DATE column for the period of time
    fl_date = pd.to_datetime(concatenated_data['FL_DATE'], format='%m/%d/%Y %I:%M:%S %p')
    period_begin = fl_date.min().strftime('%Y-%m-%d')
    period_end = fl_date.max().strftime('%Y-%m-%d')
    print(f"\nPeriod of time:")
    print(f"Begin date: {period_begin}")
    print(f"End date: {period_end}")

    return concatenated_data


def csv_to_parquet(csv_file_path, parquet_file_path):
    # Read the CSV file with tqdm progress bar
    total_lines = sum(1 for _ in open(csv_file_path, 'r', encoding='utf-8'))
    with tqdm(total=total_lines, desc="Reading CSV") as pbar:
        data = pd.read_csv(csv_file_path)
        pbar.update(len(data))

    # Convert and save the DataFrame to Parquet format
    with tqdm(total=1, desc="Saving Parquet") as pbar:
        data.to_parquet(parquet_file_path)
        pbar.update(1)


def process_directory(directory):
    # Concatenate CSV files in the directory
    concatenated_data = concat_csv_files(directory)

    # Analyze the concatenated data
    analyze_concatenated_data(concatenated_data)

    # Convert concatenated data to Parquet
    parquet_file_path = os.path.join(directory, 'concatenated_data.parquet')
    with tqdm(total=1, desc="Saving Parquet") as pbar:
        concatenated_data.to_parquet(parquet_file_path)
        pbar.update(1)

    # Read the Parquet file
    data = pd.read_parquet(parquet_file_path)

    # Print the number of rows and columns
    num_rows, num_cols = data.shape
    print(f"Number of rows: {num_rows}")
    print(f"Number of columns: {num_cols}")

    # Print the column names
    column_names = data.columns.tolist()
    print("Column names:")
    print(column_names)

    # Analyze the FL_DATE column for the period of time
    fl_date = pd.to_datetime(data['FL_DATE'], format='%m/%d/%Y %I:%M:%S %p')
    period_begin = fl_date.min().strftime('%Y-%m-%d')
    period_end = fl_date.max().strftime('%Y-%m-%d')
    print(f"\nPeriod of time:")
    print(f"Begin date: {period_begin}")
    print(f"End date: {period_end}")


# Provide the folder path where the zip files are located
folder_path = r'C:\Users\Igor\Desktop\dados\zip_files'

# Provide the output folder path where the unzipped files will be saved
unzip_output_folder = r'C:\Users\Igor\Desktop\dados\data\output_folder'

# Unzip all files in the folder
unzip_all_files(folder_path, unzip_output_folder)

# Provide the directory path where the unzipped files are located
directory_path = r'C:\Users\Igor\Desktop\dados\data\output_folder'

# Provide the new path for the renamed files
rename_output_folder = r'C:\Users\Igor\Desktop\dados\data\data_renamed'

# Rename and move files in the directory
rename_and_move_files_in_directory(directory_path, rename_output_folder)

# Provide the new path for the process the renamed files
rename_process_folder = r'C:\Users\Igor\Desktop\dados\data'

# Process the renamed files
process_directory(rename_process_folder)

