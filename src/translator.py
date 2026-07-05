"""
DeepL 翻译模块
调用 DeepL API 将项目描述和分类翻译为中文
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional


class Translator:
    """DeepL API 翻译封装"""

    def __init__(self, api_key: Optional[str] = None, cache_dir: str = "cache"):
        self.api_key = api_key or os.getenv('DEEPL_API_KEY')
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "translation_cache.json"
        self.cache: Dict[str, str] = self._load_cache()
        self.request_count = 0
        self.char_count = 0
        self._translator = None

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

    def _get_translator(self):
        """延迟初始化 DeepL 客户端"""
        if self._translator is None and self.api_key:
            import deepl
            self._translator = deepl.Translator(self.api_key)
        return self._translator

    def translate(self, text: str, target_lang: str = "ZH") -> str:
        """翻译单个文本"""
        if not text or len(text.strip()) == 0:
            return ""

        cache_key = f"{text}->{target_lang}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        translator = self._get_translator()
        if not translator:
            # 无 API key 时返回原文
            return text

        try:
            result = translator.translate_text(
                text,
                target_lang=target_lang,
                preserve_formatting=True
            )
            translated = result.text
            self.cache[cache_key] = translated
            self.request_count += 1
            self.char_count += len(text)

            # 每 50 次请求暂停一下
            if self.request_count % 50 == 0:
                time.sleep(0.5)

            return translated

        except Exception as e:
            print(f"⚠️ 翻译失败: {text[:50]}... - {e}")
            return text  # 失败时返回原文

    def translate_batch(self, texts: List[str], target_lang: str = "ZH") -> List[str]:
        """批量翻译（使用 DeepL 批量 API，更省配额）"""
        if not texts:
            return []

        # 过滤掉已缓存和空文本
        uncached_indices = []
        uncached_texts = []
        results = [""] * len(texts)

        for i, text in enumerate(texts):
            if not text or len(text.strip()) == 0:
                results[i] = ""
                continue
            cache_key = f"{text}->{target_lang}"
            if cache_key in self.cache:
                results[i] = self.cache[cache_key]
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        if not uncached_texts:
            return results

        translator = self._get_translator()
        if not translator:
            for i in uncached_indices:
                results[i] = texts[i]
            return results

        try:
            translated_list = translator.translate_text(
                uncached_texts,
                target_lang=target_lang,
                preserve_formatting=True
            )
            for idx, result in zip(uncached_indices, translated_list):
                translated = result.text
                self.cache[f"{texts[idx]}->{target_lang}"] = translated
                results[idx] = translated
                self.char_count += len(texts[idx])

            self.request_count += 1

        except Exception as e:
            print(f"⚠️ 批量翻译失败: {e}")
            for i in uncached_indices:
                results[i] = texts[i]

        return results

    def translate_projects(self, projects: List[Dict]) -> List[Dict]:
        """翻译项目中的分类和描述字段"""
        print(f"\n🌐 正在翻译项目信息...")

        # 收集需要翻译的文本（去重）
        categories = list(set(p.get('category', '') for p in projects if p.get('category')))
        descriptions = [p.get('description_en', '') for p in projects]

        # 翻译分类名称
        print(f"📑 翻译分类名称 ({len(categories)} 个)...")
        category_map = {}
        if categories:
            translated_cats = self.translate_batch(categories)
            for orig, trans in zip(categories, translated_cats):
                category_map[orig] = trans

        # 批量翻译描述
        print(f"📝 翻译项目描述 ({len(descriptions)} 条)...")
        translated_descs = self.translate_batch(descriptions)

        # 写入项目
        for i, project in enumerate(projects):
            project['category_zh'] = category_map.get(project.get('category', ''), project.get('category', ''))
            project['description_zh'] = translated_descs[i]

        self._save_cache()
        print(f"✓ 翻译完成 (API 请求: {self.request_count} 次, 字符数: {self.char_count:,}, 缓存: {len(self.cache)} 条)")
        return projects


def main():
    """测试翻译模块"""
    translator = Translator()
    if not translator.api_key:
        print("⚠️ 未设置 DEEPL_API_KEY,将跳过翻译(返回原文)")
        return

    # 测试翻译
    result = translator.translate("A safe home for all your data")
    print(f"翻译结果: {result}")

    # 批量测试
    texts = [
        "Cloud storage software",
        "Self-hosted web analytics",
        "Open source email server"
    ]
    results = translator.translate_batch(texts)
    for orig, trans in zip(texts, results):
        print(f"  [{orig}] -> [{trans}]")


if __name__ == "__main__":
    main()
