import pulumi_aws as aws

def create_load_balancer(public_subnets: list, sg_lb: aws.ec2.SecurityGroup, target_group: aws.lb.TargetGroup) -> tuple[aws.lb.LoadBalancer, aws.lb.Listener]:
    alb = aws.lb.LoadBalancer(
        "lb-WebCMS",
        internal=False,
        load_balancer_type="application",
        security_groups=[sg_lb.id],
        subnets=[s.id for s in public_subnets],
        tags={"Name": "lb-WebCMS"}
    )

    # Listener
    listener = aws.lb.Listener(
        "lb-listener",
        load_balancer_arn=alb.arn,
        port=80,
        protocol="HTTP",
        default_actions=[
            aws.lb.ListenerDefaultActionArgs(
                type="forward",
                target_group_arn=target_group.arn
            )
        ]
    )

    return alb, listener