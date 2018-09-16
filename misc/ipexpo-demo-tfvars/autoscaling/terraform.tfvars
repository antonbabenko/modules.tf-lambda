terragrunt = {
  terraform {
    source = "git::git@github.com:terraform-aws-modules/terraform-aws-autoscaling.git"
  }

  include = {
    path = "${find_in_parent_folders()}"
  }
}

# The number of Amazon EC2 instances that should be running in the group
# type: string
desired_capacity = "1"

# Controls how health checking is done. Values are - EC2 and ELB
# type: string
health_check_type = "EC2"

# The EC2 image ID to launch
# type: string
image_id = "ami-03255d32a8bf59788"

# The size of instance to launch
# type: string
instance_type = "t2.small"

# The maximum size of the auto scale group
# type: string
max_size = "1"

# The minimum size of the auto scale group
# type: string
min_size = "0"

# Creates a unique name beginning with the specified prefix
# type: string
name = "modulestf-demo"

# A list of security group IDs to assign to the launch configuration
# type: list
security_groups = ["sg-9eb9c1e7"]

# A list of subnet IDs to launch resources in
# type: list
vpc_zone_identifier = ["subnet-6fe3d837", "subnet-9211eef5"]

# A list of elastic load balancer names to add to the autoscaling group names
# type: list
load_balancers = ["modulestf-demo"]
