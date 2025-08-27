import pulumi_aws as aws

def create_igw_and_nats(vpc, public_subnets: list) -> tuple[aws.ec2.InternetGateway,list]:
    igw = aws.ec2.InternetGateway(
        "cms-igw",
        vpc_id = vpc.id,
        tags = {"Name": "cms-igw"}
    )

    nat_gateways = []
    for i, subnet in enumerate(public_subnets):
        
        # Elastic IP
        eip = aws.ec2.Eip(
            f"nat-gw-{i}", 
            domain = "vpc",
            tags = {"Name": f"nat-eip-{i}"}
        )
        
        # NatGateway
        nat = aws.ec2.NatGateway(
            f"nat-gw-{i}",
            allocation_id = eip.id,
            subnet_id = subnet.id,
            tags = {"Name": f"nat-{i}"}
        )
        nat_gateways.append(nat)

    return igw, nat_gateways