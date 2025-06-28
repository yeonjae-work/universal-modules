# Universal Data Aggregator

**커밋 데이터와 diff 정보를 가공, 집계, 통계 처리하는 범용 모듈**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 **주요 기능**

- **개발자별 활동 집계**: 커밋 수, 코드 변경량, 작업 패턴 분석
- **저장소별 통계**: 기여자, 언어 사용량, 복잡도 메트릭
- **시간대별 분석**: 피크 시간, 작업 패턴, 커밋 빈도
- **복잡도 메트릭**: 코드 품질 및 복잡도 트렌드 분석
- **캐시 기능**: 메모리 기반 캐싱으로 성능 최적화
- **타입 안전성**: Pydantic 기반의 강력한 데이터 검증

## 📦 **설치**

```bash
# GitHub에서 직접 설치
pip install git+https://github.com/yeonjae-work/universal-modules.git#subdirectory=packages/universal-data-aggregator

# 개발 의존성과 함께 설치
pip install "git+https://github.com/yeonjae-work/universal-modules.git#subdirectory=packages/universal-data-aggregator[dev]"
```

## 🚀 **빠른 시작**

### **기본 사용법**

```python
from datetime import datetime
from universal_data_aggregator import (
    DataAggregatorService, AggregationInput, DateRange,
    CommitData, DiffInfo, DiffType
)

# 서비스 초기화
service = DataAggregatorService(enable_cache=True)

# 샘플 커밋 데이터 생성
diff_info = DiffInfo(
    file_path="src/main.py",
    diff_type=DiffType.ADDED,
    lines_added=50,
    lines_deleted=10,
    language="Python"
)

commit = CommitData(
    commit_id="abc123",
    author="John Doe",
    author_email="john@example.com",
    timestamp=datetime.now(),
    message="Add new feature",
    repository="my-project",
    branch="main",
    diff_info=[diff_info]
)

# 집계 입력 데이터 구성
date_range = DateRange(start="2024-06-01", end="2024-06-01")
input_data = AggregationInput(
    commits=[commit],
    date_range=date_range
)

# 데이터 집계 수행
result = await service.aggregate_data(input_data)

print(f"총 개발자 수: {result.total_developers}")
print(f"총 커밋 수: {result.total_commits}")
print(f"총 저장소 수: {result.total_repositories}")
```

### **고급 사용법 - 필터링**

```python
# 특정 개발자만 집계
input_data = AggregationInput(
    commits=commits,
    date_range=date_range,
    developer_filter=["john@example.com", "jane@example.com"],
    repository_filter=["project-a", "project-b"]
)

result = await service.aggregate_data(input_data)

# 개발자별 상세 통계
for email, stats in result.developer_stats.items():
    print(f"개발자: {stats.developer}")
    print(f"커밋 수: {stats.commit_count}")
    print(f"추가된 라인: {stats.lines_added}")
    print(f"삭제된 라인: {stats.lines_deleted}")
    print(f"변경된 파일: {stats.files_changed}")
    print(f"사용 언어: {', '.join(stats.languages_used)}")
    print(f"평균 복잡도: {stats.avg_complexity}")
    print("---")
```

## 📊 **데이터 모델**

### **입력 데이터**

#### **CommitData**
```python
class CommitData(BaseModel):
    commit_id: str
    author: str
    author_email: str
    timestamp: datetime
    message: str
    repository: str
    branch: str
    diff_info: List[DiffInfo]
```

#### **DiffInfo**
```python
class DiffInfo(BaseModel):
    file_path: str
    diff_type: DiffType  # ADDED, MODIFIED, DELETED, RENAMED
    lines_added: int
    lines_deleted: int
    complexity_score: Optional[float]
    language: Optional[str]
```

### **출력 데이터**

#### **AggregationResult**
```python
class AggregationResult(BaseModel):
    developer_stats: Dict[str, DeveloperStats]
    repository_stats: Dict[str, RepositoryStats]
    time_analysis: TimeAnalysis
    complexity_metrics: ComplexityMetrics
    aggregation_time: datetime
    data_quality_score: float
```

#### **DeveloperStats**
```python
class DeveloperStats(BaseModel):
    developer: str
    developer_email: str
    commit_count: int
    lines_added: int
    lines_deleted: int
    files_changed: int
    repositories: List[str]
    languages_used: List[str]
    avg_complexity: float
    peak_hours: List[int]
```

## 🔧 **API 레퍼런스**

### **DataAggregatorService**

