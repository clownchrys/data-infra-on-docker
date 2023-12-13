# Setup
``` bash
make download-resources
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
DISTRIBUTED_SHELL=$(ls $HADOOP_HOME/share/hadoop/yarn/*distributedshell*.jar | sort -r | head -n 1); yarn jar $DISTRIBUTED_SHELL -jar $DISTRIBUTED_SHELL -shell_command ls -shell_args '-al' -container_resources memory-mb=512,vcores=1
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