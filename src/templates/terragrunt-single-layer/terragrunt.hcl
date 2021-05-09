{%- set module_source = cookiecutter.module_sources[this.module_type] -%}
{%- set module_variables = cookiecutter.module_variables[this.module_type] -%}
{%- set module_registry_url = cookiecutter.module_registry_urls[this.module_type] -%}
terraform {
  source = "{{ module_source }}"
}

include {
  path = find_in_parent_folders()
}

{% if this.dependencies|default("") -%}
dependencies {
  paths = [
    {%- for value in this.dependencies.split(",") -%}
    "../{{ value }}"{%- if not loop.last -%}, {% endif -%}
    {%- endfor -%}
  ]
}

{% for value in this.dependencies.split(",") -%}
dependency "{{ value }}" {
  config_path = "../{{ value }}"
}

{% endfor %}
{%- endif -%}

{%- if module_registry_url -%}
###########################################################
# View all available inputs for this module:
# {{ module_registry_url }}?tab=inputs
###########################################################
{%- endif %}
inputs = {
  {% for key, value in module_variables|dictsort -%}

  {%- if value.cloudcraft_name is defined -%}
  {%- if value.cloudcraft_name in this.params -%}
  {%- set tmp_value = this.params[value.cloudcraft_name] -%}
  {%- else -%}
  {%- set tmp_value = None -%}
  {%- endif-%}
  {%- elif key in this.params -%}
  {%- set tmp_value = this.params[key] -%}
  {%- else -%}
  {%- set tmp_value = None -%}
  {%- endif -%}


  {# printing only required variables (required = no default value) and those which were set explicitly #}
  {%- if value.default is not defined or tmp_value != None -%}
  # {{ value.description|default() }}
  # type: {{ value.value_type }}
  {%- if tmp_value == None -%}
  {%- set this_value = value.default|default(value.variable_default) -%}
  {%- else -%}
  {%- set this_value = tmp_value -%}
  {%- endif -%}


  {#- Convert boolean values from Python (False, True) into HCL (false, true) -#}
  {%- if value.variable_value_format_function == "lower" -%}
  {%- set value_formatted = value.variable_value_format|format(this_value)|lower -%}
  {%- else -%}

  {%- if value.default is not string and (value.value_type.startswith("list") or value.value_type.startswith("map")) -%}
  {#- tojson is used to convert single quotes (Python) to double quotes (as in HCL) -#}
  {%- set value_formatted = this_value|tojson -%}
  {%- else -%}
  {%- set value_formatted = value.variable_value_format|format(this_value) -%}
  {%- endif -%}

  {#- Native HCL expression - Remove prefix "HCL:" and unquote after tojson -#}
  {%- if value_formatted.startswith("\"HCL:") -%}
  {%- set value_formatted = value_formatted[5:-1]|replace("\\\"", "\"") -%}
  {%- endif -%}

  {%- endif -%}

  {#- Override value with the dynamic dependency -#}
  {%- if key in this.dynamic_params -%}
  {%- set value_formatted = this.dynamic_params[key] -%}
  {%- endif %}
  {{ key }} = {{ value_formatted }}

  {% endif -%}

  {%- endfor %}
}
