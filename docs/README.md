# Universal Modules 문서 가이드

## 📚 문서 구조

이 프로젝트의 문서는 **모듈별 분산 관리** 방식을 채택합니다.

### 📁 루트 docs/ (이 디렉터리)
전체 프로젝트 관련 문서만 포함합니다:
- 프로젝트 개요 및 아키텍처
- 통합 개발 가이드
- CI/CD 및 배포 가이드
- 문서 템플릿

### 📦 각 모듈별 docs/
각 모듈의 상세 기술명세서는 해당 모듈 디렉터리에서 관리됩니다:

```
packages/
├── git-data-parser/docs/technical-specification.md
├── http-api-client/docs/technical-specification.md  
├── llm-service/docs/technical-specification.md
├── notification-service/docs/technical-specification.md
└── notion-sync/docs/technical-specification.md
```

## 🔗 모듈별 문서 링크

### [Git Data Parser](../packages/git-data-parser/docs/technical-specification.md)
GitHub webhook 이벤트 파싱 및 diff 분석 모듈

### [HTTP API Client](../packages/http-api-client/docs/technical-specification.md)  
다중 플랫폼 API 통합 클라이언트 모듈

### [LLM Service](../packages/llm-service/docs/technical-specification.md)
다중 LLM 제공자 통합 서비스 모듈

### [Notification Service](../packages/notification-service/docs/technical-specification.md)
다중 채널 알림 전송 서비스 모듈

### [Notion Sync](../packages/notion-sync/docs/technical-specification.md)
Notion 데이터베이스 동기화 모듈

## 📋 문서 작성 가이드

새로운 모듈 문서를 작성할 때는 [module-documentation-template.md](./module-documentation-template.md)를 참고하세요.

## 🔄 문서 자동 업데이트

각 모듈의 기술명세서는 배포 시마다 자동으로 업데이트됩니다:
- 코드 변경 감지 → CI/CD 트리거
- AST 파싱으로 코드 분석
- 기술명세서 자동 업데이트
- 버전 관리 및 배포

---

**문서 관리 원칙**: 각 모듈은 독립적으로 문서를 관리하며, 마이크로서비스 아키텍처에 적합한 구조를 유지합니다. 