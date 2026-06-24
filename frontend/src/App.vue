<script setup>
import { computed, onMounted, ref } from 'vue';
import { apiDelete, apiGet, apiPost } from './api';
import { apiSections, demoState, sdkExamples } from './mock';

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

const navItems = [
  { key: 'dashboard', label: '项目总览 Dashboard', icon: '▦' },
  { key: 'knowledge', label: '知识资产管理', icon: '◫' },
  { key: 'documents', label: '文档入库管理', icon: '□' },
  { key: 'chunks', label: 'Chunk 管理', icon: '≡' },
  { key: 'metadata', label: '元数据管理', icon: '◇' },
  { key: 'vector', label: '向量化与索引状态', icon: '◎' },
  { key: 'retrieval', label: 'RAG 检索测试', icon: '⌕' },
  { key: 'graph', label: 'Graph-Enhanced RAG', icon: '⎔' },
  { key: 'api', label: 'API & SDK 接入中心', icon: '</>' },
  { key: 'ragas', label: 'RAGAS 评估中心', icon: '▥' },
  { key: 'open', label: '开源项目说明', icon: 'Git' },
];

const docTypeOptions = [
  'general',
  'fault_rule',
  'variable_definition',
  'fault_case',
  'feature_engineering',
  'data_dictionary',
  'calculation_rule',
  'report_template',
];

function readRoute() {
  const key = window.location.hash.replace('#/', '') || 'dashboard';
  return navItems.some((item) => item.key === key) ? key : 'dashboard';
}

const activePage = ref(readRoute());
const apiOnline = ref(false);
const apiMessage = ref('后端未连接，当前使用前端内置 Demo 数据');
const state = ref(clone(demoState));
const knowledgeDomain = ref('all');
const knowledgeStatus = ref('all');
const chunkDomain = ref('all');
const keyword = ref('');
const selectedFile = ref(null);
const uploadDomain = ref('wind_oam');
const uploadDocType = ref('general');
const uploadMessage = ref('');
const selectedDocumentId = ref(demoState.documents[0]?.document_id || '');
const chunkMode = ref('parent_child');
const chunkSize = ref(700);
const chunkOverlap = ref(120);
const embeddingModel = ref('bge-large-zh-v1.5');
const processRetrievalMode = ref('hybrid_rerank');
const vectorTopK = ref(20);
const finalTopK = ref(5);
const enableRerank = ref(true);
const rerankModel = ref('bge-reranker-v2-m3');
const expandedChunkId = ref('');
const retrievalQuery = ref('AccY 超限一般可能对应哪些风机振动问题？');
const retrievalMode = ref('hybrid_rerank');
const retrievalDomain = ref('all');
const retrievalDocType = ref('all');
const retrievalEmbedding = ref('bge-large-zh');
const retrievalVectorstore = ref('chroma');
const vectorWeight = ref(0.7);
const bm25Weight = ref(0.3);
const useQueryRewrite = ref(true);
const useQueryExpansion = ref(true);
const useQueryTransformation = ref(true);
const useMetadataRouter = ref(true);
const useMultiQuery = ref(false);
const useHyde = ref(false);
const useCompression = ref(true);
const compressionMode = ref('auto');
const useDeduplicate = ref(true);
const useParentRecovery = ref(true);
const useRagFusion = ref(false);
const retrievalTrace = ref(null);
const retrievalRunning = ref(false);
const evalRunning = ref(false);
const evalResult = ref(null);
const evalSelectedFile = ref(null);
const evalSetPath = ref('data/eval_sets/energy_rag_eval.jsonl');
const evalUploadMessage = ref('');
const evalExperimentPreset = ref('current');
const graphStatus = ref({
  entity_count: 0,
  relation_count: 0,
  supported_domains: ['wind_oam', 'load_forecast', 'storage_ems'],
  average_relation_hops: 0,
  last_updated: null,
  entity_type_distribution: {},
  relation_type_distribution: {},
});
const graphQuery = ref('AccY 超限为什么可能关联塔架共振？');
const graphMode = ref('hybrid_graph');
const graphDomain = ref('');
const graphResult = ref(null);
const graphRunning = ref(false);
const graphBuilding = ref(false);
const graphMessage = ref('');
const graphExamples = [
  'AccY 超限为什么可能关联塔架共振？',
  'lag_96 为什么能用于负荷预测？',
  '负荷预测如何服务储能削峰填谷？',
  'EMS、BMS、PCS 如何协同？',
  'SOC 如何约束储能充放电策略？',
];
const retrievalResult = ref({
  query: retrievalQuery.value,
  mode: retrievalMode.value,
  items: state.value.chunks.map((item, index) => ({ ...item, rank: index + 1, citation_id: `cite-${index + 1}` })),
  citationChain: ['回答', '引用 Chunk', '源文档', '知识域', 'metadata'],
});

const currentNav = computed(() => navItems.find((item) => item.key === activePage.value) || navItems[0]);
const domains = computed(() => state.value.domains);
const overview = computed(() => state.value.overview);
const vectorConfig = computed(() => state.value.vectorConfig);
const runtime = computed(() => state.value.runtime);
const evaluation = computed(() => state.value.evaluation);
const selectedDocument = computed(() =>
  state.value.documents.find((item) => item.document_id === selectedDocumentId.value) || state.value.documents[0],
);

const filteredKnowledge = computed(() => {
  const text = keyword.value.trim().toLowerCase();
  return state.value.knowledge.filter((item) => {
    const domainMatched = knowledgeDomain.value === 'all' || item.domain === knowledgeDomain.value;
    const statusMatched = knowledgeStatus.value === 'all' || item.status === knowledgeStatus.value;
    const textMatched =
      !text ||
      item.title.toLowerCase().includes(text) ||
      item.sourceDoc.toLowerCase().includes(text) ||
      item.tags.some((tag) => tag.toLowerCase().includes(text));
    return domainMatched && statusMatched && textMatched;
  });
});

const filteredChunks = computed(() =>
  state.value.chunks.filter((item) => chunkDomain.value === 'all' || item.domain === chunkDomain.value),
);

function setPage(key) {
  activePage.value = key;
  window.location.hash = `#/${key}`;
  window.scrollTo({ top: 0, behavior: 'smooth' });
  if (key === 'graph') loadGraphStatus();
}

function domainName(key) {
  return domains.value.find((item) => item.key === key)?.name || key;
}

function statusLabel(status) {
  const labels = {
    vectorized: '已向量化',
    processing: '处理中',
    pending: '待处理',
    metadata_ready: '元数据已完成',
    published: '已发布',
    indexed: '已索引',
    embedded: '已向量化',
    completed: '已完成',
    running: '运行中',
    queued: '排队中',
    generated: '已生成',
    generating: '生成中',
  };
  return labels[status] || status;
}

