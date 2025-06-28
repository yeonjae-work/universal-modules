# Universal Modules Makefile
# 개발, 테스트, 빌드, 배포를 위한 자동화 스크립트

.PHONY: help install test lint format type-check security build docs clean deploy version
.DEFAULT_GOAL := help

# 색상 정의
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

# 변수 정의
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
BLACK := $(PYTHON) -m black
ISORT := $(PYTHON) -m isort
FLAKE8 := $(PYTHON) -m flake8
MYPY := $(PYTHON) -m mypy
BANDIT := $(PYTHON) -m bandit
SAFETY := $(PYTHON) -m safety

# 패키지 목록
PACKAGES := git-data-parser http-api-client llm-service notification-service notion-sync

help: ## 도움말 표시
	@echo "$(BLUE)Universal Modules 개발 도구$(NC)"
	@echo ""
	@echo "$(GREEN)사용 가능한 명령어:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)모듈별 명령어:$(NC)"
	@echo "  $(YELLOW)test-{module}$(NC)        특정 모듈 테스트"
	@echo "  $(YELLOW)lint-{module}$(NC)        특정 모듈 린트"
	@echo "  $(YELLOW)build-{module}$(NC)       특정 모듈 빌드"
	@echo "  $(YELLOW)deploy-{module}$(NC)      특정 모듈 배포"
	@echo ""
	@echo "$(GREEN)사용 가능한 모듈:$(NC) $(PACKAGES)"

install: ## 모든 개발 의존성 설치
	@echo "$(BLUE)📦 개발 의존성 설치 중...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev,docs]"
	@for pkg in $(PACKAGES); do \
		echo "$(BLUE)📦 $$pkg 설치 중...$(NC)"; \
		cd packages/$$pkg && $(PIP) install -e ".[dev]" && cd ../..; \
	done
	@echo "$(GREEN)✅ 설치 완료$(NC)"

install-module: ## 특정 모듈 설치 (MODULE=모듈명)
	@if [ -z "$(MODULE)" ]; then \
		echo "$(RED)❌ MODULE 변수를 지정해주세요. 예: make install-module MODULE=git-data-parser$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)📦 $(MODULE) 설치 중...$(NC)"
	cd packages/$(MODULE) && $(PIP) install -e ".[dev]"
	@echo "$(GREEN)✅ $(MODULE) 설치 완료$(NC)"

test: ## 모든 모듈 테스트
	@echo "$(BLUE)🧪 전체 테스트 실행 중...$(NC)"
	@for pkg in $(PACKAGES); do \
		echo "$(BLUE)🧪 $$pkg 테스트 중...$(NC)"; \
		cd packages/$$pkg && $(PYTEST) tests/ -v --cov=src --cov-report=term-missing && cd ../..; \
	done
	@echo "$(GREEN)✅ 전체 테스트 완료$(NC)"

test-coverage: ## 커버리지 포함 테스트
	@echo "$(BLUE)🧪 커버리지 테스트 실행 중...$(NC)"
	@for pkg in $(PACKAGES); do \
		echo "$(BLUE)🧪 $$pkg 커버리지 테스트 중...$(NC)"; \
		cd packages/$$pkg && $(PYTEST) tests/ -v --cov=src --cov-report=html --cov-report=xml && cd ../..; \
	done
	@echo "$(GREEN)✅ 커버리지 테스트 완료$(NC)"

test-performance: ## 성능 테스트
	@echo "$(BLUE)⚡ 성능 테스트 실행 중...$(NC)"
	@for pkg in $(PACKAGES); do \
		echo "$(BLUE)⚡ $$pkg 성능 테스트 중...$(NC)"; \
		cd packages/$$pkg && \
		if [ -f "tests/test_performance.py" ]; then \
			$(PYTEST) tests/test_performance.py --benchmark-json=benchmark.json -v; \
		else \
			echo "$(YELLOW)⚠️  성능 테스트 파일이 없습니다: $$pkg$(NC)"; \
		fi && cd ../..; \
	done
	@echo "$(GREEN)✅ 성능 테스트 완료$(NC)"

lint: ## 코드 린트 검사
	@echo "$(BLUE)🔍 린트 검사 실행 중...$(NC)"
	@for pkg in $(PACKAGES); do \
		echo "$(BLUE)🔍 $$pkg 린트 검사 중...$(NC)"; \
		cd packages/$$pkg && \
		$(FLAKE8) src/ tests/ && \
		cd ../..; \
	done
	@echo "$(GREEN)✅ 린트 검사 완료$(NC)"

