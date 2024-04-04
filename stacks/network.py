import os

from aws_cdk import (
    aws_ec2 as ec2,
    CfnOutput, 
    Stack
)
from constructs import Construct

class NetworkStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Define variables
        self.env        = os.getenv("ENVIRONMENT")
        self.vpc_name   = '{env_name}-vpc'.format(env_name=self.env)
        self.vpc_cidr   = os.getenv("VPC_CIDR")
        self.vpc_max_az = int(os.getenv("VPC_AZ_COUNT"))

        self.vpc: ec2.Vpc = ec2.Vpc(self, 'network',
                                    
                                    # VPC Configs
                                    vpc_name=self.vpc_name,
                                    ip_addresses=ec2.IpAddresses.cidr(self.vpc_cidr),
                                    max_azs=self.vpc_max_az,

                                    # Nat Gateways Configs
                                    nat_gateway_provider=ec2.NatProvider.gateway(),
                                    nat_gateways=2,

                                    # Subnets Configs for Vpc
                                    subnet_configuration=[
                                        ec2.SubnetConfiguration(
                                            subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                                            name='{env_name}-private-isolated-'.format(env_name=self.env),
                                            cidr_mask=25), 
                                        ec2.SubnetConfiguration(
                                            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                                            name='{env_name}-private-egress-'.format(env_name=self.env),
                                            cidr_mask=25), 
                                        ec2.SubnetConfiguration(
                                            subnet_type=ec2.SubnetType.PUBLIC,
                                            name='{env_name}-public-'.format(env_name=self.env),
                                            cidr_mask=25
                                        )
                                    ],
        )

        # Set Outputs
        CfnOutput(self, "Output",
                  value=self.vpc.vpc_id
        )
