# Setup
``` bash
make build-assets
make restart
```

# Add SA in Dockerfile
```Dockerfile
ARG SERVICE_ACCOUNT=svc-user
RUN useradd ${SERVICE_ACCOUNT} --create-home --shell $(which bash) --group sudo
RUN echo "${SERVICE_ACCOUNT}:${SERVICE_ACCOUNT}" | chpasswd
# RUN echo "${SERVICE_ACCOUNT} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${SERVICE_ACCOUNT}
RUN echo "${SERVICE_ACCOUNT} ALL=NOPASSWD:/usr/sbin/sshd" > /etc/sudoers.d/${SERVICE_ACCOUNT}
RUN cp -rvf ~/.ssh /home/${SERVICE_ACCOUNT}/ && chown -hR ${SERVICE_ACCOUNT}:${SERVICE_ACCOUNT} /home/${SERVICE_ACCOUNT}/.ssh
USER ${SERVICE_ACCOUNT}
```

# Yarn DistributedShell Application
``` bash
DISTRIBUTED_SHELL=$(ls $HADOOP_HOME/share/hadoop/yarn/*distributedshell*.jar | sort -r | head -n 1); yarn jar $DISTRIBUTED_SHELL -jar $DISTRIBUTED_SHELL -shell_command ls -shell_args '-al' -container_assets memory-mb=512,vcores=1
```

# Check ServiceState
``` bash
yarn rmadmin -getServiceState rm1
yarn rmadmin -transitionToActive rm2 --forcemanual

hdfs haadmin -getServiceState nn1
hdfs haadmin -transitionToActive nn2 --forcemanual
```

# example. reading torch tensor from HDFS
``` bash
apt install python3.8-venv
python3 -m venv ~/venv
source ~/venv/bin/activate

pip install torch numpy pydoop --trusted-host download.pytorch.org --index-url https://download.pytorch.org/whl/cpu

python -c 'import torch; tensor=torch.rand(10, 10); torch.save(tensor, "tensor.pt")'
hdfs dfs -copyFromLocal tensor.pt /tmp/tensor.pt
python -c 'import torch; from pydoop import hdfs; client = hdfs.hdfs("hdp-cluster", 8020); f = hdfs.open_file("/tmp/tensor.pt"); tensor=torch.load(f); print(tensor); f.close(); client.close()'
```

# example. read delta-table from hive (without spark driver)
``` bash
apt install python3.8-venv
python3 -m venv ~/venv
source ~/venv/bin/activate

pip install pyhive thrift thrift_sasl

python -c 'from pyhive import hive; conn=hive.connect("hive-1", 10000); cursor=conn.cursor(); cursor.execute("show databases"); print(cursor.fetchall()); cursor.close(); conn.close()'
```

