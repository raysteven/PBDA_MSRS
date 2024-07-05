import pandas as pd
import gzip
from io import StringIO

def loadDF(file_path, sheet_name=None, file_type='xlsx'):
    try:
        if file_type == 'xlsx':
            if sheet_name:
                db_file_df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
            else:
                db_file_df = pd.read_excel(file_path)
        elif file_type == 'xls':
            if sheet_name:
                db_file_df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd')
            else:
                db_file_df = pd.read_excel(file_path)                
        elif file_type == 'csv':
            db_file_df = pd.read_csv(file_path)
        elif file_type == 'txt':
            db_file_df = pd.read_csv(file_path, sep = '\t')
        else:
            raise ValueError("Unsupported file type. Please use 'xlsx', 'xls', 'csv', or 'txt'")

        return db_file_df
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def save_to_excel(file_name, dfs):
    """
    Saves multiple DataFrames to an Excel file, each in a separate sheet.

    :param file_name: The name of the Excel file.
    :param dfs: A dictionary where keys are sheet names and values are DataFrames.
    """
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name)

def loadAB(file_path):

    # Define a function to find the starting string
    def find_start(line):
        return '[Data]' in line

    # Find the line number where the starting string is located
    with open(file_path, 'r') as file:
        line_number = next((i for i, line in enumerate(file, 1) if find_start(line)), None)

    # Read the text file into a pandas DataFrame, skipping rows until the starting string is found
    AB_file_df = pd.read_csv(file_path, skiprows=range(0, line_number), skipfooter=0, engine='python', index_col=0 ,delimiter='\t')

    # Remove columns without a name and all NaN values
    AB_file_df = AB_file_df.dropna(axis=1, how='all')# Display the DataFrame
    print(AB_file_df.shape)
 
    return AB_file_df

def loadVCF(file_path):
    # Check if the file is gzipped
    if file_path.endswith('.gz'):
        # Open the gzipped file
        with gzip.open(file_path, 'rt') as f:
            lines = [line for line in f if not line.startswith('##')]
    else:
        # Open a regular .vcf file
        with open(file_path, 'r') as f:
            lines = [line for line in f if not line.startswith('##')]
    
    # Use pandas to read the lines into a DataFrame
    return pd.read_csv(
        StringIO(''.join(lines)),
        sep='\t'
    )

def sheet_name_list(file_path):
    ExcelFile = pd.ExcelFile(file_path)
    sheet_names = ExcelFile.sheet_names
    return sheet_names

if __name__ == "__main__":
    pass