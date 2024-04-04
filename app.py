#!/usr/bin/env python3

import os
import aws_cdk as cdk

from dotenv import load_dotenv

# Load Target ENV variables
load_dotenv(
    dotenv_path=".env-{envars_file}".format(envars_file=os.getenv("ENVARS_FILE"))
)
print(f'ENVARS_FILE: {os.getenv("ENVARS_FILE")}')


## Define AWS Deploy environment
deploy_env = cdk.Environment(
    account=os.environ.get("CDK_DEPLOY_ACCOUNT"),
    region=os.environ.get("CDK_DEPLOY_REGION")
)
print(deploy_env)


## Define Deployment Stacks
from stacks.network import NetworkStack
from stacks.rds_postgres import RdsPostgresStack

app = cdk.App()

env_name = os.getenv("ENVIRONMENT")

vpc_stack = NetworkStack(
    scope   = app, 
    id      = '{0}-network-stack'.format(env_name),
    env     = deploy_env
)

rds_stack = RdsPostgresStack(
    scope   = app,
    id      = '{0}-rds-postgres-stack'.format(env_name),
    vpc     = vpc_stack.vpc,
    env     = deploy_env
)

app.synth()
