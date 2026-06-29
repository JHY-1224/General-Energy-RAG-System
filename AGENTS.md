# AGENTS.md - Energy O&M RAG System

本文件是本项目的唯一总说明文档。原 `README.md`、`WINDOWS_START.md` 和 `docs/ragas_evaluation.md` 的项目介绍、运行命令、架构、评估、Graph、验证、Windows 启动说明和 GitHub 发布规则已合并到这里；后续维护项目说明时优先更新本文件。

## Safety

- 禁止批量删除文件或目录。
- 禁止 `Remove-Item -Recurse`、`rm -rf`、`git clean -fd`、`git reset --hard`。
- 不要修改或输出 `.env` 中的秘密。
- 不要擅自 commit、push、merge、rebase 或回滚。
- 保留旧 `/api/*` 和现有 Vue 功能，采用渐进式重构。
- 构建使用 `npm run build -- --emptyOutDir=false`，避免清空 `dist`。
- 只允许在用户明确要求时删除单个明确文件；不要删除目录、缓存、构建产物或批量文件。

## Product

`Energy O&M RAG System` 是面向能源电气领域的本地化可配置 RAG 管理系统，覆盖风电故障诊断、区域负荷预测、风电功率预测、储能 EMS、电气工程基础、工业计算逻辑和行业案例库。

- 官方产品名称：`Energy O&M RAG System`
- 前端、API、AGENTS 和项目说明统一使用 `RAG System`，不要再使用 `RAG Agent` 作为产品品牌。
- `Agent 案例库`、`多 Agent` 等术语描述的是业务知识类别或技术架构，不属于产品品牌，可按语义保留。

```text
Vue Control Plane
  + FastAPI v1 Compatible API
  + Configurable RAG v2 Engine
  + Loader / Splitter / Index / Retriever
  + Pre Retrieval / Post Retrieval Pipeline
  + Optional LightRAG-style Graph-Enhanced Retrieval
  + Query Trace / Retrieval Metrics / RAGAS-Compatible Evaluation
  + Experiment Runner / JSON CSV Markdown Reports
```

默认策略：

```text
metadata filter
  + hybrid search (Vector 0.7 + BM25 0.3)
  + parent-child
  + rerank
  + contextual compression
```

原因：能源知识库同时存在中文语义、变量名、字段名、公式和缩写。BM25 负责精确词，Vector 负责语义，Metadata 隔离业务域，Parent-Child 补完整规则上下文，Rerank 和 Compression 控制相关性与 token 噪声。

## Current Implementation Status

截至 2026-06-29，当前本地版本已完成：

- FastAPI v1 `/api/*` 保持兼容，模块化 v2 `/api/v2/*` 已接入同一个应用。
- 文档上传、处理、单文档删除与 v2 索引生命周期已同步。
- Loader、Splitter、Embedding、Vector Store、Index、Retriever、Pre/Post Retrieval 均按模块拆分。
- 支持 Vector、BM25、Hybrid、Parent-Child、Summary、RAG-Fusion 检索模式。
- 每次查询生成 `QueryTrace`，包含查询变换、召回、排序、压缩、回答、阶段耗时、token 和 cost 字段。
- 前端支持策略配置、检索 Trace、排序变化、压缩前后对比。
- 前端评估中心支持 JSONL 上传校验、实验预设、批量评测及 JSON/CSV/Markdown 报告下载。
- 实验运行器输出分类指标、失败样例、样本级评估结果、对比报告和推荐实验。
- 评测指标按 doc/chunk id 保序去重，避免重复 Chunk 使 nDCG 超过 1。
- RAGAS Evaluation Center 已增强为四指标闭环：Faithfulness、Answer Relevancy、Context Precision、Context Recall。
- 新增 `/api/v1/evaluation/*`，用于评估数据集、运行记录、样本详情、失败样本、指标总览和自动诊断。
- 新增可选 `Graph-Enhanced Energy Retrieval`：规则实体/关系抽取、JSON 图存储、local/global/hybrid 图检索、图上下文和独立 API/前端页面。
- 侧边栏保留 11 个核心入口；LlamaIndex Runtime 设计、RAG 问答演示、报告中心三个旧入口仍保持移除。

## Quick Start

Windows PowerShell：

```powershell
cd "C:\Users\Administrator\Desktop\江翰宇\General-Energy-RAG-System"
python -m pip install -r backend/requirements.txt
python backend/main.py
```

