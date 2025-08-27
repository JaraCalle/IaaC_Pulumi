import pulumi

cfg = pulumi.Config()

network_resources = {}

# VPC
vpc_name: str = cfg.require('vpcName')
# Cidr blocks
vpc_cidr: str = cfg.require('vpcCidr')
public_cidrs: list[str] = cfg.require_object('publicCidrs')
app_private_cidrs: list[str] = cfg.require_object('appPrivateCidrs')
db_private_cidr: str = cfg.require('dbPrivateCidr')

# Availability Zones
availavity_zones: list[str] = cfg.require_object('availabilityZones')

# Hosts
ami_id: str = cfg.require('amiId')
instance_type: str = cfg.require('instanceType')
# SSH keys
ssh_key_name: str = cfg.require('sshKeyName')