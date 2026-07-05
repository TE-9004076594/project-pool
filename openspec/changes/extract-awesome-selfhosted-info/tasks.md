## 1. 环境准备与依赖安装

- [x] 1.1 创建项目目录结构(src/, templates/, assets/, output/, cache/)
- [x] 1.2 安装 Python 依赖(requests, beautifulsoup4, jinja2, deepl, python-dotenv, tqdm)
- [x] 1.3 配置环境变量(.env 文件,包含 DEEPL_API_KEY 和可选的 GITHUB_TOKEN)
- [x] 1.4 创建 .env.example 模板文件
- [x] 1.5 配置 vercel.json 部署文件

## 2. README 爬取与解析

- [x] 2.1 实现从 GitHub 下载 awesome-selfhosted README.md 的功能
- [x] 2.2 添加网络请求重试机制(指数退避策略)
- [x] 2.3 实现 Markdown 解析器,识别分类标题(## / ###)和项目列表项
- [x] 2.4 提取项目名称、GitHub URL、描述文本和分类信息
- [x] 2.5 构建分类层级数据结构
- [x] 2.6 保存解析结果到 cache/projects_raw.json

## 3. GitHub API 元数据采集

- [x] 3.1 实现 GitHub API 调用模块(github_api.py)
- [x] 3.2 获取每个项目的 language、license、stargazers_count、forks_count、topics
- [x] 3.3 实现 API 速率限制控制(使用 Token 或未认证的 60次/小时)
- [x] 3.4 添加错误处理(404、超时、API 限流等异常)
- [x] 3.5 实现元数据缓存机制(cache/github_cache.json),避免重复请求
- [x] 3.6 批量处理所有项目并保存完整数据

## 4. DeepL 翻译集成

- [x] 4.1 实现 DeepL API 封装模块(translator.py)
- [x] 4.2 实现单个文本翻译功能
- [x] 4.3 实现批量翻译功能(一次最多 50 条,节省配额)
- [x] 4.4 添加翻译结果缓存(cache/translation_cache.json)
- [x] 4.5 翻译项目分类名称为中文
- [x] 4.6 翻译项目描述为中文
- [x] 4.7 监控翻译配额使用情况,接近限额时发出警告

## 5. GitHub README 抓取

- [x] 5.1 实现 README 抓取模块(readme_fetcher.py)
- [x] 5.2 通过 GitHub API 获取 README 内容(Base64 解码)
- [x] 5.3 实现备选方案:从 HTML 页面提取 README(当 API 失败时)
- [x] 5.4 解析 Markdown,提取前 3 个段落
- [x] 5.5 限制长度为最多 500 字符,截断时保持单词完整
- [x] 5.6 缓存已抓取的 README(cache/readme_cache.json)

## 6. Jinja2 模板设计

- [x] 6.1 创建 base.html 基础模板(包含导航栏、页脚、CSS/JS 引用)
- [x] 6.2 集成 Material Components Web(CDN 链接)
- [x] 6.3 创建 index.html 首页模板(统计卡片、分类网格、语言分布)
- [x] 6.4 创建 project.html 项目详情页模板(Material Card、元数据表格、README 预览)
- [x] 6.5 创建 search.html 搜索页模板(搜索框、过滤器侧边栏、结果列表)
- [x] 6.6 创建组件模板(components/navbar.html, components/project_card.html, components/filters.html)
- [x] 6.7 设计响应式 CSS(custom.css, responsive.css)

## 7. 静态网站生成

- [x] 7.1 实现 Jinja2 模板渲染模块(generator.py)
- [x] 7.2 生成首页(output/index.html),包含统计数据和导航
- [x] 7.3 为每个项目创建独立文件夹(output/projects/{slug}/)
- [x] 7.4 生成项目详情页(output/projects/{slug}/index.html)
- [x] 7.5 生成项目元数据文件(output/projects/{slug}/metadata.json)
- [x] 7.6 生成全局搜索索引(output/search-index.json)
- [x] 7.7 生成分类统计(output/categories.json)
- [x] 7.8 生成语言统计(output/languages.json)
- [x] 7.9 复制静态资源到 output/assets/(CSS, JS, images)

## 8. 前端搜索功能实现

- [x] 8.1 实现前端搜索类(search.js),支持实时搜索(300ms 防抖)
- [x] 8.2 实现多字段搜索匹配(名称、描述、分类、语言、topics)
- [x] 8.3 实现分类过滤功能(多选,OR 逻辑)
- [x] 8.4 实现语言过滤功能(多选)
- [x] 8.5 实现 Star 数范围过滤(最小值/最大值)
- [x] 8.6 实现多字段排序(名称、Stars、更新时间,升序/降序)
- [x] 8.7 显示搜索结果数量
- [x] 8.8 绑定搜索框事件(input、ESC 清空)

## 9. 虚拟滚动实现

- [x] 9.1 实现虚拟滚动类(virtual_scroller.js)
- [x] 9.2 计算可见范围和缓冲区
- [x] 9.3 动态渲染可见项目卡片
- [x] 9.4 使用 CSS transform 实现位置偏移
- [x] 9.5 绑定滚动事件,触发重新渲染
- [x] 9.6 性能优化(减少 DOM 操作,使用 requestAnimationFrame)
- [x] 9.7 测试大数据量(>1000 项目)下的滚动流畅度

## 10. 测试与验证

- [x] 10.1 使用小规模样本测试(单个分类,10-20个项目)
- [x] 10.2 验证 GitHub API 数据提取准确性
- [x] 10.3 验证 DeepL 翻译质量和配额使用
- [x] 10.4 验证 README 抓取和段落提取
- [x] 10.5 测试前端搜索功能(实时搜索、过滤、排序)
- [x] 10.6 测试虚拟滚动性能(FPS、DOM 节点数)
- [x] 10.7 检查响应式布局(手机、平板、桌面)
- [x] 10.8 人工抽查生成的网站质量
- [x] 10.9 修正发现的解析错误或格式问题

## 11. 部署与发布

- [x] 11.1 运行完整脚本处理所有项目(~1500个)
- [x] 11.2 生成执行报告(成功数、失败数、跳过数、翻译配额使用)
- [x] 11.3 验证 output/ 目录结构完整
- [x] 11.4 本地测试网站(使用 Python http.server 或 live-server)
- [x] 11.5 配置 Vercel CLI(vercel login, vercel link)
- [x] 11.6 部署到 Vercel(vercel --prod)
- [ ] 11.7 (可选)绑定自定义域名
- [x] 11.8 验证在线访问正常,所有功能可用
- [x] 11.9 提交代码到版本控制系统(Git commit & push)
