## Why

awesome-selfhosted 是一个包含大量自托管项目的优质资源库,但目前这些项目信息分散在 GitHub README 中,缺乏结构化的数据提取和中文说明文档。为了方便开发者快速了解、筛选和使用这些自托管项目,需要将这些项目的关键信息(开发语言、功能描述、项目地址等)提取并整理成易于查阅的**独立静态网站**,支持在线浏览、高级搜索和响应式访问。

## What Changes

- 从 https://github.com/awesome-selfhosted/awesome-selfhosted 仓库爬取所有项目信息
- 提取每个项目的核心信息:项目名称、GitHub 地址、开发语言、功能描述、许可证类型、Star 数量等
- 调用 DeepL API 将项目描述和分类翻译为中文
- 抓取 GitHub README 前几段作为项目详细介绍
- 生成基于 Material Design 的响应式静态网站,按类别组织项目信息
- 实现前端高级搜索功能,支持实时搜索、分类过滤、语言过滤和多字段排序
- 采用虚拟滚动优化大数据量下的浏览性能
- 部署到 Vercel,支持自定义域名和 HTTPS

## Capabilities

### New Capabilities
- `project-extraction`: 从 awesome-selfhosted 仓库提取项目元数据的能力,包括解析 Markdown 格式、识别项目链接、提取描述文本等
- `metadata-enrichment`: 通过 GitHub API 和 DeepL API 丰富项目元数据,获取开发语言、许可证、Star 数、中文翻译等
- `readme-capture`: 抓取 GitHub 仓库 README 内容并提取前几段作为项目详细介绍
- `website-generation`: 使用 Jinja2 模板引擎生成 Material Design 风格的响应式静态网站,包括首页、项目详情页、搜索页等
- `advanced-search`: 实现前端高级搜索功能,支持实时搜索(防抖)、分类过滤、语言过滤、Star 数范围过滤和多字段排序
- `virtual-scrolling`: 实现虚拟滚动机制,优化大量项目列表的渲染性能

### Modified Capabilities
<!-- 无现有能力需要修改 -->

## Impact

- 新增 Python 脚本用于爬取、解析和生成网站
- 引入 Jinja2 模板引擎进行 HTML 页面渲染
- 集成 DeepL Translation API 进行中文化
- 采用 Material Components Web 实现 UI 组件
- 实现前端搜索引擎(纯 JavaScript,无后端依赖)
- 生成完整的静态网站文件结构(output/ 目录)
- 配置 Vercel 部署(vercel.json)
- 网站将部署到 Vercel 或 GitHub Pages,支持在线访问和分享
