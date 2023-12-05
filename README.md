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