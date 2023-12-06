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