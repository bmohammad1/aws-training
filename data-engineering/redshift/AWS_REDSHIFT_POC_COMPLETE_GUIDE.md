# AWS Redshift POC: Complete Implementation Guide

## JSON to Parquet Data Loading with Duplicate Prevention

### **Project Overview**

This document outlines the complete implementation of an AWS Redshift Serverless POC that demonstrates:

- Data conversion from JSON to Parquet format
- S3 storage and organization
- Redshift data loading via COPY commands
- Primary Learning Objective: Understanding and preventing duplicate data loading

---

## **Phase 1: Local Development & Data Preparation**

### **1.1 Project Structure**

```
c:\Users\spasumarthi\Desktop\Data Engineering\
├── json_to_parquet.py          # Main conversion script
├── order_generator.py          # Sample data generator
├── sample_order.json          # Generated sample data
├── parquet_files/
│   ├── order_summary.parquet
│   ├── order_summary_fixed.parquet
│   ├── order_items.parquet
│   └── order_items_fixed.parquet
└── venv/                      # Python virtual environment
```

### **1.2 Data Generation & Conversion**

- **Generated**: Complex nested JSON order data using `order_generator.py`
- **Converted**: JSON to 3 Parquet formats using `json_to_parquet.py`
- **Fixed**: NULL value issues that caused Redshift schema conflicts

**Key Files Created:**

- `order_summary_fixed.parquet` (94 columns, 1 record)
- `order_items_fixed.parquet` (19 columns, 1 record)

---

## **Phase 2: AWS Infrastructure Setup**

### **2.1 S3 Bucket Configuration**

**Bucket Name**: `siddhartha-redshift-bucket`

**Folder Structure:**

```
s3://siddhartha-redshift-bucket/
├── orders/
│   ├── order_summary.parquet
│   └── order_summary_fixed.parquet
└── order-items/
    ├── order_items.parquet
    └── order_items_fixed.parquet
```

### **2.2 IAM Role Configuration**

**Role Name**: `MyRedshiftS3Role`
**AWS Account ID**: `[REDACTED]`

