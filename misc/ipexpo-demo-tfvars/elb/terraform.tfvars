terragrunt = {
  terraform {
    source = "git::git@github.com:terraform-aws-modules/terraform-aws-elb.git"
  }

  include = {
    path = "${find_in_parent_folders()}"
  }
}

# A health check block
# type: list
health_check = [
  {
    target              = "HTTP:80/"
    interval            = 30
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
  },
]

# If true, ELB will be an internal ELB
# type: string
internal = "false"

# A list of listener blocks
# type: list
listener = [{
  instance_port     = "80"
  instance_protocol = "HTTP"
  lb_port           = "80"
  lb_protocol       = "HTTP"
}]

# The name of the ELB
# type: string
name = "modulestf-demo"

# A list of security group IDs to assign to the ELB
# type: list
security_groups = ["sg-9eb9c1e7"]

# A list of subnet IDs to attach to the ELB
# type: list
subnets = ["subnet-6fe3d837", "subnet-9211eef5"]
