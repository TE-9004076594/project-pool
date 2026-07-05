## ADDED Requirements

### Requirement: 实时搜索(防抖)
系统 SHALL 实现前端实时搜索功能,用户输入时自动触发搜索,使用 300ms 防抖避免频繁计算。

#### Scenario: 用户输入触发搜索
- **WHEN** 用户在搜索框输入文本
- **THEN** 系统等待 300ms,如无新输入则执行搜索

#### Scenario: 防抖取消
- **WHEN** 用户在 300ms 内继续输入
- **THEN** 系统取消之前的搜索定时器,重新开始计时

#### Scenario: ESC 清空搜索
- **WHEN** 用户按下 ESC 键
- **THEN** 系统清空搜索框,重置搜索结果,显示所有项目

### Requirement: 多字段搜索匹配
系统 SHALL 在多个字段中搜索关键词,包括项目名称、中文描述、英文描述、分类、语言、Topics。

#### Scenario: 名称匹配
- **WHEN** 搜索 "nextcloud"
- **THEN** 系统返回名称包含 "nextcloud" 的项目

#### Scenario: 描述匹配
- **WHEN** 搜索 "云存储"
- **THEN** 系统返回中文或英文描述包含 "云存储" 或 "cloud storage" 的项目

#### Scenario: 分类匹配
- **WHEN** 搜索 "文件共享"
- **THEN** 系统返回分类为 "File Sharing & Synchronization" 的项目

#### Scenario: Topic 匹配
- **WHEN** 搜索 "docker"
- **THEN** 系统返回 topics 包含 "docker" 的项目

### Requirement: 分类过滤
系统 SHALL 支持按分类过滤搜索结果,用户可多选分类。

#### Scenario: 单选分类过滤
- **WHEN** 用户勾选 "文件共享与同步" 分类
- **THEN** 系统仅显示该分类下的项目

#### Scenario: 多选分类过滤
- **WHEN** 用户勾选多个分类
- **THEN** 系统显示任意匹配其中一个分类的项目(OR 逻辑)

#### Scenario: 取消分类过滤
- **WHEN** 用户取消勾选某分类
- **THEN** 系统重新过滤,移除该分类的限制

### Requirement: 语言过滤
系统 SHALL 支持按开发语言过滤搜索结果,用户可多选语言。

#### Scenario: 语言过滤
- **WHEN** 用户勾选 "Python" 和 "JavaScript"
- **THEN** 系统仅显示使用这两种语言的项目

### Requirement: Star 数范围过滤
系统 SHALL 支持按 Star 数量范围过滤,用户可设置最小值和最大值。

#### Scenario: 设置 Star 范围
- **WHEN** 用户设置最小 1000 Stars,最大 10000 Stars
- **THEN** 系统仅显示 Star 数在此范围内的项目

### Requirement: 多字段排序
系统 SHALL 支持按多个字段排序搜索结果,包括名称、Star 数、更新时间,支持升序/降序。

#### Scenario: 按 Star 数降序
- **WHEN** 用户选择按 "Star 数" 排序,降序
- **THEN** 系统按 stargazers_count 从大到小排序

#### Scenario: 按名称升序
- **WHEN** 用户选择按 "名称" 排序,升序
- **THEN** 系统按项目名称字母顺序(A-Z)排序

#### Scenario: 按更新时间降序
- **WHEN** 用户选择按 "更新时间" 排序,降序
- **THEN** 系统按 updated_at 从新到旧排序

### Requirement: 搜索结果统计
系统 SHALL 显示当前搜索结果的数量,让用户了解匹配程度。

#### Scenario: 显示结果数量
- **WHEN** 搜索完成
- **THEN** 系统在页面显示 "共找到 X 个项目"

### Requirement: 虚拟滚动渲染
系统 SHALL 实现虚拟滚动机制,只渲染可视区域的项目卡片,优化大数据量性能。

#### Scenario: 初始渲染
- **WHEN** 加载搜索结果
- **THEN** 系统仅渲染可视区域的 ~10-20 个项目卡片

#### Scenario: 滚动加载
- **WHEN** 用户向下滚动
- **THEN** 系统动态渲染新进入可视区域的项目,移除离开的项目

#### Scenario: 性能优化
- **WHEN** 项目数量 > 500
- **THEN** 虚拟滚动确保 FPS > 50,无明显卡顿
