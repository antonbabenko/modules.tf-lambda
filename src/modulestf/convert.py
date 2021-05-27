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


# Security group helper - port range
def convert_port_range(port_range):
    group = port_range.split("-")
    return group[0], group[1 if len(group) > 1 else 0]


# Security group helper - protocol
def convert_protocol(protocol):
    return {"tcp": 6, "udp": 16, "icmp": 1, "icmpv6": 58}.get(protocol, "-1")


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

    logging.info(pprint(G.nodes.items(), indent=2))

    resources = []
    node_types = set()
    parsed_asg_id = set()
    warnings = set()

    supported_node_types = ["rds", "ec2", "elb", "sns", "sqs", "sg", "vpc", "s3", "redshift", "dynamodb", "cloudfront", "lambda", "vpngateway", "apigateway"]
    # supported_node_types = ["sg", "vpc"]

    for key, node_complete in G.nodes.items():

        node = node_complete.get("data")
        node_text = node_complete.get("text")

        logging.info("\n========================================\nNode key = %s" % key)

        if node is None:
            logging.warning("No node 'data' in node - %s" % pformat(node_complete))
            continue

        logging.info("Node: {}".format(node))

        # edges = G.adj[key]
        # logging.info("Edges: {}".format(edges))

        if node.get("type") not in supported_node_types:
            warnings.add("node type %s is not implemented yet" % node.get("type"))
            continue

        logging.info(pformat(node, indent=2))

        vpc_id = node.get("vpc_id")
        sg_id = node.get("sg_id")
        asg_id = node.get("asg_id")
        node_types.add(node.get("type"))

        elb_id = ""
        elb_type = ""
        tmp_edges = []

        if node.get("type") == "rds" and node.get("engine") in ["aurora-mysql", "aurora-postgresql"]:
            r = Resource(key, "rds-aurora", node_text)

            r.update_params({
                "isMultiAZ": node.get("multiAZ"),
                "db_subnet_group_name": "",
                "identifier": random_pet(),
                "username": random_pet(words=1),
                "password": random_password(),
                "allocated_storage": 5,
                "replica_count": 0,
                "vpc_id": "",
                "vpc_security_group_ids": [],
            })

            if vpc_id:
                r.append_dependency(vpc_id)
                r.update_dynamic_params("db_subnet_group_name",
                                        "dependency." + vpc_id + ".outputs.database_subnet_group")
                r.update_dynamic_params("vpc_id",
                                        "dependency." + vpc_id + ".outputs.vpc_id")

            if sg_id:
                r.append_dependency(sg_id)
                r.update_dynamic_params("vpc_security_group_ids",
                                        "[dependency." + sg_id + ".outputs.security_group_id]")
                r.update_params({"create_security_group": False})

            if node.get("engine") == "aurora-mysql":
                r.update_params({
                    "engine": "aurora-mysql",
                    "port": "3306",
                    "engine_version": "5.7.12",
                })
            elif node.get("engine") == "postgres":
                r.update_params({
                    "engine": "aurora-postgresql",
                    "port": "5432",
                    "engine_version": "9.6.9",
                })

            if node.get("role") == "serverless":
                r.update_params({
                    "engine": "aurora",
                    "engine_mode": "serverless",
                })

            if node.get("role") != "serverless" and node.get("instanceType") and node.get("instanceSize"):
                r.update_params({
                    "instanceType": "db." + node.get("instanceType", "") + "." + node.get("instanceSize", ""),
                })

            resources.append(r.content())

        if node.get("type") == "rds" and node.get("engine") not in ["aurora-mysql", "aurora-postgresql"]:
            r = Resource(key, "rds", node_text)

            r.update_params({
                "isMultiAZ": node.get("multiAZ"),
                "db_subnet_group_name": "",
                "identifier": node_text if node_text else random_pet(),
                "username": random_pet(words=1),
                "password": random_password(),
                "allocated_storage": 5,
                "major_engine_version": "",
                "family": "",
                "backup_retention_period": "0",  # Disable backups to create DB faster
                "vpc_security_group_ids": [],
                "create_db_subnet_group": False,
                "skip_final_snapshot": True,
            })

            if vpc_id:
                r.append_dependency(vpc_id)
                r.update_dynamic_params("db_subnet_group_name",
                                        "dependency." + vpc_id + ".outputs.database_subnet_group")

            if sg_id:
                r.append_dependency(sg_id)
                r.update_dynamic_params("vpc_security_group_ids",
                                        "[dependency." + sg_id + ".outputs.security_group_id]")

            if node.get("engine") == "mysql":
                r.update_params({
                    "engine": "mysql",
                    "port": "3306",
                    "engine_version": "8.0.20",
                    "major_engine_version": "8.0",
                    "family": "mysql8.0",
                })
            elif node.get("engine") == "mariadb":
                r.update_params({
                    "engine": "mariadb",
                    "port": "3306",
                    "engine_version": "10.3.13",
                    "major_engine_version": "10.3",
                    "family": "mariadb10.3",
                })
            elif node.get("engine") == "postgres":
                r.update_params({
                    "engine": "postgres",
                    "port": "5432",
                    "engine_version": "11.10",
                    "major_engine_version": "11",
                    "family": "postgres11",
                })
            else:
                r.update_params({
                    "engine": node.get("engine"),
                    "port": "...",
                    "engine_version": "...",
                    "major_engine_version": "...",
                    "family": "...",
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

                    asg_name = G.nodes.get(asg_id, {}).get("text")

                    r = Resource(asg_id, "autoscaling", asg_name)

                    r.update_params({
                        "name": asg_name if asg_name else random_pet(),
                        "min_size": 0,
                        "max_size": 1,
                        "desired_capacity": 1,
                        "health_check_type": "EC2",
                        "use_lt": True,
                        "create_lt": True,
                        "image_id": "HCL:dependency.aws-data.outputs.amazon_linux2_aws_ami_id",
                        "vpc_zone_identifier": [],
                        "security_groups": [],
                    })

                    r.append_dependency("aws-data")

                    if vpc_id:
                        r.append_dependency(vpc_id)
                        r.update_dynamic_params("vpc_zone_identifier", "dependency." + vpc_id + ".outputs.public_subnets")

                    if sg_id:
                        r.append_dependency(sg_id)
                        r.update_dynamic_params("security_groups", "[dependency." + sg_id + ".outputs.security_group_id]")

                    if elb_id and elb_type == "application":
                        r.update_params({
                            "target_group_arns": [],
                        })
                        r.append_dependency(elb_id)
                        r.update_dynamic_params("target_group_arns",
                                                "dependency." + elb_id + ".outputs.target_group_arns")

                    if node.get("instanceType") and node.get("instanceSize"):
                        r.update_params({
                            "instanceType": node.get("instanceType", "") + "." + node.get("instanceSize", ""),
                        })

                    resources.append(r.content())

                parsed_asg_id.add(asg_id)
            else:
                r = Resource(key, "ec2-instance", node_text)

                r.update_params({
                    "name": node_text if node_text else random_pet(),
                    "ami": "HCL:dependency.aws-data.outputs.amazon_linux2_aws_ami_id",
                })

                r.append_dependency("aws-data")

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
                r = Resource(key, "alb", node_text)

                r.update_params({
                    "name": random_pet(),
                })

                if vpc_id:
                    r.append_dependency(vpc_id)
                    r.update_dynamic_params("subnets", "dependency." + vpc_id + ".outputs.public_subnets")
                    r.update_dynamic_params("vpc_id", "dependency." + vpc_id + ".outputs.vpc_id")

                if sg_id:
                    r.append_dependency(sg_id)
                    r.update_dynamic_params("security_groups", "[dependency." + sg_id + ".outputs.security_group_id]")

            elif node.get("elbType") == "network":
                r = Resource(key, "nlb", node_text)

                r.update_params({
                    "name": random_pet(),
                })

                if vpc_id:
                    r.append_dependency(vpc_id)
                    r.update_dynamic_params("subnets", "dependency." + vpc_id + ".outputs.public_subnets")
                    r.update_dynamic_params("vpc_id", "dependency." + vpc_id + ".outputs.vpc_id")

            else:
                r = Resource(key, "elb", node_text)

                r.update_params({
                    "name": random_pet(),
                    "listener": [{
                        "instance_port": "80",
                        "instance_protocol": "http",
                        "lb_port": "80",
                        "lb_protocol": "http"
                    }],
                    "health_check": {
                        "target": "HTTP:80/",
                        "interval": 30,
                        "healthy_threshold": 2,
                        "unhealthy_threshold": 2,
                        "timeout": 5,
                    }
                })

                if vpc_id:
                    r.append_dependency(vpc_id)
                    r.update_dynamic_params("subnets", "dependency." + vpc_id + ".outputs.public_subnets")

                if sg_id:
                    r.append_dependency(sg_id)
                    r.update_dynamic_params("security_groups", "[dependency." + sg_id + ".outputs.security_group_id]")

            resources.append(r.content())

        if node.get("type") == "redshift":
            r = Resource(key, "redshift", node_text)

            r.update_params({
                "cluster_identifier": random_pet(),
                "cluster_database_name": random_pet(),
                "cluster_master_username": random_pet(words=1),
                "cluster_master_password": random_password(),
                "nodeCount": node.get("nodeCount"),
                "subnets": [],
            })

            if node.get("instanceType") and node.get("instanceSize"):
                r.update_params({
                    "instanceType": node.get("instanceType") + "." + node.get("instanceSize"),
                })

            if vpc_id:
                r.append_dependency(vpc_id)
                r.update_dynamic_params("subnets", "dependency." + vpc_id + ".outputs.redshift_subnets")

            if sg_id:
                r.append_dependency(sg_id)
                r.update_dynamic_params("vpc_security_group_ids", "[dependency." + sg_id + ".outputs.security_group_id]")

            resources.append(r.content())

        if node.get("type") == "dynamodb":
            r = Resource(key, "dynamodb-table", node_text)

            r.update_params({
                "name": random_pet(),
                "read_capacity": node.get("readUnits"),
                "write_capacity": node.get("writeUnits"),
                "billing_mode": "PROVISIONED" if node.get("capacityMode") == "provisioned" else "PAY_PER_REQUEST",
                "hash_key": "id",
                "attributes": [{
                    "name": "id",
                    "type": "N"
                }]
            })

            resources.append(r.content())

        if node.get("type") == "s3":
            r = Resource(key, "s3-bucket", node_text)

            r.update_params({
                "bucket": node_text.lower() if node_text else random_pet(),
                "region": node.get("region", ""),
            })

            resources.append(r.content())

        if node.get("type") == "cloudfront":
            r = Resource(key, "cloudfront", node_text)

            r.update_params({
                "wait_for_deployment": False,
                "origin": "{ \
                    \"default\": { \
                        \"domain_name\": \"website.example.com\", \
                        \"custom_origin_config\": { \
                            \"http_port\": 80, \
                            \"https_port\": 443, \
                            \"origin_protocol_policy\": \"match-viewer\", \
                            \"origin_ssl_protocols\": [\"TLSv1\"], \
                        } \
                    } \
                }",
                "default_cache_behavior": "{ \
                    \"target_origin_id\": \"default\", \
                    \"viewer_protocol_policy\": \"allow-all\", \
                }"
            })

            resources.append(r.content())

        if node.get("type") == "lambda":
            r = Resource(key, "lambda", node_text)

            r.update_params({
                "memory_size": node.get("memory"),
                "function_name": node_text if node_text else random_pet(),
                "handler": "handler.lambda_handler",
                "runtime": "python3.8",
                "source_path": "jsonencode(\"handler.py\")"
            })

            resources.append(r.content())

        if node.get("type") == "apigateway":
            r = Resource(key, "apigateway-v2", node_text)

            r.update_params({
                "name": node_text if node_text else random_pet(),
                "protocol_type": "WEBSOCKET" if node.get("apiType") == "websocket" else "HTTP",
                "create_api_domain_name": False
            })

            resources.append(r.content())

        if node.get("type") == "vpngateway":
            r = Resource(key, "vpn-gateway", node_text)

            if vpc_id:
                r.append_dependency(vpc_id)
                r.update_dynamic_params("vpc_id", "dependency." + vpc_id + ".outputs.vpc_id")
                r.update_dynamic_params("vpn_gateway_id", "dependency." + vpc_id + ".outputs.vgw_id")
                r.update_dynamic_params("customer_gateway_id", "dependency." + vpc_id + ".outputs.cgw_ids[0]")

            resources.append(r.content())

        if node.get("type") == "sns":
            r = Resource(key, "sns", node_text)

            resources.append(r.content())

        if node.get("type") == "sqs":
            r = Resource(key, "sqs", node_text)

            r.update_params({
                "fifoQueue": node.get("queueType") == "fifo",
            })

            resources.append(r.content())

        if node.get("type") == "sg":
            r = Resource(key, "security-group", node.get("group_name"))

            # Security group rules are disabled here because there is no functionality in renderer
            # which allows to convert from Python dict or JSON into valid HCL2 syntax
            # Issue: https://github.com/antonbabenko/modules.tf-lambda/issues/26
            enable_sg_rules = False

            # START disabled sg rules
            if enable_sg_rules:

                all_rules = {
                    "ingress": node.get("inbound_rules"),
                    "egress": node.get("outbound_rules")
                }

                for rule_type, rules in all_rules.items():
                    rules_with_cidr_blocks = []
                    rules_with_source_security_group_id = []

                    for rule in rules:
                        port_range = convert_port_range(rule.get("portRange"))

                        tmp_rule = {
                            "from_port": port_range[0],
                            "to_port": port_range[1],
                            "protocol": convert_protocol(rule.get("protocol")),
                            "description": rule.get("description"),
                        }

                        if rule.get("targetType") == "ip":
                            tmp_rule.update({"cidr_blocks": rule.get("target")})
                            rules_with_cidr_blocks.append(tmp_rule)
                        else:
                            dependency_sg_id = rule.get("target")
                            tmp_rule.update({"source_security_group_id": "HCL:dependency." + dependency_sg_id + ".outputs.security_group_id"})
                            rules_with_source_security_group_id.append(tmp_rule)

                            r.append_dependency(dependency_sg_id)

                    r.update_params({rule_type + "_with_cidr_blocks": rules_with_cidr_blocks})
                    r.update_dynamic_params(rule_type + "_with_source_security_group_id", rules_with_source_security_group_id)

                r.update_params({
                    "ingress_with_source_security_group_id": [],
                    "egress_with_source_security_group_id": [],
                })
            # END disabled sg rules

            r.update_params({
                "name": node.get("group_name", random_pet()),
                "ingress_rules": ["all-all"],
                "ingress_cidr_blocks": ["0.0.0.0/0"],
            })

            if vpc_id:
                r.append_dependency(vpc_id)
                r.update_dynamic_params("vpc_id", "dependency." + vpc_id + ".outputs.vpc_id")

            resources.append(r.content())

        if node.get("type") == "vpc":
            r = Resource(key, "vpc", node.get("group_name"))

            selected_vpc_cidr = "10.0.0.0/16"

            r.update_params({
                "name": node.get("group_name", random_pet()),
                "cidr": selected_vpc_cidr,
                "azs":
                    "HCL:[for v in dependency.aws-data.outputs.available_aws_availability_zones_names: v]",
                "public_subnets":
                    "HCL:[for k,v in dependency.aws-data.outputs.available_aws_availability_zones_names: cidrsubnet(\"" +
                    selected_vpc_cidr + "\", 8, k)]",
                "private_subnets":
                    "HCL:[for k,v in dependency.aws-data.outputs.available_aws_availability_zones_names: cidrsubnet(\"" +
                    selected_vpc_cidr + "\", 8, k+10)]",
                "database_subnets":
                    "HCL:[for k,v in dependency.aws-data.outputs.available_aws_availability_zones_names: cidrsubnet(\"" +
                    selected_vpc_cidr + "\", 8, k+20)]",
            })

            r.append_dependency("aws-data")

            resources.append(r.content())

    # Add aws-data if there was a node with dependent type
    if list({"vpc", "ec2"} & node_types):
        r = Resource("aws-data", "aws-data", None)
        resources.append(r.content())

    logging.info(pformat(resources))

    if len(warnings):
        logging.warning("; ".join(warnings))

    return json.dumps(resources)
