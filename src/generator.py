"""
网站生成器
使用 Jinja2 模板引擎生成 Material Design 静态网站
"""

import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from jinja2 import Environment, FileSystemLoader


def slugify(text: str) -> str:
    """生成 URL 友好的 slug"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def format_number(value: int) -> str:
    """格式化数字"""
    return f"{value:,}"


class SiteGenerator:
    """静态网站生成器"""

    def __init__(self, output_dir: str = "output", templates_dir: str = "templates",
                 assets_dir: str = "assets"):
        self.output_dir = Path(output_dir)
        self.templates_dir = Path(templates_dir)
        self.assets_dir = Path(assets_dir)

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "projects").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "assets" / "css").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "assets" / "js").mkdir(parents=True, exist_ok=True)

        # 初始化 Jinja2 环境
        self.env = Environment(loader=FileSystemLoader(str(templates_dir)))
        self.env.filters['slugify'] = slugify
        self.env.filters['format_number'] = format_number

        self.generation_time = datetime.now().strftime("%Y-%m-%d")

    def copy_assets(self):
        """复制静态资源到输出目录"""
        for item in self.assets_dir.iterdir():
            dest = self.output_dir / "assets" / item.name
            if item.is_file():
                shutil.copy2(item, dest)
                print(f"  📄 复制资源: {item.name}")
            elif item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
                print(f"  📁 复制资源目录: {item.name}")

    def build_search_index(self, projects: List[Dict]) -> Dict:
        """构建搜索索引"""
        index_projects = []
        for p in projects:
            index_projects.append({
                "id": p.get('slug', ''),
                "slug": p.get('slug', ''),
                "name": p.get('name', ''),
                "category": p.get('category', ''),
                "category_zh": p.get('category_zh', ''),
                "language": p.get('language'),
                "license": p.get('license'),
                "stars": p.get('stargazers_count', 0),
                "forks": p.get('forks_count', 0),
                "description_en": p.get('description_en', ''),
                "description_zh": p.get('description_zh', ''),
                "topics": p.get('topics', []),
                "updated_at": p.get('updated_at', ''),
                "url": p.get('url', ''),
            })

        # 统计 Faces
        categories = {}
        languages = {}
        licenses = {}

        for p in projects:
            cat = p.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1

            lang = p.get('language', 'Unknown')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1

            lic = p.get('license', 'Unknown')
            if lic:
                licenses[lic] = licenses.get(lic, 0) + 1

        return {
            "version": "1.0",
            "generated_at": self.generation_time,
            "projects": index_projects,
            "facets": {
                "categories": dict(sorted(categories.items(), key=lambda x: -x[1])),
                "languages": dict(sorted(languages.items(), key=lambda x: -x[1])),
                "licenses": dict(sorted(licenses.items(), key=lambda x: -x[1])),
            }
        }

    def generate_index_page(self, projects: List[Dict], categories: List[Dict],
                            languages: List[Dict]):
        """生成首页"""
        # Top 20 热门项目
        top_projects = sorted(projects, key=lambda p: p.get('stargazers_count', 0), reverse=True)[:20]

        template = self.env.get_template('index.html')
        html = template.render(
            total_count=len(projects),
            categories=categories,
            languages=languages,
            top_projects=top_projects,
            generation_time=self.generation_time,
        )

        output_path = self.output_dir / "index.html"
        output_path.write_text(html, encoding='utf-8')
        print(f"  ✅ 生成首页")
        return output_path

    def generate_project_page(self, project: Dict):
        """生成项目详情页"""
        project_dir = self.output_dir / "projects" / project['slug']
        project_dir.mkdir(parents=True, exist_ok=True)

        # 生成 HTML
        template = self.env.get_template('project.html')
        html = template.render(
            project=project,
            generation_time=self.generation_time,
        )

        html_path = project_dir / "index.html"
        html_path.write_text(html, encoding='utf-8')

        # 生成 metadata.json
        meta_path = project_dir / "metadata.json"
        meta = {k: v for k, v in project.items()
                if k != 'readme_preview_raw'}
        meta_path.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

    def generate_categories_page(self, categories: List[Dict], projects: List[Dict]):
        """生成分类页面"""
        # 简单生成分类索引 HTML
        html_parts = [
            '<!DOCTYPE html><html lang="zh-CN"><head>',
            '<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '<title>分类浏览 - Awesome Selfhosted</title>',
            '<link rel="stylesheet" href="assets/css/custom.css">',
            '<link rel="stylesheet" href="assets/css/responsive.css">',
            '<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">',
            '</head><body>',
            '<div class="main-content" style="max-width:1200px;margin:0 auto;padding:24px;">',
            '<a href="index.html" style="color:#1976d2;text-decoration:none;">← 返回首页</a>',
            '<h1>分类浏览</h1>',
        ]

        for cat in categories:
            cat_slug = slugify(cat['name'])
            html_parts.append(f'<section id="{cat_slug}" style="margin-bottom:32px;">')
            html_parts.append(f'<h2 style="border-bottom:2px solid #1976d2;padding-bottom:8px;">{cat["name_zh"] or cat["name"]} ({cat["count"]})</h2>')

            cat_projects = [p for p in projects if p.get('category') == cat['name']]
            cat_projects_sorted = sorted(cat_projects, key=lambda p: p.get('stargazers_count', 0), reverse=True)

            for p in cat_projects_sorted[:20]:
                html_parts.append(f'''
                <div class="mdc-card project-card" onclick="location.href='projects/{p["slug"]}/index.html'" style="padding:16px;margin-bottom:8px;cursor:pointer;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <h3 style="margin:0;font-size:1rem;">{p['name']}</h3>
                        <span>⭐ {p.get('stargazers_count', 0):,}</span>
                    </div>
                    <p style="color:#555;margin:8px 0 0;">{p.get('description_zh') or p.get('description_en', '')}</p>
                    <div style="margin-top:8px;font-size:0.85rem;color:#666;">
                        💻 {p.get('language', 'N/A')} | 📄 {p.get('license', 'N/A')}
                    </div>
                </div>
                ''')

            if len(cat_projects) > 20:
                html_parts.append(f'<p style="color:#666;">...以及 {len(cat_projects) - 20} 个更多项目</p>')
            html_parts.append('</section>')

        html_parts.append('</div></body></html>')

        output_path = self.output_dir / "categories.html"
        output_path.write_text('\n'.join(html_parts), encoding='utf-8')
        print(f"  ✅ 生成分类页 ({len(categories)} 个分类)")

    def generate_languages_page(self, languages: List[Dict], projects: List[Dict]):
        """生成语言页面"""
        html_parts = [
            '<!DOCTYPE html><html lang="zh-CN"><head>',
            '<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '<title>按语言浏览 - Awesome Selfhosted</title>',
            '<link rel="stylesheet" href="assets/css/custom.css">',
            '<link rel="stylesheet" href="assets/css/responsive.css">',
            '<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">',
            '</head><body>',
            '<div class="main-content" style="max-width:1200px;margin:0 auto;padding:24px;">',
            '<a href="index.html" style="color:#1976d2;text-decoration:none;">← 返回首页</a>',
            '<h1>按开发语言浏览</h1>',
            '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:32px;">',
        ]

        for lang in languages:
            lang_slug = slugify(lang['name'])
            html_parts.append(
                f'<a href="#{lang_slug}" style="padding:8px 16px;background:#e3f2fd;color:#1565c0;'
                f'border-radius:20px;text-decoration:none;">{lang["name"]} ({lang["count"]})</a>'
            )

        html_parts.append('</div>')

        for lang in languages:
            lang_slug = slugify(lang['name'])
            html_parts.append(f'<section id="{lang_slug}" style="margin-bottom:32px;">')
            html_parts.append(f'<h2 style="border-bottom:2px solid #1976d2;padding-bottom:8px;">{lang["name"]} ({lang["count"]})</h2>')

            lang_projects = [p for p in projects if p.get('language') == lang['name']]
            lang_projects_sorted = sorted(lang_projects, key=lambda p: p.get('stargazers_count', 0), reverse=True)

            for p in lang_projects_sorted[:20]:
                html_parts.append(f'''
                <div class="mdc-card project-card" onclick="location.href='projects/{p["slug"]}/index.html'" style="padding:16px;margin-bottom:8px;cursor:pointer;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <h3 style="margin:0;font-size:1rem;">{p['name']}</h3>
                        <span>⭐ {p.get('stargazers_count', 0):,}</span>
                    </div>
                    <p style="color:#555;margin:8px 0 0;">{p.get('description_zh') or p.get('description_en', '')}</p>
                    <div style="margin-top:8px;font-size:0.85rem;color:#666;">
                        {p.get('category_zh') or p.get('category', '')} | 📄 {p.get('license', 'N/A')}
                    </div>
                </div>
                ''')

            if len(lang_projects) > 20:
                html_parts.append(f'<p style="color:#666;">...以及 {len(lang_projects) - 20} 个更多项目</p>')
            html_parts.append('</section>')

        html_parts.append('</div></body></html>')

        output_path = self.output_dir / "languages.html"
        output_path.write_text('\n'.join(html_parts), encoding='utf-8')
        print(f"  ✅ 生成语言页 ({len(languages)} 种语言)")

    def generate_search_page(self, total_count: int = 0):
        """生成搜索页面"""
        html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>搜索项目 - Awesome Selfhosted</title>
    <link href="https://unpkg.com/material-components-web@latest/dist/material-components-web.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/custom.css">
    <link rel="stylesheet" href="assets/css/responsive.css">
</head>
<body>
    <a href="index.html" style="display:inline-block;padding:16px;color:#1976d2;text-decoration:none;">← 返回首页</a>
    <div class="search-page">
        <div class="search-header">
            <h1>搜索项目</h1>
            <p>在 ''' + str(total_count) + ''' 个自托管项目中搜索</p>
            <div style="display:flex;gap:8px;margin-bottom:16px;">
                <input type="text" id="search-input" class="search-input"
                       placeholder="输入关键词搜索..." style="flex:1;padding:12px;border:1px solid #e0e0e0;border-radius:4px;font-size:16px;">
            </div>
            <div class="search-result-count" id="result-count">共找到 0 个项目</div>
        </div>

        <div class="filter-panel">
            <div class="filter-section">
                <div class="filter-section-title">分类</div>
                <div class="filter-options" id="filter-categories"></div>
            </div>
            <div class="filter-section">
                <div class="filter-section-title">语言</div>
                <div class="filter-options" id="filter-languages"></div>
            </div>
            <div class="filter-section">
                <div class="filter-section-title">Star 数量</div>
                <div class="star-range">
                    <input type="number" id="star-min" placeholder="最小值" min="0" onchange="search.setStarRange(this.value, document.getElementById('star-max').value)">
                    <span>—</span>
                    <input type="number" id="star-max" placeholder="最大值" min="0" onchange="search.setStarRange(document.getElementById('star-min').value, this.value)">
                    <button class="mdc-button mdc-button--outlined" onclick="search.resetFilters()" style="padding:6px 12px;">重置过滤</button>
                </div>
            </div>
        </div>

        <div class="sort-controls">
            <label>排序:</label>
            <select id="sort-by" onchange="search.setSort(this.value, document.getElementById('sort-order').value)">
                <option value="stars">Star 数</option>
                <option value="name">名称</option>
                <option value="updated">更新时间</option>
            </select>
            <select id="sort-order" onchange="search.setSort(document.getElementById('sort-by').value, this.value)">
                <option value="desc">降序</option>
                <option value="asc">升序</option>
            </select>
        </div>

        <div id="search-results"></div>
        <div class="loading-indicator" id="search-loading">加载中...</div>
    </div>

    <script src="assets/js/search.js"></script>
    <script src="assets/js/virtual_scroller.js"></script>
    <script>
        const search = new ProjectSearch({
            onFilterChange: function() {
                const query = document.getElementById('search-input').value;
                search.search(query);
            }
        });

        window.searchInstance = search;

        // 初始化搜索
        search.loadIndex('search-index.json').then(function(success) {
            if (success) {
                search.search('');

                // 绑定搜索框
                document.getElementById('search-input').addEventListener('input', function(e) {
                    search.search(e.target.value);
                });
                document.getElementById('search-input').addEventListener('keydown', function(e) {
                    if (e.key === 'Escape') {
                        this.value = '';
                        search.search('');
                        this.blur();
                    }
                });
            }
        });
    </script>
</body>
</html>'''

        output_path = self.output_dir / "search.html"
        output_path.write_text(html, encoding='utf-8')
        print(f"  ✅ 生成搜索页")

    def generate(self, projects: List[Dict]) -> Dict:
        """生成完整网站"""
        print(f"\n🏗️ 正在生成静态网站...")

        # 1. 复制静态资源
        print("  📁 复制静态资源...")
        self.copy_assets()

        # 2. 生成 slug
        slug_map = {}
        for project in projects:
            slug = slugify(project['name'])
            if slug in slug_map:
                slug = f"{slug}-{slug_map[slug]}"
                slug_map[project['name']] += 1
            else:
                slug_map[project['name']] = 1
            project['slug'] = slug

        # 3. 统计分类和语言
        category_dict = {}
        language_dict = {}

        for project in projects:
            cat = project.get('category', 'Unknown')
            if cat not in category_dict:
                category_dict[cat] = {'name': cat, 'name_zh': project.get('category_zh', cat), 'count': 0}
            category_dict[cat]['count'] += 1

            lang = project.get('language')
            if lang:
                if lang not in language_dict:
                    language_dict[lang] = {'name': lang, 'count': 0, 'name_zh': lang}
                language_dict[lang]['count'] += 1

        categories = sorted(category_dict.values(), key=lambda x: -x['count'])
        languages = sorted(language_dict.values(), key=lambda x: -x['count'])

        # 4. 生成搜索索引
        print("  🔍 构建搜索索引...")
        search_index = self.build_search_index(projects)
        index_path = self.output_dir / "search-index.json"
        index_path.write_text(
            json.dumps(search_index, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # 5. 生成分类统计
        cat_stats_path = self.output_dir / "categories.json"
        cat_stats_path.write_text(
            json.dumps(categories, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # 6. 生成语言统计
        lang_stats_path = self.output_dir / "languages.json"
        lang_stats_path.write_text(
            json.dumps(languages, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        # 7. 生成首页
        print("  🏠 生成页面...")
        self.generate_index_page(projects, categories, languages)

        # 8. 生成项目详情页
        print(f"  📄 生成项目详情页 ({len(projects)} 个)...")
        for i, project in enumerate(projects):
            self.generate_project_page(project)
            if (i + 1) % 200 == 0:
                print(f"    ...已生成 {i + 1}/{len(projects)} 个")

        # 9. 生成分类和语言页
        self.generate_categories_page(categories, projects)
        self.generate_languages_page(languages, projects)

        # 10. 生成搜索页
        self.generate_search_page(total_count=len(projects))

        print(f"\n✅ 网站生成完成!")
        print(f"   输出目录: {self.output_dir.absolute()}")
        print(f"   页面总数: {2 + len(projects)} 个 (首页 + 搜索页 + {len(projects)} 个项目详情页)")

        return {
            "output_dir": str(self.output_dir.absolute()),
            "total_pages": 2 + len(projects),
            "total_projects": len(projects),
            "categories": len(categories),
            "languages": len(languages),
        }


def main():
    """测试生成器"""
    import json

    # 尝试加载测试数据
    data_file = Path("cache") / "projects_raw.json"
    if data_file.exists():
        projects = json.loads(data_file.read_text(encoding='utf-8'))
        # 添加一些测试元数据
        for p in projects[:10]:
            p['language'] = 'Python' if 'python' in p.get('name', '').lower() else 'JavaScript'
            p['license'] = 'MIT'
            p['stargazers_count'] = 1000
            p['forks_count'] = 500
            p['topics'] = ['web', 'selfhosted']
            p['description_zh'] = p.get('description_en', '')[:50] + '的中文翻译（示例）'
            p['category_zh'] = p.get('category', '')

        generator = SiteGenerator()
        result = generator.generate(projects[:10])  # 只用前10个测试
        print(f"\n测试结果: {result}")
    else:
        print("⚠️ 未找到测试数据,请先运行 crawler.py")


if __name__ == "__main__":
    main()