**IAM Policy**: Custom S3 Access Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": [
        "arn:aws:s3:::siddhartha-redshift-bucket/orders/*",
        "arn:aws:s3:::siddhartha-redshift-bucket/order-items/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": ["arn:aws:s3:::siddhartha-redshift-bucket"],
      "Condition": {
        "StringLike": {
          "s3:prefix": ["orders/*", "order-items/*"]
        }
      }
    }
  ]
}
```

**Full IAM Role ARN**: `arn:aws:iam::[AWS-ACCOUNT-ID]:role/MyRedshiftS3Role`

### **2.3 Redshift Serverless Setup**

**Namespace**: `order-analytics-namespace1`
**Workgroup**: `order-analytics-workgroup1`
**Database**: `dev`
**Admin User**: `admin`

---

## **Phase 3: Database Schema Creation**

### **3.1 Orders Table Creation**

**Challenge**: Schema mismatch between Parquet file structure and initial table definition.
**Solution**: Analyzed actual Parquet schema and created matching table structure.

```sql
CREATE TABLE orders (
    order_orderId VARCHAR(255),
    order_orderNumber VARCHAR(255),
    order_orderDate TIMESTAMPTZ,
    order_status VARCHAR(255),
    order_totalAmount DOUBLE PRECISION,
    order_currency VARCHAR(255),
    order_customer_customerId VARCHAR(255),
    order_customer_personalInfo_firstName VARCHAR(255),
    order_customer_personalInfo_lastName VARCHAR(255),
    order_customer_personalInfo_email VARCHAR(255),
    order_customer_personalInfo_phone VARCHAR(255),
    order_customer_addresses_billing_street VARCHAR(255),
    order_customer_addresses_billing_apartment VARCHAR(255),
    order_customer_addresses_billing_city VARCHAR(255),
    order_customer_addresses_billing_state VARCHAR(255),
    order_customer_addresses_billing_zipCode BIGINT,
    order_customer_addresses_billing_country VARCHAR(255),
    order_customer_addresses_shipping_street VARCHAR(255),
    order_customer_addresses_shipping_apartment VARCHAR(255),
    order_customer_addresses_shipping_city VARCHAR(255),
    order_customer_addresses_shipping_state VARCHAR(255),
    order_customer_addresses_shipping_zipCode BIGINT,
    order_customer_addresses_shipping_country VARCHAR(255),
    order_customer_preferences_emailNotifications BOOLEAN,
    order_customer_preferences_smsAlerts BOOLEAN,
    order_customer_preferences_loyaltyMember BOOLEAN,
    order_customer_preferences_loyaltyTier VARCHAR(255),
    order_payment_paymentId VARCHAR(255),
    order_payment_method VARCHAR(255),
    order_payment_status VARCHAR(255),
    order_payment_processedAt VARCHAR(255),
    order_payment_cardDetails_type VARCHAR(255),
    order_payment_cardDetails_lastFourDigits BIGINT,
    order_payment_cardDetails_expiryMonth BIGINT,
    order_payment_cardDetails_expiryYear BIGINT,
    order_payment_cardDetails_cardholderName VARCHAR(255),
    order_payment_cardDetails_billingAddress_street VARCHAR(255),
    order_payment_cardDetails_billingAddress_apartment VARCHAR(255),
    order_payment_cardDetails_billingAddress_city VARCHAR(255),
    order_payment_cardDetails_billingAddress_state VARCHAR(255),
    order_payment_cardDetails_billingAddress_zipCode BIGINT,
    order_payment_cardDetails_billingAddress_country VARCHAR(255),
    order_payment_transactionDetails_subtotal DOUBLE PRECISION,
    order_payment_transactionDetails_taxes_salesTax DOUBLE PRECISION,
    order_payment_transactionDetails_taxes_stateTax DOUBLE PRECISION,
    order_payment_transactionDetails_taxes_localTax DOUBLE PRECISION,
    order_payment_transactionDetails_taxes_totalTax DOUBLE PRECISION,
    order_payment_transactionDetails_shipping_method VARCHAR(255),
    order_payment_transactionDetails_shipping_cost DOUBLE PRECISION,
    order_payment_transactionDetails_shipping_estimatedDelivery VARCHAR(255),
    order_payment_transactionDetails_shipping_carrier VARCHAR(255),
    order_payment_transactionDetails_shipping_trackingNumber VARCHAR(255),
    order_payment_transactionDetails_fees_processingFee DOUBLE PRECISION,
    order_payment_transactionDetails_fees_handlingFee DOUBLE PRECISION,
    order_payment_transactionDetails_fees_totalFees DOUBLE PRECISION,
    order_payment_transactionDetails_discounts_itemDiscounts BIGINT,
    order_payment_transactionDetails_discounts_shippingDiscount BIGINT,
    order_payment_transactionDetails_discounts_promoCode VARCHAR(255),
    order_payment_transactionDetails_discounts_totalDiscounts BIGINT,
    order_payment_transactionDetails_finalTotal DOUBLE PRECISION,
    order_payment_receipt_receiptNumber VARCHAR(255),
    order_payment_receipt_downloadUrl VARCHAR(255),
    order_payment_receipt_emailSent BOOLEAN,
    order_payment_receipt_printRequested BOOLEAN,
    order_fulfillment_warehouseId VARCHAR(255),
    order_fulfillment_fulfillmentStatus VARCHAR(255),
    order_fulfillment_packaging_packageCount BIGINT,
    order_fulfillment_packaging_packages_0_packageId VARCHAR(255),
    order_fulfillment_packaging_packages_0_items_0 VARCHAR(255),
    order_fulfillment_packaging_packages_0_dimensions_length BIGINT,
    order_fulfillment_packaging_packages_0_dimensions_width BIGINT,
    order_fulfillment_packaging_packages_0_dimensions_height BIGINT,
    order_fulfillment_packaging_packages_0_dimensions_unit VARCHAR(255),
    order_fulfillment_packaging_packages_0_weight_value DOUBLE PRECISION,
    order_fulfillment_packaging_packages_0_weight_unit VARCHAR(255),
    order_fulfillment_shipping_shippedDate TIMESTAMPTZ,
    order_fulfillment_shipping_estimatedDelivery VARCHAR(255),
    order_fulfillment_shipping_carrier VARCHAR(255),
    order_fulfillment_shipping_service VARCHAR(255),
    order_fulfillment_shipping_tracking_trackingNumber VARCHAR(255),
    order_fulfillment_shipping_tracking_trackingUrl VARCHAR(255),
    order_fulfillment_shipping_tracking_lastUpdate TIMESTAMPTZ,
    order_fulfillment_shipping_tracking_currentStatus VARCHAR(255),
    order_metadata_source VARCHAR(255),
    order_metadata_deviceInfo_userAgent VARCHAR(255),
    order_metadata_deviceInfo_ipAddress VARCHAR(255),
    order_metadata_deviceInfo_sessionId VARCHAR(255),
    order_metadata_timestamps_created TIMESTAMPTZ,
    order_metadata_timestamps_updated TIMESTAMPTZ,
    order_metadata_timestamps_completed TIMESTAMPTZ,
    order_metadata_notes_customerNotes VARCHAR(255),
    order_metadata_notes_internalNotes VARCHAR(255),
    order_metadata_notes_specialInstructions VARCHAR(255),
    order_items_count BIGINT
);
```

### **3.2 Order Items Table Creation**

```sql
CREATE TABLE order_items (
    itemId VARCHAR(255),
    productInfo_sku VARCHAR(255),
    productInfo_name VARCHAR(255),
    productInfo_category VARCHAR(255),
    productInfo_subcategory VARCHAR(255),
    productInfo_brand VARCHAR(255),
    pricing_unitPrice DOUBLE PRECISION,
    pricing_quantity BIGINT,
    pricing_discount_type VARCHAR(255),
    pricing_discount_value BIGINT,
    pricing_discount_amount BIGINT,
    pricing_discount_reason VARCHAR(255),
    pricing_subtotal DOUBLE PRECISION,
    specifications_processor VARCHAR(255),
    specifications_memory VARCHAR(255),
    specifications_storage VARCHAR(255),
    specifications_display VARCHAR(255),
    order_id VARCHAR(255),
    order_date TIMESTAMPTZ
);
```

---

## **Phase 4: Data Loading & Duplicate Testing**

### **4.1 Initial Data Loading**

**Orders Table Load:**

```sql
COPY orders
FROM 's3://siddhartha-redshift-bucket/orders/order_summary_fixed.parquet'
IAM_ROLE 'arn:aws:iam::[AWS-ACCOUNT-ID]:role/MyRedshiftS3Role'
FORMAT AS PARQUET;
```

**Order Items Table Load:**

```sql
COPY order_items
FROM 's3://siddhartha-redshift-bucket/order-items/order_items_fixed.parquet'
IAM_ROLE 'arn:aws:iam::[AWS-ACCOUNT-ID]:role/MyRedshiftS3Role'
FORMAT AS PARQUET;
```

### **4.2 Duplicate Loading Demonstration**

**Objective**: Demonstrate what happens when the same file is loaded multiple times.

**Step 1: Check Initial Count**

```sql
SELECT COUNT(*) FROM orders;
```

**Step 2: Load Same File Again**

```sql
COPY orders
FROM 's3://siddhartha-redshift-bucket/orders/order_summary_fixed.parquet'
IAM_ROLE 'arn:aws:iam::[AWS-ACCOUNT-ID]:role/MyRedshiftS3Role'
FORMAT AS PARQUET;
```

**Step 3: Verify Duplicates Created**

```sql
SELECT COUNT(*) FROM orders;
-- Result: 2