format: ## 코드 포맷팅
	@echo "$(BLUE)🎨 코드 포맷팅 실행 중...$(NC)"
	@for pkg in $(PACKAGES); do \
		echo "$(BLUE)🎨 $$pkg 포맷팅 중...$(NC)"; \
		cd packages/$$pkg && \
		$(BLACK) src/ tests/ && \
		$(ISORT) src/ tests/ && \
		cd ../..; \
	done
	@echo "$(GREEN)✅ 코드 포맷팅 완료$(NC)"

format-check: ## 코드 포맷 검사
	@echo "$(BLUE)🎨 코드 포맷 검사 실행 중...$(NC)"
	@for pkg in $(PACKAGES); do \
		echo "$(BLUE)🎨 $$pkg 포맷 검사 중...$(NC)"; \
		cd packages/$$pkg && \
		$(BLACK) --check src/ tests/ && \
		$(ISORT) --check-only src/ tests/ && \
		cd ../..; \
	done
	@echo "$(GREEN)✅ 코드 포맷 검사 완료$(NC)"

type-check: ## 타입 검사
	@echo "$(BLUE)🔍 타입 검사 실행 중...$(NC)"
	@for pkg in $(PACKAGES); do \
		echo "$(BLUE)🔍 $$pkg 타입 검사 중...$(NC)"; \
		cd packages/$$pkg && $(MYPY) src/ && cd ../..; \
	done
	@echo "$(GREEN)✅ 타입 검사 완료$(NC)"

security: ## 보안 검사
	@echo "$(BLUE)🔒 보안 검사 실행 중...$(NC)"
	@for pkg in $(PACKAGES); do \
		echo "$(BLUE)🔒 $$pkg 보안 검사 중...$(NC)"; \
		cd packages/$$pkg && \
		$(BANDIT) -r src/ -f json -o bandit-report.json || true && \
		$(SAFETY) check --json --output safety-report.json || true && \
		cd ../..; \
	done
	@echo "$(GREEN)✅ 보안 검사 완료$(NC)"

quality: format-check lint type-check security ## 전체 코드 품질 검사
	@echo "$(GREEN)✅ 전체 코드 품질 검사 완료$(NC)"

