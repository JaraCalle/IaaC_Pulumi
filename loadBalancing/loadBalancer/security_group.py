import pulumi_aws as aws

def create_lb_sg(vpc: aws.ec2.Vpc) -> aws.ec2.SecurityGroup:
    sg_lb = aws.ec2.SecurityGroup(
        "lb-sg",
        vpc_id=vpc.id,
        description="Allow HTTP from anywhere",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=80,
                to_port=80,
                cidr_blocks=["0.0.0.0/0"],
                ipv6_cidr_blocks=["::/0"]
            )
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"]
            )
        ],
        tags={"Name": "lb-sg"}
    )
    return sg_lb