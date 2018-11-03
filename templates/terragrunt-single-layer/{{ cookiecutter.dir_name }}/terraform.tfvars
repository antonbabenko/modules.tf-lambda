terragrunt = {
  terraform {
    source = "{{ cookiecutter.module_source }}"
  }

  include = {
    path = "${find_in_parent_folders()}"
  }

  {% if cookiecutter.dependencies|default("") -%}
  # dependencies = {{ cookiecutter.dependencies|pprint }}

  dependencies {
    paths = [
      {%- for value in cookiecutter.dependencies -%}
      "../{{ value }}"{%- if not loop.last -%}, {% endif -%}
      {%- endfor -%}
    ]
  }
  {%- endif %}
}

{% for key, value in cookiecutter.module_variables|dictsort -%}

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


{# printing only required variables (required = no default value) and those which were set explicitely #}
{%- if value.default is not defined or tmp_value != None -%}
# {{ value.description|default() }}
# type: {{ value.value_type }}
{%- if tmp_value == None -%}
{%- set this_value = value.default|default(value.variable_default) -%}
{%- else -%}
{%- set this_value = tmp_value -%}
{%- endif -%}


{%- if value.variable_value_format_function == "lower" -%}
{%- set value_formatted = value.variable_value_format|format(this_value)|lower -%}
{%- else -%}

{%- if value.default is not string and value.value_type in ["list", "map"] -%}
{%- set value_formatted = this_value|tojson -%}
{%- else -%}
{%- set value_formatted = value.variable_value_format|format(this_value) -%}
{%- endif -%}

{%- endif %}
{{ key }} = {{ value_formatted }}


{% endif -%}

{% endfor %}
