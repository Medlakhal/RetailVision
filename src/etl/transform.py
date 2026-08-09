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
    Return the number of duplicated values for a business simple or composite key.
    """

    return df.duplicated(subset=key).sum()

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
        "Columns": len(data.columns),
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

import unicodedata


def normalize_text_columns(data, columns):
    """
    Standardize selected text columns.

    Transformations:
    1. Remove leading and trailing spaces.
    2. Convert text to lowercase.
    3. Remove accents.
    """

    cleaned_data = data.copy()

    for column in columns:
        cleaned_data[column] = (
            cleaned_data[column]
            .str.strip()
            .str.lower()
            .apply(
                lambda value: "".join(
                    char for char in unicodedata.normalize("NFKD", value)
                    if not unicodedata.combining(char)
                )
                if isinstance(value, str)
                else value
            )
        )

    return cleaned_data


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

def clean_products(data):
    """
    Clean the products dataset according to business rules.
    Business Rule:
    Products with a missing category are assigned to 'unknown'
    to preserve them for BI analysis.
    """

    cleaned_data = data.copy()
    cleaned_data["product_category_name"] = cleaned_data["product_category_name"].fillna("unknown")

    return cleaned_data

def clean_order_payments(data):
    """
    Clean the order payments dataset according to business rules.

    Business Rule:
    A payment with a positive value cannot have 0 installments.
    In this case, it is considered a single-payment transaction.
    """

    cleaned_data = data.copy()

    condition = (
        (cleaned_data["payment_installments"] == 0)
        & (cleaned_data["payment_value"] > 0)
    )

    cleaned_data.loc[condition, "payment_installments"] = 1
    return cleaned_data

def clean_order_reviews(data):
    """
    Clean the order reviews dataset according to business rules.

    Business Rules:
    1. Missing review titles are replaced with "No title".
    2. Missing review messages are replaced with "No comment".
    """
    cleaned_data = data.copy()

    cleaned_data["review_comment_title"] = cleaned_data["review_comment_title"].fillna("No title")
    cleaned_data["review_comment_message"] = cleaned_data["review_comment_message"].fillna("No comment")
    return cleaned_data

def clean_geolocation(data):
    """
    Clean the geolocation dataset according to business rules.

    Business Rule:
    Geolocation records with missing latitude or longitude are removed.
    """

    # Pas besoin de copy() : drop_duplicates() retourne un nouveau DataFrame 
    # On ne modifie pas directement data
    cleaned_data = data.drop_duplicates()
    return cleaned_data
    