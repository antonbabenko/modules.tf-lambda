terragrunt = {
  terraform {
    source = "{{ cookiecutter.module_source }}"
  }

  include = {
    path = "${find_in_parent_folders()}"
  }

{#  {% if cookiecutter.dependencies|length -%}
  dependencies = [
    "for loop goes here"
  ]
  {%- endif %} #}
}

# MODULE PARAMETERS
# todo: print only required variables and whose which were set by cloudcraft

{% for key, value in cookiecutter.module_variables|dictsort -%}
# {{ value.description }}
{% if value.cloudcraft_param|default() == "" %}
{{ key }} = "..."
{% else %}
{% set tmp_value = cookiecutter.params[value.cloudcraft_param] %}
{% set value_type = value.type|default("string") %}

{%- if value_type == 'string' -%}
  {%- set variable_default = '""' -%}
  {%- set tmp_value = '"%s"'|format(tmp_value) -%}
{%- elif value_type == 'int' -%}
  {%- set variable_default = '""' -%}
  {%- set tmp_value = '%s'|format(tmp_value) -%}
{%- elif value_type == 'bool' -%}
  {%- set variable_default = '' -%}
  {%- set tmp_value = '%s'|format(tmp_value)|lower -%}
{%- elif value_type in ['list', 'set'] -%}
  {%- set variable_default = '[]' -%}
  {%- set tmp_value = '["%s"]'|format(tmp_value) -%}
{%- elif value_type == 'map' -%}
  {%- set variable_default = '{}' -%}
  {%- set tmp_value = '"%s"'|format(tmp_value) -%}
{%- endif -%}

{{ key }} = {{ tmp_value }}

{% endif %}
{% endfor %}
