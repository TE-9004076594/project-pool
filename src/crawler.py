"""
README 爬取和解析模块
从 awesome-selfhosted 仓库获取并解析项目列表
"""

import re
import requests
import time
from pathlib import Path
from typing import List, Dict, Optional
from tqdm import tqdm


class ReadmeCrawler:
    """awesome-selfhosted README 爬取器"""
    
    def __init__(self, cache_dir: str = "cache", max_retries: int = 3, github_token: str = None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_retries = max_retries
        self.github_token = github_token
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; AwesomeSelfhostedExtractor/1.0)'
        })
    
    def fetch_readme(self, repo_url: str = "https://raw.githubusercontent.com/awesome-selfhosted/awesome-selfhosted/master/README.md",
                      api_url: str = "https://api.github.com/repos/awesome-selfhosted/awesome-selfhosted/readme") -> str:
        """
        从多个来源尝试获取 README.md

        Args:
            repo_url: README 文件的原始 URL(raw.githubusercontent.com)
            api_url: GitHub API 地址

        Returns:
            README 文本内容
        """
        cache_file = self.cache_dir / "readme.md"

        # 检查缓存
        if cache_file.exists():
            print("✓ 使用缓存的 README 文件")
            return cache_file.read_text(encoding='utf-8')

        # 尝试多个来源
        sources = [
            ("raw.githubusercontent.com", repo_url, self._fetch_http),
            ("GitHub API", api_url, self._fetch_via_github_api),
        ]

        for source_name, url, fetch_func in sources:
            print(f"📥 正在从 {source_name} 下载 README...")
            for attempt in range(1, self.max_retries + 1):
                try:
                    content = fetch_func(url)
                    if content:
                        cache_file.write_text(content, encoding='utf-8')
                        print(f"✓ README 下载成功 ({len(content)} 字符)")
                        return content
                except Exception as e:
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        print(f"⚠️ 尝试 {attempt}/{self.max_retries} 失败,等待 {wait_time} 秒...")
                        time.sleep(wait_time)
                    else:
                        print(f"⚠️ {source_name} 最终失败: {e}")

        raise Exception("所有下载来源均失败,无法获取 README")

    def _fetch_http(self, url: str) -> str:
        """通过 HTTP 下载"""
        response = self.session.get(url, timeout=30, verify=False)
        response.raise_for_status()
        return response.text

    def _fetch_via_github_api(self, url: str) -> Optional[str]:
        """通过 GitHub API 获取 README"""
        headers = {
            'Accept': 'application/vnd.github.v3.raw',
            'User-Agent': 'AwesomeSelfhostedExtractor/1.0',
        }
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'

        response = self.session.get(url, headers=headers, timeout=30, verify=False)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 404:
            headers['Accept'] = 'application/vnd.github.v3+json'
            response = self.session.get(url, headers=headers, timeout=30, verify=False)
            if response.status_code == 200:
                import base64
                data = response.json()
                content = data.get('content', '')
                if content:
                    return base64.b64decode(content).decode('utf-8')
        return None

    def parse_projects(self, readme_text: str) -> List[Dict]:
        """
        解析 README,提取项目列表
        
        Args:
            readme_text: README 文本内容
            
        Returns:
            项目列表,每个项目包含 category, name, url, description
        """
        lines = readme_text.splitlines()
        current_category = None
        items = []
        
        # 匹配 markdown 列表项中的链接
        # 格式: - [Project Name](URL) - Description
        link_pattern = re.compile(r'^\s*[-*]\s+\[([^\]]+)\]\(([^)]+)\)\s*-\s*(.+)$')
        
        print("🔍 正在解析项目列表...")
        
        for line in tqdm(lines, desc="解析行", unit="line"):
            line = line.rstrip()
            
            # 识别标题作为分类 (## 或 ###)
            if line.startswith("### "):
                current_category = self._clean_text(line[4:])
                continue
            elif line.startswith("## "):
                current_category = self._clean_text(line[3:])
                continue
            
            # 匹配项目链接
            m = link_pattern.match(line)
            if m:
                name, url, desc = m.groups()
                items.append({
                    "category": current_category,
                    "name": self._clean_text(name),
                    "url": self._clean_text(url),
                    "description_en": self._clean_text(desc),
                })
        
        print(f"✓ 解析完成: 共 {len(items)} 个项目")
        return items
    
    def _clean_text(self, text: str) -> str:
        """清理文本:移除多余空白"""
        return re.sub(r'\s+', ' ', text).strip()
    
    def save_raw_data(self, projects: List[Dict], filename: str = "projects_raw.json"):
        """
        保存原始解析结果到 JSON
        
        Args:
            projects: 项目列表
            filename: 输出文件名
        """
        import json
        
        output_file = self.cache_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 原始数据已保存到 {output_file}")


def main():
    """测试爬虫功能"""
    crawler = ReadmeCrawler()
    
    # 下载 README
    readme_text = crawler.fetch_readme()
    
    # 解析项目
    projects = crawler.parse_projects(readme_text)
    
    # 保存原始数据
    crawler.save_raw_data(projects)
    
    # 显示前5个项目
    print("\n前5个项目示例:")
    for i, project in enumerate(projects[:5], 1):
        print(f"{i}. {project['name']}")
        print(f"   分类: {project['category']}")
        print(f"   URL: {project['url']}")
        print(f"   描述: {project['description_en'][:100]}...")
        print()


if __name__ == "__main__":
    main()
