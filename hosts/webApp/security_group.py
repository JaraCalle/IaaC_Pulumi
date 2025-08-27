import pulumi_aws as aws
from config import public_cidrs

def create_web_sg(vpc: aws.ec2.Vpc) -> aws.ec2.SecurityGroup:
    web_sg = aws.ec2.SecurityGroup(
        "webcms-sg",
        vpc_id=vpc.id,
        description="Enable HTTP Access for Web Servers",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=80,
                to_port=80,
                cidr_blocks=public_cidrs
            ),
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=22,
                to_port=22,
                cidr_blocks=["172.16.1.0/24"]
            )
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
            )
        ],
        tags={"Name": "webcms-sg"}
    )

    return web_sg