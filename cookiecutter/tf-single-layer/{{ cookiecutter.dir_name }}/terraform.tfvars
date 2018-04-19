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
{% for key, value in cookiecutter.params|dictsort -%}
{{ key }} = "{{ value }}"
{%- endfor %}
