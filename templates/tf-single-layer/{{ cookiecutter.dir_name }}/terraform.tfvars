terragrunt = {
  terraform {
    source = "{{ cookiecutter.module_source }}"
  }

  include = {
    path = "${find_in_parent_folders()}"
  }
}

# MODULE PARAMETERS
{# printing only required variables and those which were set by cloudcraft #}

{% for key, value in cookiecutter.module_variables|dictsort -%}

{% if value.cloudcraft_name|default() != "" %}
  {% set tmp_value = cookiecutter.params[value.cloudcraft_name] %}
{% elif key in cookiecutter.params %}
  {% set tmp_value = cookiecutter.params[key] %}
{% else %}
  {% set tmp_value = None %}
{% endif %}


{% set value_type = value.type|default("string") %}


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
  {%- set tf_value = '["%s"]'|format(tmp_value) -%}
{%- elif value_type == 'map' -%}
  {%- set variable_default = '{}' -%}
  {%- set tf_value = '"%s"'|format(tmp_value) -%}
{%- endif -%}


{% if value.required|default(False) or tmp_value != None %}
# {{ value.description }}
  {% if tmp_value == None %}
    {{ key }} = {{ variable_default }}
  {% else %}
    {{ key }} = {{ tf_value }}
  {% endif %}
{% endif %}

{% endfor %}
