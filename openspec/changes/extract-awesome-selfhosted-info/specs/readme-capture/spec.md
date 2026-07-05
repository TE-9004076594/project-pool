## ADDED Requirements

### Requirement: GitHub README 抓取
系统 SHALL 通过 GitHub API 获取项目的 README 文件内容,用于提取项目详细介绍。

#### Scenario: 通过 API 获取 README
- **WHEN** 处理项目元数据时
- **THEN** 系统调用 GET /repos/{owner}/{repo}/readme API,获取 README 内容(Base64 编码)

#### Scenario: README 解码
- **WHEN** 接收到 Base64 编码的 README 内容
- **THEN** 系统解码为 UTF-8 文本,准备解析

#### Scenario: API 失败降级到 HTML 解析
- **WHEN** GitHub API 无法获取 README(如私有仓库)
- **THEN** 系统尝试访问 GitHub 仓库页面,从 HTML 中提取 README 内容

### Requirement: README 段落提取
系统 SHALL 从完整的 README 中提取前 3 个段落(最多 500 字符),作为项目的详细介绍。

#### Scenario: 提取 Markdown 段落
- **WHEN** 解析 README Markdown 文本
- **THEN** 系统识别段落边界(空行分隔),提取前 3 个非标题、非代码块、非列表的段落

#### Scenario: 长度限制
- **WHEN** 提取的段落总长度超过 500 字符
- **THEN** 系统截断到最后一个完整单词,添加省略号(...)

#### Scenario: 无 README 处理
- **WHEN** 项目没有 README 文件或无法获取
- **THEN** 系统跳过此步骤,仅使用简短描述,不报错

### Requirement: README 缓存
系统 SHALL 缓存已抓取的 README 内容,避免重复请求 GitHub API。

#### Scenario: 缓存命中
- **WHEN** 需要获取某项目的 README
- **THEN** 系统检查缓存,如存在则直接返回,不调用 API

#### Scenario: 缓存持久化
- **WHEN** 脚本执行完成
- **THEN** 系统将 README 缓存保存到 cache/ 目录
