import pulumi
from config import network_resources
from loadBalancing.loadBalancer.load_balancer import create_load_balancer
from loadBalancing.loadBalancer.target_group import create_target_group
from loadBalancing.loadBalancer.security_group import create_lb_sg
from loadBalancing.autoScaling.ami import create_web_server_ami
from loadBalancing.autoScaling.launch_template import create_launch_template
from loadBalancing.autoScaling.autoscaling_group import create_asg


def initialize():
    # 1. Target Group
    tg_cms = create_target_group(network_resources["vpc"])

    # 2. Security group for Application Load Balancer
    sg_lb = create_lb_sg(network_resources["vpc"])

    # 3. Load Balancer
    alb, listener = create_load_balancer(network_resources["public_subnets"], sg_lb, tg_cms)

    # 4. Ami from i-WebServer
    ami_webcms = create_web_server_ami(network_resources["web_instance"])

    # 5. Launch template
    lt_webcms = create_launch_template(ami_webcms, network_resources["web_sg"])

    # 6. Auto Scaling Group
    asg_webcms = create_asg(network_resources["private_subnets"], lt_webcms, tg_cms)

    pulumi.export("load_balancer_dns", alb.dns_name)