另开一个 PowerShell：

```powershell
cd "C:\Users\Administrator\Desktop\江翰宇\General-Energy-RAG-System"
npm install
npm run dev
```

默认地址：

- 前端：http://127.0.0.1:8080
- RAGAS 页面：http://127.0.0.1:8080/#/ragas
- 后端：http://127.0.0.1:8000
- FastAPI Swagger：http://127.0.0.1:8000/docs
- v2 配置能力：http://127.0.0.1:8000/api/v2/config/options

前端通过 Vite proxy 访问后端 `/api/*`，因此本地联调时需要同时启动 FastAPI 和 Vite。

如果提示 `Port 8080 is already in use`，说明前端已经启动。可以直接打开前端地址，或用下面命令查占用进程：

```powershell
Get-NetTCPConnection -LocalPort 8080 | Select-Object LocalPort,OwningProcess
```

原来的 `python backend/main.py` 仍然可用，但实际会加载模块化的 `app.main:app`，旧 `/api/*` 与新 `/api/v2/*` 同时保留。

## Windows Troubleshooting

打开前端看到后端不可用：

- 说明 Vite 已启动，但 FastAPI 没有启动。
- 回到后端终端执行：

```powershell
python backend/main.py
```

`npm run dev` 提示依赖缺失：

- 在项目根目录重新执行：

```powershell
npm install
```

端口被占用：

- `8080` 被占用通常说明前端已经在运行。
- `8000` 被占用通常说明后端已经在运行。
- 可以先查占用进程：

```powershell
Get-NetTCPConnection -LocalPort 8080 | Select-Object LocalPort,OwningProcess
Get-NetTCPConnection -LocalPort 8000 | Select-Object LocalPort,OwningProcess
```

如果确认要关闭某个明确进程，再执行：

```powershell
Stop-Process -Id <PID>
```

不要为了处理端口问题删除目录、缓存、`node_modules`、`dist` 或重装项目。

## Runtime Entrypoints

- 兼容启动：`python backend/main.py`
- 模块启动：`python -m app.main serve`
- 前端：`npm run dev`
- v1 兼容 API：`/api/*`
- v2 策略 API：`/api/v2/*`
- v1 Evaluation API：`/api/v1/evaluation/*`

## Core Pipeline

```text
loader
  -> cleaner
  -> structure/table parser
  -> content type detector
  -> splitter
  -> metadata enricher
  -> index builder

query
  -> rewrite / expand / transform / router
  -> retrieve / fusion
  -> rerank / compress / dedupe / parent recovery
  -> answer
  -> trace
  -> evaluation

optional graph
  -> entity/relation extraction
  -> JSON graph
  -> local/global/hybrid graph retrieval
  -> graph context
```

## Architecture Rules

- 不要把新逻辑继续堆进 `backend/main.py`。
- Loader 放 `app/loaders/`。
- 清洗和结构抽取放 `app/preprocessors/`。
- Chunk 策略放 `app/splitters/`。
- Embedding 和 Vector Store 通过 Factory 选择。
- Index、Retriever、Pre Retrieval、Post Retrieval 独立。
- 每次 query 必须生成并保存 `QueryTrace`。
- 旧文档处理接口与 v2 引擎必须保持同步；处理时替换该文档 Chunk，删除时调用 `engine.remove_document()`。
- 评测指标放 `app/evaluation/`，同时输出检索、RAGAS-compatible 和 latency/token 指标。
- 新策略必须可以通过 `QueryOptions` 或 YAML 配置启用/关闭。
- 图增强逻辑只能放在 `app/graph_retrieval/` 和独立 Graph API，不得替换基础 Hybrid Retrieval 默认路径。

## Supported Strategies

- Loaders：Markdown、TXT、PDF、DOCX、HTML、CSV/Excel、ChatML/JSONL
- Splitters：Recursive、Markdown Header、Parent-Child、Business Object
- Index：Vector、BM25、Hybrid、Metadata、Parent-Child、Summary
- Pre Retrieval：Rewrite、Expansion、Transformation、Metadata Router、MultiQuery、HyDE
- Post Retrieval：Rerank、Compression、Deduplication、Filter、Parent Recovery、RRF
- Vector stores：Chroma、FAISS、Qdrant、pgvector、Milvus adapters
- Embeddings：Local/HuggingFace、BGE、Qwen、OpenAI、DashScope adapters
- Graph Retrieval：Naive、Local Graph、Global Graph、Hybrid Graph；默认不进入基础 Query API

