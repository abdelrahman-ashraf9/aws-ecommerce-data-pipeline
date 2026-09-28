# End-to-End AWS E-Commerce Data Pipeline

A comprehensive, cloud-native Data Engineering ecosystem featuring dual ingestion (batch + real-time streaming), distributed PySpark ETL, Star Schema modeling, and serverless querying via Amazon Athena.

![Architecture](./architecture/architecture.svg)

## 📌 Architecture Highlights
- **Synthetic Batch Generator**: Custom Python script using `Faker` to generate 12 relational CSV tables (~100k records).
- **Automated S3 Sync**: Boto3 script syncing batch datasets directly to `s3://aws-ecommerce-data-abdelrahman/raw/ecommerce/`.
- **Live Stream Simulator**: FastAPI REST server generating live orders with AWS Lambda ingestion and S3 state checkpointing.
- **Distributed ETL**: PySpark on AWS Glue to clean nulls, remove duplicate records, handle schema mapping, and build a 16-table Star Schema.
- **Curated Lakehouse Storage**: Compressed Snappy Parquet format stored in S3 for fast, cost-effective queries.
- **Serverless Analytics**: Amazon Athena integration with advanced SQL analytics (MoM growth, running totals, customer ranks).

## Tech Stack
- **Languages**: Python, SQL, PySpark
- **AWS Services**: Amazon S3, AWS Glue, AWS Lambda, Amazon Athena
- **Frameworks & Tools**: FastAPI, Boto3, Faker, ngrok, Git

## 📂 Repository Structure
