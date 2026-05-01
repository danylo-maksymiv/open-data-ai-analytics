output "web_public_ip" {
  description = "Публічна IP-адреса нашого сервера"
  value       = aws_instance.app_server.public_ip
}

output "website_url" {
  description = "Готове посилання на твій сайт"
  value       = "http://${aws_instance.app_server.public_ip}:${var.app_port}"
}