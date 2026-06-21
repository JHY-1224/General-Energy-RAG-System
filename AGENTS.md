# AGENTS.md - Vernova-RAG v2

## Safety

- 禁止批量删除文件或目录。
- 禁止 `Remove-Item -Recurse`、`rm -rf`、`git clean -fd`、`git reset --hard`。
- 不要修改或输出 `.env` 中的秘密。
- 不要擅自 commit、push、merge、rebase 或回滚。
- 保留旧 `/api/*` 和现有 Vue 功能，采用渐进式重构。
- 构建使用 `npm run build -- --emptyOutDir=false`，避免清空 `dist`。

## Product

Vernova-RAG 是能源电气领域的可配置 RAG 管理系统：

```text
Vue Control Plane + FastAPI + Configurable RAG Engine + Evaluation/Experiment Platform
```

默认策略：`metadata filter + hybrid + parent-child + rerank + compression`。

## Current implementation status

截至 2026-06-21，当前本地版本已完成：

- FastAPI v1 `/api/*` 保持兼容，模块化 v2 `/api/v2/*` 已接入同一个应用。
- 文档上传、处理、单文档删除与 v2 索引生命周期已同步。
- Loader、Splitter、Embedding、Vector Store、Index、Retriever、Pre/Post Retrieval 均按模块拆分。
- 支持 Vector、BM25、Hybrid、Parent-Child、Summary、RAG-Fusion 检索模式。
- 每次查询生成 Trace，包含查询变换、召回、排序、压缩、回答、阶段耗时、token 和 cost 字段。
- 前端支持策略配置、检索 Trace、排序变化、压缩前后对比。
- 前端评测中心支持 JSONL 上传校验、实验预设、批量评测及 JSON/CSV/Markdown 报告下载。
- 实验运行器输出分类指标、失败样例、对比报告和推荐实验。
- 评测指标按 `doc_id` 保序去重，避免重复 Chunk 使 nDCG 超过 1。
- 侧边栏保留 10 个核心入口；LlamaIndex Runtime 设计、RAG 问答演示、报告中心三个独立入口已移除。

## Runtime entrypoints

- 兼容启动：`python backend/main.py`
- 模块启动：`python -m app.main serve`
- 前端：`npm run dev`
- v1 兼容 API：`/api/*`
- v2 策略 API：`/api/v2/*`

## Architecture rules

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

## Core pipeline

```text
loader -> cleaner -> table/structure parser -> splitter -> metadata -> indexes
query -> rewrite/expand/transform/router -> retrieve/fusion -> rerank/compress/dedupe/parent -> answer -> trace -> evaluation
```

## Supported strategies

- Loaders：Markdown、TXT、PDF、DOCX、HTML、CSV/Excel、ChatML/JSONL
- Splitters：Recursive、Markdown Header、Parent-Child、Business Object
- Index：Vector、BM25、Hybrid、Metadata、Parent-Child、Summary
- Pre Retrieval：Rewrite、Expansion、Transformation、Metadata Router、MultiQuery、HyDE
- Post Retrieval：Rerank、Compression、Deduplication、Filter、Parent Recovery、RRF
- Vector stores：Chroma、FAISS、Qdrant、pgvector、Milvus adapters
- Embeddings：Local/HuggingFace、BGE、Qwen、OpenAI、DashScope adapters

## Data contracts

- 每个 Document 有 `doc_id`。
- 每个 Chunk 有 `chunk_id`、`doc_id`、content 和 metadata。
- Parent-Child 的 child metadata 必须包含 parent 信息。
- Table chunk 不得被普通 splitter 切碎，必须有 `table_id`。
- Figure 接口保留 `figure_id`、caption 和 image path。
- ChatML 一个案例一个 Case chunk。

## Evaluation

- Eval set：`data/eval_sets/energy_rag_eval.jsonl`
- Metrics：Hit@K、Recall@K、MRR、nDCG@K
- RAGAS-compatible：faithfulness、answer_relevancy、context_precision、context_recall、answer_correctness
- Engineering：各阶段 latency、tokens、cost 字段
- Reports：`reports/eval_reports/`，输出 JSON/CSV/Markdown
- Batch evaluation：前端可上传 UTF-8 JSONL 到 `data/eval_sets/`，报告通过受限下载接口获取
- Experiment comparison：生成 `experiment_comparison.*`，包含质量分和推荐实验

## Validation baseline

发布前至少执行：

```powershell
python -m pip install -r backend/requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q app backend tests scripts
npm ci
npm run build -- --emptyOutDir=false
```

2026-06-21 本地验证结果：Python 单元测试 4/4 通过、全模块编译通过、Vite 构建通过、FastAPI 接口烟测通过、浏览器检索与批量评测流程通过。全局 Python 环境的 `pip check` 存在其他项目包版本冲突，不属于 `backend/requirements.txt` 声明的依赖；生产部署应使用独立 `.venv`。

## GitHub publication

- 远端：`https://github.com/JHY-1224/Vernova-RAG.git`
- 默认分支：`main`
- CI：`.github/workflows/ci.yml`
- 可以提交：源码、配置、示例评测集、`.gitkeep`、示例报告、测试和文档。
- 禁止提交：`.env`、上传文件、`data/traces/`、生成的评测 JSON/CSV/Markdown、`node_modules/`、`dist/`、缓存。
- 推送前先执行 `git status`、`git diff --check` 和上述验证命令。
- 不要在 README、AGENTS、Issue 或 Commit 中粘贴 API Key、Token 或 GitHub 凭据。

## Commands

```powershell
python -m app.main ingest --path data/raw/manual.md --config app/config/rag_config.yaml
python -m app.main ingest --config app/config/rag_config.yaml
python -m app.main query --question "塔架一阶共振怎么判断？" --config app/config/rag_config.yaml
python -m app.main eval --eval-set data/eval_sets/energy_rag_eval.jsonl --config app/config/eval_config.yaml
python -m app.main experiment --config app/config/experiment_config.yaml
python -m unittest discover -s tests -v
npm run build -- --emptyOutDir=false
```

## Known boundaries

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
