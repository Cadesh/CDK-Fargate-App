from aws_cdk import (
    Stack,
)
from constructs import Construct

import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_elasticloadbalancingv2 as elbv2
from aws_cdk import Duration

class CdkFargateStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, 'cdk-fargate-vpc', ip_addresses=ec2.IpAddresses.cidr('10.0.0.0/16'))

        cluster = ecs.Cluster(self, 'cdk-fargate-cluster', vpc=vpc)

        task_definition = ecs.FargateTaskDefinition(self, 'TaskDef', cpu=256, memory_limit_mib=512)

        container = task_definition.add_container('web', image=ecs.ContainerImage.from_registry('amazon/amazon-ecs-sample'))
        container.add_port_mappings(ecs.PortMapping(container_port=80, protocol=ecs.Protocol.TCP))

        service = ecs.FargateService(self, 'Service', cluster=cluster, task_definition=task_definition, desired_count=3)

        lb = elbv2.ApplicationLoadBalancer(self, 'ALB', vpc=vpc, internet_facing=True)
        listener = lb.add_listener('Listener', port=80, open=True)
        listener.add_targets('ECS', port=80, targets=[service], health_check=elbv2.HealthCheck(interval=Duration.seconds(60), path='/', timeout=Duration.seconds(5)))