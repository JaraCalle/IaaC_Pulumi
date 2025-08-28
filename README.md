# Requirements
1. **Pulumi**
2. **Python 3**
3. **AWS CLI**
4. **AWS Laboratory**

# Step by Step
## First installing and configurations

1. Install **Pulumi**

``` bash
curl -fsSL https://get.pulumi.com | sh
```

> you can verify the correct installation of Pulumi restarting the terminal and running 
> `pulumi version`

2. Install **AWS CLI**

A recommendation is to move to the /Download folder, but it's not mandatory

``` bash
# Download aws with curl
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Unzip the Download
unzip awscliv2.zip
```

> [!info]
> If you don't have unzip installed, you can install it with your packages manager. For instance in Debian/Ubuntu based `sudo apt install unzip`

``` bash
# Install aws
sudo ./aws/install
```

> you can verify the correct installation of AWS restarting the terminal or running 
> `aws --version`

3. Configure the **AWS CLI** credential and keys

When you've installed AWS, you must configure the credentials of your AWS, in this case your credential will be in AWS Academy in the path:  **Course-name** > **Module** > **AWS Academy Learner Lab** > **Launch AWS Academy Learner Lab**.

   -  First Start your Lab
   ![[StartLab.jpg]]

> Wait until the AWS indicator turns green

   - Then click on AWS Details 

![[AWSDetails.png]]

This will show your credentials when you click on **Show** to display them.

- One of the methods to configure you CLI is setting your credentials as default on you AWS CLI. To do this you should follow this commands:

``` bash
# Create if not exist .aws on root
mkdir -p ~/.aws

# Set your credentials
cat > ~/.aws/credentials <<'EOF'
[default]
aws_access_key_id=<PLACE_YOUR_aws_access_key_id>
aws_secret_access_key=<PLACE_YOUR_aws_secret_access_key>
aws_session_token=<PLACE_YOUR_aws_session_token>
EOF

# Set your default configs
cat > ~/.aws/config <<'EOF'
[default]
region = us-east-1
output = json
EOF
```

> [!warning]
> Remember to place your credentials on the respective spaces!

> you can check the AWS connection with the command `aws sts get-caller-identity`, it should respond with a JSON like this
>
~~~ json
{
    "UserId": "AROARPY6XUNE7B7TFPNA:user123123=",
    "Account": "123123412341",
    "Arn": "arn:aws:sts::102606807881:assumed role/voclabs/user123123="
}
~~~
> If this doesn't happen then check your AWS Lab to be running and your credentials placed on the command "_Set your credentials_"


## Start Pulumi Project
First you have to start a console on the folder where you want to save the project.
> [!tip]
> ~~~ bash
> 	# Create a folder
> 	mkdir lab-vpc
> 	
> 	# Move to the folder
> 	cd lab-vpc
> ~~~

1. To create the project run the following command
~~~ bash
# Define new Pulumi python Project
pulumi new aws-python --force
~~~

This will open this Pulumi _Sign In_ page on your browser 
![[PulimiLogin.png]]
Just follow the process and then go back to the console.

2. In the console select the following options

**Project name:** vpc-lab
**Project description:** Infrastructure for vpc-lab
**Stack name:** dev
**The toolchain to use for installing dependencies and running the program**: pip
**The AWS region to deploy into (aws:region)**: _Press enter_

> [!Success]
> Now you can open this folder with the code editor of your preference an you will see this structure created by default
> ![[Captura1.png]]

## Create and configure VPC and network

1. Set a new config on the Pulumi.dev.yaml

~~~
pulumi config set vpc_name DrupalCMS-vpc
~~~

