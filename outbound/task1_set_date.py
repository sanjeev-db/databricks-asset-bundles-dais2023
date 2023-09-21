# Databricks notebook source
from datetime import datetime, timedelta

# COMMAND ----------

# DBTITLE 1,Get job and task level parameters
param_job_date = dbutils.widgets.get("run_date")
param_jobid = dbutils.widgets.get("job_id")
param_task2_run_day = int(dbutils.widgets.get("task2_run_day"))
param_task3_run_day = int(dbutils.widgets.get("task3_run_day"))

# COMMAND ----------

# Convert string to datetime object
date_obj = datetime.strptime(param_job_date, "%Y-%m-%d")

# Add one day to the datetime object
task2_run_date = date_obj + timedelta(days=param_task2_run_day)
task3_run_date = date_obj + timedelta(days=param_task3_run_day)

# COMMAND ----------

dbutils.jobs.taskValues.set(key="task2_rundate", value=task2_run_date.strftime("%Y-%m-%d"))
dbutils.jobs.taskValues.set(key="task3_rundate", value=task3_run_date.strftime("%Y-%m-%d"))
print(task3_run_date)

# COMMAND ----------


