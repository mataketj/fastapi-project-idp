# Dummy Snowflake Module
resource "null_resource" "snowflake_account" {
  provisioner "local-exec" {
    command = "echo 'Provisioning Snowflake Account: ${var.account_name}'"
  }
}

variable "account_name" {
  type = string
}
