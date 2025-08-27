import pulumi_aws as aws
from config import availavity_zones, public_cidrs, db_private_cidr, app_private_cidrs

def create_subnets(vpc) -> tuple[list, list]:
    public_subnets = create_subnets_block(vpc, public_cidrs)
    
    private_subnets = create_subnets_block(vpc, app_private_cidrs, "WebApp", True)
    private_subnets.append(create_single_subnet(vpc, db_private_cidr, "DB", True))

    return public_subnets, private_subnets

# Create multiple Subnets
def create_subnets_block(vpc, cidrs_block: list[str], identifier: str = "", are_private: bool = False) -> list:
    subnets = []
    protection = 'private' if are_private else 'public'

    for i, cidr in enumerate(cidrs_block):
        subnet = aws.ec2.Subnet(
            f"SN-{protection}-{identifier}{i}",
            vpc_id = vpc.id,
            cidr_block = cidr,
            availability_zone = availavity_zones[i % len(availavity_zones)],
            map_public_ip_on_launch = not are_private,
            tags={"Name": f"{protection}-{availavity_zones[i % len(availavity_zones)]}"}
        )
        subnets.append(subnet)

    return subnets

# Create single Subnet
def create_single_subnet(vpc, cidr: str, identifier: str = "", is_private: bool = False):
    protection = 'private' if is_private else 'public'
    
    subnet = aws.ec2.Subnet(
        f"SN-{protection}-{identifier}",
        vpc_id = vpc.id,
            cidr_block = cidr,
            availability_zone = availavity_zones[0],
            map_public_ip_on_launch = not is_private,
            tags={"Name": f"{protection}-{availavity_zones[0]}"}
    )

    return subnet