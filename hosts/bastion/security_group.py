import pulumi_aws as aws

def create_bastion_sg(vpc) -> aws.ec2.SecurityGroup:
    bastion_sg = aws.ec2.SecurityGroup(
        "bastion-sg",
        vpc_id=vpc.id,
        description="Security group for Bastion Host",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=22,
                to_port=22,
                cidr_blocks=["0.0.0.0/0"]
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
        tags={"Name": "bastion-sg"}
    )

    return bastion_sg