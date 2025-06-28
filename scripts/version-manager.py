#!/usr/bin/env python3
"""
Universal Modules 버전 관리 시스템

이 스크립트는 다음 기능을 제공합니다:
- 시맨틱 버전 관리 (major.minor.patch)
- 모듈별 독립적 버전 관리
- 자동 버전 태깅
- 변경사항 추적
- 의존성 버전 동기화
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import toml
import semver


@dataclass
class ModuleInfo:
    """모듈 정보 클래스"""
    name: str
    path: Path
    current_version: str
    dependencies: List[str]
    last_modified: datetime


class VersionManager:
    """버전 관리 매니저"""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.packages_path = root_path / "packages"
        self.version_history_path = root_path / "docs" / "version-history.json"
        self.modules = self._discover_modules()
        
    def _discover_modules(self) -> Dict[str, ModuleInfo]:
        """패키지 디렉터리에서 모듈들을 자동 발견"""
        modules = {}
        
        for module_dir in self.packages_path.iterdir():
            if module_dir.is_dir() and (module_dir / "pyproject.toml").exists():
                pyproject_path = module_dir / "pyproject.toml"
                
                try:
                    pyproject_data = toml.load(pyproject_path)
                    project_info = pyproject_data.get("project", {})
                    
                    name = project_info.get("name", module_dir.name)
                    version = project_info.get("version", "0.1.0")
                    dependencies = project_info.get("dependencies", [])
                    
                    # Git에서 마지막 수정 시간 가져오기
                    try:
                        result = subprocess.run(
                            ["git", "log", "-1", "--format=%ct", str(module_dir)],
                            capture_output=True,
                            text=True,
                            cwd=self.root_path
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            timestamp = int(result.stdout.strip())
                            last_modified = datetime.fromtimestamp(timestamp)
                        else:
                            last_modified = datetime.now()
                    except Exception:
                        last_modified = datetime.now()
                    
                    modules[name] = ModuleInfo(
                        name=name,
                        path=module_dir,
                        current_version=version,
                        dependencies=dependencies,
                        last_modified=last_modified
                    )
                    
                except Exception as e:
                    print(f"⚠️  모듈 {module_dir.name} 로드 실패: {e}")
                    
        return modules
    
    def get_version_history(self) -> Dict:
        """버전 히스토리 로드"""
        if self.version_history_path.exists():
            with open(self.version_history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_version_history(self, history: Dict):
        """버전 히스토리 저장"""
        self.version_history_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.version_history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False, default=str)
    
    def bump_version(self, module_name: str, bump_type: str, message: str = "") -> str:
        """버전 업데이트"""
        if module_name not in self.modules:
            raise ValueError(f"모듈 '{module_name}'을 찾을 수 없습니다.")
        
        module = self.modules[module_name]
        current_version = module.current_version
        
        # 시맨틱 버전 업데이트
        if bump_type == "major":
            new_version = semver.bump_major(current_version)
        elif bump_type == "minor":
            new_version = semver.bump_minor(current_version)
        elif bump_type == "patch":
            new_version = semver.bump_patch(current_version)
        else:
            raise ValueError(f"잘못된 bump_type: {bump_type}")
        
        # pyproject.toml 업데이트
        self._update_pyproject_version(module.path, new_version)
        
        # 버전 히스토리 업데이트
        self._update_version_history(module_name, current_version, new_version, message)
        
        # Git 태그 생성
        self._create_git_tag(module_name, new_version, message)
        
        # 모듈 정보 업데이트
        module.current_version = new_version
        
        return new_version
    
    def _update_pyproject_version(self, module_path: Path, new_version: str):
        """pyproject.toml 파일의 버전 업데이트"""
        pyproject_path = module_path / "pyproject.toml"
        
        with open(pyproject_path, 'r', encoding='utf-8') as f:
            data = toml.load(f)
        
        data["project"]["version"] = new_version
        
        with open(pyproject_path, 'w', encoding='utf-8') as f:
            toml.dump(data, f)
    
    def _update_version_history(self, module_name: str, old_version: str, new_version: str, message: str):
        """버전 히스토리 업데이트"""
        history = self.get_version_history()
        
        if module_name not in history:
            history[module_name] = []
        
        history[module_name].append({
            "version": new_version,
            "previous_version": old_version,
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "changes": self._get_git_changes(module_name, old_version)
        })
        
        self.save_version_history(history)
    
    def _get_git_changes(self, module_name: str, since_version: str) -> List[str]:
        """Git 변경사항 가져오기"""
        module = self.modules[module_name]
        
        try:
            # 이전 태그부터의 커밋 로그 가져오기
            tag_name = f"{module_name}-v{since_version}"
            result = subprocess.run(
                ["git", "log", f"{tag_name}..HEAD", "--oneline", "--", str(module.path)],
                capture_output=True,
                text=True,
                cwd=self.root_path
            )
            
            if result.returncode == 0:
                return [line.strip() for line in result.stdout.split('\n') if line.strip()]
            else:
                return []
                
        except Exception:
            return []
    
    def _create_git_tag(self, module_name: str, version: str, message: str):
        """Git 태그 생성"""
        tag_name = f"{module_name}-v{version}"
        tag_message = f"{module_name} v{version}"
        if message:
            tag_message += f": {message}"
        
        try:
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", tag_message],
                cwd=self.root_path,
                check=True
            )
            print(f"✅ Git 태그 생성: {tag_name}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git 태그 생성 실패: {e}")
    
    def check_dependencies(self) -> Dict[str, List[str]]:
        """모듈 간 의존성 확인"""
        dependency_issues = {}
        
        for module_name, module in self.modules.items():
            issues = []
            
            for dep in module.dependencies:
                # 내부 모듈 의존성 확인
                if dep.startswith("universal-"):
                    dep_module_name = dep.replace("universal-", "")
                    if dep_module_name in self.modules:
                        # 버전 호환성 확인 로직 추가 가능
                        pass
                    else:
                        issues.append(f"존재하지 않는 내부 모듈: {dep}")
            
            if issues:
                dependency_issues[module_name] = issues
        
        return dependency_issues
    
    def generate_release_notes(self, module_name: str, version: Optional[str] = None) -> str:
        """릴리스 노트 생성"""
        if module_name not in self.modules:
            raise ValueError(f"모듈 '{module_name}'을 찾을 수 없습니다.")
        
        history = self.get_version_history()
        module_history = history.get(module_name, [])
        
        if not module_history:
            return f"# {module_name} 릴리스 노트\n\n버전 히스토리가 없습니다."
        
        # 특정 버전 또는 최신 버전
        if version:
            target_entry = next((entry for entry in module_history if entry["version"] == version), None)
            if not target_entry:
                raise ValueError(f"버전 {version}을 찾을 수 없습니다.")
            entries = [target_entry]
        else:
            entries = module_history[-5:]  # 최근 5개 버전
        
        release_notes = f"# {module_name} 릴리스 노트\n\n"
        
        for entry in reversed(entries):
            release_notes += f"## v{entry['version']} ({entry['timestamp'][:10]})\n\n"
            
            if entry.get('message'):
                release_notes += f"**{entry['message']}**\n\n"
            
            changes = entry.get('changes', [])
            if changes:
                release_notes += "### 변경사항\n"
                for change in changes:
                    release_notes += f"- {change}\n"
                release_notes += "\n"
            
            release_notes += "---\n\n"
        
        return release_notes
    
    def list_modules(self) -> None:
        """모듈 목록 출력"""
        print("📦 Universal Modules 목록:\n")
        
        for name, module in self.modules.items():
            print(f"• {name}")
            print(f"  버전: v{module.current_version}")
            print(f"  경로: {module.path.relative_to(self.root_path)}")
            print(f"  마지막 수정: {module.last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  의존성: {len(module.dependencies)}개")
            print()
    
    def sync_dependencies(self) -> None:
        """모듈 간 의존성 동기화"""
        print("🔄 의존성 동기화 중...")
        
        for module_name, module in self.modules.items():
            pyproject_path = module.path / "pyproject.toml"
            
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
            
            dependencies = data.get("project", {}).get("dependencies", [])
            updated = False
            
            # 내부 모듈 의존성 업데이트
            for i, dep in enumerate(dependencies):
                if dep.startswith("universal-"):
                    dep_name = dep.split(">=")[0].split("==")[0].strip()
                    dep_module_name = dep_name.replace("universal-", "")
                    
                    if dep_module_name in self.modules:
                        current_dep_version = self.modules[dep_module_name].current_version
                        new_dep = f"{dep_name}>={current_dep_version}"
                        
                        if dependencies[i] != new_dep:
                            dependencies[i] = new_dep
                            updated = True
                            print(f"  {module_name}: {dep_name} 의존성 업데이트 -> {current_dep_version}")
            
            if updated:
                data["project"]["dependencies"] = dependencies
                with open(pyproject_path, 'w', encoding='utf-8') as f:
                    toml.dump(data, f)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="Universal Modules 버전 관리")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="프로젝트 루트 경로")
    
    subparsers = parser.add_subparsers(dest="command", help="사용 가능한 명령어")
    
    # 모듈 목록
    subparsers.add_parser("list", help="모듈 목록 출력")
    
    # 버전 업데이트
    bump_parser = subparsers.add_parser("bump", help="버전 업데이트")
    bump_parser.add_argument("module", help="모듈 이름")
    bump_parser.add_argument("type", choices=["major", "minor", "patch"], help="버전 업데이트 타입")
    bump_parser.add_argument("-m", "--message", default="", help="변경사항 메시지")
    
    # 릴리스 노트
    notes_parser = subparsers.add_parser("release-notes", help="릴리스 노트 생성")
    notes_parser.add_argument("module", help="모듈 이름")
    notes_parser.add_argument("-v", "--version", help="특정 버전 (기본: 최근 5개)")
    
    # 의존성 확인
    subparsers.add_parser("check-deps", help="의존성 확인")
    
    # 의존성 동기화
    subparsers.add_parser("sync-deps", help="의존성 동기화")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    vm = VersionManager(args.root)
    
    try:
        if args.command == "list":
            vm.list_modules()
            
        elif args.command == "bump":
            new_version = vm.bump_version(args.module, args.type, args.message)
            print(f"✅ {args.module} 버전 업데이트: v{new_version}")
            
        elif args.command == "release-notes":
            notes = vm.generate_release_notes(args.module, args.version)
            print(notes)
            
        elif args.command == "check-deps":
            issues = vm.check_dependencies()
            if issues:
                print("⚠️  의존성 문제 발견:")
                for module, problems in issues.items():
                    print(f"\n{module}:")
                    for problem in problems:
                        print(f"  - {problem}")
            else:
                print("✅ 의존성 문제 없음")
                
        elif args.command == "sync-deps":
            vm.sync_dependencies()
            print("✅ 의존성 동기화 완료")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 