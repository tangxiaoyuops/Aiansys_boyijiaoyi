# 皇帝内经模块前后端优化方案 v1.0

最后更新：2026-01-10
适用范围：frontend (Vue 3 + Vite + TS + Element Plus)，server (FastAPI)，core/agents 与 core/tools（知识库/嵌入/LLM）

---

## 1. 概览
- **目标**：在不改变现有业务行为的前提下，提升皇帝内经模块的安全性、性能、可维护性与可观测性。
- **核心问题概述**：
  - 前端使用 `v-html` 渲染 LLM 文本，存在 XSS 风险。
  - 后端 `async` 端点中执行阻塞 I/O（LLM/Chroma），可能阻塞事件循环。
  - 向量库初始化延迟导致首请求耗时大；缺少启动预热。
  - `huangdi_vector_store.py` 存在默认 API Key 字面值（高风险）。
  - 诊断正则匹配精度低（未正确匹配多字词）。
  - 混合检索的分值量纲不统一（文本与向量分数不可比）。
  - 错误映射与前端提示不统一；缺少取消/限流；日志与可观测性可提升。

---

## 2. 现状与模块关系（简）
- 前端 `/huangdi` 页面包含三面板：
  - 知识查询：`HuangdiQueryPanel.vue` → `POST /api/huangdi/analyze`（query）
  - 诊断建议：`HuangdiDiagnosisPanel.vue` → 同接口（diagnosis）
  - 健康咨询：`HuangdiConsultationPanel.vue` → 同接口（consultation）
- 后端 `server/app.py`：`/api/huangdi/analyze` 分发到 `core/agents`：
  - `huangdi_query_node`、`huangdi_diagnosis_node`、`huangdi_consultation_node`
- 知识库：`core/tools/huangdi_knowledge_base.py`（文本结构化 + 向量检索）；
  - 结构化：`huangdi_text_processor.py`
  - 向量库：`huangdi_vector_store.py`（Chroma + Qwen Embeddings）
- LLM 客户端：`core/tools/llm_client.py`（OpenAI 兼容接口调用千问）。

---

## 3. Quick Wins（本周即可落地）
- **[安全] 前端 LLM 文本安全渲染**
  - 问题：`v-html` 与简易 `formatLLMText` 未做消毒，存在 XSS 风险。
  - 方案：
    - 方案A：新增 `components/LLMContent.vue`，内部用 DOMPurify 清理后再 `v-html`。新增依赖 `dompurify`。
    - 方案B（无新增依赖）：用现有 `markdown-it` 渲染为 HTML，并限制/过滤危险标签与属性（推荐搭配简易白名单）。
  - 验收：E2E 手工注入 `<script>`/`onerror` 无效；页面样式与换行/标题渲染正常。

- **[稳定] 后端避免阻塞事件循环**
  - 问题：`async def huangdi_analyze` 内部执行 LLM/Chroma（同步阻塞）。
  - 方案：
    - 方案A：改为同步 `def huangdi_analyze`，由 FastAPI 线程池处理阻塞 I/O。
    - 方案B：保留 `async`，将阻塞调用包裹进 `anyio.to_thread.run_sync(...)`。
  - 验收：并发 20 req，P95 延迟显著下降，无事件循环卡顿日志。

- **[安全] 移除默认 API Key 与完善环境变量**
  - 问题：`huangdi_vector_store.get_embeddings()` 中存在默认 `OPENAI_API_KEY` 字面值并打印尾号。
  - 方案：强制从环境变量读取，找不到则抛错；日志不再打印 Key。
  - 配置：新增 `.env.example`（见第 7 节）。

- **[性能] 知识库预热（应用启动）**
  - 方案：FastAPI `startup` 钩子里执行 `get_knowledge_base().ensure_initialized()`。
  - 验收：应用启动日志包含向量库/结构化数据统计；首请求响应时间显著降低。

- **[准确性] 改进症状提取正则**
  - 问题：当前正则只匹配单个汉字，未覆盖“头痛/发热”等多字词。
  - 方案：改为分组匹配：`(头痛|发热|恶寒|咳嗽|腹痛|腹泻|失眠|乏力|胸闷|心悸)`，并去重合并别名。
  - 验收：输入“头痛、发热、恶寒”能稳定提取三项；中文变体同样识别。

- **[相关性] 混合检索分值标准化**
  - 问题：文本结果人工分（1.0 - i*0.1），向量结果（1 - distance）量纲不统一。
  - 方案：
    - 将 textScore / vectorScore 分别做 min-max 标准化到 [0,1]；
    - 引入权重 `w_text`/`w_vector`（默认 0.4/0.6）；
    - 最终得分 `score = w_text*textScore + w_vector*vectorScore`，并统一排序。
  - 验收：相关章节排序更合理，前端显示的“相关性”波动减小。

- **[体验/流量] 请求取消与限流治理**
  - 前端：为三面板增加 `AbortController`，新请求触发时取消旧请求；按钮忙碌态与禁用逻辑保持。
  - 后端：可选接入 `slowapi` 做基础限流（如：IP/路径 30 req/min）。
  - 验收：快速频点不会堆积；后端 QPS 平稳，错误码可预期（429 时提示“稍后再试”）。

