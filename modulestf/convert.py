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

    for key, node in G.nodes.items():

        node = node.get("data")

        # logging.info("\n========================================\nID = {}".format(key))

        if node is None:
            logging.error("No node data for this node - {}".format(node))
            continue

        # logging.info("Node: {}".format(node))

        edges = G.adj[key]
        # logging.info("Edges: {}".format(edges))

        ################
        if node.get("type") not in ["sg", "vpc"]:
            warnings.add("node type %s is not implemented yet" % node.get("type"))
            continue
        ################

        # if node.get("type") not in ["rds", "ec2", "elb", "sns", "sqs", "s3", "cloudfront", "sg", "vpc"]:
        #     warnings.add("node type %s is not implemented yet" % node.get("type"))
        #     continue

        logging.info(pformat(node, indent=2))

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
                        "isMultiAZ": is_multi_az
                    }
                }

                if node.get("engine") is not None:
                    tmp_resource["params"].update({"engine": node.get("engine")})

                if node.get("instanceType") is not None and node.get("instanceSize") is not None:
                    tmp_resource["params"].update(
                        {"instanceType": node.get("instanceType", "") + "." + node.get("instanceSize", "")})

                resources.append(tmp_resource)

            parsed_rds_id.add(rds_id)

        if node.get("type") == "ec2":
            asg_id = node.get("asg_id")

            elb_id = None

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
                            "elb_id": elb_id if elb_id else None,
                            "target_group_arns": ["arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-targets/123"]
                        }
                    }

                    if node.get("instanceType") is not None and node.get("instanceSize") is not None:
                        tmp_resource["params"].update(
                            {"instanceType": node.get("instanceType", "") + "." + node.get("instanceSize", "")})

                    resources.append(tmp_resource)

                parsed_asg_id.add(asg_id)
            else:
                tmp_resource = {
                    "type": "ec2-instance",
                    "ref_id": key,
                    "text": node.get("text"),
                    "params": {}
                }

                if node.get("instanceType") is not None and node.get("instanceSize") is not None:
                    tmp_resource["params"].update(
                        {"instanceType": node.get("instanceType", "") + "." + node.get("instanceSize", "")})

                resources.append(tmp_resource)

        if node.get("type") == "elb":
            is_asg = False

            for edge_id in edges:
                if get_node_data(G, edge_id, "group_nodes") is not None:
                    is_asg = True
                    break

            if node.get("elbType") == "application":
                resources.append({
                    "type": "alb",
                    "ref_id": key,
                    "text": node.get("text"),
                    "params": {
                        "asg_id": edge_id if is_asg else None,
                    }
                })
            else:
                resources.append({
                    "type": "elb",
                    "ref_id": key,
                    "text": node.get("text"),
                    "params": {
                        "asg_id": edge_id if is_asg else None,
                    }
                })

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
            resources.append({
                "type": "security-group",
                "ref_id": key,
                "text": node.get("text"),
                "params": {
                },
                "dependencies": {"vpc": node.get("vpc_id")} if node.get("vpc_id") else {}
            })

        if node.get("type") == "vpc":
            resources.append({
                "type": "vpc",
                "ref_id": key,
                "text": node.get("text"),
                "params": {
                }
            })

    # print("-START------------------------------------")
    # pprint(resources)
    # pprint(G.groups.items())
    # print("-END------------------------------------")

    if len(warnings):
        logging.warning("; ".join(warnings))

    return json.dumps(resources)