Go to Pulumi.dev.yaml, you should see something like this:
~~~ yaml
config:
	aws:region: us-east-1
	vpc-lab:vpcName: DrupalCMS-vpc
	vpc-lab:vpcCidr: 172.16.0.0/16
	vpc-lab:publicCidrs:
		- 172.16.1.0/24
		- 172.16.4.0/24
	vpc-lab:appPrivateCidrs:
		- 172.16.2.0/24
		- 172.16.5.0/24
	vpc-lab:dbPrivateCidr: 172.16.3.0/24
	vpc-lab:availabilityZones:
	- us-east-1a
	- us-east-1b
	vpc-lab:amiId: ami-0fc5d935ebf8bc3bc
	vpc-lab:instanceType: t2.micro
	vpc-lab:sshKeyName: si3006
~~~

the last line, `vpc-lab:vpcName: DrupalCMS-vpc`, is what you added with the previous command, it structure is **\<project-name>:\<var-name>: \<value>**

Now you have to add all the Cidrs that we will use during the project
- **VPC**: 172.16.0.0/16
- **Publics**: 172.16.1.0/24 | 172.16.4.0/24
- **Web App Privates**: 172.16.2.0/24 | 172.16.5.0/24
- **DB Private**: 172.16.3.0/24

You also need to add the availability zones
- us-east-1a
- us-east-1b

2. Create a Config file on the project root

~~~ python
import pulumi

cfg = pulumi.Config()

# VPC
vpc_name: str = cfg.require('vpcName')

# Cidr blocks
vpc_cidr: str = cfg.require('vpcCidr')
public_cidrs: list[str] = cfg.require_object('publicCidrs')
app_private_cidrs: list[str] = cfg.require_object('appPrivateCidrs')
db_private_cidr: str = cfg.require('dbPrivateCidr')

# Availability Zones
availavity_zones: list[str] = cfg.require_object('availabilityZones')
~~~

3. Create a Network module

This will be a folder in your root project named as network. This folder will contain the following python files:

- _vpc.py_
~~~ python
import pulumi_aws as aws
from config import vpc_name, vpc_cidr

def create_vpc():
	vpc = aws.ec2.Vpc(
		vpc_name,
		cidr_block=vpc_cidr,
		enable_dns_support=True,
		enable_dns_hostnames=True,
		tags={"Name": vpc_name}
	)

	return vpc
~~~

- _subnets.py_
~~~ python
import pulumi_aws as aws
from config import availavity_zones, public_cidrs, db_private_cidr, app_private_cidrs

def create_subnets(vpc) -> tuple[list, list]:
	public_subnets = create_subnets_block(vpc, public_cidrs)
	private_subnets = create_subnets_block(vpc, app_private_cidrs, "WebApp", True)
	private_subnets.append(create_single_subnet(vpc, db_private_cidr, "DB", True))
	
	return public_subnets, private_subnets

  

# Create multiple Subnets
def create_subnets_block(vpc, cidrs_block: list[str], identifier: str = "", are_private: bool = False) -> list:
	subnets = []
	protection = 'private' if are_private else 'public'
	
	for i, cidr in enumerate(cidrs_block):
		subnet = aws.ec2.Subnet(
			f"SN-{protection}-{identifier}{i}",
			vpc_id = vpc.id,
			cidr_block = cidr,
			availability_zone = availavity_zones[i % len(availavity_zones)],
			map_public_ip_on_launch = not are_private,
			tags={"Name": f"{protection}-{availavity_zones[i % len(availavity_zones)]}"}
		)
		
		subnets.append(subnet)
	return subnets

  
# Create single Subnet
def create_single_subnet(vpc, cidr: str, identifier: str = "", is_private: bool = False):
	protection = 'private' if is_private else 'public'
	subnet = aws.ec2.Subnet(
		f"SN-{protection}-{identifier}",
		vpc_id = vpc.id,
		cidr_block = cidr,
		availability_zone = availavity_zones[0],
		map_public_ip_on_launch = not is_private,
		tags={"Name": f"{protection}-{availavity_zones[0]}"}
	)
	
	return subnet
~~~

- _routes.py_
~~~ python
import pulumi_aws as aws

  

