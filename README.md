# Energy O&M RAG Agent

面向风电智能运维、区域负荷预测、储能 EMS、工业计算逻辑和报告模板的能源 RAG 知识库管理原型。

这个项目用于开源展示和面试说明：它不是生产诊断系统，也不是单纯聊天机器人，而是一个 **RAG Control Plane + LlamaIndex 风格 RAG Runtime** 的本地可运行 Demo。前端负责知识库管理、文档上传、Chunk 处理、索引配置、检索测试和 API 展示；后端用 FastAPI 提供 Document / TextNode / VectorStoreIndex / Retriever / Rerank / Context API 的核心流程。

## 当前技术栈

- 后端：Python FastAPI
- 前端：Vue 3 + Vite
- RAG 核心框架语义：LlamaIndex 风格对象模型
- 本地文档目录：`backend/uploaded_documents/`
- 默认端口：后端 `8000`，前端 `8080`

## 快速启动（Windows PowerShell）

```powershell
cd "C:\Users\Administrator\Desktop\江翰宇\Vernova-RAG"
python -m pip install -r backend/requirements.txt
python backend/main.py
```

另开一个 PowerShell：

```powershell
cd "C:\Users\Administrator\Desktop\江翰宇\Vernova-RAG"
npm install
npm run dev
```

访问地址：

- 前端：http://127.0.0.1:8080
- 后端健康检查：http://127.0.0.1:8000/api/health
- FastAPI 文档：http://127.0.0.1:8000/docs

## 核心流程

```text
本地文档上传
  -> FastAPI 保存到 backend/uploaded_documents/
  -> 解析文本或生成二进制文档占位解析
  -> EnergyNodeParser 切分为 TextNode
  -> Metadata 标注
  -> Embedding
  -> VectorStoreIndex
  -> BM25 / Vector / Hybrid Retrieval
  -> RRF Fusion
  -> Rerank
  -> Context Package API
  -> 外部 LlamaIndex / LangChain / LangGraph 调用
```

## 前端页面

当前侧边栏保留 10 个核心入口：

- 项目总览 Dashboard
- 知识资产管理
- 文档入库管理
- Chunk 管理
- 元数据管理
- 向量化与索引状态
- RAG 检索测试
- API & SDK 接入中心
- RAGAS 评估中心
- 开源项目说明

已移除前端独立入口：

- LlamaIndex Runtime 设计
- RAG 问答演示
- 报告中心

说明：LlamaIndex 没有从项目里移除，只是不再作为单独前端页面展示。它现在作为后端 RAG Runtime 的核心对象模型和 API 语义保留。

## 文档入库能力

文档入库管理页支持：

- 前端直接选择本地文件上传
- 任意格式文件上传
- 选择知识域 `domain`
- 选择文档类型 `doc_type`
- 后端保存到 `backend/uploaded_documents/`
- 展示本地保存路径
- 手动删除单个文档及其关联 Chunk
- 一键跳转到 Chunk 管理进行切分、嵌入、索引和发布

当前解析策略：

- 文本类文件：`.txt`、`.md`、`.csv`、`.json`、代码文本等会读取内容用于切分
- 二进制文件：PDF / Word / Excel 等先保存本地并生成占位解析文本
- 后续可接入 `pymupdf`、`python-docx`、`pandas`、`unstructured` 和数据库持久化

## Chunk 管理能力

Chunk 管理页已经合并处理控制台：

- 选择文档
- 选择分段模式：`General`、`Parent-Child`、`Q&A`、`Semantic`
- 设置 `chunk_size`
- 设置 `chunk_overlap`
- 选择 Embedding 模型
- 选择检索策略：`vector`、`bm25`、`hybrid`、`hybrid + rerank`
- 设置 `vector_top_k`
- 设置 `final_top_k`
- 启用或关闭 Rerank
- 选择 Rerank 模型
- 一键“切分并发布为知识库 API”

Chunk 表格中的内容预览默认收缩，点击“展开 / 收起”查看完整文本，避免长文本撑开页面。

## RAG 检索测试

RAG 检索测试页支持：

- 输入检索问题
- 选择检索模式
- 选择 domain 过滤
- 选择 doc_type 过滤
- 设置 `vector_top_k`
- 设置 `final_top_k`
- 启用或关闭 Rerank
- 查看 `score`、`rerank_score`、metadata、source file 和 citation chain
- 内容预览默认收缩，可点击展开

## API 概览

核心 API：

- `GET /api/health`
- `GET /api/state`
- `GET /api/documents`
- `POST /api/documents/upload`
- `POST /api/documents/{document_id}/process`
- `DELETE /api/documents/{document_id}`
- `GET /api/chunks`
- `GET /api/metadata`
- `GET /api/vector-index`
- `GET /api/evaluations`
- `GET /api/retrieval`
- `POST /api/retrieval/search`
- `POST /api/context/build`
- `POST /api/chat`
- `GET /api/reports`

`POST /api/context/build` 用于生成外部 RAG 框架可消费的上下文包，返回 `context_text`、`sources` 和 LlamaIndex Runtime 对象说明。

## 目录结构

```text
Vernova-RAG/
├─ backend/
│  ├─ main.py
│  ├─ requirements.txt
│  └─ uploaded_documents/       # 本地上传文档目录，运行时生成
├─ frontend/
│  ├─ index.html
│  └─ src/
│     ├─ App.vue
│     ├─ api.js
│     ├─ main.js
│     ├─ mock.js
│     └─ styles.css
├─ package.json
├─ vite.config.ts
├─ WINDOWS_START.md
└─ README.md
```

## 校验命令

```powershell
python -m py_compile backend/main.py
npm run build -- --emptyOutDir=false
```

## 开源前注意

`.gitignore` 已忽略 `.env`、`node_modules/`、`dist/`、`__pycache__/`、日志和 npm 缓存。不要提交真实 API Key、Token、密码或内部接口信息。
