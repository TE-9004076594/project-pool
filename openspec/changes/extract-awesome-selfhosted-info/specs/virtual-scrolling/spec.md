## ADDED Requirements

### Requirement: 虚拟滚动核心机制
系统 SHALL 实现虚拟滚动,仅渲染可视区域的 DOM 元素,动态替换内容以提升性能。

#### Scenario: 计算可见范围
- **WHEN** 用户滚动容器
- **THEN** 系统根据 scrollTop 和容器高度计算可见的项目索引范围

#### Scenario: 动态渲染
- **WHEN** 可见范围变化
- **THEN** 系统清空当前容器,重新渲染可见范围的项目卡片

#### Scenario: 位置偏移
- **WHEN** 渲染可见项目
- **THEN** 系统使用 CSS transform translateY 将内容偏移到正确位置,模拟完整列表

### Requirement: 缓冲区管理
系统 SHALL 在可见区域上下添加缓冲区,预渲染少量额外项目,避免滚动时白屏。

#### Scenario: 设置缓冲区
- **WHEN** 配置虚拟滚动
- **THEN** 系统在可见区域上下各添加 5 个项目的缓冲区

#### Scenario: 平滑滚动
- **WHEN** 用户快速滚动
- **THEN** 缓冲区确保新内容已渲染,无闪烁或白屏

### Requirement: 性能监控
系统 SHALL 监控虚拟滚动的性能指标,确保流畅体验。

#### Scenario: FPS 监控
- **WHEN** 用户滚动列表
- **THEN** 系统保持 FPS > 50,无明显卡顿

#### Scenario: DOM 节点数量控制
- **WHEN** 项目总数为 1500
- **THEN** 系统同时存在的 DOM 节点数 < 30(可见 + 缓冲区)
