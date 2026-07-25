from pathlib import Path
import pandas as pd
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_PATH = PROJECT_ROOT / "data" / "bronze"

# Cette fonction charge automatiquement plusieurs fichiers (Données sources)
def extract_data():
 
    """
        EN :Load all CSV files from the Bronze layer.
        Returns a dictionary of DataFrames.

        FR:Charger tous les fichiers CSV présents dans la couche Bronze.
        Renvoie un dictionnaire contenant plusieurs DataFrames

        Ces Dataframes sont les table de sources key= nom de chaque table et value=Dataframe correspondant à cette table.
        les colonnes, les lignes, les types, les valeurs, les index etc... de chaque table
        """
    datasets={}
    for file in BRONZE_PATH.glob("*.csv"): #.glob :parcourt le dossier et retourne tous les fichiers CSV trouvés
        table_name = file.stem #stem : retourne le nom du fichier sans extension.
        datasets[table_name]=pd.read_csv(file) # Tu lis un CSV -> un DataFrame
    return datasets 
