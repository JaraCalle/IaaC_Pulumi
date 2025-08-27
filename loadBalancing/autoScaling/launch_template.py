import pulumi_aws as aws
from config import instance_type

def create_launch_template(ami: aws.ec2.AmiFromInstance, sg_web: aws.ec2.SecurityGroup) -> aws.ec2.LaunchTemplate:
    launch_template = aws.ec2.LaunchTemplate(
        "template-WebCMS",
        name="template-WebCMS",
        description="Template for web cms",
        image_id=ami.id,
        instance_type=instance_type,
        vpc_security_group_ids=[sg_web.id],
        tag_specifications=[aws.ec2.LaunchTemplateTagSpecificationArgs(
            resource_type="instance",
            tags={"Name": "webcms-instance"}
        )]
    )

    return launch_template