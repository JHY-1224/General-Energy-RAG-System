# AGENTS.md - Energy O&M RAG Agent

本文件给后续代码助手使用，描述当前项目真实结构、核心逻辑和安全边界。修改本项目时以这里为准。

## 最高优先级安全规则

- 不要批量删除文件或目录。
- 不要执行 `Remove-Item -Recurse`、`rm -rf`、`git clean -fd`、`git reset --hard` 等破坏性命令。
- 如确实需要清理运行产物，只列出路径让用户手动删除，不要代为批量删除。
- 不要提交、推送、回滚代码，除非用户明确要求。
- 不要输出或提交 `.env` 中的敏感信息。
- 修改代码遵循最小改动原则，优先局部修改。
- 运行构建时优先使用 `npm run build -- --emptyOutDir=false`，避免构建前清空 `dist`。

## 当前项目定位

Energy O&M RAG Agent 是一个能源 RAG 知识库管理原型，用于开源展示和面试说明。

它不是生产风机诊断系统，也不是单纯聊天机器人，而是：

```text
RAG Control Plane + LlamaIndex 风格 RAG Runtime + FastAPI API Layer + Vue 管理界面
```

前端负责管理和展示：

- 知识资产
- 文档入库
- Chunk 切分与处理
- Metadata
- 向量化与索引
- RAG 检索测试
- API & SDK 接入
- RAGAS 评估
- 开源项目说明

后端负责核心 RAG 流程：

- 文档上传和本地保存
- 文本解析或占位解析
- LlamaIndex 风格 Document / TextNode 生成
- Metadata 标注
- Embedding 状态模拟
- VectorStoreIndex 状态模拟
- BM25 / Vector / Hybrid Retrieval
- RRF Fusion
- Rerank
- Context Package API

## 技术栈

- 后端：Python FastAPI
- 前端：Vue 3 + Vite
- 默认后端端口：`8000`
- 默认前端端口：`8080`
- 本地上传目录：`backend/uploaded_documents/`

## 启动方式

后端：

```powershell
cd "C:\Users\Administrator\Desktop\江翰宇\Vernova-RAG"
python -m pip install -r backend/requirements.txt
python backend/main.py
```

前端：

```powershell
cd "C:\Users\Administrator\Desktop\江翰宇\Vernova-RAG"
npm install
npm run dev
```

访问：

- 前端：`http://127.0.0.1:8080`
- 后端文档：`http://127.0.0.1:8000/docs`

## 当前前端导航

侧边栏只保留 10 个核心入口：

1. 项目总览 Dashboard
2. 知识资产管理
3. 文档入库管理
4. Chunk 管理
5. 元数据管理
6. 向量化与索引状态
7. RAG 检索测试
8. API & SDK 接入中心
9. RAGAS 评估中心
10. 开源项目说明

以下三个页面入口已按用户要求移除：

- LlamaIndex Runtime 设计
- RAG 问答演示
- 报告中心

注意：LlamaIndex 不是被删除，而是作为后端 RAG Runtime 的核心对象模型保留，不再单独做前端展示页面。

## 文档入库核心逻辑

文件：`backend/main.py`、`frontend/src/App.vue`

能力：

- 前端选择本地文件直接上传。
- 后端保存文件到 `backend/uploaded_documents/`。
- 支持任意格式上传。
- 文本类文件会读取内容用于切分。
- PDF / Word / Excel 等二进制文件先保存本地并生成占位解析文本。
- 每个上传文档生成 `document_id`。
- 前端可手动删除单个文档。
- 删除单个文档时，同时删除该文档关联 Chunk。
- 后续可把本地路径和文档元数据接数据库。

核心 API：

- `POST /api/documents/upload`
- `GET /api/documents`
- `POST /api/documents/{document_id}/process`
- `DELETE /api/documents/{document_id}`

## Chunk 管理核心逻辑

Chunk 管理页不是单纯表格，而是文档处理控制台。

用户可以：

- 选择文档
- 选择分段模式：`General`、`Parent-Child`、`Q&A`、`Semantic`
- 设置 `chunk_size`
- 设置 `chunk_overlap`
- 选择 Embedding 模型
- 选择检索策略
- 设置 `vector_top_k`
- 设置 `final_top_k`
- 启用或关闭 Rerank
- 选择 Rerank 模型
- 一键切分并发布为知识库 API

后端处理语义：

```text
Document
  -> EnergyNodeParser
  -> TextNode
  -> Metadata
  -> Embedding
  -> VectorStoreIndex
  -> Retriever / QueryEngine
```

Chunk 表格中的 `content preview` 默认收缩，点击展开 / 收起。

## 检索测试核心逻辑

RAG 检索测试页独立保留。

支持：

- query 输入
- retrieval mode：`vector`、`bm25`、`hybrid`、`hybrid_rerank`
- domain filter
- doc_type filter
- `vector_top_k`
- `final_top_k`
- rerank 开关
- 结果表格展示 score、rerank_score、metadata、source_file、citation_id
- content preview 默认收缩，可点击展开

核心 API：

- `GET /api/retrieval`
- `POST /api/retrieval/search`
- `POST /api/context/build`

## API & SDK 页面

API 页面只保留端点分组和 SDK 示例。

已移除多余的两栏：

- Context Package API 请求
- Context Package API 返回

Context 能力仍由后端 `POST /api/context/build` 提供。

## 后端核心 API 清单

- `GET /api/health`
- `GET /api/state`
- `GET /api/overview`
- `GET /api/knowledge`
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

其中 `POST /api/chat` 和 `GET /api/reports` 保留为后端接口能力，不再作为前端侧边栏入口。

## 目录结构

```text
Vernova-RAG/
├─ backend/
│  ├─ main.py
│  ├─ requirements.txt
│  └─ uploaded_documents/       # 运行时上传目录
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
├─ README.md
└─ AGENTS.md
```

## 非破坏性校验

```powershell
python -m py_compile backend/main.py
npm run build -- --emptyOutDir=false
```

## 后续可扩展方向

- 用 SQLite / PostgreSQL 保存文档元数据、Chunk、检索配置和评估结果。
- 用 `pymupdf` 解析 PDF。
- 用 `python-docx` 解析 Word。
- 用 `pandas` 解析 CSV / Excel。
- 接入真实 LlamaIndex 包和真实向量库。
- 将 `backend/uploaded_documents/` 替换为对象存储或数据库文件表。