SELECT order_orderId, COUNT(*) as duplicate_count
FROM orders
GROUP BY order_orderId
HAVING COUNT(*) > 1;
-- Result: ORD-2025-850386 | 2
```

COPY commands create duplicates - they don't check for existing data!

---

## **Phase 5: Production Solution - UPSERT Pattern**

### **5.1 UPSERT Implementation**

Implement duplicate prevention using staging tables.

**Step 1: Create Staging Table**

```sql
CREATE TABLE orders_staging (LIKE orders);
```

**Step 2: Load Data into Staging**

```sql
COPY orders_staging
FROM 's3://siddhartha-redshift-bucket/orders/order_summary_fixed.parquet'
IAM_ROLE 'arn:aws:iam::[AWS-ACCOUNT-ID]:role/MyRedshiftS3Role'
FORMAT AS PARQUET;
```

**Step 3: UPSERT Logic (Delete + Insert)**

```sql
-- Remove existing records that will be updated
DELETE FROM orders
WHERE order_orderId IN (SELECT order_orderId FROM orders_staging);

-- Insert all records from staging (new + updated)
INSERT INTO orders SELECT * FROM orders_staging;

-- Clean up staging table
DROP TABLE orders_staging;
```

**Step 4: Verification**

```sql
-- Check no duplicates exist
SELECT order_orderId, COUNT(*)
FROM orders
GROUP BY order_orderId
HAVING COUNT(*) > 1;
-- Result: No rows (no duplicates)

