output "fqdn" {
  description = "FQDN of API Endpoint"
  value       = "https://${module.records.route53_record_fqdn["${var.subdomain} A"]}"
}