## RAG Optimization Angles

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

## Data Ingestion

统一入库管线：

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

推荐 metadata：

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

省略 `--path` 时会递归处理 `data/raw/` 下的非隐藏普通文件，不处理 `.gitkeep`。前端旧版文档处理接口与 v2 引擎共享同一索引生命周期：重新处理文档会替换该文档 Chunk，删除文档会同步从 Vector、BM25、Hybrid 与 Summary 索引移除。

## Data Contracts

- 每个 Document 有 `doc_id`。
- 每个 Chunk 有 `chunk_id`、`doc_id`、content 和 metadata。
- Parent-Child 的 child metadata 必须包含 parent 信息。
- Table chunk 不得被普通 splitter 切碎，必须有 `table_id`。
- Figure 接口保留 `figure_id`、caption 和 image path。
- ChatML 一个案例一个 Case chunk。
- Graph Entity 必须有稳定 `entity_id`、类型、domain 和 `source_chunk_ids`。
- Graph Relation 必须有稳定 `relation_id`、合法关系类型、端点实体和来源 Chunk。

## Index Strategies

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

## Pre Retrieval

- Query Rewrite：补全口语、省略和指代
- Query Expansion：加入中文名、英文名、字段名、变量名、单位和同义词
- Query Transformation：生成 metadata filter 或结构化意图
- Metadata Router：识别风电、负荷、储能、电气工程和行业案例域
- MultiQuery：生成多个查询提高召回
- HyDE：生成假设文档再检索，实验项，默认关闭

## Post Retrieval

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

## Query Trace

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

前端“RAG 检索测试”页可直接配置策略并查看 trace，同时展示 `original_rank`、`final_rank`、各阶段 latency，以及上下文压缩前后的内容。

## RAGAS Evaluation Center

示例评测集：`data/eval_sets/energy_rag_eval.jsonl`

```powershell
python -m app.main eval --eval-set data/eval_sets/energy_rag_eval.jsonl --config app/config/eval_config.yaml
```

检索指标：

- Hit@K：TopK 是否命中正确文档
- Recall@K：TopK 覆盖多少 gold documents
- MRR：第一个正确文档是否靠前
- nDCG@K：综合相关性与排序位置

RAGAS-compatible 四个核心指标：

- `faithfulness`：回答是否被上下文支持，用于判断幻觉。
- `answer_relevancy`：回答是否真正回应用户问题。
- `context_precision`：相关 chunk 是否排在 Top-K 前面。
- `context_recall`：回答所需关键证据是否完整召回。

RAGAS 指标总表：

| 指标 | 评估对象 | 低分表现 | 优化方向 |
|---|---|---|---|
| Context Precision | 检索排序 | 相关 chunk 排名靠后，无关 chunk 混入前列 | Metadata Filter、Hybrid Retrieval、RRF、Rerank、优化 chunk 粒度 |
| Context Recall | 检索覆盖 | 必要证据没召回，多跳信息缺失 | 提高 top_k、多查询、Query Decomposition、Parent Document Retriever |
| Faithfulness | 答案可信度 | 回答包含上下文不支持的内容 | Prompt 约束、引用来源、无证据拒答、Context Compression |
| Answer Relevancy | 答案贴题度 | 回答偏题、啰嗦、没有正面回答 | Query Rewrite、Intent Router、Few-shot、结构化输出 |

扩展指标：

- `answer_correctness`：仅在 ground_truth 存在时计算。
- `context_entity_recall`：上下文实体覆盖。
- 工程指标：Embedding、Retrieval、Rerank、Compression、Generation、Total latency，输入/输出 tokens，Embedding 维度和向量库文档数。

当前默认使用离线兼容评分器，输出字段与 RAGAS 对齐；接入真实 LLM/RAGAS 后可替换 `app/evaluation/ragas_evaluator.py`，不影响实验接口。

前端评估中心能力：

