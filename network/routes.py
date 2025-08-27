import pulumi_aws as aws

def create_routes(vpc, igw, nat_gateways: list, public_subnets: list, private_subnets: list) -> None:
    # Pubic table routes
    public_rt = aws.ec2.RouteTable(
        "public-rt",
        vpc_id = vpc.id,
        tags = {"Name": "public-rt"}
    )

    aws.ec2.Route(
        "public-default-route",
        route_table_id = public_rt.id,
        destination_cidr_block = "0.0.0.0/0",
        gateway_id = igw.id
    )

    for subnet in public_subnets:
        aws.ec2.RouteTableAssociation(
            f"public-rt-assoc-{subnet._name}",
            subnet_id = subnet.id,
            route_table_id = public_rt.id 
        )

    # Private tables (One per Nat/AZ)
    for i, subnet in enumerate(private_subnets):
        rt = aws.ec2.RouteTable(
            f"private-rt-{i}",
            vpc_id = vpc.id,
            tags = {"Name": f"private-rt-{i}"}
        )

        aws.ec2.Route(
            f"private-default-route-{i}",
            route_table_id = rt.id,
            destination_cidr_block = "0.0.0.0/0",
            nat_gateway_id = nat_gateways[i % len(nat_gateways)].id
        )

        aws.ec2.RouteTableAssociation(
            f"private-rt-assoc-{i}",
            subnet_id = subnet.id,
            route_table_id = rt.id
        )