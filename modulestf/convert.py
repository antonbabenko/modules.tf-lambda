import json
import logging
from pprint import pformat, pprint


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

    for key, node in G.nodes.items():

        node = node.get("data")

        # logging.info("\n========================================\nID = {}".format(key))

        if node is None:
            logging.error("No node data for this node - {}".format(node))
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
                tmp_resource = {
                    "type": "rds",
                    "ref_id": rds_id,
                    "text": node.get("text"),
                    "params": {
                        "isMultiAZ": is_multi_az,
                        "db_subnet_group_name": "",
                    },
                    "dependencies": [],
                    "dynamic_params": {},
                }

                if vpc_id:
                    tmp_resource["dependencies"].append(vpc_id)
                    tmp_resource["dynamic_params"].update(
                        dict(db_subnet_group_name="terraform_output." + vpc_id + ".database_subnet_group"))

                if node.get("engine"):
                    tmp_resource["params"].update(
                        dict(engine=node.get("engine")))

                if node.get("instanceType") and node.get("instanceSize"):
                    tmp_resource["params"].update(
                        dict(instanceType=node.get("instanceType", "") + "." + node.get("instanceSize", "")))

                resources.append(tmp_resource)

            parsed_rds_id.add(rds_id)

        if node.get("type") == "ec2":
            asg_id = node.get("asg_id")

            if bool(asg_id):

                if asg_id not in parsed_asg_id:
                    # Find ELB/ALB in edges from or to ASG
                    tmp_edges = G.adj[asg_id]

                    for edge_id in tmp_edges:
                        if get_node_data(G, edge_id, "type") == "elb":
                            elb_id = get_node_data(G, edge_id, "id")
                            break

                    tmp_resource = {
                        "type": "autoscaling",
                        "ref_id": asg_id,
                        "text": node.get("text"),
                        "params": {
                            "target_group_arns": [],
                            "vpc_zone_identifier": []
                        },
                        "dependencies": [],
                        "dynamic_params": {}
                    }

                    if elb_id:
                        tmp_resource["dependencies"].append(elb_id)
                        tmp_resource["dynamic_params"].update(
                            dict(target_group_arns="terraform_output." + elb_id + ".target_group_arns"))

                    if vpc_id:
                        tmp_resource["dependencies"].append(vpc_id)
                        tmp_resource["dynamic_params"].update(
                            dict(vpc_zone_identifier="terraform_output." + vpc_id + ".public_subnets"))

                    if node.get("instanceType") and node.get("instanceSize"):
                        tmp_resource["params"].update(
                            dict(instanceType=node.get("instanceType", "") + "." + node.get("instanceSize", "")))

                    resources.append(tmp_resource)

                parsed_asg_id.add(asg_id)
            else:
                tmp_resource = {
                    "type": "ec2-instance",
                    "ref_id": key,
                    "text": node.get("text"),
                    "params": {}
                }

                if node.get("instanceType") and node.get("instanceSize"):
                    tmp_resource["params"].update(
                        {"instanceType": node.get("instanceType", "") + "." + node.get("instanceSize", "")})

                resources.append(tmp_resource)

        if node.get("type") == "elb":
            # for edge_id in edges:
            #     if get_node_data(G, edge_id, "group_nodes"):
            #         asg_id = edge_id
            #         break

            if node.get("elbType") == "application":
                tmp_resource = {
                    "type": "alb",
                    "ref_id": key,
                    "text": node.get("text"),
                    "params": {},
                    "dependencies": [],
                    "dynamic_params": {}
                }

            else:
                tmp_resource = {
                    "type": "elb",
                    "ref_id": key,
                    "text": node.get("text"),
                    "params": {},
                    "dependencies": [],
                    "dynamic_params": {}
                }

                if vpc_id:
                    tmp_resource["dependencies"].append(vpc_id)
                    tmp_resource["dynamic_params"].update(
                        dict(subnets="terraform_output." + vpc_id + ".public_subnets"))

            resources.append(tmp_resource)

        if node.get("type") == "s3":
            resources.append({
                "type": "s3",
                "ref_id": key,
                "text": node.get("text"),
                "params": {
                }
            })

        if node.get("type") == "cloudfront":
            resources.append({
                "type": "cloudfront",
                "ref_id": key,
                "text": node.get("text"),
                "params": {
                }
            })

        if node.get("type") == "sns":
            resources.append({
                "type": "sns",
                "ref_id": key,
                "text": node.get("text"),
                "params": {
                }
            })

        if node.get("type") == "sqs":
            resources.append({
                "type": "sqs",
                "ref_id": key,
                "text": node.get("text"),
                "params": {
                    "fifoQueue": node.get("queueType") == "fifo",
                }
            })

        if node.get("type") == "sg":
            tmp_resource = {
                "type": "security-group",
                "ref_id": key,
                "text": node.get("text"),
                "params": {},
                "dependencies": [],
                "dynamic_params": {}
            }

            if vpc_id:
                tmp_resource["dependencies"].append(vpc_id)
                tmp_resource["dynamic_params"].update(
                    dict(vpc_id="terraform_output." + vpc_id + ".vpc_id"))

            resources.append(tmp_resource)

        if node.get("type") == "vpc":
            resources.append({
                "type": "vpc",
                "ref_id": key,
                "text": node.get("text"),
                "params": {
                    "name": "",
                    "cidr": "",
                    "azs": [],
                    "public_subnets": [],
                    "private_subnets": [],
                },
                "dependencies": [],
                "dynamic_params": {}
            })

    logging.info(pformat(resources))

    if len(warnings):
        logging.warning("; ".join(warnings))

    return json.dumps(resources)
