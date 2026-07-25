from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SILVER_PATH = PROJECT_ROOT / "data" / "silver"

def save_to_silver(df,table_name):
    """
    Save a cleaned DataFrame -> Silver 
    """
    # Create the Silver folder if it doesn't exist
    # parents=True: create missing parent directories.
    # exist_ok=True: don't raise an error if the folder already exists.
    SILVER_PATH.mkdir(parents=True , exist_ok=True)
    file_path = SILVER_PATH / f"{table_name}.csv"
    df.to_csv(file_path, index=False)
    print(f"{table_name} : Saved")
    
    
