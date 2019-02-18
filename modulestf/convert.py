import json
import logging
import random
import string
import uuid
from hashlib import md5
from pprint import pformat, pprint

import petname


# Class which represents modules.tf definition of resource
class Resource:
    def __init__(self, ref_id, type, text):
        self.ref_id = ref_id
        self.type = type
        self.text = text
        self.params = {}
        self.dependencies = []
        self.dynamic_params = {}

    def append_dependency(self, key):
        self.dependencies.append(key)

    def update_dynamic_params(self, name, value):
        self.dynamic_params.update({name: value})

    def update_params(self, value):
        self.params.update(value)

    def content(self):
        return {
            "ref_id": self.ref_id,
            "type": self.type,
            "text": self.text,
            "params": self.params,
            "dependencies": self.dependencies,
            "dynamic_params": self.dynamic_params
        }


# Generate human readable random names
def random_pet(words=2, separator="-"):
    return petname.generate(words, separator)


def random_password(length=12):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits

    return ''.join(random.choice(chars) for _ in range(length))


def get_node(G, node_id):
    try:
        return G.nodes.get(node_id)
    except (AttributeError, KeyError):
        return None


def get_node_attr(G, node_id, attribute):
    try:
        return G.nodes.get(node_id).get(attribute)
    except (AttributeError, KeyError):
        return None


def get_node_data(G, node_id, attribute):
    try:
        return get_node_attr(G, node_id, "data").get(attribute)
    except (AttributeError, KeyError):
        return None