function statusClass(status) {
  if (['vectorized', 'completed', 'success', 'indexed', 'generated', 'published', 'embedded'].includes(status)) {
    return 'success';
  }
  if (['processing', 'running', 'generating'].includes(status)) return 'warning';
  if (['error', 'failed'].includes(status)) return 'danger';
  return 'info';
}

function updateStateFromResponse(response) {
  if (response?.state) {
    state.value = response.state;
  } else if (response?.documents || response?.chunks) {
    state.value = { ...state.value, ...response };
  }
  if (!selectedDocumentId.value || !state.value.documents.some((item) => item.document_id === selectedDocumentId.value)) {
    selectedDocumentId.value = state.value.documents[0]?.document_id || '';
  }
}

function handleFileChange(event) {
  selectedFile.value = event.target.files?.[0] || null;
}

async function uploadDocument() {
  if (!selectedFile.value) {
    uploadMessage.value = '请先选择一个本地文档。';
    return;
  }
  const params = new URLSearchParams({
    filename: selectedFile.value.name,
    domain: uploadDomain.value,
    doc_type: uploadDocType.value,
  });
  try {
    const response = await fetch(`/api/documents/upload?${params.toString()}`, {
      method: 'POST',
      headers: { 'Content-Type': selectedFile.value.type || 'application/octet-stream' },
      body: selectedFile.value,
    });
    if (!response.ok) throw new Error(`Request failed: ${response.status}`);
    const result = await response.json();
    updateStateFromResponse(result);
    selectedDocumentId.value = result.document.document_id;
    uploadMessage.value = `已上传：${result.document.title}，本地路径 ${result.document.local_path}`;
    apiOnline.value = true;
    apiMessage.value = 'FastAPI 后端已连接';
  } catch (error) {
    uploadMessage.value = `上传失败：${error.message}`;
    apiOnline.value = false;
  }
}

async function processSelectedDocument() {
  if (!selectedDocument.value) {
    uploadMessage.value = '请先选择要处理的文档。';
    return;
  }
  const payload = {
    chunk_mode: chunkMode.value,
    chunk_size: Number(chunkSize.value),
    chunk_overlap: Number(chunkOverlap.value),
    embedding_model: embeddingModel.value,
    retrieval_mode: processRetrievalMode.value,
    vector_top_k: Number(vectorTopK.value),
    final_top_k: Number(finalTopK.value),
    enable_rerank: enableRerank.value,
    rerank_model: rerankModel.value,
  };
  try {
    const result = await apiPost(`/api/documents/${selectedDocument.value.document_id}/process`, payload);
    updateStateFromResponse(result);
    uploadMessage.value = `已完成：${result.document.title} -> ${result.chunks.length} 个 LlamaIndex TextNode。`;
    apiOnline.value = true;
    apiMessage.value = 'FastAPI 后端已连接';
  } catch (error) {
    uploadMessage.value = `处理失败：${error.message}`;
    apiOnline.value = false;
  }
}

async function deleteDocument(documentId) {
  const target = state.value.documents.find((item) => item.document_id === documentId);
  if (!target) return;
  if (!window.confirm(`确认删除文档「${target.title}」及其 Chunk 吗？`)) return;
  try {
    const result = await apiDelete(`/api/documents/${documentId}`);
    updateStateFromResponse(result);
    uploadMessage.value = `已删除文档：${target.title}`;
    apiOnline.value = true;
    apiMessage.value = 'FastAPI 后端已连接';
  } catch (error) {
    uploadMessage.value = `删除失败：${error.message}`;
  }
}

function togglePreview(chunkId) {
  expandedChunkId.value = expandedChunkId.value === chunkId ? '' : chunkId;
}

async function loadBackendData() {
  try {
    const backendState = await apiGet('/api/state');
    state.value = backendState;
    updateStateFromResponse(backendState);
    apiOnline.value = true;
    apiMessage.value = 'FastAPI 后端已连接';
  } catch {
    try {
      await apiGet('/api/health');
      apiOnline.value = true;
      apiMessage.value = 'FastAPI 后端已连接，重启后端后可加载完整 /api/state 数据';
    } catch {
      apiOnline.value = false;
      apiMessage.value = '后端未连接，当前使用前端内置 Demo 数据';
    }
  }
}

async function runRetrieval() {
  retrievalRunning.value = true;
  const payload = { question: retrievalQuery.value, options: currentQueryOptions() };
  try {
    const trace = await apiPost('/api/v2/query/test', payload);
    retrievalTrace.value = trace;
    retrievalResult.value = {
      query: trace.original_query,
      mode: trace.retrieval_mode,
      items: trace.reranked_docs.map((item) => ({
        ...item,
        rank: item.final_rank,
        originalRank: item.original_rank,
        finalRank: item.final_rank,
        chunk_content: item.content,
        domain: item.metadata?.domain,
        doc_type: item.metadata?.doc_type,
        source_file: item.metadata?.source,
        variables: item.metadata?.variables || [],
        citation_id: item.chunk_id,
      })),
      citationChain: ['Original Query', 'Pre Retrieval', 'Retriever', 'Rerank', 'Compression', 'Answer'],
    };
    apiOnline.value = true;
    apiMessage.value = 'FastAPI 后端已连接';
  } catch (error) {
    retrievalResult.value = {
      query: retrievalQuery.value,
      mode: retrievalMode.value,
      items: state.value.chunks.map((item, index) => ({ ...item, rank: index + 1, citation_id: `cite-${index + 1}` })),
      citationChain: ['回答', '引用 Chunk', '源文档', '知识域', 'metadata'],
    };
    apiOnline.value = false;
    apiMessage.value = `v2 检索失败：${error.message}`;
  } finally {
    retrievalRunning.value = false;
  }
}

