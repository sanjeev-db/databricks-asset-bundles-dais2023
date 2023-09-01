# Databricks notebook source
# MAGIC %md ## Top Medium Posts by Databricks Field Engineering

# COMMAND ----------

# MAGIC %md ### Read Data

# COMMAND ----------

from pyspark.sql.functions import desc

dbutils.widgets.text("dbname", "")

# COMMAND ----------

# Read Medium metrics table


# COMMAND ----------

# MAGIC %md ### Visualize

# COMMAND ----------

# MAGIC %md
# MAGIC #### Top 20 Articles by Applause

# COMMAND ----------
# schema creation by passing list
df = spark.createDataFrame([
    Row(a=1, b=4., c='GFG1', d=date(2000, 8, 1),
        e=datetime(2000, 8, 1, 12, 0)),
   
    Row(a=2, b=8., c='GFG2', d=date(2000, 6, 2),
        e=datetime(2000, 6, 2, 12, 0)),
   
    Row(a=4, b=5., c='GFG3', d=date(2000, 5, 3),
        e=datetime(2000, 5, 3, 12, 0))
])
 
# show table
df.show()
 
# show schema
df.printSchema()

# COMMAND ----------

# MAGIC %md #### Top 5 longest articles

# COMMAND ----------

# COMMAND ----------

# MAGIC %md #### Top 5 Shortest Articles

# COMMAND ----------

# COMMAND ----------

# MAGIC %md #### Explore full dataset

# COMMAND ----------
