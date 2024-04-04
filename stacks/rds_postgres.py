import os
import json

from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_iam as iam,
    aws_secretsmanager as scrtmgr,
    Duration, 
    Stack, 
    CfnOutput
)
from constructs import Construct


class RdsPostgresStack(Stack):

    def __init__(self, scope: Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define variables
        self.env = os.getenv("ENVIRONMENT")
        rds_instance_identifier='{0}-rds-postgres-{1}'.format(self.env, os.getenv("RDS_PG_INSTANCE_IDENTIFIER"))
        rds_engine = rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_15_6)
        rds_instance_type = ec2.InstanceType.of( ec2.InstanceClass.C6GD, ec2.InstanceSize.MEDIUM)
        '{0}-vpc'.format(self.env)
        rds_vpc_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)
        rds_multi_AZ=True
        rds_allocated_storage = int(os.getenv("RDS_PG_ALLOCATED_STORAGE"))
        rds_max_allocated_storage = int(os.getenv("RDS_PG_MAX_ALLOCATED_STORAGE"))
        rds_storage_type=rds.StorageType.GP2
        rds_cloudwatch_log_exports = ["postgresql", "upgrade"]
        rds_db_name=os.getenv("RDS_PG_DB_NAME")
        
        rds_db_secret_creds = scrtmgr.Secret(
            self,
            "secret_db_creds",
            secret_name="{env_name}/rds_postgres_db_creds".format(env_name=self.env),
            generate_secret_string=scrtmgr.SecretStringGenerator(
                secret_string_template=json.dumps({"username": os.getenv("RDS_PG_USERNAME")}),
                exclude_punctuation=True,
                generate_string_key="password"))

        rds_db_parameter_groups = rds.ParameterGroup(self, "parameter_group_postgres", engine=rds_engine,
                                                 parameters={
                                                     "max_standby_streaming_delay": "600000",    # milliseconds (5 minutes)
                                                     "max_standby_archive_delay": "600000",      # milliseconds (5 minutes)
                                                     })

        rds_db_monitoring_role_name="{0}-rds-postgres-monitoring-role".format(self.env)
        rds_monitoring_role = iam.Role(
            self,
            rds_db_monitoring_role_name,
            assumed_by=iam.ServicePrincipal("monitoring.rds.amazonaws.com"),
            role_name=rds_db_monitoring_role_name,
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonRDSEnhancedMonitoringRole")])
        
        rds_db_sg_name="{0}-rds-postgres-sg".format(self.env)
        rds_db_security_group = ec2.SecurityGroup(
            self,
            rds_db_sg_name,
            vpc=vpc,
            security_group_name=rds_db_sg_name,
            allow_all_outbound=True)

        rds_db_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(5432),
        )

        # RDS Instance Configs
        self.rds = rds.DatabaseInstance(self, 'rds-postgres',
                                        instance_identifier=rds_instance_identifier,
                                        engine=rds_engine,
                                        instance_type=rds_instance_type,

                                        vpc=vpc,
                                        vpc_subnets= rds_vpc_subnets,
                                        multi_az=rds_multi_AZ,
                                        publicly_accessible=False,
                                        security_groups=[rds_db_security_group],

                                        allocated_storage=rds_allocated_storage,
                                        max_allocated_storage=rds_max_allocated_storage,
                                        storage_type=rds_storage_type,
                                        deletion_protection=False,
                                        delete_automated_backups=False,
                                        backup_retention=Duration.days(7),

                                        database_name=rds_db_name,                                        
                                        parameter_group=rds_db_parameter_groups,
                                        credentials=rds.Credentials.from_secret(rds_db_secret_creds),
                                        
                                        enable_performance_insights=True,
                                        performance_insight_retention=rds.PerformanceInsightRetention.DEFAULT,
                                        monitoring_interval=Duration.seconds(60),
                                        monitoring_role=rds_monitoring_role,
                                        cloudwatch_logs_exports=rds_cloudwatch_log_exports
        )

        # Set Outputs
        CfnOutput(self, "Output",
                  value=self.rds.instance_resource_id
        )