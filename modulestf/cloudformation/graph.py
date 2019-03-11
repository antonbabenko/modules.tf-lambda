import random
from collections import namedtuple
from pprint import pprint

import networkx as nx

# Notes for myself:
# In Cloudformation there are Resources, which should be combined in blocks (to match Terraform modules)
# In Cloudcraft there are nodes, which are usually consist of resources and already match Terraform modules
# In MTF/convert.py there are nodes and edges

def populate_graph(data):  # noqa: C901

    Graph = namedtuple('Graph', 'G source regions')

    G = nx.Graph()  # We can't trust directions of edges, so graph should be not-directional
    # MG = nx.Graph()  # converted graph to modules.tf schema

    # @todo: convert from graph (G) to modules.tf graph (MG), which can be dumped to json and passed to generator function

    # pprint(data["Resources"])


    regions = []
    connectors = []

    data_id = random.randint(1, 1000)
    resources = data.get("Resources", {})

    # data_nodes = data.get("nodes", [])
    # data_edges = data.get("edges", [])
    # data_groups = data.get("groups", [])
    # data_connectors = data.get("connectors", [])
    # data_text = data.get("text", [])
    data_name = random.random()

    ########
    # NODES
    ########
    for resource_id, resource_data in resources.items():
        G.add_node(resource_id, data=resource_data)

    # Go through references in all Resources to find available values for modules

    pprint(G.nodes)

    return

    ########
    # EDGES
    ########
    # for edge in data_edges:
    #     G.add_edge(edge["from"], edge["to"])

    #####################
    # AUTOSCALING GROUPS, SECURITY GROUPS AND VPCS
    #####################
    # for group in data_groups:
    #     group_type = group.get("type")
    #
    #     if group_type in ["asg", "sg", "vpc"]:
    #         group_id = group.get("id")
    #         group_nodes = group.get("nodes")
    #         group_region = group.get("region")
    #
    #         regions.append(group_region)
    #
    #         G.add_node(group_id, data={
    #             "type": group_type,
    #             "group_nodes": group_nodes,
    #             "group_region": group_region
    #         })
    #
    #         for group_node in group_nodes:
    #             if group_type == "asg":
    #                 G.node[group_node]["data"]["asg_id"] = group_id
    #             elif group_type == "sg":
    #                 G.node[group_node]["data"]["sg_id"] = group_id
    #             elif group_type == "vpc":
    #                 G.node[group_node]["data"]["vpc_id"] = group_id
    #
    # #############
    # # CONNECTORS
    # #############
    # for connector in data_connectors:
    #     G.add_node(connector["id"], type="connector")
    #     connectors.append(connector["id"])
    #
    # # Merge connectors by contracting edges
    # edge = []
    # while True:
    #     # Find first edge which contains connector
    #     for edge in G.edges.data():
    #         edge = list(edge)
    #
    #         if edge[0] == edge[1]:
    #             edge = []
    #         elif edge[0] in connectors or edge[1] in connectors:
    #             break
    #         else:
    #             edge = []
    #
    #     # No edges with connectors remaining - all done
    #     if len(edge) == 0:
    #         break
    #
    #     G = nx.contracted_edge(G, (edge[0], edge[1]), self_loops=False)
    #
    # ########
    # # TEXTS
    # ########
    # for text in data_text:
    #     mapPos = text.get("mapPos", {})
    #     if isinstance(mapPos, dict):
    #         relTo = mapPos.get("relTo")
    #
    #         if relTo in G.nodes:
    #             G.nodes[relTo]["text"] = text["text"]

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
    # print("NODES===")
    # print(G.nodes.data())
    # print("EDGES===")
    # print(G.edges.data())

    # pprint(regions)

    # pprint(regions.keys())
    # pprint(nodes)
    # pprint(texts)
    # pprint(edges, indent=2)
    # pprint(edges_rev)

    return Graph(G, source, regions)
