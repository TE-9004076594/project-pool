## ADDED Requirements

### Requirement: 爬取 awesome-selfhosted 仓库内容
系统 SHALL 能够从 https://github.com/awesome-selfhosted/awesome-selfhosted 获取完整的 README.md 文件内容,支持网络请求失败时的重试机制。

#### Scenario: 成功获取仓库内容
- **WHEN** 执行爬取脚本
- **THEN** 系统下载并保存 awesome-selfhosted 的 README.md 完整内容

#### Scenario: 网络请求失败时重试
- **WHEN** 首次网络请求失败
- **THEN** 系统自动重试最多3次,每次间隔递增

### Requirement: 解析项目列表结构
系统 SHALL 能够解析 Markdown 格式的项目列表,识别每个项目的名称、链接和描述信息,并按照分类层级组织。

#### Scenario: 识别项目条目
- **WHEN** 解析 Markdown 中的列表项
- **THEN** 系统提取项目名称(链接文本)、GitHub URL 和项目描述

#### Scenario: 识别分类层级
- **WHEN** 遇到 Markdown 标题(## 或 ###)
- **THEN** 系统记录当前分类,将后续项目归入该分类

### Requirement: 提取项目元数据
系统 SHALL 从每个项目的 GitHub 页面提取开发语言、许可证类型、Star 数量等元数据信息。

#### Scenario: 获取开发语言
- **WHEN** 访问项目的 GitHub 页面
- **THEN** 系统提取主要开发语言信息

#### Scenario: 获取许可证信息
- **WHEN** 访问项目的 GitHub 页面
- **THEN** 系统提取 LICENSE 文件中的许可证类型

### Requirement: 处理异常情况
系统 SHALL 优雅地处理无法访问的项目链接、缺失的信息或格式异常,记录错误但不中断整体流程。

#### Scenario: 项目链接无效
- **WHEN** 某个项目链接返回 404 或无法访问
- **THEN** 系统记录错误日志并跳过该项目,继续处理下一个

#### Scenario: 元数据缺失
- **WHEN** 项目缺少某些元数据(如无明确许可证)
- **THEN** 系统标记为"未知"并继续处理
