
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.database.connection import get_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SILVER_PATH = PROJECT_ROOT / "data" / "silver"


def build_dim_date(orders: pd.DataFrame) -> pd.DataFrame:
    """Build the date dimension from order purchase timestamps."""

    dates = pd.to_datetime(
        orders["order_purchase_timestamp"],
        errors="coerce",
    ).dropna()

    unique_dates = dates.dt.normalize().drop_duplicates().sort_values()

    dim_date = pd.DataFrame({"full_date": unique_dates})

    dim_date["date_key"] = (
        dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    )
    dim_date["day"] = dim_date["full_date"].dt.day
    dim_date["day_name"] = dim_date["full_date"].dt.day_name()
    dim_date["week"] = (
        dim_date["full_date"].dt.isocalendar().week.astype(int)
    )
    dim_date["month"] = dim_date["full_date"].dt.month
    dim_date["month_name"] = dim_date["full_date"].dt.month_name()
    dim_date["quarter"] = dim_date["full_date"].dt.quarter
    dim_date["year"] = dim_date["full_date"].dt.year
    dim_date["is_weekend"] = dim_date["full_date"].dt.dayofweek >= 5

    return dim_date[
        [
            "date_key",
            "full_date",
            "day",
            "day_name",
            "week",
            "month",
            "month_name",
            "quarter",
            "year",
            "is_weekend",
        ]
    ]


def build_dim_client(customers: pd.DataFrame) -> pd.DataFrame:
    """Build the customer dimension from the Silver dataset."""

    dim_client = customers[
        ["customer_id", "customer_unique_id"]
    ].copy()

    dim_client = dim_client.drop_duplicates(subset=["customer_id"])

    dim_client.insert(
        0,
        "customer_key",
        range(1, len(dim_client) + 1),
    )

    return dim_client



def build_dim_produit(products: pd.DataFrame) -> pd.DataFrame:
    """Build the product dimension from the Silver dataset."""

    column_mapping = {
        "product_name_lenght": "product_name_length",
        "product_description_lenght": "product_description_length",
    }

    dim_produit = products.rename(columns=column_mapping).copy()

    dim_produit.insert(
        0,
        "product_key",
        range(1, len(dim_produit) + 1),
    )

    return dim_produit[
        [
            "product_key",
            "product_id",
            "product_category_name",
            "product_name_length",
            "product_description_length",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ]
    ]


def build_dim_vendeur(sellers: pd.DataFrame) -> pd.DataFrame:
    """Build the seller dimension from the Silver dataset."""

    dim_vendeur = sellers[["seller_id"]].copy()
    dim_vendeur = dim_vendeur.drop_duplicates(subset=["seller_id"])

    dim_vendeur.insert(
        0,
        "seller_key",
        range(1, len(dim_vendeur) + 1),
    )

    return dim_vendeur


def build_dim_geography(geolocation: pd.DataFrame) -> pd.DataFrame:
    """Build the geography dimension from the Silver geolocation dataset."""

    dim_geography = (
        geolocation
        .groupby(
            [
                "geolocation_zip_code_prefix",
                "geolocation_city",
                "geolocation_state",
            ],
            as_index=False,
            dropna=False,
        )
        .agg(
            latitude=("geolocation_lat", "mean"),
            longitude=("geolocation_lng", "mean"),
        )
        .rename(
            columns={
                "geolocation_zip_code_prefix": "zip_code_prefix",
                "geolocation_city": "city",
                "geolocation_state": "state",
            }
        )
    )

    dim_geography.insert(
        0,
        "geography_key",
        range(1, len(dim_geography) + 1),
    )

    # Region will be populated separately if a reliable mapping exists.
    dim_geography["region"] = None

    return dim_geography[
        [
            "geography_key",
            "zip_code_prefix",
            "city",
            "state",
            "region",
            "latitude",
            "longitude",
        ]
    ]


def load_dimension(
    table_name: str,
    data: pd.DataFrame,
) -> None:
    """Replace the contents of a dimension table in PostgreSQL."""

    engine = get_engine()

    try:
        with engine.begin() as connection:
            connection.execute(text("SET search_path TO retailvision"))
            connection.execute(text(f"DELETE FROM {table_name}"))

            data.to_sql(
                table_name,
                con=connection,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=1000,
            )
    finally:
        engine.dispose()


def main() -> None:
    # Load Silver data
    orders_path = SILVER_PATH / "olist_orders_dataset.csv"
    customers_path = SILVER_PATH / "olist_customers_dataset.csv"
    products_path = SILVER_PATH / "olist_products_dataset.csv"
    sellers_path = SILVER_PATH / "olist_sellers_dataset.csv"
    geolocation_path = SILVER_PATH / "olist_geolocation_dataset.csv"

    orders = pd.read_csv(orders_path)
    customers = pd.read_csv(customers_path)
    products = pd.read_csv(products_path)
    sellers = pd.read_csv(sellers_path)
    geolocation = pd.read_csv(geolocation_path)

    # Build dimensions
    dim_date = build_dim_date(orders)
    dim_client = build_dim_client(customers)
    dim_produit = build_dim_produit(products)
    dim_vendeur = build_dim_vendeur(sellers)
    dim_geography = build_dim_geography(geolocation)

    # Load dimensions into PostgreSQL
    load_dimension("dim_date", dim_date)
    print(f"Dimension date chargée : {len(dim_date)} lignes.")

    load_dimension("dim_client", dim_client)
    print(f"Dimension client chargée : {len(dim_client)} lignes.")

    load_dimension("dim_produit", dim_produit)
    print(f"Dimension produit chargée : {len(dim_produit)} lignes.")

    load_dimension("dim_vendeur", dim_vendeur)
    print(f"Dimension vendeur chargée : {len(dim_vendeur)} lignes.")

    load_dimension("dim_geography", dim_geography)
    print(f"Dimension géographie chargée : {len(dim_geography)} lignes.")


if __name__ == "__main__":
    main()
