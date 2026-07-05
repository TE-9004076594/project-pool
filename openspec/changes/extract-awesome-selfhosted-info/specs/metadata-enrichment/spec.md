## ADDED Requirements

### Requirement: GitHub API 元数据获取
系统 SHALL 通过 GitHub REST API v3 获取每个项目的元数据信息,包括开发语言、许可证、Star 数量、Fork 数量、Topics 等。

#### Scenario: 成功获取项目元数据
- **WHEN** 调用 GitHub API 查询项目
- **THEN** 系统获取 language、license.spdx_id、stargazers_count、forks_count、topics 等字段

#### Scenario: API 速率限制处理
- **WHEN** API 请求达到速率限制(60次/小时未认证或5000次/小时已认证)
- **THEN** 系统等待后重试,或使用 Personal Access Token 提升限额

#### Scenario: API 请求失败降级
- **WHEN** GitHub API 返回错误或超时
- **THEN** 系统记录错误,标记该字段为"未知",继续处理下一个项目

### Requirement: DeepL API 翻译集成
系统 SHALL 调用 DeepL Translation API 将项目描述和分类名称翻译为中文,支持批量翻译以节省配额。

#### Scenario: 单个文本翻译
- **WHEN** 需要翻译项目描述
- **THEN** 系统调用 DeepL API,传入英文文本,获取中文翻译结果

#### Scenario: 批量翻译优化
- **WHEN** 需要翻译多个项目描述
- **THEN** 系统使用批量翻译 API,一次请求翻译最多 50 条文本,减少 API 调用次数

#### Scenario: 翻译配额监控
- **WHEN** 接近 DeepL 免费额度上限(50万字符/月)
- **THEN** 系统发出警告,记录已使用配额

#### Scenario: 翻译失败降级
- **WHEN** DeepL API 返回错误或配额耗尽
- **THEN** 系统保留英文原文,记录错误日志,不中断整体流程

### Requirement: 翻译结果缓存
系统 SHALL 缓存已翻译的文本,避免重复调用翻译 API,节省配额并提升性能。

#### Scenario: 缓存命中
- **WHEN** 需要翻译的文本已在缓存中
- **THEN** 系统直接返回缓存结果,不调用 API

#### Scenario: 缓存持久化
- **WHEN** 脚本执行完成
- **THEN** 系统将翻译缓存保存到文件,下次执行时加载
