import time

df = spark.createDataFrame([{"id": i, "value": "test"} for i in range(10000000)])

mode = "overwrite"
options = {
    # server opt
    "url": "jdbc:sqlserver://sqlserver:1433;",
    "user": "sa",
    "password": "SA_password!",
    "encrypt": False,
    "trustServerCertificate": True,
    # operation opt
    "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver",
    "isolationLevel": "READ_COMMITTED",
    "reliabilityLevel": "BEST_EFFORT",
    "dbtable": "testdb.dbo.tbl1",
    "truncate": True,
    "tableLock": True,
    "schemaCheckEnabled": False,
    "batchsize": 100000,
}

start = time.perf_counter()
df.write.format("com.microsoft.sqlserver.jdbc.spark").mode("overwrite").options(**options).save()
# df.write.format("jdbc").mode(mode).options(**options).save()
# df.write.format("delta").mode(mode).options(**options).save()
end = time.perf_counter()
print(end - start)
