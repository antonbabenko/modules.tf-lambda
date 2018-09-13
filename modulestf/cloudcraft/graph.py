import networkx as nx

from collections import namedtuple

Graph = namedtuple('Graph', 'G source regions surfaces')


def populate_graph(data):
    # global source
    # global surfaces
    # global regions
    # global G

    G = nx.Graph() # We can't trust directions of edges, so graph should be not-directional
    # MG = nx.Graph()  # converted graph to modules.tf schema

    # @todo: convert from graph (G) to modules.tf graph (MG), which can be dumped to json and passed to generator function

    surfaces = {}
    regions = {}
    connectors = []

    # We don't care about these keys in json: images, icons
    data_id = data["id"]
    data = data.get("data", {})

    data_nodes = data.get("nodes", [])
    data_edges = data.get("edges", [])
    data_groups = data.get("groups", [])
    data_connectors = data.get("connectors", [])
    data_text = data.get("text", [])
    data_surfaces = data.get("surfaces", [])
    data_name = data.get("name", "")

    ########
    # NODES
    ########
    for node in data_nodes:
        G.add_node(node["id"], data=node)

    ########
    # EDGES
    ########
    for edge in data_edges:
        G.add_edge(edge["from"], edge["to"])

    #####################
    # AUTOSCALING GROUPS
    #####################
    for group in data_groups:
        if group.get("type") == "asg":
            group_id = group.get("id")
            group_nodes = group.get("nodes")

            G.add_node(group_id, data={"group_nodes": group_nodes})

            for group_node in group_nodes:
                G.node[group_node]["data"]["asg_id"] = group_id

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

            if edge[0] in connectors or edge[1] in connectors:
                break
            else:
                edge = []

        # No edges with connectors remaining - all done
        if len(edge) == 0:
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
                G.nodes[relTo]["text"] = text["text"]

    ###########
    # SURFACES
    ###########
    for surface in data_surfaces:
        surfaces[surface.get("id")] = surface

        if surface.get("type") == "zone":
            region = surface.get("region")
            if region:
                if region not in regions.keys():
                    regions[region] = []

                regions[region].append(surface)

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
    print("NODES===")
    print(G.nodes.data())
    print("EDGES===")
    print(G.edges.data())

    # pprint(regions)
    # pprint(regions.keys())
    # pprint(nodes)
    # pprint(texts)
    # pprint(edges, indent=2)
    # pprint(edges_rev)

    return Graph(G, source, regions, surfaces)
