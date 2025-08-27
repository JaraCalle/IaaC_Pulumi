import pulumi_aws as aws
from config import vpc_name, vpc_cidr

def create_vpc():
    vpc = aws.ec2.Vpc(
        vpc_name,
        cidr_block=vpc_cidr,
        enable_dns_support=True,
        enable_dns_hostnames=True,
        tags={"Name": vpc_name}
    )

    return vpc