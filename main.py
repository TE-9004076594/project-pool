"""
Awesome Selfhosted 提取器 - 主入口
从 awesome-selfhosted 仓库提取项目信息,生成静态网站
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def step_crawl_and_parse() -> list:
    """步骤1: 爬取和解析 README"""
    print("\n" + "=" * 60)
    print("📖 步骤 1/5: 爬取和解析 README")
    print("=" * 60)

    from src.crawler import ReadmeCrawler

    crawler = ReadmeCrawler(
        cache_dir=os.getenv('CACHE_DIR', 'cache'),
        max_retries=3
    )

    readme_text = crawler.fetch_readme()
    projects = crawler.parse_projects(readme_text)
    crawler.save_raw_data(projects)

    print(f"\n✅ 步骤1完成: 共提取 {len(projects)} 个项目")
    return projects


def step_enrich_github(projects: list) -> list:
    """步骤2: 采集 GitHub 元数据"""
    print("\n" + "=" * 60)
    print("📊 步骤 2/5: 采集 GitHub 元数据")
    print("=" * 60)

    from src.github_api import GitHubApi

    github_token = os.getenv('GITHUB_TOKEN')
    api = GitHubApi(token=github_token)
    projects = api.enrich_projects(projects)

    # 保存中间结果
    cache_dir = os.getenv('CACHE_DIR', 'cache')
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    with open(f"{cache_dir}/projects_with_github.json", 'w', encoding='utf-8') as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 步骤2完成: 已采集 {api.request_count} 条 API 数据")
    return projects


def step_translate(projects: list) -> list:
    """步骤3: 翻译项目信息"""
    print("\n" + "=" * 60)
    print("🌐 步骤 3/5: 翻译项目信息")
    print("=" * 60)

    from src.translator import Translator

    translator = Translator()
    if not translator.api_key:
        print("⚠️ 未设置 DEEPL_API_KEY,将跳过翻译(保留英文原文)")
        return projects

    projects = translator.translate_projects(projects)

    # 保存中间结果
    cache_dir = os.getenv('CACHE_DIR', 'cache')
    with open(f"{cache_dir}/projects_translated.json", 'w', encoding='utf-8') as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 步骤3完成: 已翻译 {translator.request_count} 批文本")
    return projects


def step_fetch_readmes(projects: list) -> list:
    """步骤4: 获取 README 预览"""
    print("\n" + "=" * 60)
    print("📖 步骤 4/5: 获取 README 预览")
    print("=" * 60)

    from src.readme_fetcher import ReadmeFetcher

    fetcher = ReadmeFetcher()
    projects = fetcher.enrich_projects(
        projects,
        max_paragraphs=int(os.getenv('README_MAX_PARAGRAPHS', '3')),
        max_length=int(os.getenv('README_MAX_LENGTH', '500')),
    )

    print(f"\n✅ 步骤4完成: 已获取 README 预览")
    return projects


def step_generate_site(projects: list):
    """步骤5: 生成静态网站"""
    print("\n" + "=" * 60)
    print("🏗️  步骤 5/5: 生成静态网站")
    print("=" * 60)

    from src.generator import SiteGenerator

    output_dir = os.getenv('OUTPUT_DIR', 'output')
    generator = SiteGenerator(output_dir=output_dir)
    result = generator.generate(projects)

    # 保存执行报告
    report = {
        "generated_at": result.get("generation_time", ""),
        "total_projects": result.get("total_projects", 0),
        "total_pages": result.get("total_pages", 0),
        "categories": result.get("categories", 0),
        "languages": result.get("languages", 0),
        "output_dir": result.get("output_dir", ""),
    }

    report_path = os.path.join(output_dir, "generation_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 步骤5完成!")
    print(f"   输出目录: {result.get('output_dir', '')}")
    print(f"   生成报告: {report_path}")

    return report


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Awesome Selfhosted 提取器")
    print("   从 awesome-selfhosted 仓库提取项目信息,生成静态网站")
    print("=" * 60)

    start_time = time.time()

    try:
        # 步骤1: 爬取和解析 README
        projects = step_crawl_and_parse()

        # 步骤2: 采集 GitHub 元数据
        projects = step_enrich_github(projects)

        # 步骤3: 翻译
        projects = step_translate(projects)

        # 步骤4: README 预览
        projects = step_fetch_readmes(projects)

        # 步骤5: 生成网站
        report = step_generate_site(projects)

        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print(f"🎉 全部完成! 耗时: {elapsed:.1f} 秒")
        print(f"📊 项目总数: {report['total_projects']}")
        print(f"📄 页面总数: {report['total_pages']}")
        print(f"💾 输出目录: {report['output_dir']}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 执行失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
