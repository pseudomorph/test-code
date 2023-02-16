resource "null_resource" "localexec" {
  provisioner "local-exec" {
    command = "ls -la"
  }
}
