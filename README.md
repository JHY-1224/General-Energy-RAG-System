# Vernova-RAG · Energy O&M RAG System

面向风电故障诊断、区域负荷预测、风电功率预测、储能 EMS、电气工程基础和 Agent 案例库的本地化可配置 RAG 管理系统。

项目已经从固定 Demo 升级为：

```text
Vue Control Plane
  + FastAPI v1 兼容 API
  + Configurable RAG v2 Engine
  + 多 Loader / Splitter / Index / Retriever
  + Pre Retrieval / Post Retrieval Pipeline
  + Optional LightRAG-style Graph-Enhanced Retrieval
  + Query Trace / Retrieval Metrics / RAGAS-Compatible Evaluation
  + Experiment Runner / JSON CSV Markdown Reports
```

## 快速启动

Windows PowerShell：

```powershell
cd "C:\Users\Administrator\Desktop\江翰宇\Vernova-RAG"
python -m pip install -r backend/requirements.txt
python backend/main.py
```

另开一个 PowerShell：

```powershell
npm install
npm run dev
```

- 前端：http://127.0.0.1:8080
- FastAPI：http://127.0.0.1:8000/docs
- v2 配置能力：http://127.0.0.1:8000/api/v2/config/options

原来的 `python backend/main.py` 仍然可用，但实际会加载模块化的 `app.main:app`，旧 `/api/*` 与新 `/api/v2/*` 同时保留。

## 默认能源 RAG 策略

```text
metadata filter
  + hybrid search (Vector 0.7 + BM25 0.3)
  + parent-child
  + rerank
  + contextual compression
```

原因：能源知识库同时存在中文语义、变量名、字段名、公式和缩写。BM25 负责精确词，Vector 负责语义，Metadata 隔离业务域，Parent-Child 补完整规则上下文，Rerank 和 Compression 控制相关性与 token 噪声。

## RAG 优化角度

1. 数据采集
2. 文档结构化
3. Chunk 切分
4. Metadata 设计
5. Embedding 模型选择
6. 向量数据库选择
7. 索引策略选择
8. 预检索优化
9. 检索融合
10. 后检索优化
11. RAGAS 评估
12. 实验对比

## 文档入库

统一管线：

```text
raw document
  -> loader
  -> cleaner
  -> structure/table parser
  -> content type detector
  -> splitter
  -> metadata enricher
  -> index builder
```

支持的 Loader：

- Markdown / TXT
- PDF：优先用 PyMuPDF 转 Markdown；未安装时保留占位解析
- DOCX：优先用 python-docx
- HTML
- CSV / Excel：转换为 Markdown Table Document
- ChatML / JSONL：一个 system-user-assistant 案例一个 Case chunk

表格会抽成独立 Document，生成 `table_id`，正文使用占位符，避免普通 Chunk 把表格切碎。Figure/OCR 接口已预留，默认不启用。

每个 Chunk 都包含 `doc_id`、`chunk_id` 和 metadata。推荐 metadata：

```json
{
  "domain": "风电故障诊断",
  "task": "变量解释",
  "doc_type": "变量字典",
  "chunk_type": "变量解释",
  "source": "wind_variables.xlsx",
  "section": "机舱振动变量",
  "page": 12
}
```

CLI 入库：

```powershell
python -m app.main ingest --path data/raw/manual.md --config app/config/rag_config.yaml
python -m app.main ingest --config app/config/rag_config.yaml
```

省略 `--path` 时会递归处理 `data/raw/` 下的非隐藏文件。前端旧版文档处理接口与 v2 引擎共享同一索引生命周期：重新处理文档会替换该文档 Chunk，删除文档会同步从 Vector、BM25、Hybrid 与 Summary 索引移除。

## 索引策略

| 策略 | 适合场景 |
|---|---|
| Vector Index | 语义问答、概念解释、故障规则、建模流程 |
| BM25 Index | 变量名、字段名、公式、缩写、精确术语 |
| Hybrid Search | 能源电气默认场景，融合 BM25 与 Vector |
| Metadata Index | 多业务域、任务类型、故障类型过滤 |
| Parent-Child | 故障规则、技术手册、长章节、表格上下文 |
| Summary Index | 长 PDF、课程资料、图表混合章节 |
| RAG-Fusion | 复杂、多角度且召回不足的问题 |

向量库统一通过 `VectorStoreFactory` 选择：Chroma、FAISS、Qdrant、pgvector、Milvus。当前本地 Demo 使用内存 Chroma-compatible fallback，外部数据库适配器已预留。

