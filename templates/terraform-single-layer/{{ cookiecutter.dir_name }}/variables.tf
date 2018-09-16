{% for key, value in cookiecutter.module_variables|dictsort -%}

{%- if value.default is not defined %}

variable "{{ key }}" {
  description = "{{ value.description|default() }}"

{%- if value.value_type not in ["string", "bool"] %}
  type = "{{ value.value_type }}"
{% endif %}

{%- if value.default is defined %}

{% if value.variable_value_format_function == "lower" %}
{% set value_formatted = value.variable_value_format|format(value.default)|lower %}
{% else %}

{% if value.default is not string and value.value_type in ["list", "map"] %}
  {% set value_formatted = value.default|tojson %}
{% else %}
  {% set value_formatted = value.variable_value_format|format(value.default) %}
{% endif %}

{% endif %}

  default = {{ value_formatted }}

{% endif %}

}

{% endif %}

{% endfor -%}
