# Terraform configurations required to provision AWS infrastructure for d2c.modules.tf

- HTTP API Gateway
- ACM
- Lambda Function
- S3 bucket for downloads
- Route53 records

## Deployments

### cloudcraft - prod

```
$ awsp modules-deploy  # Assume IAM role in correct account
$ make cloudcraft
```

### betajob - dev

```
$ awsp private-anton  # Assume IAM role in correct account
$ make betajob
```

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 0.15, <1.0.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 3.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | ~> 3.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_acm"></a> [acm](#module\_acm) | terraform-aws-modules/acm/aws | ~> 3.0 |
| <a name="module_alarm_lambda_is_popular"></a> [alarm\_lambda\_is\_popular](#module\_alarm\_lambda\_is\_popular) | terraform-aws-modules/cloudwatch/aws//modules/metric-alarm |  |
| <a name="module_alarm_lambda_is_slow"></a> [alarm\_lambda\_is\_slow](#module\_alarm\_lambda\_is\_slow) | terraform-aws-modules/cloudwatch/aws//modules/metric-alarm |  |
| <a name="module_alarm_lambda_with_errors"></a> [alarm\_lambda\_with\_errors](#module\_alarm\_lambda\_with\_errors) | terraform-aws-modules/cloudwatch/aws//modules/metric-alarm | ~> 2.0 |
| <a name="module_api_gateway"></a> [api\_gateway](#module\_api\_gateway) | terraform-aws-modules/apigateway-v2/aws | ~> 1.0 |
| <a name="module_dl_bucket"></a> [dl\_bucket](#module\_dl\_bucket) | terraform-aws-modules/s3-bucket/aws | ~> 2.0 |
| <a name="module_lambda"></a> [lambda](#module\_lambda) | terraform-aws-modules/lambda/aws | ~> 2.0 |
| <a name="module_records"></a> [records](#module\_records) | terraform-aws-modules/route53/aws//modules/records | ~> 2.0 |
| <a name="module_sns_topic"></a> [sns\_topic](#module\_sns\_topic) | terraform-aws-modules/sns/aws | ~> 3.0 |

## Resources

| Name | Type |
|------|------|
| [aws_sns_topic_subscription.sns_to_email](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic_subscription) | resource |
| [aws_route53_zone.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/route53_zone) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_allowed_account_ids"></a> [allowed\_account\_ids](#input\_allowed\_account\_ids) | List of allowed AWS acount ids where infrastructure will be created | `list(string)` | n/a | yes |
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | AWS region where infrastructure will be created | `string` | `"eu-west-1"` | no |
| <a name="input_create_dl_bucket"></a> [create\_dl\_bucket](#input\_create\_dl\_bucket) | Whether to create S3 bucket for downloads | `bool` | `false` | no |
| <a name="input_dl_bucket_name"></a> [dl\_bucket\_name](#input\_dl\_bucket\_name) | Name of S3 bucket for downloads (should not include route53\_zone\_name) | `string` | `null` | no |
| <a name="input_dl_dir"></a> [dl\_dir](#input\_dl\_dir) | Name of directory in S3 bucket | `string` | `""` | no |
| <a name="input_email"></a> [email](#input\_email) | Email address to receive CloudWatch alerts | `string` | n/a | yes |
| <a name="input_name"></a> [name](#input\_name) | Name or prefix for many related resources | `string` | `"modulestf-d2c"` | no |
| <a name="input_subdomain"></a> [subdomain](#input\_subdomain) | Route53 subdomain | `string` | `""` | no |
| <a name="input_zone_name"></a> [zone\_name](#input\_zone\_name) | Zone name for ALB and ACM | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_fqdn"></a> [fqdn](#output\_fqdn) | FQDN of API Endpoint |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