def create_routes(vpc, igw, nat_gateways: list, public_subnets: list, private_subnets: list) -> None:

# Pubic table routes
public_rt = aws.ec2.RouteTable(
	"public-rt",
	vpc_id = vpc.id,
	tags = {"Name": "public-rt"}
)

aws.ec2.Route(
	"public-default-route",
	route_table_id = public_rt.id,
	destination_cidr_block = "0.0.0.0/0",
	gateway_id = igw.id
)
 
for subnet in public_subnets:
	aws.ec2.RouteTableAssociation(
		f"public-rt-assoc-{subnet._name}",
		subnet_id = subnet.id,
		route_table_id = public_rt.id
	)

# Private tables (One per Nat/AZ)
for i, subnet in enumerate(private_subnets):
	rt = aws.ec2.RouteTable(
		f"private-rt-{i}",
		vpc_id = vpc.id,
		tags = {"Name": f"private-rt-{i}"}
	)

aws.ec2.Route(
	f"private-default-route-{i}",
	route_table_id = rt.id,
	destination_cidr_block = "0.0.0.0/0",
	nat_gateway_id = nat_gateways[i % len(nat_gateways)].id
)  

aws.ec2.RouteTableAssociation(
	f"private-rt-assoc-{i}",
	subnet_id = subnet.id,
	route_table_id = rt.id
)
~~~

- _igw_nat.py_
~~~ python
import pulumi_aws as aws

def create_igw_and_nats(vpc, public_subnets: list) -> tuple[aws.ec2.InternetGateway,list]:

	igw = aws.ec2.InternetGateway(
		"cms-igw",
		vpc_id = vpc.id,
		tags = {"Name": "cms-igw"}
	)
	
	nat_gateways = []
	
	for i, subnet in enumerate(public_subnets):
		# Elastic IP
		eip = aws.ec2.Eip(
			f"nat-gw-{i}",
			domain = "vpc",
			tags = {"Name": f"nat-eip-{i}"}
		)
		
		# NatGateway
		nat = aws.ec2.NatGateway(
			f"nat-gw-{i}",
			allocation_id = eip.id,
			subnet_id = subnet.id,
			tags = {"Name": f"nat-{i}"}
		)
		
		nat_gateways.append(nat)
	
	return igw, nat_gateways
~~~

- \_\_init\_\_.py
~~~ python
import pulumi
from config import network_resources
from network.vpc import create_vpc
from network.subnets import create_subnets
from network.igw_nat import create_igw_and_nats
from network.routes import create_routes

  

def initialize():
# 1. Create vpc
vpc = create_vpc()
network_resources["vpc"] = vpc

# 2. Create subnets
public_subnets, private_subnets = create_subnets(vpc)
network_resources["public_subnets"] = public_subnets
network_resources["private_subnets"] = private_subnets

# 3. Create IGW & NATs
igw, nat_gateways = create_igw_and_nats(vpc, public_subnets)
network_resources["igw"] = igw
network_resources["nat_gateways"] = nat_gateways

# 4. Create routes
create_routes(vpc, igw, nat_gateways, public_subnets, private_subnets)

pulumi.export("vpc_id", vpc.id)
pulumi.export("public_subnets", [s.id for s in public_subnets])
pulumi.export("private_subnets", [s.id for s in private_subnets])
~~~


- \_\_main\_\_.py
~~~ python
import network

network.initialize()
~~~

### Expected project structure
At this moment your project structure may looks like this:

![[Captura2.png]]

### Upload the changes to AWS
Now you can initialize your project on AWS running the following command on your terminal:

>[!warning]
>Before running pulumi up, make sure you have elastic IPs available in your AWS account (the maximum number of elastic IPs per lab is 5).

~~~ bash
pulumi up
~~~


## Create Hosts
Create the module hosts folder from the root folder of your project

~~~ bash
# create folders
mkdir -p hosts
mkdir -p hosts/bastion
mkdir -p hosts/db
mkdir -p hosts/webApp

