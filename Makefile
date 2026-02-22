.PHONY: help install test lint format clean run init-db

help:
	@echo "可用的命令:"
	@echo "  make install      - 安装依赖"
	@echo "  make test         - 运行测试"
	@echo "  make lint         - 代码检查"
	@echo "  make format       - 代码格式化"
	@echo "  make clean        - 清理临时文件"
	@echo "  make run          - 运行应用"
	@echo "  make init-db      - 初始化数据库"

install:
	pip install -r requirements.txt

test:
	pytest -v

test-coverage:
	pytest --cov=src --cov-report=html

lint:
	flake8 src
	mypy src

format:
	black src
	isort src

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/

run:
	python -m uvicorn src.main:app --reload

init-db:
	python scripts/init_data.py
