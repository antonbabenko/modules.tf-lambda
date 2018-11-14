#!/bin/bash

############################
# This script is used by Terragrunt hook to find and replace references in terraform.tfvars with the real values fetched using `terragrunt output`
############################
# 1. check if this script has not been disabled using special flag (@modulestf:disable_values_updates)
# 2. get list of things to replace
# 3. go through the list of things to replace
# 4. get actual value
# 5. replace value in terraform.tfvars
############################

readonly tfvars_file="$1/terraform.tfvars"
readonly parent_dir="$1/../"

readonly modulestf_disable_values_updates_flag="@modulestf:disable_values_updates"
readonly modulestf_terraform_output_prefix="@modulestf:terraform_output"

############################

if $(grep -q "$modulestf_disable_values_updates_flag" "$tfvars_file"); then
  echo "Dynamic update has been disabled in terraform.tfvars"
  exit 0
fi

keys_to_replace=($(grep -oh "$modulestf_terraform_output_prefix\.[^ ]*" "$tfvars_file" | sort | uniq))

for key_to_replace in "${keys_to_replace[@]}"; do
  dir_name=$(cut -d "." -f 2 <<< "$key_to_replace")
  output_name=$(cut -d "." -f 3 <<< "$key_to_replace")

  cd "${parent_dir}/${dir_name}"

  item=$(terragrunt output -json "$output_name")

  item_type=$(echo "$item" | jq -rc ".type")
  item_value=$(echo "$item" | jq -rc ".value")

  if [[ "$item_type" == "string" ]]; then
    item_value="\"$item_value\""
  fi

  echo "Updating value of $key_to_replace with $item_value"

  sed -i -r "s/^(.+) =.+(\#)+(.*)${key_to_replace}(.*)/\1 = ${item_value} \2\3${key_to_replace}\4/g" "$tfvars_file"
done
