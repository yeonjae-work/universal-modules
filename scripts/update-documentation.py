#!/usr/bin/env python3
"""
기술명세서 자동 업데이트 스크립트

이 스크립트는 모듈 배포 시 기술명세서를 자동으로 업데이트합니다:
- 버전 정보 업데이트
- 변경사항 추적
- API 문서 생성
- 데이터 흐름 다이어그램 업데이트
- 성능 메트릭 업데이트
"""

import os
import sys
import json
import subprocess
import argparse
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import toml
import importlib.util
from dataclasses import dataclass
import re


@dataclass
class APIEndpoint:
    """API 엔드포인트 정보"""
    name: str
    description: str
    parameters: List[Dict[str, Any]]
    returns: Dict[str, Any]
    examples: List[str]


@dataclass
class ModuleAnalysis:
    """모듈 분석 결과"""
    name: str
    version: str
    description: str
    classes: List[str]
    functions: List[str]
    dependencies: List[str]
    api_endpoints: List[APIEndpoint]
    performance_metrics: Dict[str, Any]


class DocumentationUpdater:
    """문서 업데이트 관리자"""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.packages_path = root_path / "packages"
        self.docs_path = root_path / "docs"
        self.template_path = self.docs_path / "module-documentation-template.md"
        
    def analyze_module(self, module_name: str) -> ModuleAnalysis:
        """모듈 분석"""
        module_path = self.packages_path / module_name
        
        if not module_path.exists():
            raise ValueError(f"모듈 '{module_name}'을 찾을 수 없습니다.")
        
        # pyproject.toml 읽기
        pyproject_path = module_path / "pyproject.toml"
        pyproject_data = toml.load(pyproject_path)
        project_info = pyproject_data.get("project", {})
        
        version = project_info.get("version", "0.1.0")
        description = project_info.get("description", "")
        dependencies = project_info.get("dependencies", [])
        
        # 소스 코드 분석
        src_path = module_path / "src" / f"universal_{module_name.replace('-', '_')}"
        classes, functions, api_endpoints = self._analyze_source_code(src_path)
        
        # 성능 메트릭 수집
        performance_metrics = self._collect_performance_metrics(module_path)
        
        return ModuleAnalysis(
            name=module_name,
            version=version,
            description=description,
            classes=classes,
            functions=functions,
            dependencies=dependencies,
            api_endpoints=api_endpoints,
            performance_metrics=performance_metrics
        )
    
    def _analyze_source_code(self, src_path: Path) -> Tuple[List[str], List[str], List[APIEndpoint]]:
        """소스 코드 분석"""
        classes = []
        functions = []
        api_endpoints = []
        
        if not src_path.exists():
            return classes, functions, api_endpoints
        
        for py_file in src_path.glob("*.py"):
            if py_file.name.startswith("_") and py_file.name != "__init__.py":
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes.append(node.name)
                        
                        # 클래스 메서드 분석
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                                endpoint = self._extract_api_endpoint(item, content)
                                if endpoint:
                                    api_endpoints.append(endpoint)
                    
                    elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                        functions.append(node.name)
                        endpoint = self._extract_api_endpoint(node, content)
                        if endpoint:
                            api_endpoints.append(endpoint)
                            
            except Exception as e:
                print(f"⚠️  파일 {py_file} 분석 실패: {e}")
        
        return classes, functions, api_endpoints
    
    def _extract_api_endpoint(self, node: ast.FunctionDef, content: str) -> Optional[APIEndpoint]:
        """함수/메서드에서 API 엔드포인트 정보 추출"""
        docstring = ast.get_docstring(node)
        if not docstring:
            return None
        
        # 매개변수 분석
        parameters = []
        for arg in node.args.args:
            if arg.arg != "self":
                param_info = {
                    "name": arg.arg,
                    "type": self._get_type_annotation(arg),
                    "description": self._extract_param_description(docstring, arg.arg)
                }
                parameters.append(param_info)
        
        # 반환 타입 분석
        returns = {
            "type": self._get_type_annotation(node.returns) if node.returns else "Any",
            "description": self._extract_return_description(docstring)
        }
        
        # 예제 추출
        examples = self._extract_examples(docstring)
        
        return APIEndpoint(
            name=node.name,
            description=docstring.split('\n')[0],
            parameters=parameters,
            returns=returns,
            examples=examples
        )
    
    def _get_type_annotation(self, annotation) -> str:
        """타입 어노테이션을 문자열로 변환"""
        if annotation is None:
            return "Any"
        
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        else:
            return "Any"
    
    def _extract_param_description(self, docstring: str, param_name: str) -> str:
        """독스트링에서 매개변수 설명 추출"""
        lines = docstring.split('\n')
        for i, line in enumerate(lines):
            if f"Args:" in line or f"Parameters:" in line:
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().startswith(f"{param_name}:"):
                        return lines[j].split(":", 1)[1].strip()
        return ""
    
    def _extract_return_description(self, docstring: str) -> str:
        """독스트링에서 반환값 설명 추출"""
        lines = docstring.split('\n')
        for i, line in enumerate(lines):
            if "Returns:" in line:
                if i + 1 < len(lines):
                    return lines[i + 1].strip()
        return ""
    
    def _extract_examples(self, docstring: str) -> List[str]:
        """독스트링에서 예제 추출"""
        examples = []
        lines = docstring.split('\n')
        in_example = False
        current_example = []
        
        for line in lines:
            if "Example:" in line or "Examples:" in line:
                in_example = True
                continue
            
            if in_example:
                if line.strip() == "" and current_example:
                    examples.append('\n'.join(current_example))
                    current_example = []
                    in_example = False
                elif line.strip():
                    current_example.append(line.strip())
        
        if current_example:
            examples.append('\n'.join(current_example))
        
        return examples
    
    def _collect_performance_metrics(self, module_path: Path) -> Dict[str, Any]:
        """성능 메트릭 수집"""
        metrics = {
            "test_coverage": 0.0,
            "benchmark_results": {},
            "code_complexity": 0,
            "lines_of_code": 0
        }
        
        # 테스트 커버리지
        coverage_file = module_path / "coverage.xml"
        if coverage_file.exists():
            metrics["test_coverage"] = self._parse_coverage(coverage_file)
        
        # 벤치마크 결과
        benchmark_file = module_path / "benchmark.json"
        if benchmark_file.exists():
            with open(benchmark_file, 'r') as f:
                metrics["benchmark_results"] = json.load(f)
        
        # 코드 복잡도 및 라인 수
        src_path = module_path / "src"
        if src_path.exists():
            metrics["lines_of_code"] = self._count_lines_of_code(src_path)
            metrics["code_complexity"] = self._calculate_complexity(src_path)
        
        return metrics
    
    def _parse_coverage(self, coverage_file: Path) -> float:
        """커버리지 파일에서 커버리지 비율 추출"""
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(coverage_file)
            root = tree.getroot()
            
            coverage_elem = root.find(".//coverage")
            if coverage_elem is not None:
                line_rate = coverage_elem.get("line-rate", "0")
                return float(line_rate) * 100
        except Exception:
            pass
        
        return 0.0
    
    def _count_lines_of_code(self, src_path: Path) -> int:
        """소스 코드 라인 수 계산"""
        total_lines = 0
        
        for py_file in src_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # 빈 줄과 주석 제외
                    code_lines = [line for line in lines 
                                if line.strip() and not line.strip().startswith('#')]
                    total_lines += len(code_lines)
            except Exception:
                pass
        
        return total_lines
    
    def _calculate_complexity(self, src_path: Path) -> int:
        """코드 복잡도 계산 (간단한 순환 복잡도)"""
        total_complexity = 0
        
        for py_file in src_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 간단한 순환 복잡도 계산
                complexity_keywords = ['if', 'elif', 'for', 'while', 'except', 'and', 'or']
                for keyword in complexity_keywords:
                    total_complexity += content.count(f' {keyword} ')
                    total_complexity += content.count(f'\t{keyword} ')
                    
            except Exception:
                pass
        
        return total_complexity
    
    def generate_documentation(self, module_name: str, version: Optional[str] = None) -> str:
        """기술명세서 생성"""
        analysis = self.analyze_module(module_name)
        
        if version:
            analysis.version = version
        
        # 템플릿 로드
        if not self.template_path.exists():
            raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {self.template_path}")
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 변수 치환
        replacements = {
            '{모듈명}': analysis.name,
            '{버전}': analysis.version,
            '{날짜}': datetime.now().strftime('%Y-%m-%d'),
            '{담당자}': 'Universal Modules Team',
            '{모듈의 핵심 목적과 단일 책임 설명}': analysis.description or f"{analysis.name} 모듈의 핵심 기능을 제공합니다.",
            '{주요클래스}': analysis.classes[0] if analysis.classes else 'MainService',
            '{설정클래스}': f"{analysis.name.title().replace('-', '')}Config",
            '{문서버전}': f"v{analysis.version}",
            '{업데이트날짜}': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '{리뷰날짜}': datetime.now().strftime('%Y-%m-%d')
        }
        
        documentation = template
        for placeholder, value in replacements.items():
            documentation = documentation.replace(placeholder, value)
        
        # API 문서 생성
        api_docs = self._generate_api_documentation(analysis.api_endpoints)
        documentation = documentation.replace('## 📚 사용 설명서', f'## 📚 사용 설명서\n\n{api_docs}')
        
        # 성능 메트릭 업데이트
        metrics_section = self._generate_metrics_section(analysis.performance_metrics)
        documentation = documentation.replace('## 📈 성능 지표', metrics_section)
        
        # 의존성 다이어그램 업데이트
        deps_diagram = self._generate_dependency_diagram(analysis.dependencies)
        documentation = re.sub(
            r'```mermaid\ngraph LR\n.*?\n```',
            deps_diagram,
            documentation,
            flags=re.DOTALL
        )
        
        return documentation
    
    def _generate_api_documentation(self, endpoints: List[APIEndpoint]) -> str:
        """API 문서 생성"""
        if not endpoints:
            return ""
        
        api_docs = "\n### API 참조\n\n"
        
        for endpoint in endpoints:
            api_docs += f"#### `{endpoint.name}`\n\n"
            api_docs += f"{endpoint.description}\n\n"
            
            if endpoint.parameters:
                api_docs += "**매개변수:**\n"
                for param in endpoint.parameters:
                    api_docs += f"- `{param['name']}` ({param['type']}): {param['description']}\n"
                api_docs += "\n"
            
            if endpoint.returns['description']:
                api_docs += f"**반환값:** {endpoint.returns['description']}\n\n"
            
            if endpoint.examples:
                api_docs += "**예제:**\n```python\n"
                api_docs += endpoint.examples[0]
                api_docs += "\n```\n\n"
        
        return api_docs
    
    def _generate_metrics_section(self, metrics: Dict[str, Any]) -> str:
        """성능 지표 섹션 생성"""
        section = "## 📈 성능 지표\n\n"
        
        section += "### 코드 품질\n"
        section += f"- **테스트 커버리지**: {metrics['test_coverage']:.1f}%\n"
        section += f"- **코드 라인 수**: {metrics['lines_of_code']:,} 라인\n"
        section += f"- **순환 복잡도**: {metrics['code_complexity']}\n\n"
        
        if metrics['benchmark_results']:
            section += "### 벤치마크 결과\n"
            for test_name, result in metrics['benchmark_results'].items():
                if isinstance(result, dict) and 'mean' in result:
                    section += f"- **{test_name}**: {result['mean']:.3f}초 (평균)\n"
            section += "\n"
        
        section += "### 확장성\n"
        section += "- **동시 처리**: 테스트 결과 기반으로 업데이트 예정\n"
        section += "- **메모리 사용량**: 프로파일링 결과 기반으로 업데이트 예정\n\n"
        
        return section
    
    def _generate_dependency_diagram(self, dependencies: List[str]) -> str:
        """의존성 다이어그램 생성"""
        diagram = "```mermaid\ngraph LR\n"
        diagram += "    A[모듈] --> B[pydantic]\n"
        
        for i, dep in enumerate(dependencies[:5], 3):  # 최대 5개만 표시
            clean_dep = dep.split('>=')[0].split('==')[0].strip()
            diagram += f"    A --> {chr(66+i)}[{clean_dep}]\n"
        
        diagram += "    \n    subgraph \"선택적 의존성\"\n"
        diagram += "        E[dev dependencies]\n"
        diagram += "        F[platform specific]\n"
        diagram += "    end\n```"
        
        return diagram
    
    def save_documentation(self, module_name: str, documentation: str):
        """기술명세서 저장"""
        module_docs_path = self.packages_path / module_name / "docs"
        module_docs_path.mkdir(exist_ok=True)
        
        doc_file = module_docs_path / "technical-specification.md"
        
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(documentation)
        
        print(f"✅ 기술명세서 저장: {doc_file}")
    
    def update_changelog(self, module_name: str, version: str):
        """변경사항 로그 업데이트"""
        module_path = self.packages_path / module_name
        changelog_path = module_path / "CHANGELOG.md"
        
        # Git에서 변경사항 가져오기
        changes = self._get_git_changes_since_last_tag(module_name)
        
        changelog_entry = f"\n## [{version}] - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        if changes:
            changelog_entry += "### 변경사항\n"
            for change in changes:
                changelog_entry += f"- {change}\n"
        else:
            changelog_entry += "### 변경사항\n- 마이너 업데이트 및 개선사항\n"
        
        changelog_entry += "\n"
        
        # 기존 CHANGELOG.md 읽기
        existing_content = ""
        if changelog_path.exists():
            with open(changelog_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        
        # 새 내용 추가
        if existing_content.startswith("# Changelog"):
            # 기존 헤더 유지
            parts = existing_content.split('\n', 2)
            if len(parts) >= 3:
                new_content = f"{parts[0]}\n{parts[1]}\n{changelog_entry}{parts[2]}"
            else:
                new_content = f"{existing_content}\n{changelog_entry}"
        else:
            new_content = f"# Changelog\n\n모든 주요 변경사항이 이 파일에 기록됩니다.\n{changelog_entry}{existing_content}"
        
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ CHANGELOG.md 업데이트: {changelog_path}")
    
    def _get_git_changes_since_last_tag(self, module_name: str) -> List[str]:
        """마지막 태그 이후 Git 변경사항 가져오기"""
        try:
            # 마지막 태그 찾기
            result = subprocess.run(
                ["git", "tag", "-l", f"{module_name}-v*", "--sort=-version:refname"],
                capture_output=True,
                text=True,
                cwd=self.root_path
            )
            
            if result.returncode == 0 and result.stdout.strip():
                last_tag = result.stdout.strip().split('\n')[0]
                
                # 태그 이후 변경사항 가져오기
                changes_result = subprocess.run(
                    ["git", "log", f"{last_tag}..HEAD", "--oneline", "--", f"packages/{module_name}"],
                    capture_output=True,
                    text=True,
                    cwd=self.root_path
                )
                
                if changes_result.returncode == 0:
                    changes = []
                    for line in changes_result.stdout.strip().split('\n'):
                        if line.strip():
                            # 커밋 해시 제거하고 메시지만 추출
                            commit_msg = ' '.join(line.split()[1:])
                            changes.append(commit_msg)
                    return changes
            
        except Exception as e:
            print(f"⚠️  Git 변경사항 가져오기 실패: {e}")
        
        return []


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="기술명세서 자동 업데이트")
    parser.add_argument("module", help="모듈 이름")
    parser.add_argument("--version", help="버전 (선택사항)")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="프로젝트 루트 경로")
    parser.add_argument("--save", action="store_true", help="문서 저장")
    parser.add_argument("--changelog", action="store_true", help="CHANGELOG.md 업데이트")
    
    args = parser.parse_args()
    
    try:
        updater = DocumentationUpdater(args.root)
        
        print(f"📝 {args.module} 모듈 문서 업데이트 중...")
        
        # 기술명세서 생성
        documentation = updater.generate_documentation(args.module, args.version)
        
        if args.save:
            updater.save_documentation(args.module, documentation)
        else:
            print(documentation)
        
        # CHANGELOG.md 업데이트
        if args.changelog and args.version:
            updater.update_changelog(args.module, args.version)
        
        print(f"✅ {args.module} 문서 업데이트 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 