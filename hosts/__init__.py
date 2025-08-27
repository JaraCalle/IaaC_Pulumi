import pulumi
from hosts.bastion.security_group import create_bastion_sg
from hosts.bastion.instance import create_bastion_instance
from hosts.db.security_group import create_db_sg
from hosts.db.instance import create_db_instance
from hosts.webApp.security_group import create_web_sg
from hosts.webApp.instance import create_web_server
from config import network_resources

def initialize():
    # === Bastion Host ===
    bastion_sg = create_bastion_sg(network_resources["vpc"])
    bastion = create_bastion_instance(network_resources["public_subnets"][0], bastion_sg)

    network_resources["bastion"] = bastion

    # === DataBase Instance ===
    db_sg = create_db_sg(network_resources["vpc"])
    db_instance = create_db_instance(network_resources["private_subnets"][2], db_sg)

    network_resources["db_instance"] = db_instance

    # === WebApp Server ===
    web_sg = create_web_sg(network_resources["vpc"])
    web_instance = create_web_server(network_resources["private_subnets"][0], web_sg)

    network_resources["web_sg"] = web_sg
    network_resources["web_instance"] = web_instance

    pulumi.export("bastion_public_ip", bastion.public_ip)
    pulumi.export("db_private_ip", db_instance.private_ip)
    pulumi.export("web_private_ip", web_instance.private_ip)
