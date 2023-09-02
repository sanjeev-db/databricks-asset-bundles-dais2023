from os import path

import dlt
import json
from pyspark.sql import DataFrame
from pyspark.sql.functions import regexp_replace


#config_file = "/dbfs/FileStore/users/dlt_config.json"
config_file = "./dlt_config.json"


with open(config_file) as f:
    sources = json.load(f)


def create_pipeline(source_config):
    table_name = source_config["source_name"]

    @dlt.create_table(
            name=table_name + "_raw", 
            comment="New Raw " + table_name
            )
    @dlt.expect("No null links", "link is not null")
    def create_raw_table():
        #csv_path = "dbfs:/data-asset-bundles-dais2023/fe_medium_posts_raw.csv"
        csv_path = "dbfs:/FileStore/users/fe_medium_posts_raw.csv"
        return spark.read.csv(csv_path, header=True)


    @dlt.create_table(
        name=table_name + "_silver", 
        comment="New Silver " + table_name
        )
    def create_silver_table():
        df: DataFrame = dlt.read(table_name + "_raw")
        df = df.filter(df.link != 'null')
        df = df.withColumn("author", regexp_replace("author", "\\([^()]*\\)", ""))
        return df


for source_config in sources:
    create_pipeline(source_config)