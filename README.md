<div align="center">

# 🛍️ RetailVision

**An end-to-end Data Engineering, Data Warehousing & Analytics portfolio project**  
Built with the Brazilian Olist e-commerce dataset

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458?style=flat-square&logo=pandas&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Data_Warehouse-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-Analytics-4479A1?style=flat-square&logo=mysql&logoColor=white)
![Status](https://img.shields.io/badge/Status-In_Progress-yellow?style=flat-square)

</div>

---

## 📌 Project Overview

**RetailVision** is a hands-on portfolio project that transforms raw e-commerce data into a structured data platform for business analysis. It follows a layered data-processing approach and uses a PostgreSQL dimensional model to support analytical SQL queries.

The project currently includes the Bronze/Silver data preparation work, a PostgreSQL data warehouse with dimensions and a sales fact table, and initial data-quality validation. Business KPI analysis is now in progress. Dashboards and machine-learning use cases are future phases, not completed deliverables.

## 💼 Business Problem

E-commerce platforms produce data about orders, customers, products, sellers, payments, reviews and delivery. Raw transactional files are not immediately suitable for reliable analysis.

RetailVision builds a structured foundation to investigate questions such as:

| # | Business question |
|---|---|
| 1 | How does sales revenue evolve over time? |
| 2 | Which products generate the most revenue? |
| 3 | Which sellers contribute most to sales? |
| 4 | How are sales distributed geographically? |
| 5 | How do order statuses and payment patterns affect business analysis? |
| 6 | How could historical data support future forecasting? |

**Goal:** build a maintainable data pipeline and dimensional model, then use SQL to produce business-oriented metrics.

## 🎯 Project Status

- [x] Organize source data into project layers
- [x] Develop Python/Pandas ETL and data-standardization utilities
- [x] Prepare Silver datasets and perform data-quality checks
- [x] Create PostgreSQL dimensional tables
- [x] Load the dimension tables
- [x] Load the `fact_ventes` fact table
- [x] Validate fact row count, key nulls and duplicate order-item keys
- [ ] Complete and document the business KPI SQL analysis
- [ ] Build a Gold/analytics layer if needed by the selected use cases
- [ ] Create dashboards (tool to be decided)
- [ ] Explore a well-defined machine-learning use case
- [ ] Add automated tests and improve pipeline orchestration

Status is updated as implementation progresses; checked items indicate work completed at the current project stage.

## 🗂️ Dataset

RetailVision uses the [Brazilian Olist E-commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), with source tables covering customers, orders, order items, products, sellers, payments, reviews, geolocation and product-category translations.

The project uses transformed dates in its current working dataset. Therefore, dates displayed by the current warehouse should not be interpreted as the original historical dates unless the transformation is reversed or explicitly accounted for.

## 🏗️ Architecture & Data Warehouse

The data preparation process is organized around the following layers:

| Layer | Purpose | Current status |
|---|---|---|
| **Bronze** | Preserve source/raw data | Prepared |
| **Silver** | Cleaned, standardized and validated datasets | Implemented |
| **Data Warehouse** | PostgreSQL dimensional model for analysis | Implemented; validation completed for the sales fact table |
| **Gold / analytics** | Business-ready aggregates or data products, if required | Not yet implemented as a separate layer |

The warehouse uses a dimensional model with dimensions such as `dim_date`, `dim_client`, `dim_produit`, `dim_vendeur` and `dim_geography`, plus the sales fact table `fact_ventes`. The schema also includes `dim_paiement`; payment analysis must respect its own grain and should not be joined directly to order-item facts in a way that duplicates sales rows.

### Fact table grain

`fact_ventes` is designed at **one row per order item and seller** (`order_id`, `order_item_id`). This grain matters: counting rows is not the same as counting orders, because one order may contain multiple items.

For the current project, `sales_amount` is defined as:

`price + freight_value`

This is the project's chosen sales amount metric, not a universal accounting definition of revenue.

### Current fact-table validation

The latest successful load reported:

| Check | Result |
|---|---:|
| Silver order-item rows | 112,650 |
| Items matched to orders and loaded | 112,626 |
| Items without a matching order | 24 |
| Duplicate `(order_id, order_item_id)` groups in the fact table | 0 |
| Null `date_key` values | 0 |
| Null `customer_key` values | 0 |
| Null `product_key` values | 0 |
| Null `seller_key` values | 0 |
| Sum of `sales_amount` | 15,840,025.74 |
| Customer geography keys mapped to the unknown member | 331 |
| Seller geography keys mapped to the unknown member | 2,535 |

The 24 unmatched item records are excluded by the inner join to orders and should remain documented as a data-quality exception. Unknown geography mappings are also a known limitation; they do not imply that the customer or seller dimension key itself is missing.

## 📈 Business Analysis & KPIs

The first monthly sales query has been executed. It calculates the number of distinct orders and the sum of `sales_amount` by year and month. Initial results show a peak monthly value of **1,179,008.94 in November 2025** in the transformed date timeline.

This is an initial descriptive result, not a conclusion about original calendar-year performance. Some displayed months have very few rows and may be partial periods. These months should not be compared directly with full months without checking date coverage.

The detailed validation notes and analysis plan are maintained in:

- [`docs/data_warehouse_validation.txt`](docs/data_warehouse_validation.txt)
- [`docs/business_analysis_guide.txt`](docs/business_analysis_guide.txt)

Planned/ongoing KPI work includes:
- Monthly sales amount and distinct order count
- Month-over-month change
- Top products by sales amount
- Seller performance
- Geographic distribution of sales
- Order-status analysis, with metric definitions stated explicitly

## 🛠️ Technologies

| Technology | Purpose | Status |
|---|---|---|
| Python | ETL and data processing | Used |
| Pandas | Tabular transformation and validation | Used |
| PostgreSQL | Dimensional data warehouse | Used |
| SQL | Data validation and business analysis | Used |
| Git / GitHub | Version control and portfolio | Used |
| Jupyter | Exploration and quality analysis | Used where applicable |
| BI dashboard tool | Visualization | Future phase; tool not yet finalized |
| Scikit-learn | Machine-learning use case | Future phase |

## 🗂️ Project Structure

The following is a simplified overview; keep it aligned with the actual repository as files evolve.

```text
RetailVision/
├── data/
│   ├── bronze/
│   ├── silver/
│   └── reference/
├── docs/
│   ├── data_warehouse_validation.txt
│   └── business_analysis_guide.txt
├── notebooks/
├── src/
│   ├── database/
│   │   └── connection.py
│   └── etl/
│       ├── extract.py
│       ├── transform.py
│       ├── load.py
│       ├── load_dimensions.py
│       └── load_fact.py
├── README.md
├── .gitignore
└── environment.yml
```

This tree is illustrative, not an exhaustive file listing. Preserve any additional existing files in the repository.

## ▶️ Running the fact loader

From the project root, the module command is:

```powershell
cd C:\RetailVision
& "C:\Users\simol\miniconda3\envs\retailvision\python.exe" c:/RetailVision/src/etl/load_fact.py
```

The loader was also configured to support direct execution from VS Code's **Run Python File** action by adding the project root to `sys.path`. Database credentials should remain in local environment/configuration files and must not be committed to GitHub.

## 🔍 Data quality notes

- The fact table has no duplicate `(order_id, order_item_id)` groups in the validation performed so far.
- The required date, customer, product and seller surrogate keys were not null in the validation query.
- 24 Silver order-item rows did not find a matching order and were excluded by the current inner join.
- Some customer and seller geography records map to the warehouse's unknown geography member. This is documented rather than silently treated as a precise location.
- The dataset dates have been transformed for this project; time-based interpretation must account for that transformation.
- Payment facts have a different grain from order-item sales facts. Joining payment rows directly to order items can inflate sales totals unless the grain is handled correctly.

## 🗺️ Roadmap

1. Finish data warehouse validation and document exceptions.
2. Develop and validate business KPIs with SQL.
3. Add repeatable tests for key assumptions and transformations.
4. Decide whether a separate Gold analytics layer is useful for the selected use cases.
5. Build a dashboard if it adds value to the portfolio.
6. Select and evaluate a clearly scoped machine-learning use case.

## 👨‍💻 Author

**Data Science & AI student**

RetailVision is a practical portfolio project to strengthen skills in Data Engineering, Python, SQL, ETL, dimensional modeling, data quality and business analytics.
