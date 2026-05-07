# 00 Data Availability

## 路径检查

| 路径 | 存在 | 实际位置 |
| --- | --- | --- |
| 结构化目录 | True | data/structured |
| formula_library | True | data/structured/formula_library.json |
| table_library | True | data/structured/table_library.json |
| data/paddle_output | False | data/paddle_output |
| data/glmocr_output | False | data/glmocr_output |

## 结构化统计

| 指标 | 值 |
| --- | --- |
| structured JSON 文件数 | 1005 |
| structured blocks 总数 | 6138 |
| formula_library 条目数 | 2247 |
| table_library 条目数 | 146 |

## OCR 输出覆盖

| 来源 | 存在 | 可用章节数 | 备注 |
| --- | --- | --- | --- |
| requested data/paddle_output | False | 0 | missing |
| requested data/glmocr_output | False | 0 | missing |
| tmp/paddle_output | True | 36 | usable fallback |
| tmp/glmocr_output | True | 36 | usable fallback |

## 覆盖细节

- structured 章节键：appendix1, appendix2, appendix3, appendix4, appendix5, appendix6, chapter1, chapter2, chapter3, chapter4, chapter5, chapter6 ...
- tmp/glmocr_output 是否全章节覆盖 structured：是
- tmp/glmocr_output 相对 structured 的缺失章节数：0
- tmp/paddle_output 相对 structured 的缺失章节数：0

## 可行性初判

- structured 数据目录：可用
- formula/table 库：可用
- 用户指定的 data/paddle_output 与 data/glmocr_output：当前工作树下缺失
- 实际可用 OCR 根目录：tmp/paddle_output=是，tmp/glmocr_output=是
- 结论：structured 质量评估方案可做，且后续比较脚本可基于 tmp 下的实际 OCR 输出只读运行。

