terraform {
  backend "s3" {}
}

provider "aws" {
  region = "{{ cookiecutter.region }}"
}

module "{{ cookiecutter.layer_name }}" {
  source = "{{ cookiecutter.module_source }}"


{%- for key, value in cookiecutter.module_variables|dictsort -%}

{%- if value.cloudcraft_name is defined -%}
{%- if value.cloudcraft_name in cookiecutter.params -%}
{%- set tmp_value = cookiecutter.params[value.cloudcraft_name] -%}
{%- else -%}
{%- set tmp_value = None -%}
{%- endif-%}
{%- elif key in cookiecutter.params -%}
{%- set tmp_value = cookiecutter.params[key] -%}
{%- else -%}
{%- set tmp_value = None -%}
{%- endif -%}

{%- if value.default is defined -%}
{%- if value.default|lower() in ["true", "false"] -%}
{%- set value_type = value.type|default("bool") -%}
{%- elif value.default is mapping -%}
{%- set value_type = value.type|default("map") -%}
{%- elif value.default is string -%}
{%- set value_type = value.type|default("string") -%}
{%- else -%}
{%- set value_type = value.type|default("list") -%}
{%- endif %}
{%- else -%}
{%- set value_type = value.type|default("string") -%}
{%- endif -%}

{%- if value_type == 'string' -%}
{%- set variable_default = '""' -%}
{%- set tf_value = '"%s"'|format(tmp_value) -%}
{%- elif value_type == 'int' -%}
{%- set variable_default = '""' -%}
{%- set tf_value = '%s'|format(tmp_value) -%}
{%- elif value_type == 'bool' -%}
{%- set variable_default = '' -%}
{%- set tf_value = '%s'|format(tmp_value)|lower -%}
{%- elif value_type in ['list', 'set'] -%}
{%- set variable_default = '[]' -%}

{%- if tmp_value is string -%}
{%- set tf_value = '["%s"]'|format(tmp_value) -%}
{%- else -%}
{# Terraform list values should be double quoted, but Python use single quote, so using tojson for this #}
{%- set tf_value = tmp_value|tojson -%}
{%- endif -%}

{%- elif value_type == 'map' -%}
{%- set variable_default = '{}' -%}
{%- set tf_value = '"%s"'|format(tmp_value) -%}
{%- endif -%}

{# printing only required variables (required = no default value) and those which were set explicitely #}
{%- if value.default is not defined or tmp_value != None %}
# {{ value.description|default() }}
# type: {{ value_type }}
{%- if tmp_value == None %}
{{ key }} = {{ variable_default }}
{% else %}
{{ key }} = {{ tf_value }}
{% endif %}

{%- endif -%}

{% endfor -%}


}