Embedding 统一通过 `EmbeddingFactory` 选择：HuggingFace Local、BGE、Qwen、OpenAI、DashScope。无外部模型时使用确定性 Hash Embedding，保证 Demo 可启动、可测试。

## 预检索优化

- Query Rewrite：补全口语、省略和指代
- Query Expansion：加入中文名、英文名、字段名、变量名、单位和同义词
- Query Transformation：生成 metadata filter 或结构化意图
- Metadata Router：识别风电、负荷、储能、电气工程和 Agent 案例域
- MultiQuery：生成多个查询提高召回
- HyDE：生成假设文档再检索，实验项，默认关闭

## 后检索优化

- Rerank：对初召回结果重新排序
- Contextual Compression：抽取与 query 相关句子
- Deduplication：按 chunk_id / 内容标识去重
- Document Filter：过滤低相关结果
- Parent Context Recovery：child 命中后补全 parent
- RAG-Fusion / RRF：多 query 排名融合，默认 `k=60`

## Graph-Enhanced Energy Retrieval

`Graph-Enhanced Energy Retrieval` 是基础 RAG 之上的可选进阶层，参考 LightRAG 的 local / global / hybrid 双层检索思想，但不替换现有 Vector、BM25、RRF、Rerank 和 RAGAS 主线。

```text
RagChunk
  -> 规则优先实体抽取
  -> 能源关系抽取
  -> 轻量 JSON Graph Store
  -> Local / Global / Hybrid Graph Retrieval
  -> Graph Context + Related Chunk Context
```

第一版特点：

- 支持 `wind_oam`、`load_forecast`、`storage_ems` 三个能源知识域。
- 实体类型包括 Variable、FaultType、Component、Feature、Model、Metric、System、Scenario、Strategy 等。
- 关系包括 INDICATES、USED_FOR、INPUT_FEATURE_OF、SUPPORTS、CONSTRAINED_BY、PART_OF、EVIDENCED_BY 等。
- `local_graph` 面向 AccY、lag_96、SOC 等具体实体的一跳/二跳检索。
- `global_graph` 面向负荷预测到储能削峰填谷、EMS/BMS/PCS 协同等业务链路。
- `hybrid_graph` 合并局部实体证据和全局多跳路径。
- 默认存储为 `data/graph/energy_graph.json`，不强制引入 Neo4j。
- 前端 `Graph-Enhanced RAG` 页面提供构图、统计分布、示例问题和 Prompt-ready Context。

该模块不会改变 `/api/v2/query/test` 的默认行为。后续可把规则抽取替换为 LLM 抽取，把 JSON Store 替换为 Neo4j，或接入原生 LightRAG Runtime。

## 单问题测试与 Trace

```powershell
python -m app.main query --question "塔架一阶共振怎么判断？" --config app/config/rag_config.yaml
```

每次 query 都保存 trace 到 `data/traces/`，内容包括：

- original query
- rewritten query
- expanded queries
- metadata filter
- retrieval mode 和完整配置
- retrieved docs 与原始排名
- reranked docs 与最终排名
- compressed context
- answer
- pre/retrieval/rerank/compression/generation/total latency
- input/output token 估算与 cost 字段

前端“RAG 检索测试”页可直接配置上述策略并查看 trace。

Trace 页面同时展示 `original_rank`、`final_rank`、各阶段 latency，以及上下文压缩前后的内容，便于定位召回、排序和压缩问题。

## 批量评测

示例评测集：`data/eval_sets/energy_rag_eval.jsonl`

```powershell
python -m app.main eval --eval-set data/eval_sets/energy_rag_eval.jsonl --config app/config/eval_config.yaml
```

检索指标：

- Hit@K：TopK 是否命中正确文档
- Recall@K：TopK 覆盖多少 gold documents
- MRR：第一个正确文档是否靠前
- nDCG@K：综合相关性与排序位置

RAGAS-compatible 指标：

- faithfulness
- answer_relevancy
- context_precision
- context_recall
- answer_correctness：仅在 ground_truth 存在时计算
- context_entity_recall

工程指标：Embedding、Retrieval、Rerank、Compression、Generation、Total latency，输入/输出 tokens，Embedding 维度和向量库文档数。

当前默认使用离线兼容评分器，输出字段与 RAGAS 对齐；接入真实 LLM/RAGAS 后可替换 `app/evaluation/ragas_evaluator.py`，不影响实验接口。

