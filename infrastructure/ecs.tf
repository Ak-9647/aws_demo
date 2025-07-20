# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = "${var.project_name}-cluster"
    Environment = var.environment
  }
}

# Application Load Balancer
resource "aws_lb" "gui" {
  name               = "analytics-gui-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false

  tags = {
    Name        = "${var.project_name}-gui-alb"
    Environment = var.environment
  }
}

# ALB Target Group
resource "aws_lb_target_group" "gui" {
  name     = "analytics-gui-tg"
  port     = 8501
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/_stcore/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name        = "${var.project_name}-gui-tg"
    Environment = var.environment
  }
}

# ALB Listener
resource "aws_lb_listener" "gui" {
  load_balancer_arn = aws_lb.gui.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.gui.arn
  }
}

# Security Group for ALB
resource "aws_security_group" "alb" {
  name        = "analytics-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-alb-sg"
    Environment = var.environment
  }
}

# Security Group for ECS Tasks
resource "aws_security_group" "ecs_tasks" {
  name        = "analytics-ecs-tasks-sg"
  description = "Security group for ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "HTTP from ALB"
    from_port       = 8501
    to_port         = 8501
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-ecs-tasks-sg"
    Environment = var.environment
  }
}

# ECS Task Definition for GUI
resource "aws_ecs_task_definition" "gui" {
  family                   = "${var.project_name}-gui"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn           = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name  = "gui"
      image = "${aws_ecr_repository.gui.repository_url}:v2.0"

      portMappings = [
        {
          containerPort = 8501
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "AWS_DEFAULT_REGION"
          value = var.aws_region
        },
        {
          name  = "CONVERSATION_TABLE"
          value = aws_dynamodb_table.conversation_history.name
        },
        {
          name  = "USER_PREFERENCES_TABLE"
          value = aws_dynamodb_table.user_preferences.name
        },
        {
          name  = "REDIS_ENDPOINT"
          value = aws_elasticache_replication_group.redis.primary_endpoint_address
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.gui.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      essential = true
    }
  ])

  tags = {
    Name        = "${var.project_name}-gui-task"
    Environment = var.environment
  }
}

# CloudWatch Log Group for GUI
resource "aws_cloudwatch_log_group" "gui" {
  name              = "/ecs/${var.project_name}-gui"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-gui-logs"
    Environment = var.environment
  }
}

# ECS Service for GUI
resource "aws_ecs_service" "gui" {
  name            = "${var.project_name}-gui-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.gui.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = aws_subnet.private[*].id
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.gui.arn
    container_name   = "gui"
    container_port   = 8501
  }

  depends_on = [aws_lb_listener.gui]

  tags = {
    Name        = "${var.project_name}-gui-service"
    Environment = var.environment
  }
}