cd hosts
touch __init__.py
~~~

- \_\_init\_\_.py

~~~ python
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
~~~

### Bastion Host 
In the folder `hosts/bastion` create the following files
- \_\_init.py\_\_

- _instance.py_
~~~ python
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
~~~

- _security\_group.py_
~~~ python
import pulumi_aws as aws

def create_bastion_sg(vpc) -> aws.ec2.SecurityGroup:
	bastion_sg = aws.ec2.SecurityGroup(
		"bastion-sg",
		vpc_id=vpc.id,
		description="Security group for Bastion Host",
		ingress=[
			aws.ec2.SecurityGroupIngressArgs(
			protocol="tcp",
			from_port=22,
			to_port=22,
			cidr_blocks=["0.0.0.0/0"]
	)
	],
		egress=[
		aws.ec2.SecurityGroupEgressArgs(
			protocol="-1",
			from_port=0,
			to_port=0,
			cidr_blocks=["0.0.0.0/0"]
		)
		],
		tags={"Name": "bastion-sg"}
	)
	
	return bastion_sg
~~~
### DB Host
In the folder `hosts/db` create the following files
- \_\_init.py\_\_

- _instance.py_

~~~ python
import pulumi_aws as aws
from config import ami_id, instance_type, ssh_key_name

def create_db_instance(subnet, security_group) -> aws.ec2.Instance:
	db_instance = aws.ec2.Instance(
		"db-instance",
		ami=ami_id,
		instance_type=instance_type,
		subnet_id=subnet.id,
		vpc_security_group_ids=[security_group.id],
		key_name=ssh_key_name,
		associate_public_ip_address=False,
		tags={"Name": "db-server"}
	)
	
	return db_instance
~~~

- _security\_group.py_

~~~ python
import pulumi_aws as aws
from config import app_private_cidrs

def create_db_sg(vpc: aws.ec2.Vpc) -> aws.ec2.SecurityGroup:
	db_sg = aws.ec2.SecurityGroup(
		"db-sg",
		vpc_id=vpc.id,
		description="Security group for MySQL database",
		ingress=[
		aws.ec2.SecurityGroupIngressArgs(
			protocol="tcp",
			from_port=3306,
			to_port=3306,
			cidr_blocks=app_private_cidrs
		),
		aws.ec2.SecurityGroupIngressArgs(
			protocol="tcp",
			from_port=22,
			to_port=22,
			cidr_blocks=["172.16.1.0/24"]
		)
		],
		egress=[
			aws.ec2.SecurityGroupEgressArgs(
			protocol="-1",
			from_port=0,
			to_port=0,
			cidr_blocks=["0.0.0.0/0"],
		)
		],
		tags={"Name": "db-sg"}
	)
	
	return db_sg
~~~

### Web App
In the folder `hosts/webApp` create the following files
- \_\_init.py\_\_

- _instance.py_
~~~ python
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
~~~

- _security\_group.py_

~~~ python
import pulumi_aws as aws
from config import public_cidrs

def create_web_sg(vpc: aws.ec2.Vpc) -> aws.ec2.SecurityGroup:
	web_sg = aws.ec2.SecurityGroup(
	"webcms-sg",
	vpc_id=vpc.id,
	description="Enable HTTP Access for Web Servers",
	ingress=[
		aws.ec2.SecurityGroupIngressArgs(
		protocol="tcp",
		from_port=80,
		to_port=80,
		cidr_blocks=public_cidrs
		),
		aws.ec2.SecurityGroupIngressArgs(
		protocol="tcp",
		from_port=22,
		to_port=22,
		cidr_blocks=["172.16.1.0/24"]
		)
	],
	egress=[
		aws.ec2.SecurityGroupEgressArgs(
		protocol="-1",
		from_port=0,
		to_port=0,
		cidr_blocks=["0.0.0.0/0"],
	)
	],
	tags={"Name": "webcms-sg"}
	)
	
	return web_sg