前端评估中心支持上传并校验 UTF-8 JSONL 评测集，选择当前配置或 Vector、Hybrid、Parent-Child、RAG-Fusion 预设实验，并下载 JSON、CSV、Markdown 三种报告。上传文件保存在 `data/eval_sets/`，文件名会执行路径与字符安全检查。

## 实验对比

```powershell
python -m app.main experiment --config app/config/experiment_config.yaml
```

默认包含：

1. Vector + BGE
2. Hybrid + BGE + Metadata
3. Parent-Child + Hybrid + Rerank + Compression
4. RAG-Fusion + Rerank

报告输出到 `reports/eval_reports/`：

- JSON：完整机器可读结果
- CSV：指标对比
- Markdown：人工阅读报告
- `experiment_comparison.*`：所有实验横向指标、综合质量分和推荐实验

选型建议：

- 变量解释：BM25 + Metadata Filter
- 故障规则：Parent-Child + Hybrid + Rerank
- 表格问答：Metadata Filter + Table Retriever + Compression
- 复杂语义问题：MultiQuery 或 RAG-Fusion，但延迟更高

## CLI

```powershell
python -m app.main ingest --path data/raw/manual.md --config app/config/rag_config.yaml
python -m app.main query --question "塔架一阶共振怎么判断？" --config app/config/rag_config.yaml
python -m app.main eval --eval-set data/eval_sets/energy_rag_eval.jsonl --config app/config/eval_config.yaml
python -m app.main experiment --config app/config/experiment_config.yaml
python -m app.main serve --port 8000
```

也可使用：

- `scripts/run_ingest.py`
- `scripts/run_query.py`
- `scripts/run_eval.py`
- `scripts/run_experiment.py`

## API v2

- `GET /api/v2/config/options`
- `POST /api/v2/ingest`
- `POST /api/v2/query/test`
- `GET /api/v2/traces/{trace_id}`
- `POST /api/v2/eval/run`
- `POST /api/v2/eval/upload?filename=*.jsonl`
- `GET /api/v2/eval/reports/{filename}`
- `POST /api/v2/experiments/run`
- `GET /api/v2/graph/status`
- `POST /api/v2/graph/build`
- `POST /api/v2/graph/query`
- `GET /api/v2/graph/entities`
- `GET /api/v2/graph/relations`

FastAPI Swagger 提供完整请求模型：http://127.0.0.1:8000/docs

## 配置文件

- `app/config/rag_config.yaml`
- `app/config/model_config.yaml`
- `app/config/eval_config.yaml`
- `app/config/experiment_config.yaml`

所有策略均通过配置或 API Request 选择，避免写死在单一脚本中。

## 项目结构

```text
app/
  api/                 # ingest/query/eval/config/experiment routes
  chains/              # RAG chain 与 prompt
  config/              # YAML 配置
  core/                # models 与 ConfigurableRagEngine
  embeddings/          # EmbeddingFactory
  evaluation/          # metrics/RAGAS/experiment/report
  graph_retrieval/     # LightRAG-style energy graph layer
  indexes/             # vector/BM25/hybrid/metadata/parent/summary
  loaders/             # md/pdf/docx/html/csv/excel/chatml
  post_retrieval/      # rerank/compression/dedupe/filter/parent/RRF
  pre_retrieval/       # rewrite/expansion/transformation/router/HyDE
  preprocessors/       # clean/table/figure/metadata
  retrievers/          # 多检索器
  splitters/           # recursive/header/parent-child/business
  vectorstores/        # Chroma/FAISS/Qdrant/pgvector/Milvus adapters
data/eval_sets/        # JSONL 评测集
data/graph/            # 运行时轻量图谱 JSON
reports/eval_reports/  # JSON/CSV/Markdown 报告
scripts/               # 示例入口
tests/                 # 非破坏性单元测试
```

## 验证

```powershell
python -m unittest discover -s tests -v
python -m compileall -q app backend tests scripts
npm run build -- --emptyOutDir=false
```

## 当前边界

- 外部 Embedding、LLM、Reranker 和数据库使用可替换适配器；无凭据时走本地 fallback。
- PDF/DOCX/Excel 在对应解析库缺失时使用占位解析，不阻断入库。
- 所有数据为演示数据，生产诊断结论必须经过工程师复核。
- Graph Retrieval 当前使用规则抽取与 JSON 图存储，是进阶展示模块，不是完整知识图谱平台或原生 LightRAG 实现。
