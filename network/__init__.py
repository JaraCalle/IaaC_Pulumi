import pulumi
from config import network_resources
from network.vpc import create_vpc
from network.subnets import create_subnets
from network.igw_nat import create_igw_and_nats
from network.routes import create_routes

def initialize():
    # 1. Create vpc
    vpc = create_vpc()
    network_resources["vpc"] = vpc

    # 2. Create subnets
    public_subnets, private_subnets = create_subnets(vpc)
    network_resources["public_subnets"] = public_subnets
    network_resources["private_subnets"] = private_subnets

    # 3. Create IGW & NATs
    igw, nat_gateways = create_igw_and_nats(vpc, public_subnets)
    network_resources["igw"] = igw
    network_resources["nat_gateways"] = nat_gateways
    
    # 4. Create routes
    create_routes(vpc, igw, nat_gateways, public_subnets, private_subnets)


    pulumi.export("vpc_id", vpc.id)
    pulumi.export("public_subnets", [s.id for s in public_subnets])
    pulumi.export("private_subnets", [s.id for s in private_subnets])
