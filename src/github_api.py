"""
GitHub API 模块
获取项目的开发语言、许可证、Star 数等元数据
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import Dict, Optional, List
from tqdm import tqdm


class GitHubApi:
    """GitHub REST API v3 封装"""

    def __init__(self, token: Optional[str] = None, cache_dir: str = "cache"):
        self.token = token
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "github_cache.json"
        self.cache: Dict[str, Dict] = self._load_cache()

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AwesomeSelfhostedExtractor/1.0',
            'Accept': 'application/vnd.github.v3+json',
        })
        if token:
            self.session.headers.update({'Authorization': f'token {token}'})

        self.rate_limit_remaining = None
        self.request_count = 0

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
        """从 URL 中提取 owner/repo 格式"""
        if 'github.com/' not in url:
            return None
        parts = url.rstrip('/').split('/')
        if len(parts) >= 2 and 'github.com' in parts:
            idx = parts.index('github.com')
            if idx + 2 < len(parts):
                return f"{parts[idx + 1]}/{parts[idx + 2]}"
        return None

    def _handle_rate_limit(self, response: requests.Response):
        """处理 GitHub API 速率限制"""
        remaining = response.headers.get('X-RateLimit-Remaining')
        if remaining is not None:
            self.rate_limit_remaining = int(remaining)
            if self.rate_limit_remaining == 0:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                wait = max(reset_time - time.time(), 0) + 1
                print(f"\n⚠️ API 速率限制已到,等待 {wait:.0f} 秒...")
                time.sleep(wait)

    def fetch_metadata(self, repo_full_name: str) -> Dict:
        """获取单个仓库的元数据"""
        if repo_full_name in self.cache:
            return self.cache[repo_full_name]

        api_url = f"https://api.github.com/repos/{repo_full_name}"
        try:
            response = self.session.get(api_url, timeout=15)
            self._handle_rate_limit(response)

            if response.status_code == 200:
                data = response.json()
                metadata = {
                    "language": data.get("language"),
                    "license": data.get("license", {}).get("spdx_id") if data.get("license") else None,
                    "stargazers_count": data.get("stargazers_count", 0),
                    "forks_count": data.get("forks_count", 0),
                    "open_issues_count": data.get("open_issues_count", 0),
                    "topics": data.get("topics", []),
                    "homepage": data.get("homepage"),
                    "description": data.get("description", ""),
                    "updated_at": data.get("updated_at"),
                    "pushed_at": data.get("pushed_at"),
                    "full_name": data.get("full_name"),
                }
                self.cache[repo_full_name] = metadata
                self.request_count += 1
                return metadata
            elif response.status_code == 404:
                print(f"⚠️ 仓库未找到: {repo_full_name}")
                metadata = {"language": None, "license": None, "stargazers_count": 0,
                            "forks_count": 0, "open_issues_count": 0, "topics": [],
                            "homepage": None, "description": "", "updated_at": None,
                            "pushed_at": None, "full_name": repo_full_name}
                self.cache[repo_full_name] = metadata
                return metadata
            elif response.status_code == 403:
                self._handle_rate_limit(response)
                # 重试
                return self.fetch_metadata(repo_full_name)
            else:
                print(f"⚠️ API 错误 ({response.status_code}): {repo_full_name}")
                return {"language": None, "license": None, "stargazers_count": 0,
                        "forks_count": 0, "open_issues_count": 0, "topics": [],
                        "homepage": None, "description": "", "updated_at": None,
                        "pushed_at": None, "full_name": repo_full_name}

        except requests.exceptions.RequestException as e:
            print(f"⚠️ 请求失败: {repo_full_name} - {e}")
            return {"language": None, "license": None, "stargazers_count": 0,
                    "forks_count": 0, "open_issues_count": 0, "topics": [],
                    "homepage": None, "description": "", "updated_at": None,
                    "pushed_at": None, "full_name": repo_full_name}

    def enrich_projects(self, projects: List[Dict],
                        rate_limit_delay: float = 0.5,
                        max_sample: Optional[int] = None) -> List[Dict]:
        """批量采集项目元数据"""
        sample = projects[:max_sample] if max_sample else projects

        print(f"\n📊 正在采集 {len(sample)} 个项目的 GitHub 元数据...")

        for project in tqdm(sample, desc="GitHub API"):
            repo_path = self._extract_repo_path(project['url'])
            if repo_path:
                meta = self.fetch_metadata(repo_path)
                project.update(meta)
                # 避免触发速率限制
                time.sleep(rate_limit_delay)
            else:
                # 非 GitHub 链接
                project.update({"language": None, "license": None,
                                "stargazers_count": 0, "forks_count": 0,
                                "open_issues_count": 0, "topics": [],
                                "homepage": None, "description": "",
                                "updated_at": None, "pushed_at": None,
                                "full_name": None})

        # 保存缓存
        self._save_cache()
        print(f"✓ GitHub 元数据采集完成 (API 请求: {self.request_count} 次, 缓存: {len(self.cache)} 条)")
        return projects


def main():
    """测试 GitHub API 模块"""
    token = os.getenv('GITHUB_TOKEN')
    api = GitHubApi(token=token)

    # 测试单个项目
    meta = api.fetch_metadata("nextcloud/server")
    print(f"Nextcloud Server 元数据:")
    print(f"  语言: {meta['language']}")
    print(f"  许可证: {meta['license']}")
    print(f"  Stars: {meta['stargazers_count']:,}")
    print(f"  Forks: {meta['forks_count']:,}")
    print(f"  Topics: {', '.join(meta['topics'][:5])}..." if meta['topics'] else "  无")


if __name__ == "__main__":
    main()
