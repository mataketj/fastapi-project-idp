# Dummy GitHub Module
resource "null_resource" "github_repo" {
  provisioner "local-exec" {
    command = "echo 'Provisioning GitHub Repo'"
  }
}
