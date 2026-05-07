# 08 Current Delivery Snapshot

本快照用于冻结当前已经达到交付标准的 `data/structured` 和核心结构化代码逻辑。它只写入 tmp，不修改正式数据。

| item | value |
| --- | --- |
| snapshot_dir | tmp/structured_quality_probe/cache/current_delivery_snapshot |
| copied_file_count | 1013 |
| manifest | tmp/structured_quality_probe/cache/current_delivery_snapshot/manifest.json |
| source_structured_dir | data/structured |

## 说明

- GitHub 提交作为外层回滚保险；本地 tmp 快照用于审计、三版对比和报告引用。
- 快照包含 `data/structured/*.json` 和 `knowledge_engineering` 的核心 `.py` / README 文件。
