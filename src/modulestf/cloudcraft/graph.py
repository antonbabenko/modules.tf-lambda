from builtins import isinstance, list
from collections import namedtuple
from pprint import pprint

import networkx as nx


def populate_graph(data):  # noqa: C901

    Graph = namedtuple('Graph', 'G source regions')

    G = nx.Graph()  # We can't trust directions of edges, so graph should be not-directional
    # MG = nx.Graph()  # converted graph to modules.tf schema

    # @todo: convert from graph (G) to modules.tf graph (MG), which can be dumped to json and passed to generator function

    regions = []
    connectors = []

    # We don't care about these keys in json: images, icons
    data_id = data["id"]
    data = data.get("data", {})

    data_nodes = data.get("nodes", [])
    data_edges = data.get("edges", [])
    data_groups = data.get("groups", [])
    data_connectors = data.get("connectors", [])
    data_text = data.get("text", [])
    data_name = data.get("name", "unnamed")

    ########
    # NODES
    ########
    for node in data_nodes:
        G.add_node(node["id"], data=node)

    ########
    # EDGES
    ########
    for edge in data_edges:
        if "from" in edge and "to" in edge:
            G.add_edge(edge["from"], edge["to"])

    #####################
    # AUTOSCALING GROUPS, SECURITY GROUPS AND VPCS
    #####################
    for group in data_groups:
        group_type = group.get("type")

        if group_type in ["asg", "sg", "vpc"]:
            group_id = group.get("id")
            group_nodes = group.get("nodes")
            group_region = group.get("region")
            group_name = group.get("name")

            regions.append(group_region)

            G.add_node(group_id, data={
                "type": group_type,
                "group_nodes": group_nodes,
                "group_region": group_region,
                "group_name": group_name,
            })

            if group_type == "sg":
                G.nodes[group_id]["data"]["inbound_rules"] = group.get("inboundRules")
                G.nodes[group_id]["data"]["outbound_rules"] = group.get("outboundRules")
            elif group_type == "vpc":
                G.nodes[group_id]["data"]["peering_connections"] = group.get("peeringConnections")

            for group_node in group_nodes:
                # some items (like "text") may belong to groups, but are not in "nodes"
                if group_node not in G.nodes:
                    continue

                # nodes type "icon" does not have "data", so we skip them
                if "data" not in G.nodes[group_node]:
                    continue

                if group_type == "asg":
                    G.nodes[group_node]["data"]["asg_id"] = group_id
                elif group_type == "sg":
                    G.nodes[group_node]["data"]["sg_id"] = group_id
                elif group_type == "vpc":
                    G.nodes[group_node]["data"]["vpc_id"] = group_id

    #############
    # CONNECTORS
    #############
    for connector in data_connectors:
        G.add_node(connector["id"], type="connector")
        connectors.append(connector["id"])

    # Merge connectors by contracting edges
    edge = []
    while True:
        # Find first edge which contains connector
        for edge in G.edges.data():
            edge = list(edge)

            if edge[0] == edge[1]:
                edge = []  # maybe continue
            elif edge[0] in connectors or edge[1] in connectors:
                break
            else:
                edge = []

        # Skip edges without connectors and edges which does not have nodes on one any side
        if len(edge) == 0 or edge[0] not in G or edge[1] not in G:
            break

        G = nx.contracted_edge(G, (edge[0], edge[1]), self_loops=False)

    ########
    # TEXTS
    ########
    for text in data_text:
        mapPos = text.get("mapPos", {})
        if isinstance(mapPos, dict):
            relTo = mapPos.get("relTo")

            if relTo in G.nodes:
                G.nodes[relTo]["text"] = text["text"].strip()

    ###########
    # REGION
    ###########
    regions = list(set(regions))

    ########
    # SOURCE
    ########
    source = {
        "name": data_name,
        "id": data_id,
    }

    # Debug - draw into file
    # import matplotlib.pyplot as plt
    # plt.rcParams["figure.figsize"] = (10, 10)
    # nx.draw(G, pos=nx.spring_layout(G), with_labels=True)
    # plt.savefig("graph.png")

    # pprint(G.edges["0820fb86-ee74-49ce-9fe5-03f610ca5e75"])
    pprint("NODES===")
    pprint(G.nodes.data())
    # print("EDGES===")
    # print(G.edges.data())

    # pprint(regions)

    # pprint(regions.keys())
    # pprint(nodes)
    # pprint(texts)
    # pprint(edges, indent=2)
    # pprint(edges_rev)

    # nx.drawing.nx_agraph.write_dot(G, "graph.dot")

    return Graph(G, source, regions)
