# SkillHub Makefile

.PHONY: help env up down build logs restart ps clean

help:  ## 显示帮助信息
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Docker 开发环境

env:  ## 检查并初始化环境变量文件
	@python -c "import os, shutil; not os.path.exists('.env') and os.path.exists('.env.example') and shutil.copy('.env.example', '.env') and print('[INFO] 已自动通过 .env.example 模板创建了 .env 文件！')"

up: env  ## 启动所有服务
	docker-compose up -d

down:  ## 停止所有服务
	docker-compose down

build:  ## 构建所有镜像
	docker-compose build

logs:  ## 查看所有服务日志
	docker-compose logs -f

restart:  ## 重启所有服务
	docker-compose restart

ps:  ## 查看服务状态
	docker-compose ps

clean:  ## 清理所有容器和卷
	docker-compose down -v

##@ 开发工具

format-backend:  ## 格式化后端代码 (Black + isort)
	cd backend && black . && isort .

lint-backend:  ## 检查后端代码 (flake8 + mypy)
	cd backend && flake8 . && mypy .

test-backend:  ## 运行后端测试
	cd backend && pytest

format-frontend:  ## 格式化前端代码
	cd frontend && npm run format

lint-frontend:  ## 检查前端代码
	cd frontend && npm run lint

test-frontend:  ## 运行前端测试
	cd frontend && npm run test
