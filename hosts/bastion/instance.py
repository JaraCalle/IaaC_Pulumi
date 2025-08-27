import pulumi_aws as aws
from config import ami_id, instance_type, ssh_key_name

def create_bastion_instance(subnet, security_group) -> aws.ec2.Instance:
    bastion = aws.ec2.Instance(
        "bastion-instance",
        ami=ami_id,
        instance_type=instance_type,
        subnet_id=subnet.id,
        vpc_security_group_ids=[security_group.id],
        key_name=ssh_key_name,
        associate_public_ip_address=True,
        tags={"Name": "bastion-host"}
    )
    
    return bastion