-- Check total count
SELECT COUNT(*) FROM orders;
-- Result: 1 (clean data)
```

### **5.2 UPSERT Implementation for Order Items Table**

**Apply the same pattern to order_items table:**

**Step 1: Initial Load**

```sql
COPY order_items
FROM 's3://siddhartha-redshift-bucket/order-items/order_items_fixed.parquet'
IAM_ROLE 'arn:aws:iam::[AWS-ACCOUNT-ID]:role/MyRedshiftS3Role'
FORMAT AS PARQUET;

-- Verify initial load
SELECT * FROM order_items;
```

**Step 2: Create Staging Table**

```sql
CREATE TABLE order_items_staging (LIKE order_items);
```

**Step 3: Load Data into Staging**

```sql
COPY order_items_staging
FROM 's3://siddhartha-redshift-bucket/order-items/order_items_fixed.parquet'
IAM_ROLE 'arn:aws:iam::[AWS-ACCOUNT-ID]:role/MyRedshiftS3Role'
FORMAT AS PARQUET;
```

**Step 4: UPSERT Logic (Delete + Insert)**

```sql
-- Remove existing records that will be updated
DELETE FROM order_items
WHERE itemId IN (SELECT itemId FROM order_items_staging);

-- Insert all records from staging (new + updated)
INSERT INTO order_items SELECT * FROM order_items_staging;

-- Clean up staging table
DROP TABLE order_items_staging;
```

**Step 5: Verification**

```sql
-- Check no duplicates exist
SELECT itemId, COUNT(*)
FROM order_items
GROUP BY itemId
HAVING COUNT(*) > 1;
-- Result: No rows (no duplicates)

-- Check final count
SELECT COUNT(*) FROM order_items;
-- Result: 1 (clean data)
```

**Key Difference**: Uses `itemId` as the unique identifier instead of `order_orderId`.

---

## **Phase 6: Monitoring & Auditing**

### **6.1 Data Load Tracking System**

**Create Load Log Table:**

```sql
CREATE TABLE data_load_log (
    load_id BIGINT IDENTITY(1,1),
    file_path VARCHAR(500),
    table_name VARCHAR(100),
    load_timestamp TIMESTAMP DEFAULT GETDATE(),
    record_count INTEGER,
    status VARCHAR(20),
    load_method VARCHAR(50),
    notes VARCHAR(500)
);
```

### **6.2 Log Successful Loads**

```sql
INSERT INTO data_load_log (file_path, table_name, record_count, status, load_method, notes)
VALUES ('s3://siddhartha-redshift-bucket/orders/order_summary_fixed.parquet',
        'orders', 1, 'SUCCESS', 'UPSERT_STAGING', 'Duplicate prevention successful');
```

### **6.3 View Load History**

```sql
SELECT * FROM data_load_log ORDER BY load_timestamp DESC;
```

---

## **Phase 7: Business Analytics Validation**

### **7.1 Data Quality Verification**

```sql
-- Verify clean data across both tables
SELECT 'orders' as table_name, COUNT(*) as record_count FROM orders
UNION ALL
SELECT 'order_items' as table_name, COUNT(*) as record_count FROM order_items;
```

---

## **Phase 8: Key Learnings & Best Practices**

### **8.1 Technical Challenges Overcome**

1. **Schema Mismatches**: Parquet column names didn't match initial table definitions
2. **Data Type Conflicts**: DECIMAL vs DOUBLE PRECISION, INTEGER vs BIGINT
3. **NULL Value Issues**: Parquet NULLs caused COPY failures

### **8.2 Solutions Implemented**

1. **NULL Value Fixing**: Replaced NULLs with appropriate defaults
2. **Exact Type Matching**: Aligned Redshift types with Parquet data types

---

## **Phase 9: Cost Management & Cleanup**

### **9.1 AWS Resources Created**

- **S3 Bucket**: minimal storage costs
- **IAM Role**: no cost
- **Redshift Serverless**: pay-per-use

### **9.2 Cleanup Commands (When POC Complete)**

```sql
-- Drop tables if no longer needed
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS data_load_log;

-- In AWS Console:
-- 1. Delete Redshift Serverless workgroup/namespace
-- 2. Delete S3 bucket contents and bucket
-- 3. Delete IAM role
```

---
