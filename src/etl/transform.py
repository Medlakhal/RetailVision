import pandas as pd

# DATA QUALITY CHECKS
# Valeurs manquantes
def check_missing_value(data):
    """
    Return the number of missing values for each column.
    """ 
    return data.isnull().sum()


# Doublons techniques
def check_duplicates_rows(df):
    """
    Return the number of duplicate rows.
    """
    return df.duplicated().sum() 

## Doublons métier
def check_duplicates_keys(df,key):
    """
    Return the number of duplicated values for a business key.
    """

    return df[key].duplicated().sum()

#Vérifier les types de données
def check_data_types(df):
    """
    Return the data type of each column.
    """
    return df.dtypes

#Fonction general : DATA QUALITY REPORT

def data_quality_report(data, primary_key):
    """
    Generate a basic data quality report for a table.
    """
    missing_count = check_missing_value(data).sum()

    duplicate_keys = None

    if primary_key is not None:
        duplicate_keys = check_duplicates_keys(data, primary_key)

    report = {
        "Rows": len(data),
        "Columns": len(data),
        "Missing Values Count": missing_count,
        "Duplicate Rows": check_duplicates_rows(data),
        "Duplicate Keys": duplicate_keys
    }
    return report

# DATA TRANSFORMATION
# Conversion des dates
def convert_datetime_columns(df,columns):
    """
    Convert specified columns to datetime.
    """
    for col in columns:
        df[col]=pd.to_datetime(df[col], errors='coerce')
    
    return df

# Nettoyer Les ordres
def clean_orders(data):
    """
    Clean the orders dataset according to business rules.

    Business Rules:
    1. A delivered order must have a customer delivery date.
    2. A delivered order must have a carrier delivery date.
    3. A delivered order must have an approval date.
    """
    invalid_orders = (( data["order_status"] == "delivered") & ( data["order_delivered_customer_date"].isna()
                                                               | data["order_delivered_carrier_date"].isna()
                                                               | data["order_approved_at"].isna() ) )

    cleaned_data = data.loc[~invalid_orders]

    return cleaned_data

