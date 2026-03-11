variable "account_id" {
  description = "New Relic Account ID"
  type        = number
}

variable "user_api_key" {
  description = "New Relic User API Key (NRAK-...) — requires account admin permissions"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "New Relic region"
  type        = string
  default     = "US"

  validation {
    condition     = contains(["US", "EU"], var.region)
    error_message = "Region must be US or EU."
  }
}