build: ## 모든 모듈 빌드
	@echo "$(BLUE)🏗️  전체 빌드 실행 중...$(NC)"
	@for pkg in $(PACKAGES); do \
		echo "$(BLUE)🏗️  $$pkg 빌드 중...$(NC)"; \
		cd packages/$$pkg && \
		$(PYTHON) -m build && \
		$(PYTHON) -m twine check dist/* && \
		cd ../..; \
	done
	@echo "$(GREEN)✅ 전체 빌드 완료$(NC)"

docs: ## 문서 생성
	@echo "$(BLUE)📚 문서 생성 중...$(NC)"
	@for pkg in $(PACKAGES); do \
		echo "$(BLUE)📚 $$pkg 문서 생성 중...$(NC)"; \
		$(PYTHON) scripts/update-documentation.py $$pkg --save --changelog; \
	done
	@echo "$(GREEN)✅ 문서 생성 완료$(NC)"

clean: ## 빌드 아티팩트 정리
	@echo "$(BLUE)🧹 정리 작업 실행 중...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ 정리 완료$(NC)"

version: ## 버전 정보 표시
	@echo "$(BLUE)📋 버전 정보$(NC)"
	$(PYTHON) scripts/version-manager.py list

version-bump: ## 버전 업데이트 (MODULE=모듈명 TYPE=major|minor|patch MESSAGE=메시지)
	@if [ -z "$(MODULE)" ] || [ -z "$(TYPE)" ]; then \
		echo "$(RED)❌ MODULE과 TYPE을 지정해주세요.$(NC)"; \
		echo "$(YELLOW)예: make version-bump MODULE=git-data-parser TYPE=patch MESSAGE='버그 수정'$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)📈 $(MODULE) 버전 업데이트 중... ($(TYPE))$(NC)"
	$(PYTHON) scripts/version-manager.py bump $(MODULE) $(TYPE) -m "$(MESSAGE)"
	@echo "$(GREEN)✅ 버전 업데이트 완료$(NC)"

deploy: ## 전체 배포 (프로덕션)
	@echo "$(BLUE)🚀 전체 배포 실행 중...$(NC)"
	@echo "$(YELLOW)⚠️  프로덕션 배포를 진행합니다. 계속하시겠습니까? [y/N]$(NC)"
	@read confirm && [ "$$confirm" = "y" ] || exit 1
	$(MAKE) quality
	$(MAKE) test
	$(MAKE) build
	@for pkg in $(PACKAGES); do \
		echo "$(BLUE)🚀 $$pkg 배포 중...$(NC)"; \
		cd packages/$$pkg && \
		$(PYTHON) -m twine upload dist/* && \
		cd ../..; \
	done
	@echo "$(GREEN)✅ 전체 배포 완료$(NC)"

deploy-test: ## 테스트 PyPI 배포
	@echo "$(BLUE)🧪 테스트 PyPI 배포 실행 중...$(NC)"
	$(MAKE) quality
	$(MAKE) test
	$(MAKE) build
	@for pkg in $(PACKAGES); do \
		echo "$(BLUE)🧪 $$pkg 테스트 배포 중...$(NC)"; \
		cd packages/$$pkg && \
		$(PYTHON) -m twine upload --repository testpypi dist/* && \
		cd ../..; \
	done
	@echo "$(GREEN)✅ 테스트 배포 완료$(NC)"

check-deps: ## 의존성 확인
	@echo "$(BLUE)🔍 의존성 확인 중...$(NC)"
	$(PYTHON) scripts/version-manager.py check-deps
	@echo "$(GREEN)✅ 의존성 확인 완료$(NC)"

sync-deps: ## 의존성 동기화
	@echo "$(BLUE)🔄 의존성 동기화 중...$(NC)"
	$(PYTHON) scripts/version-manager.py sync-deps
	@echo "$(GREEN)✅ 의존성 동기화 완료$(NC)"

dev-setup: install ## 개발 환경 설정
	@echo "$(BLUE)🔧 개발 환경 설정 중...$(NC)"
	@echo "$(BLUE)Git hooks 설정 중...$(NC)"
	@if [ -d ".git" ]; then \
		echo "#!/bin/sh" > .git/hooks/pre-commit; \
		echo "make format-check lint" >> .git/hooks/pre-commit; \
		chmod +x .git/hooks/pre-commit; \
		echo "$(GREEN)✅ Pre-commit hook 설정 완료$(NC)"; \
	fi
	@echo "$(GREEN)✅ 개발 환경 설정 완료$(NC)"

ci: quality test build ## CI 파이프라인 실행
	@echo "$(GREEN)✅ CI 파이프라인 완료$(NC)"

# 모듈별 타겟 생성
define create-module-targets
test-$(1): ## $(1) 모듈 테스트
	@echo "$(BLUE)🧪 $(1) 테스트 실행 중...$(NC)"
	cd packages/$(1) && $(PYTEST) tests/ -v --cov=src --cov-report=term-missing
	@echo "$(GREEN)✅ $(1) 테스트 완료$(NC)"

lint-$(1): ## $(1) 모듈 린트
	@echo "$(BLUE)🔍 $(1) 린트 검사 중...$(NC)"
	cd packages/$(1) && $(FLAKE8) src/ tests/
	@echo "$(GREEN)✅ $(1) 린트 완료$(NC)"

build-$(1): ## $(1) 모듈 빌드
	@echo "$(BLUE)🏗️  $(1) 빌드 중...$(NC)"
	cd packages/$(1) && $(PYTHON) -m build && $(PYTHON) -m twine check dist/*
	@echo "$(GREEN)✅ $(1) 빌드 완료$(NC)"

deploy-$(1): ## $(1) 모듈 배포
	@echo "$(BLUE)🚀 $(1) 배포 중...$(NC)"
	cd packages/$(1) && $(PYTHON) -m twine upload dist/*
	@echo "$(GREEN)✅ $(1) 배포 완료$(NC)"

docs-$(1): ## $(1) 모듈 문서 생성
	@echo "$(BLUE)📚 $(1) 문서 생성 중...$(NC)"
	$(PYTHON) scripts/update-documentation.py $(1) --save
	@echo "$(GREEN)✅ $(1) 문서 생성 완료$(NC)"
endef

# 각 패키지에 대해 타겟 생성
$(foreach pkg,$(PACKAGES),$(eval $(call create-module-targets,$(pkg))))

# 환경 정보 표시
info: ## 환경 정보 표시
	@echo "$(BLUE)🔧 환경 정보$(NC)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Pip: $$($(PIP) --version)"
	@echo "작업 디렉터리: $$(pwd)"
	@echo "패키지 목록: $(PACKAGES)"
	@echo ""
	@echo "$(BLUE)📦 설치된 패키지$(NC)"
	@for pkg in $(PACKAGES); do \
		if [ -d "packages/$$pkg" ]; then \
			version=$$(cd packages/$$pkg && $(PYTHON) -c "import toml; print(toml.load('pyproject.toml')['project']['version'])" 2>/dev/null || echo "unknown"); \
			echo "  $$pkg: v$$version"; \
		fi; \
	done 