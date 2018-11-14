import json
import logging
from pprint import pformat, pprint


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
    parsed_rds_id = set()
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
        # logging.info("Edges: {}".format(edges))

        if node.get("type") not in supported_node_types:
            warnings.add("node type %s is not implemented yet" % node.get("type"))
            continue

        logging.info(pformat(node, indent=2))

        vpc_id = node.get("vpc_id")
        asg_id = ""
        elb_id = ""

        if node.get("type") == "rds":
            is_multi_az = False

            for edge_id in edges:
                if get_node_data(G, edge_id, "type") == "rds" and \
                        get_node_data(G, edge_id, "engine") == node.get("engine") and \
                        get_node_data(G, edge_id, "role") == ("master" if node.get("role") == "slave" else "slave"):
                    master_rds_id = (key if node.get("role") == "master" else edge_id)
                    is_multi_az = True

            rds_id = master_rds_id if is_multi_az else key

            if rds_id not in parsed_rds_id:

                r = Resource(rds_id, "rds", node.get("text"))

                r.update_params({
                    "isMultiAZ": is_multi_az,
                    "db_subnet_group_name": "",
                })

                if vpc_id:
                    r.append_dependency(vpc_id)
                    r.update_dynamic_params("db_subnet_group_name",
                                            "terraform_output." + vpc_id + ".database_subnet_group")

                if node.get("engine"):
                    r.update_params({
                        "engine": node.get("engine"),
                    })

                if node.get("instanceType") and node.get("instanceSize"):
                    r.update_params({
                        "instanceType": node.get("instanceType", "") + "." + node.get("instanceSize", ""),
                    })

                resources.append(r.content())

            parsed_rds_id.add(rds_id)

        if node.get("type") == "ec2":
            asg_id = node.get("asg_id")

            if asg_id:

                if asg_id not in parsed_asg_id:
                    # Find ELB/ALB in edges from or to ASG
                    tmp_edges = G.adj[asg_id]

                    for edge_id in tmp_edges:
                        if get_node_data(G, edge_id, "type") == "elb":
                            elb_id = get_node_data(G, edge_id, "id")
                            break

                    r = Resource(asg_id, "autoscaling", node.get("text"))

                    r.update_params({
                        "target_group_arns": [],
                        "vpc_zone_identifier": []
                    })

                    if elb_id:
                        r.append_dependency(elb_id)
                        r.update_dynamic_params("target_group_arns",
                                                "terraform_output." + elb_id + ".target_group_arns")

                    if vpc_id:
                        r.append_dependency(vpc_id)
                        r.update_dynamic_params("vpc_zone_identifier", "terraform_output." + vpc_id + ".public_subnets")

                    if node.get("instanceType") and node.get("instanceSize"):
                        r.update_params({
                            "instanceType": node.get("instanceType", "") + "." + node.get("instanceSize", ""),
                        })

                    resources.append(r.content())

                parsed_asg_id.add(asg_id)
            else:
                r = Resource(key, "ec2-instance", node.get("text"))

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
            else:
                r = Resource(key, "elb", node.get("text"))

                if vpc_id:
                    r.append_dependency(vpc_id)
                    r.update_dynamic_params("subnets", "terraform_output." + vpc_id + ".public_subnets")

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

            if vpc_id:
                r.append_dependency(vpc_id)
                r.update_dynamic_params("vpc_id", "terraform_output." + vpc_id + ".vpc_id")

            resources.append(r.content())

        if node.get("type") == "vpc":
            r = Resource(key, "vpc", node.get("text"))

            r.update_params({
                "name": "",
                "cidr": "",
                "azs": [],
                "public_subnets": [],
                "private_subnets": [],
            })

            resources.append(r.content())

    logging.info(pformat(resources))

    if len(warnings):
        logging.warning("; ".join(warnings))

    return json.dumps(resources)