- **[可观测性] 日志与错误映射**
  - 方案：统一用 `logging`，为请求生成 `request_id`；LLM/Chroma 错误映射为明确的 HTTP 状态（如 502/504）。
  - 前端：axios 响应拦截器集中解析 `error.response?.data?.detail`，友好弹窗。

---

## 4. 中期改进（两周内）
- **SSE 流式化：`/api/huangdi/analyze/stream`**
  - 对齐已实现的股票/期货流式接口，输出 `start/progress/result/done`。
  - 前端展示过程反馈，显著降低长耗时超时概率与用户焦虑。

- **检索质量升级**
  - 文本检索：引入中文分词 + BM25（`rank_bm25`）替代纯包含匹配；
  - 向量重排：为 top-k 做 cross-encoder 轻量重排（`sentence-transformers`）。
  - Metadata 规范：Chroma `themes` 使用数组字段（若版本支持），where 过滤更自然。

- **响应结构增强**
  - 返回片段命中 offset/高亮信息与引用 ID，便于前端高亮与“查看原文”。
  - 新增只读接口：按章节标题获取全文（分页/分块返回）。

- **缓存与熔断**
  - LLM 结果与热门查询缓存（TTL）；LLM 失败自动降级为非 LLM 路径；重试与退避。

---

## 5. 具体改动包（可按 PR 拆分）
- **包A（安全/稳定小改）**
  - 前端：新增 `LLMContent` 组件保障安全渲染；axios 响应拦截与请求取消；`.env.example`（前端）。
  - 后端：去除默认 API Key；`startup` 预热；`huangdi_analyze` 非阻塞化；日志改为 `logging`；错误映射统一。

- **包B（检索质量）**
  - 诊断正则修复与测试；混合检索分值归一化；主题/书籍组合过滤逻辑完善。

- **包C（体验提升）**
  - `analyze` 流式接口 + 前端进度展示；“查看原文/复制导出”能力。

---

## 6. 落地步骤与验收标准
- 步骤
  - 1）提交包A → 冒烟测试（查询/诊断/咨询三路径）；
  - 2）提交包B → 相关性与关键词提取 A/B 对比；
  - 3）提交包C → 长文案/慢请求体验验证；
  - 4）预生产/生产发布，开启指标与日志观察（48 小时）。
- 验收（关键指标）
  - 首请求响应：降低 ≥30%；
  - 报错率：降低 ≥50%；
  - LLM/XSS 安全：攻防用例通过；
  - 检索满意度（人工评估 Top-3 相关性）：提升 ≥20%。

---

## 7. 环境变量与配置（建议 `.env.example`）
- 后端：
  - `OPENAI_API_KEY=`（必填）
  - `OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1`（千问兼容）
  - `QWEN_MODEL=qwen-plus`（可选）
  - `QWEN_EMBEDDING_MODEL=text-embedding-v2`（可选）
- 前端：
  - `VITE_API_BASE=http://localhost:8000`（或网关地址）
- 其他：
  - CORS 建议收紧到可信域；Nginx 建议开启 gzip 与 SSE 透传。

---

## 8. 风险与回滚
- 依赖风险：新增/升级依赖需锁定版本，先走测试环境；
- 兼容风险：改变日志与错误码映射前先与调用方确认；
- 回滚：按包A/B/C 分支发布，可独立回滚；保留构建产物与向量库旧快照。

---

## 9. 测试清单（节选）
- 功能：三面板正常收敛到预期结构字段（见接口契约）。
- 安全：XSS（标签、事件、svg、css 注入）阻断；敏感信息不落日志。
- 并发：并发 20/50/100 请求，P95/P99 时延稳定；
- 失败路径：LLM 超时/限流、Chroma 初始化失败、空结果、异常输入。

---

## 10. 接口契约（对齐现状）
- `POST /api/huangdi/analyze` 请求体：
  - `question: string`
  - `query_type?: 'query' | 'diagnosis' | 'consultation'`
  - `include_llm?: boolean`
  - `context?: { season?: string; age?: number; constitution?: string[] }`
- 响应体（按类型返回字段）：
  - query：`relevant_chapters[] { book, chapter_title, content, relevance_score, themes[] }`，`llm_explanation`，`total_results`
  - diagnosis：`symptom_keywords[]`，`relevant_theories[]`，`llm_analysis`，`disclaimer`
  - consultation：`season/age/constitution[]`，`relevant_theories[]`，`llm_suggestions`，`disclaimer`

---

## 11. 时间计划（建议）
- 周一-周二：包A（安全/稳定）开发与联调；
- 周三：包B（检索质量）实现与回归；
- 周四：包C（SSE）与前端进度 UI；
- 周五：预发观测与复盘，准备生产发布。

---

## 12. 后续展望
- 增加结构化知识图谱（概念-关系-章节）辅助重排与解释；
- 引入轻量 RAG Guardrails（提示词与输出约束）；
- 结合用户画像（合规前提）提升咨询建议个性化。

---

如需，我可以基于本文件先提交“包A（安全/稳定小改）”的最小改动 PR，以便你快速验证与上线。