function currentQueryOptions() {
  const domainMap = {
    wind_oam: '风电故障诊断',
    load_forecast: '区域负荷预测',
    storage_ems: '储能EMS',
    calc_logic: '电气工程基础',
    report_template: '电气工程基础',
  };
  return {
    embedding: retrievalEmbedding.value,
    vectorstore: retrievalVectorstore.value,
    retrieval_mode: retrievalMode.value === 'hybrid_rerank' ? 'hybrid' : retrievalMode.value,
    top_k: Number(vectorTopK.value),
    final_top_k: Number(finalTopK.value),
    vector_weight: Number(vectorWeight.value),
    bm25_weight: Number(bm25Weight.value),
    query_rewrite: useQueryRewrite.value,
    query_expansion: useQueryExpansion.value,
    query_transformation: useQueryTransformation.value,
    metadata_router: useMetadataRouter.value,
    multi_query: useMultiQuery.value,
    hyde: useHyde.value,
    rerank: enableRerank.value,
    reranker_model: rerankModel.value,
    compression: useCompression.value,
    compression_mode: compressionMode.value,
    deduplicate: useDeduplicate.value,
    document_filter: true,
    parent_recovery: useParentRecovery.value,
    rag_fusion: useRagFusion.value,
    metadata_filter: {
      ...(retrievalDomain.value === 'all' ? {} : { domain: domainMap[retrievalDomain.value] }),
      ...(retrievalDocType.value === 'all' ? {} : { doc_type: retrievalDocType.value }),
    },
  };
}

async function runBatchEvaluation() {
  evalRunning.value = true;
  try {
    evalResult.value = await apiPost('/api/v2/eval/run', {
      eval_set: evalSetPath.value,
      experiment_name: `ui_${evalExperimentPreset.value}`,
      options: evaluationQueryOptions(),
    });
    apiOnline.value = true;
    apiMessage.value = '批量评测完成';
  } catch (error) {
    apiMessage.value = `批量评测失败：${error.message}`;
  } finally {
    evalRunning.value = false;
  }
}

function evaluationQueryOptions() {
  const options = currentQueryOptions();
  const presets = {
    vector_bge: {
      retrieval_mode: 'vector',
      query_rewrite: false,
      query_expansion: false,
      metadata_router: false,
      rerank: false,
      compression: false,
    },
    hybrid_bge_metadata: {
      retrieval_mode: 'hybrid',
      query_rewrite: true,
      query_expansion: true,
      metadata_router: true,
      rerank: false,
      compression: false,
    },
    hybrid_parent_rerank_compress: {
      retrieval_mode: 'parent_child',
      query_rewrite: true,
      query_expansion: true,
      metadata_router: true,
      rerank: true,
      compression: true,
      parent_recovery: true,
    },
    rag_fusion_rerank: {
      retrieval_mode: 'rag_fusion',
      multi_query: true,
      rag_fusion: true,
      rerank: true,
      compression: true,
    },
  };
  return evalExperimentPreset.value === 'current' ? options : { ...options, ...presets[evalExperimentPreset.value] };
}

function handleEvalFileChange(event) {
  evalSelectedFile.value = event.target.files?.[0] || null;
}