~~~

### Upload the changes to AWS

1. Modify the file \_\_main\_\_.py
~~~ python
import network
import hosts

hosts.initialize()
network.initialize()
~~~~

2. Create a .pem key on your AWS Account

~~~ bash
aws ec2 create-key-pair \
    --key-name si3006 \
    --query 'KeyMaterial' \
    --output text > si3006.pem
~~~

3. Adjust permission for the key
~~~ bash
chmod 400 si3006.pem
~~~

Run this command to create the instances defined on this step
~~~ bash
pulumi up
~~~

### Configure Each Instance
In the files for this tutorial you will have a si3006.pem this is the ssh key used to connect to each Instance

#### Bastion Host
1. Connect to you bastion Host with ssh

~~~ bash
# Send the ssh key to the bastion machine
scp -i si3006.pem si3006.pem ubuntu@<Bastion_public_ip>:/home/ubuntu
scp -i si3006.pem drupal_backup.sql ubuntu@<Bastion_public_ip>:/home/ubuntu
scp -i si3006.pem drupal.tar.gz ubuntu@<Bastion_public_ip>:/home/ubuntu

# Connect via ssh
ssh -i si3006.pem ubuntu@<Bastion_public_ip>
~~~

2. 
#### DB Host
First you have to send the `drupal_backup.sql` from the bastion Host to the DB host. Run the following command from your bastion Host

~~~ bash
scp -i si3006.pem drupal_backup.sql ubuntu@<DB_Private_IP>:/home/ubuntu/
~~~

1.  Update the operative system and packages
~~~ bash
# Download updates
sudo apt update

# Install updates
sudo apt upgrade
~~~

2. Download mariaDB
~~~ bash
sudo apt-get install mariadb-server
~~~

3. Install the database
~~~ bash
sudo mysql_secure_installation
~~~

Press enter, to indicate that we do not have root password configured yet. Then, you can see a set of questions to which you can answer yes as shown in the figure at below.

![[MYsqlInstall.png]]

4. Configure the database

~~~ sql
GRANT ALL ON *.* TO 'admin'@'localhost' IDENTIFIED BY 'pass123' WITH GRANT OPTION;
FLUSH PRIVILEGES;

CREATE DATABASE drupal DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;

CREATE USER 'wpuser'@'172.16.2.%' IDENTIFIED BY 'wppassword';
CREATE USER 'wpuser'@'172.16.5.%' IDENTIFIED BY 'wppassword';
GRANT ALL PRIVILEGES ON *.* TO 'wpuser'@'172.16.2.%';
GRANT ALL PRIVILEGES ON *.* TO 'wpuser'@'172.16.5.%';
FLUSH PRIVILEGES;

exit
~~~

~~~ bash
# Create the database
mariadb -u admin -p -e "CREATE DATABASE drupal_db;"

# Import the sql script 
sed 's/utf8mb4_0900_ai_ci/utf8mb4_general_ci/g' drupal_backup.sql | mysql -u admin -p drupal_db

exit
~~~

#### Web Server
First you have to send the `drupal.tar.gz` from the bastion Host to the Web Server. Run the following command from your bastion Host

~~~ bash
scp -i si3006.pem drupal.tar.gz ubuntu@<IP_Private_WebSever>:/home/ubuntu/
~~~

1.  Update the operative system and packages
~~~ bash
# Download updates
sudo apt update

# Install updates
sudo apt upgrade
~~~

2. Install required packages
~~~ bash
sudo apt install -y apache2 mariadb-client unzip tar nodejs npm composer

sudo apt install php8.3 php8.3-cli php8.3-common php8.3-mysql php8.3-xml php8.3-mbstring php8.3-gd php8.3-curl php8.3-zip -y


sudo a2enmod rewrite
sudo systemctl restart apache2

sudo nano /etc/apache2/sites-available/drupal.conf
~~~

