## ADDED Requirements

### Requirement: Jinja2 模板渲染
系统 SHALL 使用 Jinja2 模板引擎将数据渲染为 HTML 页面,支持模板继承和组件复用。

#### Scenario: 渲染首页
- **WHEN** 生成网站首页
- **THEN** 系统使用 index.html 模板,传入项目列表、分类统计、语言统计等数据

#### Scenario: 渲染项目详情页
- **WHEN** 生成单个项目的详情页面
- **THEN** 系统使用 project.html 模板,传入项目完整元数据和 README 预览

#### Scenario: 模板继承
- **WHEN** 渲染任何页面
- **THEN** 所有页面继承 base.html 基础模板,复用导航栏、页脚、CSS/JS 引用

### Requirement: Material Design UI
系统 SHALL 使用 Material Components Web 实现 UI 组件,确保视觉一致性和现代感。

#### Scenario: 使用 Material Card 组件
- **WHEN** 展示项目列表
- **THEN** 系统使用 mdc-card 组件呈现项目卡片,包含阴影、圆角、悬停效果

#### Scenario: 响应式布局
- **WHEN** 在不同设备(手机、平板、桌面)上浏览
- **THEN** 页面自动适配屏幕宽度,使用 CSS Grid/Flexbox 调整布局

#### Scenario: Material Typography
- **WHEN** 显示文本内容
- **THEN** 系统使用 Roboto 字体和 Material Design 字号规范

### Requirement: 项目文件夹结构生成
系统 SHALL 为每个项目创建独立的文件夹,包含 index.html 和 metadata.json。

#### Scenario: 创建项目目录
- **WHEN** 处理项目 "nextcloud/server"
- **THEN** 系统在 output/projects/nextcloud-server/ 创建目录(slugified 名称)

#### Scenario: 生成项目详情页
- **WHEN** 创建项目目录后
- **THEN** 系统生成 index.html(渲染后的页面)和 metadata.json(机器可读数据)

#### Scenario: 命名冲突处理
- **WHEN** 两个项目名称 slugify 后相同
- **THEN** 系统添加数字后缀或组织名前缀确保唯一性

### Requirement: 全局索引文件生成
系统 SHALL 生成 search-index.json、categories.json、languages.json 等索引文件,支持前端搜索和统计。

#### Scenario: 生成搜索索引
- **WHEN** 所有项目处理完成
- **THEN** 系统生成 search-index.json,包含所有项目的精简数据(名称、描述、分类、语言、Stars等)

#### Scenario: 生成分类统计
- **WHEN** 所有项目处理完成
- **THEN** 系统生成 categories.json,包含每个分类的项目数量和列表

#### Scenario: 生成语言统计
- **WHEN** 所有项目处理完成
- **THEN** 系统生成 languages.json,包含每种语言的项目数量和列表
