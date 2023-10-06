# Databricks notebook source
rundate = dbutils.jobs.taskValues.get(taskKey="Set_date_for_subsequent_tasks", key="task2_rundate")

# COMMAND ----------

print(rundate)