- 四指标 Dashboard：当前均分、上次分数、趋势、指标解释、低分含义和优化入口。
- 评估数据集列表：`wind_fault_qa`、`load_forecast_qa`、`storage_ems_qa`、`calc_logic_qa`、`mixed_energy_qa`。
- 评估运行记录：run_id、配置、top_k、状态、样本数和四指标均分。
- 单样本评估详情：question、ground_truth、retrieved_contexts、retrieved_chunk_ids、reference_context_ids、generated_answer、四指标、failure_type、optimization_suggestion、trace。
- 失败样本分析：`retrieval_miss`、`bad_ranking`、`noisy_context`、`hallucination`、`off_topic`、`incomplete_answer`、`wrong_domain`、`bad_citation`。
- 自动诊断：根据四个核心分数返回 primary_failure_type、root_cause 和 suggestions。
- 能源场景说明：风电故障诊断、区域负荷预测、储能 EMS、工业计算逻辑。
- 趋势图与不同检索配置对比。

评估 API：

- `GET /api/v1/evaluation/datasets`
- `POST /api/v1/evaluation/datasets`
- `GET /api/v1/evaluation/datasets/{dataset_id}`
- `POST /api/v1/evaluation/run`
- `GET /api/v1/evaluation/runs`
- `GET /api/v1/evaluation/runs/{run_id}`
- `GET /api/v1/evaluation/runs/{run_id}/samples`
- `GET /api/v1/evaluation/runs/{run_id}/failures`
- `GET /api/v1/evaluation/metrics/summary`
- `POST /api/v1/evaluation/diagnose`

旧接口保持兼容：

- `POST /api/v2/eval/run`
- `POST /api/v2/eval/upload?filename=*.jsonl`
- `GET /api/v2/eval/reports/{filename}`

RAGAS 边界：当前实现只增强 evaluation、RAGAS 指标、评估 API、评估页面和 mock evaluation 数据；不改变文档入库、Chunk 管理、基础检索、Graph-enhanced Retrieval 和主问答 API。

## Experiment Comparison

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

## API

兼容 API：

- `GET /api/health`
- `GET /api/state`
- `POST /api/documents/upload`
- `POST /api/documents/{document_id}/process`
- `DELETE /api/documents/{document_id}`
- `GET /api/chunks`
- `GET /api/metadata`
- `GET /api/vector-index`
- `POST /api/retrieval/search`
- `POST /api/context/build`
- `POST /api/chat`

v2 API：

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

## Configuration

- `app/config/rag_config.yaml`
- `app/config/model_config.yaml`
- `app/config/eval_config.yaml`
- `app/config/experiment_config.yaml`

所有策略均通过配置或 API request 选择，避免写死在单一脚本中。

## Project Structure

```text
app/
  api/                 # ingest/query/eval/config/experiment routes
  chains/              # RAG chain 与 prompt
  config/              # YAML 配置
  core/                # models 与 ConfigurableRagEngine
  embeddings/          # EmbeddingFactory
  evaluation/          # metrics/RAGAS/experiment/report/diagnostics
  graph_retrieval/     # LightRAG-style energy graph layer
  indexes/             # vector/BM25/hybrid/metadata/parent/summary
  loaders/             # md/pdf/docx/html/csv/excel/chatml
  post_retrieval/      # rerank/compression/dedupe/filter/parent/RRF
  pre_retrieval/       # rewrite/expansion/transformation/router/HyDE
  preprocessors/       # clean/table/figure/metadata
  retrievers/          # 多检索器
  splitters/           # recursive/header/parent-child/business
  vectorstores/        # Chroma/FAISS/Qdrant/pgvector/Milvus adapters
backend/               # FastAPI v1 compatible app and upload demo state
frontend/              # Vue control plane
data/eval_sets/        # JSONL 评测集
data/graph/            # 运行时轻量图谱 JSON
indexes/               # 本地索引数据
reports/eval_reports/  # JSON/CSV/Markdown 评估报告
scripts/               # 示例入口
tests/                 # 非破坏性单元测试
```

## Commands

```powershell
python -m app.main ingest --path data/raw/manual.md --config app/config/rag_config.yaml
python -m app.main ingest --config app/config/rag_config.yaml
python -m app.main query --question "塔架一阶共振怎么判断？" --config app/config/rag_config.yaml
python -m app.main eval --eval-set data/eval_sets/energy_rag_eval.jsonl --config app/config/eval_config.yaml
python -m app.main experiment --config app/config/experiment_config.yaml
python -m app.main serve --port 8000
python -m unittest discover -s tests -v
python -m compileall -q app backend tests scripts
npm run build -- --emptyOutDir=false
```