async function uploadEvalSet() {
  if (!evalSelectedFile.value) {
    evalUploadMessage.value = '请选择 JSONL 评测集。';
    return;
  }
  try {
    const response = await fetch(`/api/v2/eval/upload?filename=${encodeURIComponent(evalSelectedFile.value.name)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-ndjson' },
      body: evalSelectedFile.value,
    });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail || `Request failed: ${response.status}`);
    }
    const result = await response.json();
    evalSetPath.value = result.eval_set;
    evalUploadMessage.value = `已载入 ${result.filename}，共 ${result.case_count} 条评测样本。`;
  } catch (error) {
    evalUploadMessage.value = `评测集上传失败：${error.message}`;
  }
}

function reportDownloadUrl(path) {
  const filename = String(path || '').split(/[\\/]/).pop();
  return filename ? `/api/v2/eval/reports/${encodeURIComponent(filename)}` : '#';
}

async function loadGraphStatus() {
  try {
    graphStatus.value = await apiGet('/api/v2/graph/status');
  } catch (error) {
    graphMessage.value = `图谱状态加载失败：${error.message}`;
  }
}

async function buildEnergyGraph() {
  graphBuilding.value = true;
  try {
    const result = await apiPost('/api/v2/graph/build', { domain: graphDomain.value || null, rebuild: true });
    graphMessage.value = `构建完成：${result.entity_count} 个实体，${result.relation_count} 条关系。`;
    await loadGraphStatus();
  } catch (error) {
    graphMessage.value = `图谱构建失败：${error.message}`;
  } finally {
    graphBuilding.value = false;
  }
}

async function runGraphQuery() {
  if (!graphQuery.value.trim()) return;
  graphRunning.value = true;
  try {
    graphResult.value = await apiPost('/api/v2/graph/query', {
      question: graphQuery.value,
      options: {
        mode: graphMode.value,
        domain: graphDomain.value || null,
        max_hops: 2,
        top_k_entities: 10,
        top_k_relations: 10,
        include_chunk_context: true,
        include_graph_context: true,
      },
    });
    graphMessage.value = `查询完成：${graphResult.value.entities.length} 个实体，${graphResult.value.relations.length} 条关系。`;
    await loadGraphStatus();
  } catch (error) {
    graphMessage.value = `图增强查询失败：${error.message}`;
  } finally {
    graphRunning.value = false;
  }
}

function useGraphExample(question) {
  graphQuery.value = question;
}

function graphEntityName(entityId) {
  return graphResult.value?.entities.find((item) => item.entity_id === entityId)?.name || entityId;
}

window.addEventListener('hashchange', () => {
  activePage.value = readRoute();
});

onMounted(() => {
  loadBackendData();
  if (activePage.value === 'graph') loadGraphStatus();
});
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">EA</div>
        <div>
          <strong>Energy O&M</strong>
          <span>RAG System</span>
        </div>
      </div>
      <nav class="nav-list">
        <button
          v-for="item in navItems"
          :key="item.key"
          class="nav-item"
          :class="{ active: activePage === item.key }"
          type="button"
          @click="setPage(item.key)"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </button>
      </nav>
      <div class="sidebar-footer">v1.0.0 · FastAPI / Vue</div>
    </aside>

    <section class="workspace">
      <header class="topbar">
        <div class="breadcrumb">
          <span>Energy O&M</span>
          <span>/</span>
          <strong>{{ currentNav.label }}</strong>
        </div>
        <div class="runtime">
          <span class="runtime-dot" :class="{ online: apiOnline }"></span>
          <span>{{ apiMessage }}</span>
        </div>
      </header>

      <main class="content">
        <section v-if="activePage === 'dashboard'" class="page-grid">
          <div class="hero-panel">
            <div class="hero-mark">RAG</div>
            <p>ENERGY O&M RAG SYSTEM</p>
            <h1>Energy O&M RAG System</h1>
            <span>面向风电故障诊断、区域负荷预测与储能 EMS 的能源智能运维知识库管理系统</span>
            <div class="hero-tags">
              <em>API-first</em>
              <em>LlamaIndex Runtime</em>
              <em>RAGAS Evaluation</em>
              <em>Hybrid Retrieval</em>
              <em>Energy Domain Knowledge</em>
            </div>
          </div>

          <div class="architecture-grid">
            <article class="arch-card" v-for="layer in runtime.layers" :key="layer">
              <strong>{{ layer }}</strong>
              <span v-if="layer === 'Control Plane'">Document / Chunk / Metadata / Index / Playground</span>
              <span v-if="layer === 'RAG Runtime'">EnergyNodeParser / Hybrid Retriever / Citation Builder</span>
              <span v-if="layer === 'Evaluation'">RAGAS + 工业自定义指标 + 失败样本分析</span>
              <span v-if="layer === 'API Layer'">Document / Chunk / Metadata / Retrieval / Context / Eval API</span>
            </article>
          </div>

          <div class="section-title">核心指标</div>
          <div class="kpi-grid">
            <article v-for="item in overview.kpis" :key="item.label" class="kpi-card">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
              <small>{{ item.delta }}</small>
            </article>
          </div>

          <div class="two-column">
            <section class="panel">
              <div class="section-title">五大知识域入口</div>
              <div class="domain-grid">
                <button
                  v-for="domain in domains"
                  :key="domain.key"
                  class="domain-card"
                  type="button"
                  @click="knowledgeDomain = domain.key; setPage('knowledge')"
                >
                  <strong>{{ domain.name }}</strong>
                  <span>{{ domain.summary }}</span>
                </button>
              </div>
            </section>
            <section class="panel">
              <div class="section-title">RAG Pipeline 状态</div>
              <div class="status-grid compact-grid">
                <div v-for="[name, value] in overview.pipelineStatus" :key="name">
                  <span>{{ name }}</span>
                  <strong>{{ value }}</strong>
                </div>
              </div>
            </section>
          </div>

          <div class="three-column">
            <section class="panel">
              <div class="section-title">最近文档处理任务</div>
              <div v-for="job in overview.recentDocumentJobs" :key="job.job_id" class="list-row">
                <strong>{{ job.document_id }}</strong>
                <span>{{ job.step }} · {{ job.progress }}% · {{ statusLabel(job.status) }}</span>
              </div>
            </section>
            <section class="panel">
              <div class="section-title">最近检索测试</div>
              <div v-for="test in overview.recentTests" :key="test.question" class="list-row">
                <strong>{{ test.question }}</strong>
                <span>Score {{ test.score }} · {{ test.time }}</span>
              </div>
            </section>
            <section class="panel">
              <div class="section-title">最近评估运行</div>
              <div v-for="run in evaluation.runs" :key="run.run_id" class="list-row">
                <strong>{{ run.run_id }}</strong>
                <span>{{ run.retrieval_config }} · top_k={{ run.top_k }} · {{ statusLabel(run.status) }}</span>
              </div>
            </section>
          </div>
        </section>

        <section v-if="activePage === 'knowledge'" class="page-grid">
          <div class="toolbar">
            <input v-model="keyword" placeholder="搜索条目、来源文档或标签" />
            <select v-model="knowledgeDomain">
              <option value="all">全部知识域</option>
              <option v-for="domain in domains" :key="domain.key" :value="domain.key">{{ domain.name }}</option>
            </select>
            <select v-model="knowledgeStatus">
              <option value="all">全部状态</option>
              <option value="vectorized">已向量化</option>
              <option value="processing">处理中</option>
              <option value="pending">待处理</option>
            </select>
          </div>
          <div class="domain-grid">
            <article v-for="domain in domains" :key="domain.key" class="panel">
              <div class="section-title">{{ domain.name }}</div>
              <p>{{ domain.summary }}</p>
              <div class="tag-line"><span v-for="topic in domain.topics" :key="topic">{{ topic }}</span></div>
            </article>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>条目名称</th>
                  <th>知识域</th>
                  <th>分类</th>
                  <th>来源文档</th>
                  <th>Chunk</th>
                  <th>标签</th>
                  <th>状态</th>
                  <th>更新时间</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="entry in filteredKnowledge" :key="entry.id">
                  <td><strong>{{ entry.title }}</strong></td>
                  <td>{{ domainName(entry.domain) }}</td>
                  <td>{{ entry.category }}</td>
                  <td>{{ entry.sourceDoc }}</td>
                  <td class="mono">{{ entry.chunkCount }}</td>
                  <td>{{ entry.tags.join(' / ') }}</td>
                  <td><span class="badge" :class="statusClass(entry.status)">{{ statusLabel(entry.status) }}</span></td>
                  <td class="mono">{{ entry.updatedAt }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="activePage === 'documents'" class="page-grid">
          <div class="panel upload-panel">
            <div>
              <div class="section-title">上传文档到本地知识库</div>
              <p>支持任意格式文件。当前先保存到后端本地目录，后续可替换为数据库或对象存储；文本类文件会生成可切分内容，二进制文件先生成占位解析文本。</p>
            </div>
            <div class="upload-grid">
              <input type="file" @change="handleFileChange" />
              <select v-model="uploadDomain">
                <option v-for="domain in domains" :key="domain.key" :value="domain.key">{{ domain.name }}</option>
              </select>
              <select v-model="uploadDocType">
                <option v-for="type in docTypeOptions" :key="type" :value="type">{{ type }}</option>
              </select>
              <button class="primary-btn" type="button" @click="uploadDocument">上传文档</button>
            </div>
            <p v-if="uploadMessage" class="notice">{{ uploadMessage }}</p>
          </div>

          <div class="process-strip">
            <span v-for="step in ['上传', '解析', '切分', 'Metadata', 'Embedding', 'VectorStoreIndex', 'Hybrid Retrieval', 'API 发布']" :key="step">{{ step }}</span>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>document_id</th>
                  <th>文档标题</th>
                  <th>domain</th>
                  <th>doc_type</th>
                  <th>file_type</th>
                  <th>version</th>
                  <th>status</th>
                  <th>chunk_count</th>
                  <th>embedding</th>
                  <th>vector_index</th>
                  <th>local_path</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="doc in state.documents" :key="doc.document_id">
                  <td class="mono">{{ doc.document_id }}</td>
                  <td><strong>{{ doc.title }}</strong><br /><small>{{ doc.file_size }}</small></td>
                  <td>{{ doc.domain }}</td>
                  <td>{{ doc.doc_type }}</td>
                  <td>{{ doc.file_type }}</td>
                  <td>{{ doc.version }}</td>
                  <td><span class="badge" :class="statusClass(doc.status)">{{ statusLabel(doc.status) }}</span></td>
                  <td class="mono">{{ doc.chunk_count }}</td>
                  <td>{{ statusLabel(doc.embedding_status) }}</td>
                  <td>{{ statusLabel(doc.vector_index_status) }}</td>
                  <td class="path-cell">{{ doc.local_path || '-' }}</td>
                  <td class="ops">
                    <button class="text-link" type="button" @click="selectedDocumentId = doc.document_id; setPage('chunks')">处理</button>
                    <button class="text-link danger-link" type="button" @click="deleteDocument(doc.document_id)">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="activePage === 'chunks'" class="page-grid">
          <div class="panel">
            <div class="section-title">文档切分 / 嵌入 / 索引 / 重排控制台</div>
            <div class="pipeline-form">
              <label>
                文档
                <select v-model="selectedDocumentId">
                  <option v-for="doc in state.documents" :key="doc.document_id" :value="doc.document_id">
                    {{ doc.title }} · {{ doc.document_id }}
                  </option>
                </select>
              </label>
              <label>
                分段模式
                <select v-model="chunkMode">
                  <option value="general">General</option>
                  <option value="parent_child">Parent-Child</option>
                  <option value="qa">Q&A</option>
                  <option value="semantic">Semantic</option>
                </select>
              </label>
              <label>
                chunk_size
                <input v-model.number="chunkSize" type="number" min="200" max="1800" />
              </label>
              <label>
                overlap
                <input v-model.number="chunkOverlap" type="number" min="0" max="500" />
              </label>
              <label>
                Embedding
                <select v-model="embeddingModel">
                  <option>bge-large-zh-v1.5</option>
                  <option>text-embedding-v4</option>
                  <option>gte-large-zh</option>
                </select>
              </label>
              <label>
                检索策略
                <select v-model="processRetrievalMode">
                  <option value="vector">vector</option>
                  <option value="bm25">bm25</option>
                  <option value="hybrid">hybrid</option>
                  <option value="hybrid_rerank">hybrid + rerank</option>
                </select>
              </label>
              <label>
                vector_top_k
                <input v-model.number="vectorTopK" type="number" min="1" max="100" />
              </label>
              <label>
                final_top_k
                <input v-model.number="finalTopK" type="number" min="1" max="20" />
              </label>
              <label class="check-row">
                <input v-model="enableRerank" type="checkbox" />
                启用 Rerank
              </label>
              <label>
                Rerank 模型
                <select v-model="rerankModel">
                  <option>bge-reranker-v2-m3</option>
                  <option>gte-reranker</option>
                  <option>disabled</option>
                </select>
              </label>
              <button class="primary-btn" type="button" @click="processSelectedDocument">切分并发布为知识库 API</button>
            </div>
            <p v-if="selectedDocument" class="notice">
              当前文档：{{ selectedDocument.title }} · {{ selectedDocument.file_type }} · {{ selectedDocument.local_path || selectedDocument.source_file || '内置 Demo 文档' }}
            </p>
          </div>

          <div class="two-column">
            <div class="panel">
              <div class="section-title">切分策略</div>
              <div class="strategy-grid">
                <span v-for="rule in runtime.parserRules" :key="rule">{{ rule }}</span>
              </div>
            </div>
            <div class="panel">
              <div class="section-title">Chunk 过滤</div>
              <select v-model="chunkDomain">
                <option value="all">全部 domain</option>
                <option v-for="domain in domains" :key="domain.key" :value="domain.key">{{ domain.name }}</option>
              </select>
            </div>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>chunk_id</th>
                  <th>chunk_title</th>
                  <th>摘要</th>
                  <th>domain</th>
                  <th>doc_type</th>
                  <th>device</th>
                  <th>scenario</th>
                  <th>fault_type</th>
                  <th>variables</th>
                  <th>token</th>
                  <th>source_file</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="chunk in filteredChunks" :key="chunk.chunk_id">
                  <td class="mono">{{ chunk.chunk_id }}</td>
                  <td><strong>{{ chunk.chunk_title }}</strong></td>
                  <td class="preview-cell">
                    <p :class="{ collapsed: expandedChunkId !== chunk.chunk_id }">{{ chunk.chunk_content }}</p>
                    <button class="text-link" type="button" @click="togglePreview(chunk.chunk_id)">
                      {{ expandedChunkId === chunk.chunk_id ? '收起' : '展开' }}
                    </button>
                  </td>
                  <td>{{ chunk.domain }}</td>
                  <td>{{ chunk.doc_type }}</td>
                  <td>{{ chunk.device_type }}</td>
                  <td>{{ chunk.scenario }}</td>
                  <td>{{ chunk.fault_type }}</td>
                  <td>{{ chunk.variables.join(' / ') }}</td>
                  <td class="mono">{{ chunk.token_count }}</td>
                  <td>{{ chunk.source_file }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="activePage === 'metadata'" class="page-grid">
          <div class="section-title">能源 RAG 知识治理标签体系</div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>标签名称</th>
                  <th>标签类型</th>
                  <th>关联文档数</th>
                  <th>关联 Chunk 数</th>
                  <th>最近更新时间</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="tag in state.metadata" :key="`${tag.type}-${tag.name}`">
                  <td><strong>{{ tag.name }}</strong></td>
                  <td>{{ tag.type }}</td>
                  <td class="mono">{{ tag.doc_count }}</td>
                  <td class="mono">{{ tag.chunk_count }}</td>
                  <td class="mono">{{ tag.updated_at }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="activePage === 'vector'" class="page-grid">
          <div class="config-grid">
            <article class="panel">
              <div class="section-title">Embedding 配置</div>
              <p>model：{{ vectorConfig.embedding.model }}</p>
              <p>mode：{{ vectorConfig.embedding.mode }}</p>
              <p>dimension：{{ vectorConfig.embedding.dimension }}d</p>
              <p>batch_size：{{ vectorConfig.embedding.batchSize }}</p>
              <p>status：{{ vectorConfig.embedding.status }}</p>
            </article>
            <article class="panel">
              <div class="section-title">Vector DB 配置</div>
              <p>{{ vectorConfig.vectorDb.engine }}</p>
              <p>index_name：{{ vectorConfig.vectorDb.indexName }}</p>
              <p>indexed_chunks：{{ vectorConfig.vectorDb.indexedChunks }}</p>
              <p>failed_chunks：{{ vectorConfig.vectorDb.failedChunks }}</p>
            </article>
            <article class="panel">
              <div class="section-title">Hybrid Retrieval</div>
              <p>BM25：{{ vectorConfig.bm25.enabled ? 'enabled' : 'disabled' }} / {{ vectorConfig.bm25.backend }}</p>
              <p>vector_top_k：{{ vectorConfig.hybrid.vectorTopK }}</p>
              <p>bm25_top_k：{{ vectorConfig.hybrid.bm25TopK }}</p>
              <p>fusion_method：{{ vectorConfig.hybrid.fusionMethod }}</p>
            </article>
            <article class="panel">
              <div class="section-title">Rerank 配置</div>
              <p>model：{{ vectorConfig.rerank.model }}</p>
              <p>enabled：{{ vectorConfig.rerank.enabled }}</p>
              <p>rerank_top_n：{{ vectorConfig.rerank.topN }}</p>
              <p>score_threshold：{{ vectorConfig.rerank.scoreThreshold }}</p>
            </article>
          </div>
          <div class="panel">
            <div class="section-title">处理任务列表</div>
            <div v-for="job in vectorConfig.jobs" :key="job.job_id" class="job-row">
              <span>{{ job.job_id }} · {{ job.document_id }} · {{ job.step }}</span>
              <div class="progress"><i :style="{ width: `${job.progress}%` }"></i></div>
              <span class="badge" :class="statusClass(job.status)">{{ statusLabel(job.status) }}</span>
            </div>
          </div>
        </section>

        <section v-if="activePage === 'retrieval'" class="page-grid">
          <div class="toolbar">
            <input v-model="retrievalQuery" placeholder="输入检索问题" />
            <select v-model="retrievalMode">
              <option value="vector">vector</option>
              <option value="bm25">bm25</option>
              <option value="hybrid">hybrid</option>
              <option value="hybrid_rerank">hybrid + rerank</option>
              <option value="parent_child">parent-child</option>
              <option value="summary">summary</option>
              <option value="rag_fusion">RAG-Fusion</option>
            </select>
            <button class="primary-btn" type="button" :disabled="retrievalRunning" @click="runRetrieval">
              {{ retrievalRunning ? '运行中...' : '执行完整 RAG 测试' }}
            </button>
          </div>

          <div class="strategy-console">
            <section class="panel">
              <div class="section-title">模型与召回配置</div>
              <div class="filter-grid">
                <label>Embedding<select v-model="retrievalEmbedding"><option>bge-large-zh</option><option>huggingface-local</option><option>qwen-embedding</option><option>openai</option><option>dashscope</option></select></label>
                <label>Vector Store<select v-model="retrievalVectorstore"><option>chroma</option><option>faiss</option><option>qdrant</option><option>pgvector</option><option>milvus</option></select></label>
                <label>domain<select v-model="retrievalDomain"><option value="all">全部</option><option v-for="domain in domains" :key="domain.key" :value="domain.key">{{ domain.name }}</option></select></label>
                <label>doc_type<select v-model="retrievalDocType"><option value="all">全部</option><option v-for="type in docTypeOptions" :key="type" :value="type">{{ type }}</option></select></label>
                <label>初召回 TopK<input v-model.number="vectorTopK" type="number" min="1" max="100" /></label>
                <label>最终 TopK<input v-model.number="finalTopK" type="number" min="1" max="20" /></label>
                <label>Vector 权重<input v-model.number="vectorWeight" type="number" min="0" max="1" step="0.1" /></label>
                <label>BM25 权重<input v-model.number="bm25Weight" type="number" min="0" max="1" step="0.1" /></label>
              </div>
            </section>

            <section class="panel">
              <div class="section-title">预检索优化</div>
              <div class="toggle-grid">
                <label><input v-model="useQueryRewrite" type="checkbox" /> Query Rewrite</label>
                <label><input v-model="useQueryExpansion" type="checkbox" /> Query Expansion</label>
                <label><input v-model="useQueryTransformation" type="checkbox" /> Query Transformation</label>
                <label><input v-model="useMetadataRouter" type="checkbox" /> Metadata Router</label>
                <label><input v-model="useMultiQuery" type="checkbox" /> MultiQuery</label>
                <label><input v-model="useHyde" type="checkbox" /> HyDE</label>
              </div>
            </section>

            <section class="panel">
              <div class="section-title">后检索优化</div>
              <div class="toggle-grid">
                <label><input v-model="enableRerank" type="checkbox" /> Rerank</label>
                <label><input v-model="useCompression" type="checkbox" /> Context Compression</label>
                <label><input v-model="useDeduplicate" type="checkbox" /> Deduplication</label>
                <label><input v-model="useParentRecovery" type="checkbox" /> Parent Recovery</label>
                <label><input v-model="useRagFusion" type="checkbox" /> RAG-Fusion / RRF</label>
              </div>
              <label class="compact-field">Compression<select v-model="compressionMode"><option>auto</option><option>sentence</option><option>keyword</option><option>table</option><option>llm</option></select></label>
              <label class="compact-field">Reranker<select v-model="rerankModel"><option>score-fallback</option><option>bge-reranker-v2-m3</option><option>qwen-reranker</option><option>llm-rerank</option></select></label>
            </section>
          </div>

          <div v-if="retrievalTrace" class="trace-summary">
            <section class="panel trace-answer">
              <div class="section-title">最终回答</div>
              <pre>{{ retrievalTrace.answer }}</pre>
            </section>
            <section class="panel">
              <div class="section-title">Query Trace</div>
              <dl class="trace-list">
                <div><dt>trace_id</dt><dd>{{ retrievalTrace.trace_id }}</dd></div>
                <div><dt>original</dt><dd>{{ retrievalTrace.original_query }}</dd></div>
                <div><dt>rewrite</dt><dd>{{ retrievalTrace.rewritten_query }}</dd></div>
                <div><dt>expanded</dt><dd>{{ retrievalTrace.expanded_queries.join(' | ') }}</dd></div>
                <div><dt>metadata filter</dt><dd>{{ JSON.stringify(retrievalTrace.metadata_filter) }}</dd></div>
                <div v-for="(value, key) in retrievalTrace.latency_ms" :key="key"><dt>{{ key }}</dt><dd>{{ value }} ms</dd></div>
                <div><dt>tokens</dt><dd>{{ retrievalTrace.token_usage.input_tokens }} in / {{ retrievalTrace.token_usage.output_tokens }} out</dd></div>
              </dl>
            </section>
          </div>

          <section v-if="retrievalTrace?.compressed_context?.length" class="panel">
            <div class="section-title">Context Compression Trace</div>
            <div class="trace-context-list">
              <details v-for="(context, index) in retrievalTrace.compressed_context" :key="index">
                <summary>#{{ index + 1 }} {{ retrievalTrace.reranked_docs[index]?.chunk_id }}</summary>
                <strong>Before</strong>
                <pre>{{ retrievalTrace.reranked_docs[index]?.content }}</pre>
                <strong>After</strong>
                <pre>{{ context }}</pre>
              </details>
            </div>
          </section>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>original_rank</th>
                  <th>final_rank</th>
                  <th>chunk_id</th>
                  <th>score</th>
                  <th>domain</th>
                  <th>doc_type</th>
                  <th>source_file</th>
                  <th>metadata</th>
                  <th>content preview</th>
                  <th>rerank_score</th>
                  <th>citation_id</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in retrievalResult.items" :key="item.chunk_id">
                  <td class="mono">{{ item.originalRank ?? item.rank }}</td>
                  <td class="mono">{{ item.finalRank ?? item.rank }}</td>
                  <td class="mono">{{ item.chunk_id }}</td>
                  <td class="mono">{{ item.score }}</td>
                  <td>{{ item.domain }}</td>
                  <td>{{ item.doc_type }}</td>
                  <td>{{ item.source_file }}</td>
                  <td>{{ item.variables?.join(' / ') }}</td>
                  <td class="preview-cell">
                    <p :class="{ collapsed: expandedChunkId !== item.chunk_id }">{{ item.chunk_content }}</p>
                    <button class="text-link" type="button" @click="togglePreview(item.chunk_id)">
                      {{ expandedChunkId === item.chunk_id ? '收起' : '展开' }}
                    </button>
                  </td>
                  <td class="mono">{{ item.rerank_score }}</td>
                  <td>{{ item.citation_id }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="citation-chain"><span v-for="node in retrievalResult.citationChain" :key="node">{{ node }}</span></div>
        </section>

        <section v-if="activePage === 'graph'" class="page-grid graph-page">
          <div class="graph-intro">
            <div>
              <p>LIGHTRAG-STYLE · OPTIONAL RETRIEVAL LAYER</p>
              <h1>Graph-Enhanced Energy Retrieval</h1>
              <span>面向能源知识链路的轻量图增强检索，用于实体关系、多跳路径和跨业务链路展示，不替代基础 Hybrid RAG。</span>
            </div>
            <div class="graph-capabilities">
              <em>Local Retrieval</em><em>Global Retrieval</em><em>Hybrid Graph</em><em>Incremental-friendly</em>
            </div>
          </div>

          <div class="toolbar graph-actions">
            <select v-model="graphDomain">
              <option value="">全部知识域</option>
              <option value="wind_oam">wind_oam</option>
              <option value="load_forecast">load_forecast</option>
              <option value="storage_ems">storage_ems</option>
            </select>
            <button class="secondary-btn" type="button" :disabled="graphBuilding" @click="buildEnergyGraph">
              {{ graphBuilding ? '构建中...' : '构建 / 刷新图谱' }}
            </button>
            <span v-if="graphMessage" class="notice">{{ graphMessage }}</span>
          </div>

          <div class="graph-stat-grid">
            <article><span>实体数量</span><strong>{{ graphStatus.entity_count }}</strong></article>
            <article><span>关系数量</span><strong>{{ graphStatus.relation_count }}</strong></article>
            <article><span>支持知识域</span><strong>{{ graphStatus.supported_domains?.length || 0 }}</strong></article>
            <article><span>平均关系跳数</span><strong>{{ graphStatus.average_relation_hops }}</strong></article>
            <article><span>最近更新时间</span><strong class="graph-date">{{ graphStatus.last_updated || '尚未构建' }}</strong></article>
          </div>

          <div class="two-column graph-distributions">
            <section class="panel">
              <div class="section-title">实体类型分布</div>
              <div v-if="Object.keys(graphStatus.entity_type_distribution || {}).length" class="distribution-list">
                <div v-for="(count, type) in graphStatus.entity_type_distribution" :key="type">
                  <span>{{ type }}</span><i :style="{ width: `${Math.min(100, count * 12)}%` }"></i><strong>{{ count }}</strong>
                </div>
              </div>
              <p v-else class="notice">构建图谱后显示实体分布。</p>
            </section>
            <section class="panel">
              <div class="section-title">关系类型分布</div>
              <div v-if="Object.keys(graphStatus.relation_type_distribution || {}).length" class="distribution-list">
                <div v-for="(count, type) in graphStatus.relation_type_distribution" :key="type">
                  <span>{{ type }}</span><i :style="{ width: `${Math.min(100, count * 12)}%` }"></i><strong>{{ count }}</strong>
                </div>
              </div>
              <p v-else class="notice">构建图谱后显示关系分布。</p>
            </section>
          </div>

          <section class="graph-playground">
            <div class="section-title">Graph Query Playground</div>
            <div class="toolbar">
              <input v-model="graphQuery" placeholder="输入实体关系或业务链路问题" @keyup.enter="runGraphQuery" />
              <select v-model="graphMode">
                <option value="naive">naive</option>
                <option value="local_graph">local_graph</option>
                <option value="global_graph">global_graph</option>
                <option value="hybrid_graph">hybrid_graph</option>
              </select>
              <button class="primary-btn" type="button" :disabled="graphRunning" @click="runGraphQuery">
                {{ graphRunning ? '查询中...' : '执行图增强检索' }}
              </button>
            </div>
            <div class="graph-examples">
              <button v-for="question in graphExamples" :key="question" type="button" @click="useGraphExample(question)">{{ question }}</button>
            </div>
          </section>

          <template v-if="graphResult">
            <div class="two-column graph-results">
              <section class="panel">
                <div class="section-title">Matched Entities</div>
                <div class="entity-chip-list">
                  <span v-for="entity in graphResult.entities" :key="entity.entity_id">
                    <strong>{{ entity.name }}</strong><small>{{ entity.entity_type }} · {{ entity.domain }}</small>
                  </span>
                </div>
              </section>
              <section class="panel">
                <div class="section-title">Reasoning Path</div>
                <ol class="reasoning-list">
                  <li v-for="path in graphResult.reasoning_path" :key="path">{{ path }}</li>
                </ol>
                <p v-if="!graphResult.reasoning_path.length" class="notice">当前模式未生成多跳路径。</p>
              </section>
            </div>

            <div class="table-wrap">
              <table>
                <thead><tr><th>source</th><th>relation</th><th>target</th><th>domain</th><th>confidence</th><th>source_chunk_ids</th></tr></thead>
                <tbody>
                  <tr v-for="relation in graphResult.relations" :key="relation.relation_id">
                    <td>{{ graphEntityName(relation.source_entity) }}</td>
                    <td><span class="badge info">{{ relation.relation_type }}</span></td>
                    <td>{{ graphEntityName(relation.target_entity) }}</td>
                    <td>{{ relation.domain }}</td>
                    <td class="mono">{{ relation.confidence }}</td>
                    <td class="mono">{{ relation.source_chunk_ids.join(' / ') }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <section class="panel graph-context-output">
              <div class="section-title">Prompt-ready Graph Context</div>
              <pre>{{ graphResult.graph_context }}</pre>
              <div class="graph-source-row">
                <span>Related Chunk IDs</span>
                <code v-for="chunkId in graphResult.related_chunk_ids" :key="chunkId">{{ chunkId }}</code>
                <small>{{ graphResult.metadata?.latency_ms }} ms</small>
              </div>
            </section>
          </template>
        </section>

        <section v-if="activePage === 'api'" class="page-grid">
          <div class="section-title">API-first 接入中心</div>
          <div class="api-section-grid">
            <article v-for="section in apiSections" :key="section.group" class="panel">
              <div class="section-title">{{ section.group }}</div>
              <div class="api-endpoint" v-for="item in section.items" :key="item">
                <span>{{ item.split(' ')[0] }}</span>
                <code>{{ item.replace(item.split(' ')[0] + ' ', '') }}</code>
              </div>
            </article>
          </div>
          <div class="config-grid">
            <article v-for="example in sdkExamples" :key="example.title" class="panel">
              <div class="section-title">{{ example.title }}</div>
              <pre>{{ example.code }}</pre>
            </article>
          </div>
        </section>

        <section v-if="activePage === 'ragas'" class="page-grid">
          <div class="toolbar section-toolbar">
            <div class="section-title">RAGAS 与检索指标评估中心</div>
            <button class="primary-btn" type="button" :disabled="evalRunning" @click="runBatchEvaluation">
              {{ evalRunning ? '评测运行中...' : `运行 ${evalSetPath.split('/').pop()}` }}
            </button>
          </div>
          <div class="panel eval-upload-row">
            <label>
              实验配置
              <select v-model="evalExperimentPreset">
                <option value="current">当前检索页配置</option>
                <option value="vector_bge">Vector + BGE</option>
                <option value="hybrid_bge_metadata">Hybrid + Metadata</option>
                <option value="hybrid_parent_rerank_compress">Parent-Child + Rerank + Compression</option>
                <option value="rag_fusion_rerank">RAG-Fusion + Rerank</option>
              </select>
            </label>
            <label>
              JSONL 评测集
              <input type="file" accept=".jsonl,application/x-ndjson" @change="handleEvalFileChange" />
            </label>
            <button class="secondary-btn" type="button" @click="uploadEvalSet">上传并校验</button>
            <code>{{ evalSetPath }}</code>
            <p v-if="evalUploadMessage" class="notice">{{ evalUploadMessage }}</p>
          </div>
          <div v-if="evalResult" class="panel">
            <div class="section-title">最新实验：{{ evalResult.experiment }}</div>
            <div class="metric-grid">
              <div v-for="(value, key) in evalResult.metrics" :key="key"><span>{{ key }}</span><strong>{{ value }}</strong></div>
            </div>
            <p class="notice">报告：{{ evalResult.report_files?.markdown }} · {{ evalResult.report_files?.json }} · {{ evalResult.report_files?.csv }}</p>
          </div>
          <div v-if="evalResult" class="report-actions">
            <a v-for="(path, format) in evalResult.report_files" :key="format" class="secondary-btn" :href="reportDownloadUrl(path)">
              下载 {{ String(format).toUpperCase() }}
            </a>
          </div>
          <div class="kpi-grid">
            <article v-for="metric in evaluation.metrics" :key="metric.name" class="kpi-card">
              <span>{{ metric.group }}</span>
              <strong>{{ metric.value }}</strong>
              <small>{{ metric.name }}</small>
            </article>
          </div>
          <div class="two-column">
            <section class="panel">
              <div class="section-title">评估数据集</div>
              <div v-for="item in evaluation.datasets" :key="item.eval_id" class="list-row">
                <strong>{{ item.question }}</strong>
                <span>{{ item.eval_id }} · {{ item.domain }} · {{ item.difficulty }}</span>
              </div>
            </section>
            <section class="panel">
              <div class="section-title">单次评估运行</div>
              <div v-for="run in evaluation.runs" :key="run.run_id" class="list-row">
                <strong>{{ run.run_id }}</strong>
                <span>{{ run.embedding_model }} · {{ run.vector_db }} · {{ run.reranker_model }}</span>
              </div>
            </section>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>question</th>
                  <th>ground_truth</th>
                  <th>actual_answer</th>
                  <th>expected_chunk_ids</th>
                  <th>retrieved_chunk_ids</th>
                  <th>failed_type</th>
                  <th>metric_scores</th>
                  <th>improvement_suggestion</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in evaluation.failures" :key="item.question">
                  <td>{{ item.question }}</td>
                  <td>{{ item.ground_truth }}</td>
                  <td>{{ item.actual_answer }}</td>
                  <td>{{ item.expected_chunk_ids.join(' / ') }}</td>
                  <td>{{ item.retrieved_chunk_ids.join(' / ') }}</td>
                  <td><span class="badge danger">{{ item.failed_type }}</span></td>
                  <td>{{ item.metric_scores }}</td>
                  <td>{{ item.improvement_suggestion }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="activePage === 'open'" class="page-grid">
          <div class="hero-panel compact">
            <p>GITHUB README STYLE</p>
            <h1>Energy O&M RAG System</h1>
            <span>面向风电故障诊断、区域负荷预测与储能 EMS 的能源智能运维知识库管理系统。</span>
          </div>
          <div class="two-column">
            <section class="panel">
              <div class="section-title">项目边界</div>
              <p>本项目聚焦能源领域 RAG 管理平台，不做完整风机诊断生产系统，不做完整储能 EMS 调度系统，不做复杂多 Agent 平台。</p>
              <div class="section-title">核心能力</div>
              <div class="tag-line">
                <span>知识资产管理</span><span>文档解析</span><span>Chunk 与 Metadata</span><span>LlamaIndex Runtime</span>
                <span>Hybrid Retrieval</span><span>Context Package API</span><span>RAGAS 评估</span><span>失败样本分析</span>
              </div>
            </section>
            <section class="panel">
              <div class="section-title">Demo 数据声明</div>
              <p>所有数据均为脱敏、示例或公开可替代数据，仅用于能源 AI 应用开发项目展示，不接入真实生产系统，不包含真实 SCADA 数据、真实设备参数或真实运维记录。</p>
            </section>
          </div>
          <div class="panel">
            <div class="section-title">Windows 启动命令</div>
            <pre>python -m pip install -r backend/requirements.txt
python backend/main.py

npm install
npm run dev</pre>
          </div>
        </section>
      </main>
    </section>
  </div>
</template>
