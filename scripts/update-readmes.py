#!/usr/bin/env python3
"""
README 파일들을 업데이트하여 올바른 패키지명과 모듈명을 사용하도록 수정합니다.
"""

import os
import re
from pathlib import Path

def update_readme_content(content: str, package_name: str) -> str:
    """README 내용을 업데이트합니다."""
    
    # 패키지명에서 모듈명 추출
    if package_name.startswith('yeonjae-universal-'):
        module_name = package_name.replace('-', '_')
        old_module_name = package_name.replace('yeonjae-universal-', 'universal_')
        old_package_name = package_name.replace('yeonjae-universal-', 'universal-')
    else:
        return content
    
    print(f"  📝 {package_name}: {old_module_name} → {module_name}")
    
    # 1. pip install 명령어 수정
    content = re.sub(
        r'pip install universal-([a-z-]+)',
        f'pip install {package_name}',
        content
    )
    
    # 2. import 구문 수정 (더 정확한 패턴)
    content = re.sub(
        rf'from {re.escape(old_module_name)} import',
        f'from {module_name} import',
        content
    )
    
    content = re.sub(
        rf'import {re.escape(old_module_name)}',
        f'import {module_name}',
        content
    )
    
    # 3. Git 설치 명령어를 PyPI 설치로 변경
    git_pattern = r'pip install git\+https://github\.com/yeonjae-work/universal-modules\.git#subdirectory=packages/([a-z-]+)'
    content = re.sub(
        git_pattern,
        f'pip install {package_name}',
        content
    )
    
    # 4. 개발 버전 설치 명령어 수정
    dev_pattern = r'pip install "git\+https://github\.com/yeonjae-work/universal-modules\.git#subdirectory=packages/([a-z-]+)\[dev\]"'
    content = re.sub(
        dev_pattern,
        f'pip install {package_name}[dev]',
        content
    )
    
    return content

def main():
    """메인 함수"""
    packages_dir = Path('packages')
    
    if not packages_dir.exists():
        print("packages 디렉터리를 찾을 수 없습니다.")
        return
    
    updated_count = 0
    
    for package_dir in packages_dir.glob('yeonjae-universal-*'):
        if not package_dir.is_dir():
            continue
            
        readme_path = package_dir / 'README.md'
        if not readme_path.exists():
            print(f"⚠️  {package_dir.name}: README.md 파일이 없습니다.")
            continue
        
        print(f"🔍 {package_dir.name} 처리 중...")
        
        # README 내용 읽기
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            print(f"❌ {package_dir.name}: README.md 읽기 실패 - {e}")
            continue
        
        # 내용 업데이트
        updated_content = update_readme_content(original_content, package_dir.name)
        
        # 변경사항이 있는지 확인
        if original_content != updated_content:
            try:
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"✅ {package_dir.name}: README.md 업데이트 완료")
                updated_count += 1
            except Exception as e:
                print(f"❌ {package_dir.name}: README.md 쓰기 실패 - {e}")
        else:
            print(f"ℹ️  {package_dir.name}: 변경사항 없음")
        
        print()
    
    print(f"총 {updated_count}개 패키지의 README가 업데이트되었습니다.")

if __name__ == '__main__':
    main() 