import pulumi_aws as aws
from config import ami_id, instance_type, ssh_key_name

def create_web_server(private_subnet: aws.ec2.Subnet, web_sg: aws.ec2.SecurityGroup) -> aws.ec2.Instance:
    web_instance = aws.ec2.Instance(
        "i-webserver",
        instance_type=instance_type,
        vpc_security_group_ids=[web_sg.id],
        ami=ami_id,
        subnet_id=private_subnet.id,
        associate_public_ip_address=False,
        key_name=ssh_key_name,
        root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
            volume_size=8,
            volume_type="gp2"
        ),
        tags={"Name": "i-WebServer"}
    )

    return web_instance