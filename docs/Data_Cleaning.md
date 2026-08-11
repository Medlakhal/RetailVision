# Data Cleaning & Quality

This document records the data quality checks, cleaning rules, and standardization decisions applied during the Bronze-to-Silver transformation of RetailVision.

The objective is to improve data reliability while preserving valid business information. Transformations are based on the meaning and intended use of each dataset.

---

## 1. Data Quality Approach

For each dataset, the following checks were performed where relevant:

- Dataset dimensions and structure
- Data types
- Missing values
- Duplicate rows
- Primary and composite key uniqueness
- Business-rule consistency
- Text standardization
- Date/time conversion

The quality report was used to validate the result after the transformations.

---

## 2. Orders

### Quality Checks

The orders dataset was checked for:

- Missing values
- Duplicate rows
- Duplicate primary keys
- Data types
- Date columns

### Business Rule

A delivered order must have:

- an approval date;
- a carrier delivery date;
- a customer delivery date.

### Cleaning Rule

Orders that were marked as `delivered` but were missing one or more of these required dates were considered inconsistent and removed from the cleaned dataset.

---

## 3. Order Items

### Quality Checks

The order items dataset was checked using the composite key:

`order_id + order_item_id`

The checks showed:

- No missing values
- No duplicate rows
- No duplicate composite keys

### Standardization

`shipping_limit_date` was converted from text to a datetime type.

No additional cleaning was required after the quality checks.

---

## 4. Products

### Quality Checks

The products dataset was checked for:

- Missing values
- Duplicate rows
- Duplicate product identifiers
- Data types

Some product attributes such as dimensions and weight contain missing values.

### Decision

These missing values were not treated as critical for the current analytical objective because the product identifier and other relevant product information remain available.

The missing category values were also inspected separately.

No blind deletion of product records was performed based only on these optional attributes.

---

## 5. Order Payments

### Quality Checks

The payment dataset was checked for:

- Missing values
- Duplicate rows
- Duplicate keys
- Data types
- Payment value and installment consistency

### Business Validation

Records with:

`payment_installments = 0`

were investigated together with:

`payment_value`

The relationship between payment value and installments was analyzed before defining a cleaning rule.

The objective was to distinguish valid zero-value cases from inconsistent payment records rather than modifying values blindly.

---

## 6. Order Reviews

### Quality Checks

The review dataset was checked for:

- Missing values
- Duplicate rows
- Review identifiers
- Composite key consistency
- Date columns

The composite key used for validation was:

`review_id + order_id`

### Missing Text

Missing values were found mainly in:

- `review_comment_title`
- `review_comment_message`

This was considered logically valid because a customer can submit a rating without writing a title or comment.

### Cleaning Rule

Missing review titles were replaced with:

`No title`

Missing review messages were replaced with:

`No comment`

Review date columns were converted to datetime types.

---

## 7. Customers

### Quality Checks

The customer dataset was checked for:

- Missing values
- Duplicate rows
- Customer identifiers
- Data types
- Location-related fields

The customer location information was retained because customers may be associated with different geographic information according to the dataset structure.

No additional cleaning rule was applied when the quality checks showed no relevant inconsistency.

---

## 8. Sellers

### Quality Checks

The seller dataset was checked for:

- Missing values
- Duplicate rows
- Seller identifiers
- Data types
- Geographic fields

No additional cleaning rule was applied when the quality checks showed no relevant inconsistency.

---

## 9. Geolocation

### Quality Checks

The geolocation dataset contained a large number of exact duplicate rows.

The dataset was also inspected for text inconsistencies in city names, including differences in capitalization and accent representation.

### Cleaning Rule

Exact duplicate geographic records were removed using:

`geolocation_zip_code_prefix + geolocation_lat + geolocation_lng`

This avoids treating repeated identical geographic observations as separate records.

Text standardization was also applied to relevant text columns.

---

## 10. Product Category Translation

The translation dataset was checked for:

- Missing values
- Duplicate rows
- Data types
- Text consistency

Relevant text columns were standardized using the project's text normalization function.

No additional business-rule transformation was required after the quality checks.

---

## 11. Date and Text Standardization

### Dates

Relevant date columns were converted from string/object representations to datetime types.

This allows reliable:

- date filtering;
- date comparisons;
- time-based analysis;
- aggregation by day, month, or year.

### Text

Relevant text columns were standardized to improve consistency in categorical values.

This helps avoid treating variations in capitalization or formatting as different business values.

---

## 12. Validation After Cleaning

After applying the transformations, the datasets were rechecked using the project's data quality reporting function.

The validation focused on:

- Row count
- Column count
- Missing values
- Duplicate rows
- Duplicate keys

The Silver datasets were saved only after the quality checks and transformations were completed.

---

## Conclusion

The Bronze-to-Silver phase focused on making the source data reliable and consistent while preserving valid business information.

The cleaning process was based on data quality analysis and business rules rather than indiscriminate removal or replacement of values.

The resulting Silver layer provides the foundation for the next phase: Data Warehouse design and the Gold analytical layer.
