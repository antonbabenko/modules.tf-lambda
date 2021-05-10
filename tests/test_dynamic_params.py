import re
from pprint import pprint

dynamic_params = {
    'key': 'dependency.a3bfbbf.outputs.security_group_id',
    'egress_with_source_security_group_id': [],
    'ingress_with_source_security_group_id': [
        {
            'description': 'All TCP from sg2',
            'from_port': '0',
            'protocol': 6,
            'source_security_group_id': 'dependency.a3bfbb.outputs.security_group_id',
            'to_port': '65535'
        },
        {
            'description': 'All TCP from sg3',
            'from_port': '0',
            'protocol': 6,
            'source_security_group_id': '[dependency.a3bfbb.outputs.security_group_id] + dependency.abcdef.outputs.security_group_id',
            'to_port': '65535'
        }
    ]
}

dirs = {
    "a3bfbb": "sg-111",
    "abcdef": "sg-999"
}


def recursive_replace_dependency(input):
    # check whether it's a dict, list, tuple, or scalar
    if isinstance(input, dict):
        items = input.items()
    elif isinstance(input, (list, tuple)):
        items = enumerate(input)
    else:

        # just a value, replace and return
        found = re.findall(r"dependency\.([^.]+)", str(input))
        for f in found:
            input = re.sub(f, dirs.get(f, f), input)

        return input

    # now call itself for every value and replace in the input
    for key, value in items:
        input[key] = recursive_replace_dependency(value)
    return input


pprint(dynamic_params)

if dynamic_params:
    for k, v in dynamic_params.items():

        dynamic_params[k] = recursive_replace_dependency(v)
        pprint(dynamic_params[k])

pprint("FINAL = ")
pprint(dynamic_params)

pprint("")
pprint("")
pprint("")

####
#
# import hcl
# import json
#
# # hcl_json = hcl.loads(json.dumps(dynamic_params))
#
# # hcl_json_input = "{\"key\": \"var.value\"}"
# hcl_json_input = "{\"key\": { \"key1\" : \"value\" } }"
# hcl_json = hcl.loads(hcl_json_input)
#
# # val2 = hcl.dumps(value)
#
# # with open('file.hcl', 'r') as fp:
# #     obj = hcl.load(fp)
#
# result = json.dumps(hcl_json)
# print(hcl_json)
# print(result)
