import pulumi_aws as aws

def create_web_server_ami(web_instance: aws.ec2.Instance) -> aws.ec2.AmiFromInstance:
    ami = aws.ec2.AmiFromInstance(
        "ami-WebCMS",
        source_instance_id=web_instance.id,
        name="ami-WebCMS",
        description="Lab AMI for Web Server",
        tags={
            "Name": "ami-WebCMS"
        }
    )

    return ami