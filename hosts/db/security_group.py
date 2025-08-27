import pulumi_aws as aws
from config import app_private_cidrs

def create_db_sg(vpc: aws.ec2.Vpc) -> aws.ec2.SecurityGroup:

    db_sg = aws.ec2.SecurityGroup(
        "db-sg",
        vpc_id=vpc.id,
        description="Security group for MySQL database",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=3306,
                to_port=3306,
                cidr_blocks=app_private_cidrs
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
        tags={"Name": "db-sg"}
    )

    return db_sg