# S3 Integration Error
``` log
Traceback (most recent call last):                                  (0 + 0) / 1]
  File "<stdin>", line 1, in <module>
  File "/opt/spark/current/python/pyspark/sql/readwriter.py", line 727, in csv
    return self._df(self._jreader.csv(self._spark._sc._jvm.PythonUtils.toSeq(path)))
  File "/opt/spark/current/python/lib/py4j-0.10.9.7-src.zip/py4j/java_gateway.py", line 1322, in __call__
  File "/opt/spark/current/python/pyspark/errors/exceptions/captured.py", line 169, in deco
    return f(*a, **kw)
  File "/opt/spark/current/python/lib/py4j-0.10.9.7-src.zip/py4j/protocol.py", line 326, in get_return_value
py4j.protocol.Py4JJavaError: An error occurred while calling o65.csv.
: org.apache.spark.SparkException: Job aborted due to stage failure: Task 0 in stage 0.0 failed 4 times, most recent failure: Lost task 0.3 in stage 0.0 (TID 3) (hdp-worker-1 executor 1): java.lang.NoSuchMethodError: org.apache.hadoop.fs.statistics.impl.IOStatisticsBinding.invokeTrackingDuration(Lorg/apache/hadoop/fs/statistics/DurationTracker;Lorg/apache/hadoop/util/functional/CallableRaisingIOE;)Ljava/lang/Object;
        at org.apache.hadoop.fs.s3a.Invoker.onceTrackingDuration(Invoker.java:147)
        at org.apache.hadoop.fs.s3a.S3AInputStream.reopen(S3AInputStream.java:282)
        at org.apache.hadoop.fs.s3a.S3AInputStream.lambda$lazySeek$1(S3AInputStream.java:435)
        at org.apache.hadoop.fs.s3a.Invoker.lambda$maybeRetry$3(Invoker.java:284)
        at org.apache.hadoop.fs.s3a.Invoker.once(Invoker.java:122)
        at org.apache.hadoop.fs.s3a.Invoker.lambda$maybeRetry$5(Invoker.java:408)
        at org.apache.hadoop.fs.s3a.Invoker.retryUntranslated(Invoker.java:468)
        at org.apache.hadoop.fs.s3a.Invoker.maybeRetry(Invoker.java:404)
        at org.apache.hadoop.fs.s3a.Invoker.maybeRetry(Invoker.java:282)
        at org.apache.hadoop.fs.s3a.Invoker.maybeRetry(Invoker.java:326)
        at org.apache.hadoop.fs.s3a.S3AInputStream.lazySeek(S3AInputStream.java:427)
        at org.apache.hadoop.fs.s3a.S3AInputStream.read(S3AInputStream.java:545)
        at java.io.DataInputStream.read(DataInputStream.java:149)
        at org.apache.hadoop.mapreduce.lib.input.UncompressedSplitLineReader.fillBuffer(UncompressedSplitLineReader.java:62)
        at org.apache.hadoop.util.LineReader.readDefaultLine(LineReader.java:227)
        at org.apache.hadoop.util.LineReader.readLine(LineReader.java:185)
        at org.apache.hadoop.mapreduce.lib.input.UncompressedSplitLineReader.readLine(UncompressedSplitLineReader.java:94)
        at org.apache.hadoop.mapreduce.lib.input.LineRecordReader.skipUtfByteOrderMark(LineRecordReader.java:158)
        at org.apache.hadoop.mapreduce.lib.input.LineRecordReader.nextKeyValue(LineRecordReader.java:198)
        at org.apache.spark.sql.execution.datasources.RecordReaderIterator.hasNext(RecordReaderIterator.scala:39)
        at org.apache.spark.sql.execution.datasources.HadoopFileLinesReader.hasNext(HadoopFileLinesReader.scala:67)
        at scala.collection.Iterator$$anon$10.hasNext(Iterator.scala:460)
        at scala.collection.Iterator$$anon$10.hasNext(Iterator.scala:460)
        at org.apache.spark.sql.execution.datasources.FileScanRDD$$anon$1.hasNext(FileScanRDD.scala:125)
        at org.apache.spark.sql.execution.datasources.FileScanRDD$$anon$1.nextIterator(FileScanRDD.scala:297)
        at org.apache.spark.sql.execution.datasources.FileScanRDD$$anon$1.hasNext(FileScanRDD.scala:125)
        at scala.collection.Iterator$$anon$10.hasNext(Iterator.scala:460)
        at org.apache.spark.sql.catalyst.expressions.GeneratedClass$GeneratedIteratorForCodegenStage1.processNext(Unknown Source)
        at org.apache.spark.sql.execution.BufferedRowIterator.hasNext(BufferedRowIterator.java:43)
        at org.apache.spark.sql.execution.WholeStageCodegenExec$$anon$1.hasNext(WholeStageCodegenExec.scala:760)
        at org.apache.spark.sql.execution.SparkPlan.$anonfun$getByteArrayRdd$1(SparkPlan.scala:388)
        at org.apache.spark.rdd.RDD.$anonfun$mapPartitionsInternal$2(RDD.scala:888)
        at org.apache.spark.rdd.RDD.$anonfun$mapPartitionsInternal$2$adapted(RDD.scala:888)
        at org.apache.spark.rdd.MapPartitionsRDD.compute(MapPartitionsRDD.scala:52)
        at org.apache.spark.rdd.RDD.computeOrReadCheckpoint(RDD.scala:364)
        at org.apache.spark.rdd.RDD.iterator(RDD.scala:328)
        at org.apache.spark.scheduler.ResultTask.runTask(ResultTask.scala:92)
        at org.apache.spark.TaskContext.runTaskWithListeners(TaskContext.scala:161)
        at org.apache.spark.scheduler.Task.run(Task.scala:139)
        at org.apache.spark.executor.Executor$TaskRunner.$anonfun$run$3(Executor.scala:554)
        at org.apache.spark.util.Utils$.tryWithSafeFinally(Utils.scala:1529)
        at org.apache.spark.executor.Executor$TaskRunner.run(Executor.scala:557)
        at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
        at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
        at java.lang.Thread.run(Thread.java:750)

Driver stacktrace:
        at org.apache.spark.scheduler.DAGScheduler.failJobAndIndependentStages(DAGScheduler.scala:2785)
        at org.apache.spark.scheduler.DAGScheduler.$anonfun$abortStage$2(DAGScheduler.scala:2721)
        at org.apache.spark.scheduler.DAGScheduler.$anonfun$abortStage$2$adapted(DAGScheduler.scala:2720)
        at scala.collection.mutable.ResizableArray.foreach(ResizableArray.scala:62)
        at scala.collection.mutable.ResizableArray.foreach$(ResizableArray.scala:55)
        at scala.collection.mutable.ArrayBuffer.foreach(ArrayBuffer.scala:49)
        at org.apache.spark.scheduler.DAGScheduler.abortStage(DAGScheduler.scala:2720)
        at org.apache.spark.scheduler.DAGScheduler.$anonfun$handleTaskSetFailed$1(DAGScheduler.scala:1206)
        at org.apache.spark.scheduler.DAGScheduler.$anonfun$handleTaskSetFailed$1$adapted(DAGScheduler.scala:1206)
        at scala.Option.foreach(Option.scala:407)
        at org.apache.spark.scheduler.DAGScheduler.handleTaskSetFailed(DAGScheduler.scala:1206)
        at org.apache.spark.scheduler.DAGSchedulerEventProcessLoop.doOnReceive(DAGScheduler.scala:2984)
        at org.apache.spark.scheduler.DAGSchedulerEventProcessLoop.onReceive(DAGScheduler.scala:2923)
        at org.apache.spark.scheduler.DAGSchedulerEventProcessLoop.onReceive(DAGScheduler.scala:2912)
        at org.apache.spark.util.EventLoop$$anon$1.run(EventLoop.scala:49)
        at org.apache.spark.scheduler.DAGScheduler.runJob(DAGScheduler.scala:971)
        at org.apache.spark.SparkContext.runJob(SparkContext.scala:2263)
        at org.apache.spark.SparkContext.runJob(SparkContext.scala:2284)
        at org.apache.spark.SparkContext.runJob(SparkContext.scala:2303)
        at org.apache.spark.sql.execution.SparkPlan.executeTake(SparkPlan.scala:530)
        at org.apache.spark.sql.execution.SparkPlan.executeTake(SparkPlan.scala:483)
        at org.apache.spark.sql.execution.CollectLimitExec.executeCollect(limit.scala:61)
        at org.apache.spark.sql.Dataset.collectFromPlan(Dataset.scala:4177)
        at org.apache.spark.sql.Dataset.$anonfun$head$1(Dataset.scala:3161)
        at org.apache.spark.sql.Dataset.$anonfun$withAction$2(Dataset.scala:4167)
        at org.apache.spark.sql.execution.QueryExecution$.withInternalError(QueryExecution.scala:526)
        at org.apache.spark.sql.Dataset.$anonfun$withAction$1(Dataset.scala:4165)
        at org.apache.spark.sql.execution.SQLExecution$.$anonfun$withNewExecutionId$6(SQLExecution.scala:118)
        at org.apache.spark.sql.execution.SQLExecution$.withSQLConfPropagated(SQLExecution.scala:195)
        at org.apache.spark.sql.execution.SQLExecution$.$anonfun$withNewExecutionId$1(SQLExecution.scala:103)
        at org.apache.spark.sql.SparkSession.withActive(SparkSession.scala:827)
        at org.apache.spark.sql.execution.SQLExecution$.withNewExecutionId(SQLExecution.scala:65)
        at org.apache.spark.sql.Dataset.withAction(Dataset.scala:4165)
        at org.apache.spark.sql.Dataset.head(Dataset.scala:3161)
        at org.apache.spark.sql.Dataset.take(Dataset.scala:3382)
        at org.apache.spark.sql.execution.datasources.csv.TextInputCSVDataSource$.infer(CSVDataSource.scala:111)
        at org.apache.spark.sql.execution.datasources.csv.CSVDataSource.inferSchema(CSVDataSource.scala:64)
        at org.apache.spark.sql.execution.datasources.csv.CSVFileFormat.inferSchema(CSVFileFormat.scala:62)
        at org.apache.spark.sql.execution.datasources.DataSource.$anonfun$getOrInferFileFormatSchema$11(DataSource.scala:208)
        at scala.Option.orElse(Option.scala:447)
        at org.apache.spark.sql.execution.datasources.DataSource.getOrInferFileFormatSchema(DataSource.scala:205)
        at org.apache.spark.sql.execution.datasources.DataSource.resolveRelation(DataSource.scala:407)
        at org.apache.spark.sql.DataFrameReader.loadV1Source(DataFrameReader.scala:229)
        at org.apache.spark.sql.DataFrameReader.$anonfun$load$2(DataFrameReader.scala:211)
        at scala.Option.getOrElse(Option.scala:189)
        at org.apache.spark.sql.DataFrameReader.load(DataFrameReader.scala:211)
        at org.apache.spark.sql.DataFrameReader.csv(DataFrameReader.scala:538)
        at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)
        at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.lang.reflect.Method.invoke(Method.java:498)
        at py4j.reflection.MethodInvoker.invoke(MethodInvoker.java:244)
        at py4j.reflection.ReflectionEngine.invoke(ReflectionEngine.java:374)
        at py4j.Gateway.invoke(Gateway.java:282)
        at py4j.commands.AbstractCommand.invokeMethod(AbstractCommand.java:132)
        at py4j.commands.CallCommand.execute(CallCommand.java:79)
        at py4j.ClientServerConnection.waitForCommands(ClientServerConnection.java:182)
        at py4j.ClientServerConnection.run(ClientServerConnection.java:106)
        at java.lang.Thread.run(Thread.java:750)
Caused by: java.lang.NoSuchMethodError: org.apache.hadoop.fs.statistics.impl.IOStatisticsBinding.invokeTrackingDuration(Lorg/apache/hadoop/fs/statistics/DurationTracker;Lorg/apache/hadoop/util/functional/CallableRaisingIOE;)Ljava/lang/Object;
        at org.apache.hadoop.fs.s3a.Invoker.onceTrackingDuration(Invoker.java:147)
        at org.apache.hadoop.fs.s3a.S3AInputStream.reopen(S3AInputStream.java:282)
        at org.apache.hadoop.fs.s3a.S3AInputStream.lambda$lazySeek$1(S3AInputStream.java:435)
        at org.apache.hadoop.fs.s3a.Invoker.lambda$maybeRetry$3(Invoker.java:284)
        at org.apache.hadoop.fs.s3a.Invoker.once(Invoker.java:122)
        at org.apache.hadoop.fs.s3a.Invoker.lambda$maybeRetry$5(Invoker.java:408)
        at org.apache.hadoop.fs.s3a.Invoker.retryUntranslated(Invoker.java:468)
        at org.apache.hadoop.fs.s3a.Invoker.maybeRetry(Invoker.java:404)
        at org.apache.hadoop.fs.s3a.Invoker.maybeRetry(Invoker.java:282)
        at org.apache.hadoop.fs.s3a.Invoker.maybeRetry(Invoker.java:326)
        at org.apache.hadoop.fs.s3a.S3AInputStream.lazySeek(S3AInputStream.java:427)
        at org.apache.hadoop.fs.s3a.S3AInputStream.read(S3AInputStream.java:545)
        at java.io.DataInputStream.read(DataInputStream.java:149)
        at org.apache.hadoop.mapreduce.lib.input.UncompressedSplitLineReader.fillBuffer(UncompressedSplitLineReader.java:62)
        at org.apache.hadoop.util.LineReader.readDefaultLine(LineReader.java:227)
        at org.apache.hadoop.util.LineReader.readLine(LineReader.java:185)
        at org.apache.hadoop.mapreduce.lib.input.UncompressedSplitLineReader.readLine(UncompressedSplitLineReader.java:94)
        at org.apache.hadoop.mapreduce.lib.input.LineRecordReader.skipUtfByteOrderMark(LineRecordReader.java:158)
        at org.apache.hadoop.mapreduce.lib.input.LineRecordReader.nextKeyValue(LineRecordReader.java:198)
        at org.apache.spark.sql.execution.datasources.RecordReaderIterator.hasNext(RecordReaderIterator.scala:39)
        at org.apache.spark.sql.execution.datasources.HadoopFileLinesReader.hasNext(HadoopFileLinesReader.scala:67)
        at scala.collection.Iterator$$anon$10.hasNext(Iterator.scala:460)
        at scala.collection.Iterator$$anon$10.hasNext(Iterator.scala:460)
        at org.apache.spark.sql.execution.datasources.FileScanRDD$$anon$1.hasNext(FileScanRDD.scala:125)
        at org.apache.spark.sql.execution.datasources.FileScanRDD$$anon$1.nextIterator(FileScanRDD.scala:297)
        at org.apache.spark.sql.execution.datasources.FileScanRDD$$anon$1.hasNext(FileScanRDD.scala:125)
        at scala.collection.Iterator$$anon$10.hasNext(Iterator.scala:460)
        at org.apache.spark.sql.catalyst.expressions.GeneratedClass$GeneratedIteratorForCodegenStage1.processNext(Unknown Source)
        at org.apache.spark.sql.execution.BufferedRowIterator.hasNext(BufferedRowIterator.java:43)
        at org.apache.spark.sql.execution.WholeStageCodegenExec$$anon$1.hasNext(WholeStageCodegenExec.scala:760)
        at org.apache.spark.sql.execution.SparkPlan.$anonfun$getByteArrayRdd$1(SparkPlan.scala:388)
        at org.apache.spark.rdd.RDD.$anonfun$mapPartitionsInternal$2(RDD.scala:888)
        at org.apache.spark.rdd.RDD.$anonfun$mapPartitionsInternal$2$adapted(RDD.scala:888)
        at org.apache.spark.rdd.MapPartitionsRDD.compute(MapPartitionsRDD.scala:52)
        at org.apache.spark.rdd.RDD.computeOrReadCheckpoint(RDD.scala:364)
        at org.apache.spark.rdd.RDD.iterator(RDD.scala:328)
        at org.apache.spark.scheduler.ResultTask.runTask(ResultTask.scala:92)
        at org.apache.spark.TaskContext.runTaskWithListeners(TaskContext.scala:161)
        at org.apache.spark.scheduler.Task.run(Task.scala:139)
        at org.apache.spark.executor.Executor$TaskRunner.$anonfun$run$3(Executor.scala:554)
        at org.apache.spark.util.Utils$.tryWithSafeFinally(Utils.scala:1529)
        at org.apache.spark.executor.Executor$TaskRunner.run(Executor.scala:557)
        at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)
        at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)
        ... 1 more
```