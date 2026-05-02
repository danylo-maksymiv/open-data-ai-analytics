variable "aws_region" {
  description = "Регіон AWS для розгортання"
  default     = "us-east-1"
}

variable "instance_type" {
  description = "Безкоштовний тип сервера"
  default     = "t3.micro"
}

variable "app_port" {
  description = "Порт, на якому працює веб-інтерфейс"
  default     = 5050
}