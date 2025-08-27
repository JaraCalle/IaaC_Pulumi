import pulumi_aws as aws

def create_target_group(vpc: aws.ec2.Vpc) -> aws.lb.TargetGroup:
    tg = aws.lb.TargetGroup(
        "tg-CMS",
        port=80,
        protocol="HTTP",
        target_type="instance",
        vpc_id=vpc.id,
        health_check=aws.lb.TargetGroupHealthCheckArgs(
            path="/",
            healthy_threshold=2,
            interval=10,
            matcher="200,300-399"
        ),
        tags={"Name": "tg-CMS"}
    )
    
    return tg