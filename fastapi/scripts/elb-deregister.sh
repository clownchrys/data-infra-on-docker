#!/bin/bash

echo 'ELB Deregister target execute'

instance_id=`ec2-metadata -i | awk '{ print $2 }'`
aws elbv2 deregister-targets \
--target-group-arn arn:aws:elasticloadbalancing:ap-northeast-2:385537130119:targetgroup/JK-DEV-TG-API-NLB-INSTANCE/d56f8bf39ea224c1 \
--targets Id=$instance_id,Port=8080