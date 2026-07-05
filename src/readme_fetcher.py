"""
README 抓取模块
从 GitHub 仓库获取 README 内容,提取前几段作为项目详细介绍
"""

import os
import re
import json
import time
import base64
import requests
from pathlib import Path
from typing import Dict, Optional, List
from tqdm import tqdm


class ReadmeFetcher:
    """GitHub README 抓取器"""

    def __init__(self, token: Optional[str] = None, cache_dir: str = "cache"):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "readme_cache.json"
        self.cache: Dict[str, str] = self._load_cache()

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AwesomeSelfhostedExtractor/1.0',
        })

    def _load_cache(self) -> Dict:
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, Exception):
                return {}
        return {}

    def _save_cache(self):
        self.cache_file.write_text(
            json.dumps(self.cache, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    def _extract_repo_path(self, url: str) -> Optional[str]:
        """从 URL 提取 owner/repo"""
        if 'github.com/' not in url:
            return None
        parts = url.rstrip('/').split('/')
        if len(parts) >= 2 and 'github.com' in parts:
            idx = parts.index('github.com')
            if idx + 2 < len(parts):
                return f"{parts[idx + 1]}/{parts[idx + 2]}"
        return None

    def fetch_readme_preview(self, repo_full_name: str,
                             max_paragraphs: int = 3,
                             max_length: int = 500) -> str:
        """
        获取 README 前几段作为项目介绍

        Args:
            repo_full_name: 如 "nextcloud/server"
            max_paragraphs: 最大段落数
            max_length: 最大字符数

        Returns:
            精简后的 README 文本
        """
        # 检查缓存
        cache_key = f"{repo_full_name}_{max_paragraphs}_{max_length}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        text = self._fetch_via_api(repo_full_name)
        if not text:
            text = self._fetch_via_api_raw(repo_full_name)

        if text:
            preview = self._extract_paragraphs(text, max_paragraphs, max_length)
            self.cache[cache_key] = preview
            return preview

        return ""

    def _fetch_via_api(self, repo_full_name: str) -> Optional[str]:
        """通过 GitHub API 获取 README"""
        url = f"https://api.github.com/repos/{repo_full_name}/readme"
        headers = {'Accept': 'application/vnd.github.v3.raw'}
        if self.token:
            headers['Authorization'] = f'token {self.token}'

        try:
            response = self.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 404:
                return None
            else:
                return None
        except requests.exceptions.RequestException:
            return None

    def _fetch_via_api_raw(self, repo_full_name: str) -> Optional[str]:
        """通过 GitHub API (JSON 方式,Base64 解码) 获取 README"""
        url = f"https://api.github.com/repos/{repo_full_name}/readme"
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if self.token:
            headers['Authorization'] = f'token {self.token}'

        try:
            response = self.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                content = data.get('content', '')
                if content:
                    return base64.b64decode(content).decode('utf-8')
            return None
        except requests.exceptions.RequestException:
            return None

    def _extract_paragraphs(self, markdown_text: str,
                            max_paragraphs: int,
                            max_length: int) -> str:
        """从 Markdown 提取前 N 个有效段落"""
        lines = markdown_text.split('\n')
        paragraphs = []
        current = []

        for line in lines:
            stripped = line.strip()

            # 跳过空行、标题、代码块、分隔线
            if (stripped.startswith('#') or stripped.startswith('```') or
                stripped.startswith('---') or stripped.startswith('___') or
                stripped.startswith('<!--') or stripped.startswith('[')):
                if current:
                    text = ' '.join(current).strip()
                    if text:
                        paragraphs.append(text)
                    current = []
                continue

            # 空行 = 段落结束
            if not stripped:
                if current:
                    text = ' '.join(current).strip()
                    if text:
                        paragraphs.append(text)
                    current = []
                continue

            current.append(stripped)

            if len(paragraphs) >= max_paragraphs:
                break

        # 最后一个段落
        if current and len(paragraphs) < max_paragraphs:
            text = ' '.join(current).strip()
            if text:
                paragraphs.append(text)

        # 合并
        result = '\n\n'.join(paragraphs[:max_paragraphs])

        # 截断
        if len(result) > max_length:
            result = result[:max_length].rsplit(' ', 1)[0] + '...'

        return result.strip()

    def enrich_projects(self, projects: List[Dict],
                        max_paragraphs: int = 3,
                        max_length: int = 500,
                        max_sample: Optional[int] = None) -> List[Dict]:
        """批量获取项目的 README 预览"""
        sample = projects[:max_sample] if max_sample else projects

        print(f"\n📖 正在获取 {len(sample)} 个项目的 README 预览...")

        for project in tqdm(sample, desc="README"):
            repo_path = self._extract_repo_path(project['url'])
            if repo_path:
                preview = self.fetch_readme_preview(repo_path, max_paragraphs, max_length)
                project['readme_preview'] = preview
                time.sleep(0.2)  # 避免触发限制
            else:
                project['readme_preview'] = ""

        self._save_cache()
        print(f"✓ README 预览获取完成 (缓存: {len(self.cache)} 条)")
        return projects


def main():
    """测试 README 抓取模块"""
    fetcher = ReadmeFetcher()

    preview = fetcher.fetch_readme_preview("nextcloud/server")
    print(f"Nextcloud Server README 预览:")
    print(preview[:300] + "..." if len(preview) > 300 else preview)
    print()


if __name__ == "__main__":
    main()
