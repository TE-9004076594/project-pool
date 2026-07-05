import re
import json
from pathlib import Path

README_FILE = "README.md"

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def parse_markdown(md_text):
    lines = md_text.splitlines()
    current_category = None
    items = []

    # 匹配 markdown 列表项中的链接
    link_pattern = re.compile(r'^\s*[-*]\s+\[([^\]]+)\]\(([^)]+)\)\s*-\s*(.+)$')

    for line in lines:
        line = line.rstrip()

        # 识别标题作为分类，可根据仓库实际结构调整层级
        if line.startswith("## "):
            current_category = clean_text(line[3:])
            continue
        elif line.startswith("### "):
            current_category = clean_text(line[4:])
            continue

        m = link_pattern.match(line)
        if m:
            name, url, desc = m.groups()
            items.append({
                "category": current_category,
                "name": clean_text(name),
                "url": clean_text(url),
                "raw_description": clean_text(desc),
            })

    return items

def generate_intro(item):
    return f"{item['name']} 是一个属于“{item['category']}”分类的开源自托管项目。它的主要特点是：{item['raw_description']}"

def main():
    md_text = Path(README_FILE).read_text(encoding="utf-8")
    items = parse_markdown(md_text)

    for item in items:
        item["intro_zh"] = generate_intro(item)

    Path("awesome_selfhosted_items.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"已提取 {len(items)} 个项目，输出到 awesome_selfhosted_items.json")

if __name__ == "__main__":
    main()