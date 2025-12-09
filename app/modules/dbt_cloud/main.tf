# Dummy dbt Cloud Module
resource "null_resource" "dbt_project" {
  provisioner "local-exec" {
    command = "echo 'Provisioning dbt Project: ${var.project_name}'"
  }
}

variable "project_name" {
  type = string
}
