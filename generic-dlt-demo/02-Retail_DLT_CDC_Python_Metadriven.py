# Databricks notebook source
# MAGIC %pip install pyaml

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC # Implementing a CDC pipeline using DLT for N tables
# MAGIC
# MAGIC We saw previously how to setup a CDC pipeline for a single table. However, real-life database typically involve multiple tables, with 1 CDC folder per table.
# MAGIC
# MAGIC Operating and ingesting all these tables at scale is quite challenging. You need to start multiple table ingestion at the same time, working with threads, handling errors, restart where you stopped, deal with merge manually.
# MAGIC
# MAGIC Thankfully, DLT takes care of that for you. We can leverage python loops to naturally iterate over the folders (see the [documentation](https://docs.databricks.com/data-engineering/delta-live-tables/delta-live-tables-cookbook.html#programmatically-manage-and-create-multiple-live-tables) for more details)
# MAGIC
# MAGIC DLT engine will handle the parallelization whenever possible, and autoscale based on your data volume.
# MAGIC
# MAGIC <img src="https://github.com/QuentinAmbard/databricks-demo/raw/main/product_demos/cdc_dlt_pipeline_full.png" width="1000"/>
# MAGIC
# MAGIC <!-- Collect usage data (view). Remove it to disable collection. View README for more details.  -->
# MAGIC <img width="1px" src="https://www.google-analytics.com/collect?v=1&gtm=GTM-NKQ8TT7&tid=UA-163989034-1&aip=1&t=event&ec=dbdemos&ea=VIEW&dp=%2F_dbdemos%2Fdata-engineering%2Fdlt-cdc%2F04-Retail_DLT_CDC_Full&cid=1444828305810485&uid=3692557000280926">
# MAGIC <!-- [metadata={"description":"Process CDC from external system and save them as a Delta Table. BRONZE/SILVER.<br/><i>Usage: demo CDC flow.</i>",
# MAGIC  "authors":["mojgan.mazouchi@databricks.com"],
# MAGIC  "db_resources":{},
# MAGIC   "search_tags":{"vertical": "retail", "step": "Data Engineering", "components": ["autoloader", "copy into", "cdc", "cdf"]},
# MAGIC                  "canonicalUrl": {"AWS": "", "Azure": "", "GCP": ""}}] -->

# COMMAND ----------

dbutils.widgets.text('jobContinue','no')

# COMMAND ----------

# DBTITLE 1,2 tables in our cdc_raw: customers and transactions
config_file = "/Volumes/sanjeev_catalog/demo/sanjeev_demo_volume/dlt-conf.json"
dbutils.fs.ls("/user/sanjeev.kumar@databricks.com/iss/cdc_raw/")

# COMMAND ----------

import dlt
from pyspark.sql.functions import *
import pyaml
import json

# COMMAND ----------

# DBTITLE 1,Create configuration

with open(config_file) as f:
    sources = json.load(f)

# COMMAND ----------

# Let's loop over all the folders and dynamically generate our DLT pipeline.
def create_pipeline(source_config):
    table_name = source_config["source_name"]
    source_file_format = source_config["source_file_format"]
    source_path = source_config["source_path"]
    SCD2 = source_config["SCD2"]
    exp_or_drop = source_config["expect_all_or_drop"]
    exp_or_fail = source_config["expect_all_or_fail"]

    print(f"Building DLT CDC pipeline for {table_name}")


    ##Raw CDC Table
    @dlt.create_table(
        name=table_name + "_cdc",
        comment="New "
        + table_name
        + " data incrementally ingested from cloud object storage landing zone",
    )
    ## Various ways to define an Expectation
    ## 1. Individually
    #@dlt.expect_or_drop("no_rescued_data", "_rescued_data IS NULL")
    #@dlt.expect("valid_id", "id IS NOT NULL")
    #@dlt.expect_or_drop("valid_operation", "operation IN ('APPEND', 'DELETE', 'UPDATE')")

    ## 2. Collectively in a dictionary
    #@dlt.expect_all_or_drop({"no_rescued_data": "_rescued_data IS NULL", "valid_id": "id IS NOT NULL", "valid_operation": "operation IN ('APPEND', 'DELETE', 'UPDATE')"})

    ## 3. From config
    @dlt.expect_all_or_drop(exp_or_drop)
    @dlt.expect_all_or_fail(exp_or_fail)
    def raw_cdc():
        return (
            spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", source_file_format)
            .option("cloudFiles.inferColumnTypes", "true")
            .load(source_path)
        )


    ##Clean CDC input 
    @dlt.create_view(
        name=table_name + "_cdc_clean",
        comment="Cleansed cdc data, tracking data quality with a view. We ensude valid JSON, id and operation type",
    )
    def raw_cdc_clean():
        return dlt.read_stream(table_name + "_cdc")


    ##Materialize the final table
    dlt.create_target_table(
        name=table_name, comment="Clean, materialized " + table_name
    )
    dlt.apply_changes(
        target=table_name,                 # The customer table being materilized
        source=table_name + "_cdc_clean",  # the incoming CDC
        keys=["id"],                       # what we'll be using to match the rows to upsert
        sequence_by=col(
            "operation_date"
        ),                                 # we deduplicate by operation date getting the most recent value
        ignore_null_updates=False,
        apply_as_deletes=expr(
            "operation = 'DELETE'"
            ),                              # DELETE condition
        except_column_list=[
            "operation", 
            "operation_date", 
            "_rescued_data"
            ],
    )                                       # in addition we drop metadata columns


    ##Create SDC2 type table
    if SCD2:
        dlt.create_target_table(
            name=f"SCD2_{table_name}",
            comment=f"Slowly Changing Dimension Type 2 for {table_name}",
        )

        ##Enable SCD2 and store individual updates
        dlt.apply_changes(
            target=f"SCD2_{table_name}",
            source=f"{table_name}_cdc_clean",
            keys=["id"],
            sequence_by=col("operation_date"),
            ignore_null_updates=False,
            apply_as_deletes=expr("operation = 'DELETE'"),
            except_column_list=["operation", "operation_date", "_rescued_data"],
            stored_as_scd_type="2",
        )  

# COMMAND ----------

##Create pipeline
for source_config in sources:
    create_pipeline(source_config)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Conclusion 
# MAGIC We can now scale our CDC pipeline to N tables using python factorization. This gives us infinite possibilities and abstraction level in our DLT pipelines.
# MAGIC
# MAGIC DLT handles all the hard work for us so that we can focus on business transformation and drastically accelerate DE team:
# MAGIC - simplify file ingestion with the autoloader
# MAGIC - track data quality using exception
# MAGIC - simplify all operations including upsert with APPLY CHANGES
# MAGIC - process all our tables in parallel
# MAGIC - autoscale based on the amount of data
# MAGIC
# MAGIC DLT gives more power to SQL-only users, letting them build advanced data pipeline without requiering strong Data Engineers skills.