3. Unzip the drupal
~~~ bash
# Unzip the drupal Web App
tar -xvzf drupal.tar.gz
# Move the folder
sudo mv drupal.tar.gz /var/www/

# Create the config
sudo nano /etc/apache2/sites-available/drupal.conf
~~~

drupal.conf
~~~ conf
<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/drupal/web

    <Directory /var/www/drupal/web>
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
~~~

enable drupal.conf
~~~ bash
sudo a2ensite drupal.conf
sudo a2dissite 000-default.conf
sudo systemctl reload apache2

sudo chown -R www-data:www-data /var/www/drupal
~~~

modify the settings of drupal
~~~ bash
sudo nano /var/www/drupal/web/sites/default/settings.php
~~~

you have to modify this variable on the file
~~~ php
$databases['default']['default'] = array (
  'database' => 'drupal',
  'username' => 'wpuser',
  'password' => 'wppassword',
  'prefix' => '',
  'host' => '172.16.2.254', # PLACE YOUR DB PRIVATE IP!!!!
  'port' => '3306',
  'isolation_level' => 'READ COMMITTED',
  'driver' => 'mysql',
  'namespace' => 'Drupal\\mysql\\Driver\\Database\\mysql',
  'autoload' => 'core/modules/mysql/src/Driver/Database/mysql/',
);
~~~

## Load Balancer
Create the module loadBalancing folder from the root folder of your project

~~~ bash
mkdir -p loadBalancing
mkdir -p loadBalancing/autoScaling
mkdir -p loadBalancing/loadBalancer

cd loadBalancing
touch __init__.py
~~~

- \_\_init\_\_.py
~~~ python
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
~~~

### Define the AutoScaling
- _ami.py_
~~~ python
import pulumi_aws as aws

def create_web_server_ami(web_instance: aws.ec2.Instance) -> aws.ec2.AmiFromInstance:
	ami = aws.ec2.AmiFromInstance(
		"ami-DefWebCMS",
		source_instance_id=web_instance.id,
		name="ami-DefWebCMS",
		description="Lab AMI for Web Server",
		tags={
		"Name": "ami-DefWebCMS"
		}
	) 
	
	return ami
~~~

- _autoscaling\_group.py_
~~~ python
import pulumi_aws as aws

def create_asg(private_subnets: list, launch_template: aws.ec2.LaunchTemplate, target_group: aws.lb.TargetGroup) -> aws.autoscaling.Group:
	asg = aws.autoscaling.Group(
		"ag-WebCMS",
			vpc_zone_identifiers=[s.id for s in private_subnets[:2]],
			desired_capacity=2,
			min_size=2,
			max_size=2,
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
~~~

- _launch\_template.py_
~~~ python
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
~~~

### Define the loadBalancer

- _load\_balancer.py_
~~~ python
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
~~~

- _security\_group.py_

~~~ python
import pulumi_aws as aws  

def create_lb_sg(vpc: aws.ec2.Vpc) -> aws.ec2.SecurityGroup:
	sg_lb = aws.ec2.SecurityGroup(
		"lb-sg",
		vpc_id=vpc.id,
		description="Allow HTTP from anywhere",
		ingress=[
			aws.ec2.SecurityGroupIngressArgs(
			protocol="tcp",
			from_port=80,
			to_port=80,
			cidr_blocks=["0.0.0.0/0"],
			ipv6_cidr_blocks=["::/0"]
		)
		],
		egress=[
			aws.ec2.SecurityGroupEgressArgs(
			protocol="-1",
			from_port=0,
			to_port=0,
			cidr_blocks=["0.0.0.0/0"]
			)
		],
		tags={"Name": "lb-sg"}
	)
	
	return sg_lb
~~~

- _target\_group.py_

~~~ python
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
~~~


> [!success]
> Finally run
> `pulumi up`

Now you can enter to you load balancer DNS and you will see your web application running.