也可使用：

- `scripts/run_ingest.py`
- `scripts/run_query.py`
- `scripts/run_eval.py`
- `scripts/run_experiment.py`

## Validation Baseline

发布前至少执行：

```powershell
python -m pip install -r backend/requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q app backend tests scripts
npm ci
npm run build -- --emptyOutDir=false
```

2026-06-29 本地验证结果：Python 单元测试 9/9 通过、全模块编译通过、Vite 构建通过；新增 `/api/v1/evaluation/diagnose` 与 `/api/v1/evaluation/metrics/summary` 烟测通过。全局 Python 环境的 `pip check` 可能存在其他项目包版本冲突，不属于 `backend/requirements.txt` 声明的依赖；生产部署应使用独立 `.venv`。

## GitHub Publication

远端：

```text
https://github.com/JHY-1224/General-Energy-RAG-System.git
```

默认分支：`main`

可以提交：

- 源码
- 配置
- 示例评测集
- `.gitkeep`
- 示例报告
- 测试
- 文档

禁止提交：

- `.env`
- API Key、Token、密码、Cookie、私钥
- 上传文件
- `data/traces/`
- 生成的评测 JSON/CSV/Markdown
- `node_modules/`
- `dist/`
- 缓存目录
- `data/graph/energy_graph.json`

`data/graph/energy_graph.json` 是运行时图索引，不提交；只保留 `data/graph/.gitkeep`。

推送前先执行：

```powershell
git status
git diff --check
python -m unittest discover -s tests -v
python -m compileall -q app backend tests scripts
npm run build -- --emptyOutDir=false
```

不要在 AGENTS、Issue、Commit 或 PR 中粘贴 API Key、Token 或 GitHub 凭据。

## GitHub Upload Commands

以下命令只给人工执行；助手默认不自动 commit 或 push。

```powershell
cd "C:\Users\Administrator\Desktop\江翰宇\General-Energy-RAG-System"
git status
git diff --check
python -m unittest discover -s tests -v
python -m compileall -q app backend tests scripts
npm run build -- --emptyOutDir=false
git add AGENTS.md README.md WINDOWS_START.md app/api/routes_eval.py app/evaluation/eval_dataset.py app/evaluation/experiment_runner.py app/evaluation/ragas_evaluator.py app/evaluation/report_generator.py app/evaluation/ragas_diagnostics.py app/main.py frontend/src/App.vue frontend/src/mock.js frontend/src/styles.css tests/test_ragas_diagnostics.py
git status
git commit -m "Enhance RAGAS evaluation center and consolidate docs"
git push origin main
```

如果需要提交 `data/graph/.gitkeep`，只添加这个明确文件，不要添加运行时图谱 JSON：

```powershell
git add data/graph/.gitkeep
```

## Known Boundaries

- 当前可离线运行，Embedding/Vector DB/RAGAS 使用稳定 fallback contract。
- 接真实外部模型或数据库时只替换 adapter，不改变 API、trace 和 evaluation contract。
- 当前 Runtime 是 LlamaIndex 风格的可配置对象模型，尚未安装并接入真实 `llama-index` SDK。
- Chroma、FAISS、Qdrant、pgvector、Milvus 当前统一落到本地内存适配层，尚未连接外部持久化服务。
- 上传文件保存在 `backend/uploaded_documents/`，文档清单、Chunk 与索引状态仍以内存为主，服务重启后需要数据库或本地 manifest 恢复。
- PDF、DOCX、Excel 在可选解析库缺失时使用占位解析；生产环境需安装对应解析库并补充真实文件回归测试。
- RagChain 与 RAGAS-compatible evaluator 当前为离线回退实现，真实 LLM、Reranker、RAGAS 和成本计费仍待接入。
- 无 ground truth 时不计算 answer_correctness。
- HyDE、Summary、RAG-Fusion 默认关闭，不影响基础路径。
- 无 `--path` 的 ingest 只扫描 `data/raw/` 下非隐藏普通文件，不处理 `.gitkeep`。
- Graph Retrieval 是 LightRAG-style 轻量实现，当前不包含原生 LightRAG、Neo4j、社区摘要或 LLM 实体抽取。
- Graph 模块默认独立运行，不改变 `/api/v2/query/test` 和现有 RAGAS 评估结果。
- 所有数据为演示数据，生产诊断结论必须经过工程师复核。