def convert_graph_to_modulestf_config(graph):  # noqa: C901

    G = graph.G

    # logging.info(pprint(G.nodes.items(), indent=2))

    resources = []
    parsed_asg_id = set()
    warnings = set()

    supported_node_types = ["rds", "ec2", "elb", "sns", "sqs", "sg", "vpc"]  # "s3", "cloudfront",
    # supported_node_types = ["sg", "vpc"]

    for key, node_complete in G.nodes.items():

        node = node_complete.get("data")

        logging.info("\n========================================\nNode key = %s" % key)

        if node is None:
            logging.error("No node 'data' in node - %s" % pformat(node_complete))
            continue

        # logging.info("Node: {}".format(node))

        edges = G.adj[key]
        logging.info("Edges: {}".format(edges))

        if node.get("type") not in supported_node_types:
            warnings.add("node type %s is not implemented yet" % node.get("type"))
            continue

        logging.info(pformat(node, indent=2))

        vpc_id = node.get("vpc_id")
        sg_id = node.get("sg_id")
        asg_id = node.get("asg_id")
        elb_id = ""
        elb_type = ""

        if node.get("type") == "rds":

            r = Resource(key, "rds", node.get("text"))

            r.update_params({
                "isMultiAZ": node.get("multiAZ"),
                "db_subnet_group_name": "",
                "identifier": random_pet(),
                "username": random_pet(words=1),
                "password": random_password(),
                "allocated_storage": "5",
                "major_engine_version": "",
                "family": "",
                "backup_retention_period": "0",  # Disable backups to create DB faster
                "vpc_security_group_ids": [],
            })

            if vpc_id:
                r.append_dependency(vpc_id)
                r.update_dynamic_params("db_subnet_group_name",
                                        "terraform_output." + vpc_id + ".database_subnet_group")

            if sg_id:
                r.append_dependency(sg_id)
                r.update_dynamic_params("vpc_security_group_ids", "terraform_output." + sg_id + ".this_security_group_id.to_list")

            if node.get("engine"):
                r.update_params({
                    "engine": node.get("engine"),  # node.get("engine") has too many options (not just supported)
                    "port": "3306",
                    "engine_version": "5.7.19",
                    "major_engine_version": "5.7",
                    "family": "mysql5.7",
                })

            if node.get("instanceType") and node.get("instanceSize"):
                r.update_params({
                    "instanceType": "db." + node.get("instanceType", "") + "." + node.get("instanceSize", ""),
                })

            resources.append(r.content())

        if node.get("type") == "ec2":
            if asg_id:

                if asg_id not in parsed_asg_id:
                    # Find ELB/ALB in edges from or to ASG
                    if asg_id in G.adj:
                        tmp_edges = G.adj[asg_id]

                    for edge_id in tmp_edges:
                        if get_node_data(G, edge_id, "type") == "elb":
                            elb_id = get_node_data(G, edge_id, "id")
                            elb_type = get_node_data(G, edge_id, "elbType")

                            break

                    r = Resource(asg_id, "autoscaling", node.get("text"))

                    r.update_params({
                        "name": random_pet(),
                        "min_size": 0,
                        "max_size": 0,
                        "desired_capacity": 0,
                        "health_check_type": "EC2",
                        "image_id": "ami-00035f41c82244dab",
                        "vpc_zone_identifier": [],
                        "security_groups": [],
                    })

                    if vpc_id:
                        r.append_dependency(vpc_id)
                        r.update_dynamic_params("vpc_zone_identifier", "terraform_output." + vpc_id + ".public_subnets")

                    if sg_id:
                        r.append_dependency(sg_id)
                        r.update_dynamic_params("security_groups", "terraform_output." + sg_id + ".this_security_group_id.to_list")

                    if elb_id and elb_type == "application":
                        r.update_params({
                            "target_group_arns": [],
                        })
                        r.append_dependency(elb_id)
                        r.update_dynamic_params("target_group_arns",
                                                "terraform_output." + elb_id + ".target_group_arns")

                    if node.get("instanceType") and node.get("instanceSize"):
                        r.update_params({
                            "instanceType": node.get("instanceType", "") + "." + node.get("instanceSize", ""),
                        })

                    resources.append(r.content())

                parsed_asg_id.add(asg_id)
            else:
                r = Resource(key, "ec2-instance", node.get("text"))

                r.update_params({
                    "name": random_pet(),
                })

                if node.get("instanceType") and node.get("instanceSize"):
                    r.update_params({
                        "instanceType": node.get("instanceType", "") + "." + node.get("instanceSize", ""),
                    })

                resources.append(r.content())

        if node.get("type") == "elb":
            # for edge_id in edges:
            #     if get_node_data(G, edge_id, "group_nodes"):
            #         asg_id = edge_id
            #         break

            if node.get("elbType") == "application":
                r = Resource(key, "alb", node.get("text"))

                r.update_params({
                    "load_balancer_name": random_pet(),
                    "logging_enabled": "false",
                })

                if vpc_id:
                    r.append_dependency(vpc_id)
                    r.update_dynamic_params("subnets", "terraform_output." + vpc_id + ".public_subnets")
                    r.update_dynamic_params("vpc_id", "terraform_output." + vpc_id + ".vpc_id")

                if sg_id:
                    r.append_dependency(sg_id)
                    r.update_dynamic_params("security_groups", "terraform_output." + sg_id + ".this_security_group_id.to_list")

            else:
                r = Resource(key, "elb", node.get("text"))

                r.update_params({
                    "name": random_pet(),
                })

                # @todo: Use https://github.com/virtuald/pyhcl to convert to valid HCL in tfvars
                # r.update_params({
                #     "listener": [{
                #         "instance_port": "80",
                #         "instance_protocol": "HTTP",
                #         "lb_port": "80",
                #         "lb_protocol": "HTTP"
                #     }],
                #     "health_check": [{
                #         "target": "HTTP:80/",
                #         "interval": 30,
                #         "healthy_threshold": 2,
                #         "unhealthy_threshold": 2,
                #         "timeout": 5
                #     }],
                # })

                if vpc_id:
                    r.append_dependency(vpc_id)
                    r.update_dynamic_params("subnets", "terraform_output." + vpc_id + ".public_subnets")

                if sg_id:
                    r.append_dependency(sg_id)
                    r.update_dynamic_params("security_groups", "terraform_output." + sg_id + ".this_security_group_id.to_list")

            resources.append(r.content())

        if node.get("type") == "s3":
            r = Resource(key, "s3", node.get("text"))

            resources.append(r.content())

        if node.get("type") == "cloudfront":
            r = Resource(key, "cloudfront", node.get("text"))

            resources.append(r.content())

        if node.get("type") == "sns":
            r = Resource(key, "sns", node.get("text"))

            resources.append(r.content())

        if node.get("type") == "sqs":
            r = Resource(key, "sqs", node.get("text"))

            r.update_params({
                "fifoQueue": node.get("queueType") == "fifo",
            })

            resources.append(r.content())

        if node.get("type") == "sg":
            r = Resource(key, "security-group", node.get("text"))

            r.update_params({
                "name": random_pet(),
            })

            if vpc_id:
                r.append_dependency(vpc_id)
                r.update_dynamic_params("vpc_id", "terraform_output." + vpc_id + ".vpc_id")

            resources.append(r.content())

        if node.get("type") == "vpc":
            r = Resource(key, "vpc", node.get("text"))

            r.update_params({
                "name": random_pet(),
                "cidr": "",
                "azs": [],
                "public_subnets": [],
                "private_subnets": [],
                "database_subnets": [],
            })

            resources.append(r.content())

    logging.info(pformat(resources))

    if len(warnings):
        logging.warning("; ".join(warnings))

    return json.dumps(resources)
