import pulumi_aws as aws

def create_asg(private_subnets: list, launch_template: aws.ec2.LaunchTemplate, target_group: aws.lb.TargetGroup) -> aws.autoscaling.Group:
    asg = aws.autoscaling.Group(
        "ag-WebCMS",
        vpc_zone_identifiers=[s.id for s in private_subnets[:2]],
        desired_capacity=0,
        min_size=0,
        max_size=0,
        launch_template=aws.autoscaling.GroupLaunchTemplateArgs(
            id=launch_template.id,
            version="$Latest",
        ),
        target_group_arns=[target_group.arn],
        health_check_type="ELB",
        health_check_grace_period=90,
        metrics_granularity="1Minute",
        tags=[aws.autoscaling.GroupTagArgs(
            key="Name",
            value="auto-WebCMS",
            propagate_at_launch=True
        )]
    )

    return asg