#### **메서드**

- `__init__(enable_cache: bool = True)` - 서비스 초기화
- `async aggregate_data(input_data: AggregationInput) -> AggregationResult` - 메인 집계 메서드
- `aggregate_by_developer(commits: List[CommitData], input_data: AggregationInput) -> Dict[str, DeveloperStats]` - 개발자별 집계
- `generate_time_analysis(commits: List[CommitData]) -> TimeAnalysis` - 시간대별 분석
- `calculate_complexity_metrics(commits: List[CommitData]) -> ComplexityMetrics` - 복잡도 계산

## 📈 **분석 기능**

### **시간대별 분석**

```python
# 시간대별 활동 패턴 분석
time_analysis = result.time_analysis
print(f"피크 시간대: {time_analysis.peak_hours}")
print(f"작업 패턴: {time_analysis.work_pattern}")
print(f"평균 커밋 간격: {time_analysis.avg_commit_interval}분")

# 시간대별 커밋 빈도
for hour, count in time_analysis.commit_frequency.items():
    print(f"{hour}시: {count}개 커밋")
```

### **복잡도 메트릭**

```python
# 코드 복잡도 분석
complexity = result.complexity_metrics
print(f"평균 복잡도: {complexity.avg_complexity}")
print(f"최대 복잡도: {complexity.max_complexity}")
print(f"복잡도 트렌드: {complexity.complexity_trend}")
print(f"고복잡도 파일: {complexity.high_complexity_files}")
```

### **저장소별 통계**

```python
# 저장소별 상세 정보
for repo_name, repo_stats in result.repository_stats.items():
    print(f"저장소: {repo_name}")
    print(f"총 커밋: {repo_stats.total_commits}")
    print(f"기여자 수: {len(repo_stats.contributors)}")
    print(f"사용 언어: {', '.join(repo_stats.languages)}")
    print("---")
```

## ⚡ **성능 최적화**

### **캐시 활용**

```python
# 캐시 활성화 (기본값)
service = DataAggregatorService(enable_cache=True)

# 캐시 비활성화 (메모리 절약)
service = DataAggregatorService(enable_cache=False)
```

### **대용량 데이터 처리**

```python
# 배치 단위로 처리
async def process_large_dataset(commits: List[CommitData], batch_size: int = 1000):
    results = []
    
    for i in range(0, len(commits), batch_size):
        batch = commits[i:i + batch_size]
        input_data = AggregationInput(
            commits=batch,
            date_range=DateRange(start="2024-06-01", end="2024-06-01")
        )
        
        result = await service.aggregate_data(input_data)
        results.append(result)
    
    return results
```

## 🧪 **테스트**

```bash
# 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=universal_data_aggregator

# 특정 테스트만 실행
pytest tests/test_service.py::TestDataAggregatorService::test_aggregate_data_success
```

## 🔧 **개발자 가이드**

### **개발 환경 설정**

```bash
# 저장소 클론
git clone https://github.com/yeonjae-work/universal-modules.git
cd universal-modules/packages/universal-data-aggregator

# 개발 의존성 설치
pip install -e .[dev]

# 코드 포맷팅
black src/ tests/
isort src/ tests/

# 린팅
flake8 src/ tests/
mypy src/
```

### **커스텀 집계 로직 추가**

```python
class CustomDataAggregatorService(DataAggregatorService):
    """커스텀 집계 서비스"""
    
    def calculate_custom_metrics(self, commits: List[CommitData]) -> Dict[str, Any]:
        """사용자 정의 메트릭 계산"""
        # 커스텀 로직 구현
        return {
            "custom_metric": "value"
        }
```

## 🤝 **기여하기**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **라이선스**

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙋‍♂️ **지원**

- **이슈 리포트**: [GitHub Issues](https://github.com/yeonjae-work/universal-modules/issues)
- **문서**: [GitHub Wiki](https://github.com/yeonjae-work/universal-modules/wiki)
- **토론**: [GitHub Discussions](https://github.com/yeonjae-work/universal-modules/discussions)

## 📈 **로드맵**

- [ ] 실시간 스트리밍 데이터 처리
- [ ] 머신러닝 기반 패턴 분석
- [ ] 그래프 데이터베이스 연동
- [ ] 대시보드 시각화 지원
- [ ] 다중 저장소 병합 분석
- [ ] 성능 벤치마크 도구

---

**Universal Data Aggregator**로 개발 활동을 체계적으로 분석하고 인사이트를 발견하세요! 📊 