# Dummy MWAA Module
resource "null_resource" "mwaa_env" {
  provisioner "local-exec" {
    command = "echo 'Provisioning MWAA Environment'"
  }
}
