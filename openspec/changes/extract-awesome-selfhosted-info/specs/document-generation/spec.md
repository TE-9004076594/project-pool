## ADDED Requirements

### Requirement: 生成结构化文档
系统 SHALL 将提取的项目信息组织成结构化的 Markdown 文档,包含项目分类、详细信息和索引。

#### Scenario: 按分类组织项目
- **WHEN** 生成文档时
- **THEN** 系统按照 awesome-selfhosted 的原始分类层级组织项目

#### Scenario: 包含完整项目信息
- **WHEN** 为每个项目生成说明
- **THEN** 文档包含项目名称、GitHub 链接、开发语言、功能描述、许可证等字段

### Requirement: 生成中文说明
系统 SHALL 将项目描述翻译或整理为中文,便于中文用户阅读理解。

#### Scenario: 翻译项目描述
- **WHEN** 处理英文项目描述
- **THEN** 系统生成对应的中文说明文本

#### Scenario: 保留关键术语
- **WHEN** 翻译技术术语
- **THEN** 系统保留专有名词和技术术语的原文(如框架名称、协议名称)

### Requirement: 生成项目索引
系统 SHALL 在文档开头提供快速索引,支持按开发语言、功能类别等方式检索项目。

#### Scenario: 按语言统计
- **WHEN** 生成索引部分
- **THEN** 系统列出所有开发语言及其对应的项目数量

#### Scenario: 按分类导航
- **WHEN** 生成索引部分
- **THEN** 系统提供分类目录,链接到文档中对应章节

### Requirement: 格式化输出
系统 SHALL 使用一致的 Markdown 格式输出文档,确保可读性和美观性。

#### Scenario: 统一表格格式
- **WHEN** 展示项目列表
- **THEN** 系统使用 Markdown 表格呈现项目名称、语言、描述等字段

#### Scenario: 添加视觉分隔
- **WHEN** 不同分类之间
- **THEN** 系统使用水平线或标题进行清晰分隔
