# Data

`data/` 存放项目的数据资产，而不是主要代码。

整个项目里最关键的数据边界就在这里。

## 一级目录

- `背景资料/`
  原始教材 PDF、参考资料、人工收集素材
- `structured/`
  结构化知识产物，包括章节 JSON、公式库、表格库

## 推荐理解顺序

1. 先看 `背景资料/`，理解原始输入
2. 再看 `tmp/paddle_output/`，理解 PDF 到 LaTeX 之后的中间结果
3. 最后看 `structured/`，这是后续 graph / retrieval / memory / agent 的直接输入

## 当前最重要的数据判断

`data/structured/` 是整个项目的知识底座。

后续这些能力都应以它为统一输入：

- `core/knowledge_graph`
- `core/retrieval`
- `core/memory`
- `core/agent`
- `apps/teaching_system`

## 维护原则

1. 原始资料尽量不手工改写
2. 新生成的中间产物允许覆盖重建，并统一优先写入 `tmp/`
3. 结构化产物必须保证字段稳定、来源可追溯
4. 临时缓存、调试输出、运行垃圾不要放进 `data/`，统一放到 `tmp/`
