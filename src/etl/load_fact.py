from pathlib import Path
import sys
import pandas as pd

# Racine du projet : C:\RetailVision
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Permet à Python de trouver le package src,
# même si le fichier est exécuté directement dans VS Code.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import get_engine
from src.etl.transform import normalize_text_columns
from sqlalchemy import text



PROJECT_ROOT = Path(__file__).resolve().parents[2]
SILVER_PATH = PROJECT_ROOT / "data" / "silver"


def read_silver(filename: str) -> pd.DataFrame:
    """Read a dataset from the Silver layer."""
    return pd.read_csv(SILVER_PATH / filename)


def load_fact() -> None:
    """Build and load the sales fact table."""

    # 1. Read Silver datasets
    orders = read_silver("olist_orders_dataset.csv")
    items = read_silver("olist_order_items_dataset.csv")
    customers = read_silver("olist_customers_dataset.csv")
    sellers = read_silver("olist_sellers_dataset.csv")

    # 2. Standardize identifiers
    for dataframe, columns in [
        (orders, ["order_id", "customer_id"]),
        (items, ["order_id", "product_id", "seller_id"]),
        (customers, ["customer_id"]),
        (sellers, ["seller_id"]),
    ]:
        for column in columns:
            dataframe[column] = (
                dataframe[column].astype("string").str.strip()
            )

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"],
        errors="coerce",
    )

    # 3. Join order items with orders
    fact = items.merge(
        orders[
            [
                "order_id",
                "customer_id",
                "order_status",
                "order_purchase_timestamp",
            ]
        ],
        on="order_id",
        how="inner",
        validate="many_to_one",
    )

    print(f"Items in Silver: {len(items):,}")
    print(f"Items matched to orders: {len(fact):,}")
    print(f"Items without a matching order: {len(items) - len(fact):,}")

    # 4. Attach customer and seller information
    fact = fact.merge(
        customers[
            [
                "customer_id",
                "customer_zip_code_prefix",
                "customer_city",
                "customer_state",
            ]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    fact = fact.merge(
        sellers[
            [
                "seller_id",
                "seller_zip_code_prefix",
                "seller_city",
                "seller_state",
            ]
        ],
        on="seller_id",
        how="left",
        validate="many_to_one",
    )

    # 5. Normalize geographic text
    fact = normalize_text_columns(
        fact,
        [
            "customer_city",
            "customer_state",
            "seller_city",
            "seller_state",
        ],
    )

    # 6. Load dimension lookups from PostgreSQL
    engine = get_engine()

    try:
        with engine.begin() as connection:

            dim_date = pd.read_sql(
                text("""
                    SELECT date_key, full_date
                    FROM retailvision.dim_date
                """),
                connection,
            )

            dim_client = pd.read_sql(
                text("""
                    SELECT customer_key, customer_id
                    FROM retailvision.dim_client
                """),
                connection,
            )

            dim_product = pd.read_sql(
                text("""
                    SELECT product_key, product_id
                    FROM retailvision.dim_produit
                """),
                connection,
            )

            dim_seller = pd.read_sql(
                text("""
                    SELECT seller_key, seller_id
                    FROM retailvision.dim_vendeur
                """),
                connection,
            )

            dim_geo = pd.read_sql(
                text("""
                    SELECT geography_key, zip_code_prefix, city, state
                    FROM retailvision.dim_geography
                """),
                connection,
            )

            # 7. Resolve date, customer, product and seller keys
            fact["full_date"] = (
                fact["order_purchase_timestamp"].dt.normalize()
            )
            dim_date["full_date"] = pd.to_datetime(
                dim_date["full_date"]
            )

            fact = fact.merge(
                dim_date,
                on="full_date",
                how="left",
                validate="many_to_one",
            )

            fact = fact.merge(
                dim_client,
                on="customer_id",
                how="left",
                validate="many_to_one",
            )

            fact = fact.merge(
                dim_product,
                on="product_id",
                how="left",
                validate="many_to_one",
            )

            fact = fact.merge(
                dim_seller,
                on="seller_id",
                how="left",
                validate="many_to_one",
            )

            # 8. Normalize geography dimension
            dim_geo = normalize_text_columns(
                dim_geo,
                ["city", "state"],
            )

            fact["customer_zip_code_prefix"] = pd.to_numeric(
                fact["customer_zip_code_prefix"],
                errors="coerce",
            ).astype("Int64")

            fact["seller_zip_code_prefix"] = pd.to_numeric(
                fact["seller_zip_code_prefix"],
                errors="coerce",
            ).astype("Int64")

            dim_geo["zip_code_prefix"] = pd.to_numeric(
                dim_geo["zip_code_prefix"],
                errors="coerce",
            ).astype("Int64")

            # 9. Create Unknown geography member if needed
            unknown_rows = dim_geo[
                dim_geo["zip_code_prefix"].eq(-1)
            ]

            if unknown_rows.empty:
                unknown_key = int(dim_geo["geography_key"].max()) + 1

                connection.execute(
                    text("""
                        INSERT INTO retailvision.dim_geography (
                            geography_key,
                            zip_code_prefix,
                            city,
                            state,
                            region,
                            latitude,
                            longitude
                        )
                        VALUES (
                            :key,
                            -1,
                            'Unknown',
                            'Unknown',
                            'Unknown',
                            NULL,
                            NULL
                        )
                    """),
                    {"key": unknown_key},
                )

                unknown_member = pd.DataFrame(
                    [{
                        "geography_key": unknown_key,
                        "zip_code_prefix": -1,
                        "city": "unknown",
                        "state": "unknown",
                    }]
                )

                dim_geo = pd.concat(
                    [dim_geo, unknown_member],
                    ignore_index=True,
                )
            else:
                unknown_key = int(
                    unknown_rows.iloc[0]["geography_key"]
                )

            # 10. Build deterministic geography lookups
            # Multiple source rows can share the same ZIP/city/state.
            # Sort by key and retain the smallest key for each combination.
            dim_geo = dim_geo.sort_values("geography_key")

            customer_geo = dim_geo.rename(
                columns={
                    "geography_key": "customer_geo_key",
                    "zip_code_prefix": "customer_zip_code_prefix",
                    "city": "customer_city",
                    "state": "customer_state",
                }
            )[
                [
                    "customer_geo_key",
                    "customer_zip_code_prefix",
                    "customer_city",
                    "customer_state",
                ]
            ].drop_duplicates(
                subset=[
                    "customer_zip_code_prefix",
                    "customer_city",
                    "customer_state",
                ],
                keep="first",
            )

            seller_geo = dim_geo.rename(
                columns={
                    "geography_key": "seller_geo_key",
                    "zip_code_prefix": "seller_zip_code_prefix",
                    "city": "seller_city",
                    "state": "seller_state",
                }
            )[
                [
                    "seller_geo_key",
                    "seller_zip_code_prefix",
                    "seller_city",
                    "seller_state",
                ]
            ].drop_duplicates(
                subset=[
                    "seller_zip_code_prefix",
                    "seller_city",
                    "seller_state",
                ],
                keep="first",
            )

            # Exact geography match: ZIP + normalized city + state
            fact = fact.merge(
                customer_geo,
                on=[
                    "customer_zip_code_prefix",
                    "customer_city",
                    "customer_state",
                ],
                how="left",
                validate="many_to_one",
            )

            fact = fact.merge(
                seller_geo,
                on=[
                    "seller_zip_code_prefix",
                    "seller_city",
                    "seller_state",
                ],
                how="left",
                validate="many_to_one",
            )

            # Keep unresolved geography without dropping sales
            fact["customer_geo_key"] = (
                fact["customer_geo_key"].fillna(unknown_key)
            )

            fact["seller_geo_key"] = (
                fact["seller_geo_key"].fillna(unknown_key)
            )

            # 11. Calculate measures
            fact["price"] = pd.to_numeric(
                fact["price"],
                errors="coerce",
            )
            fact["freight_value"] = pd.to_numeric(
                fact["freight_value"],
                errors="coerce",
            )

            # Project definition: item price + freight
            fact["sales_amount"] = (
                fact["price"] + fact["freight_value"]
            )

            # 12. Validate mandatory values
            required_columns = [
                "date_key",
                "customer_key",
                "product_key",
                "seller_key",
                "order_id",
                "order_item_id",
                "order_status",
                "price",
                "freight_value",
                "sales_amount",
            ]

            missing = fact[required_columns].isna().sum()
            missing = missing[missing > 0]

            if not missing.empty:
                raise ValueError(
                    "Missing mandatory values; no fact rows loaded:\n"
                    f"{missing.to_string()}"
                )

            fact_to_load = fact[
                [
                    "date_key",
                    "customer_key",
                    "product_key",
                    "seller_key",
                    "customer_geo_key",
                    "seller_geo_key",
                    "order_id",
                    "order_item_id",
                    "order_status",
                    "price",
                    "freight_value",
                    "sales_amount",
                ]
            ].copy()

            # Validate business key
            if fact_to_load.duplicated(
                subset=["order_id", "order_item_id"]
            ).any():
                raise ValueError(
                    "Duplicate business key: order_id + order_item_id."
                )

            integer_columns = [
                "date_key",
                "customer_key",
                "product_key",
                "seller_key",
                "customer_geo_key",
                "seller_geo_key",
                "order_item_id",
            ]

            for column in integer_columns:
                fact_to_load[column] = (
                    fact_to_load[column].astype(int)
                )

            # 13. Replace fact table contents in the transaction
            connection.execute(
                text("DELETE FROM retailvision.fact_ventes")
            )

            fact_to_load.to_sql(
                "fact_ventes",
                con=connection,
                schema="retailvision",
                if_exists="append",
                index=False,
                method="multi",
                chunksize=1000,
            )

            print("\nFact table loaded successfully.")
            print(f"Rows loaded: {len(fact_to_load):,}")
            print(
                "Sales amount (price + freight): "
                f"{fact_to_load['sales_amount'].sum():,.2f}"
            )
            print(
                "Unknown customer geographies: "
                f"{(fact_to_load['customer_geo_key'] == unknown_key).sum():,}"
            )
            print(
                "Unknown seller geographies: "
                f"{(fact_to_load['seller_geo_key'] == unknown_key).sum():,}"
            )

    finally:
        engine.dispose()


if __name__ == "__main__":
    load_fact()
