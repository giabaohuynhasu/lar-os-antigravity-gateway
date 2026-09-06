SOVEREIGN PRUNING DECREE
Về việc tinh giản MCP / Tools / Plugins / Skills của Antigravity

Đã đủ dữ liệu để phê chuẩn. Tôi sẽ không xử lý theo kiểu “có gì xóa nấy”, mà theo nguyên tắc phân quyền năng lực: Opera Neon đã là browser/research-execution layer; NotebookLM là grounding layer; Antigravity phải trở thành engineering + computational research layer.

Tổng inventory bạn gửi gồm khoảng 33 MCP tools và 117 skills được liệt kê. Đây là mức rất lớn nếu phần lớn được đưa vào context/skill discovery.

I. PHÁN QUYẾT TỔNG THỂ
Hệ thống	Quyết định
Git / local filesystem / Python / PowerShell	🟢 SOVEREIGN CORE — KEEP
Drive	🟢 KEEP — canonical export bridge
Notebook/Jupyter	🟢 KEEP LAZY
Hugging Face	🟡 KEEP LAZY
Visualization	🟡 KEEP LAZY
data-agent-kit	🟡 LAZY / REDUCE
Gemini API docs	🟡 LAZY hoặc DISABLE
Vertex AI Search	🔴 DISABLE
Chrome DevTools plugin	🔴 DISABLE mặc định
Firebase	🔴 DISABLE
Flutter	🔴 DISABLE
Android CLI	🔴 DISABLE
Gemini API skills	🟡 DISABLE trừ khi project thực sự gọi Gemini API
Google Maps	🔴 REMOVE/DISABLE
Modern Web Guidance	🔴 DISABLE
Science 37 skills	🔴 DISABLE toàn bộ
Standalone skills	🟡 chọn lọc
google-antigravity-sdk	🟢 KEEP
neon / neon-ai-gateway	🔴 DISABLE nếu Neon đã do CDP điều khiển bên ngoài
neon-postgres	🟡 KEEP LAZY nếu project dùng Neon DB
schema-mapping	🟢 KEEP
skill-repair	🟢 KEEP
agy-customizations	🟢 KEEP
antigravity-guide	🟢 KEEP LAZY
humanize-text	🔴 DISABLE
II. LUẬT CHỦ QUYỀN MỚI

Tôi ban hành 5 nguyên tắc.

LAW A — Opera Neon owns the browser

Antigravity không cần trở thành một browser agent thứ hai.

Opera Neon đã có:

CDP :9224 → tabs → NotebookLM → AI Studio → Claude → Perplexity → Manus → Grok → DeepSeek

Vì vậy mọi capability chủ yếu nhằm:

click web

inspect DOM

debug webpage

accessibility browser inspection

performance profiling

browser interaction

được coi là Browser-overlap (B).

Không cần hai bộ não tranh nhau điều khiển cùng một browser.

LAW B — NotebookLM owns corpus grounding

Antigravity không cần xây thêm một “mini-NotebookLM”.

NotebookLM hiện đang giữ:

ERI corpus

ALRP corpus

Master Context

source citations

source-grounded synthesis

Vì vậy Antigravity chỉ cần nhận canonical exports.

Kiến trúc nên là:

PRIMARY SOURCES
      ↓
Obsidian / Git
      ↓
Validation + hashing
      ↓
CANONICAL EXPORT
      ↓
Google Drive
      ↓
NotebookLM
      ↓
Research interpretation
      ↓
Antigravity
      ↓
Code / simulation / validation

NotebookLM = epistemic grounding.

Antigravity = computational execution.

III. MCP SERVERS — PHÁN QUYẾT CHI TIẾT
1. data-agent-kit
🟡 LAZY / REDUCE

Tools:

get_active_editor_context

get_active_gcp_connection

list_resource_templates

read_resource

Classification: K / D tùy task.

Nó không trực tiếp tạo ra ERI hoặc ALRP knowledge.

Nhưng có giá trị nếu Antigravity cần:

inspect environment

GCP resource context

data infrastructure

Không cần eager.

Decree

LAZY ONLY.

Không cho nó trở thành một context source thường trực.

2. drive
🟢 KEEP — STRATEGIC

Đây là một trong những MCP nên giữ.

Tools:

copy

create

download

metadata

permissions

recent files

read

search

Lý do rất rõ:

Git
 ↓
validation
 ↓
canonical_export
 ↓
Drive
 ↓
NotebookLM

Drive ở đây không phải “research brain”.

Nó là transport/release layer.

Decree

KEEP. LAZY TOOLS.

3. gemini-api-docs
🟡 LAZY / POSSIBLY DISABLE

Chỉ có:

search docs

get docs

Nếu Antigravity không trực tiếp xây Gemini API integration, đây là capability không cần thường trực.

Bạn đã có Google AI Studio trong Opera Neon.

Nhưng cần phân biệt:

AI Studio ≠ Gemini API documentation.

Nếu Worker 1/3 đang phát triển Gemini integration, giữ lazy.

Nếu không:

DISABLE.

4. huggingface
🟡 KEEP LAZY

Tools:

hf_whoami

hub_repo_search

hub_repo_details

hf_fs

Đây là capability khá sạch.

Không overlap trực tiếp với Neon.

Có thể hữu ích cho:

model

datasets

research artifacts

benchmark

reproducibility

Nhưng ERI/ALRP hiện không phụ thuộc Hugging Face.

Decree

KEEP LAZY.

Không eager.

5. notebooks
🟢 KEEP LAZY

Đây là MCP tôi không khuyến nghị xóa.

ALRP có:

simulation

residual analysis

bootstrap

sensitivity analysis

mathematical models

Notebook rất phù hợp cho computational research.

Nhưng Notebook MCP này và NotebookLM không phải cùng một thứ:

NotebookLM
= epistemic corpus / grounding

Jupyter notebook
= computational laboratory

Hai cái này không conflict.

Decree

KEEP — LAZY.

6. vertex-ai-search
🔴 DISABLE

Tools:

search

conversational_search

list_engines

Trong architecture hiện tại, đây là Research-overlap.

Bạn đã có:

NotebookLM

Perplexity

Claude

Gemini

web search

local corpus

Drive

Vertex AI Search không đóng vai trò bắt buộc trong ERI/ALRP.

Decree

DISABLE.

Không cần uninstall ngay. Disable trước để rollback được.

7. visualization
🟡 KEEP LAZY

render_chart

Cái này có giá trị cho ALRP.

Đặc biệt:

raw observations
      ↓
residuals
      ↓
model
      ↓
visualization

ALRP đã có Raw Residual Rule, nên visualization không được trở thành evidence thay thế raw data.

Nhưng chart vẫn rất hữu ích.

Decree

KEEP LAZY.

Nếu hiện tại nó EAGER, chuyển thành lazy nếu Antigravity cho phép.

IV. PLUGINS — PRUNING MASSIVE

Đây là phần sẽ đem lại hiệu quả lớn nhất.

1. Chrome DevTools Plugin

5 skills:

a11y-debugging

chrome-devtools

LCP

memory leak

troubleshooting

🔴 DISABLE

Đây là Browser-overlap rõ nhất.

Bạn đã có:

Opera Neon
   ↓
CDP :9224
   ↓
Chrome DevTools Protocol
   ↓
browser automation

Không cần Antigravity đồng thời duy trì một bộ browser-debugging knowledge stack khổng lồ.

Ngoại lệ

Khi đang debug một bug web cụ thể:

ENABLE TEMPORARILY.

Sau task:

DISABLE.

Decree

DEFAULT = DISABLED.

2. data-agent-kit-plugin

24 skills về:

BigQuery

GCP

Dataflow

Composer

dbt

Dataform

pipelines

ML

GCS...

🔴 DISABLE MOST

Đây là một massive context surface.

ERI/ALRP không phải GCP data-engineering project.

Có thể giữ:

bigquery-sql

managing-python-dependencies

notebook-guidance

gcloud-auth-verification

nếu thực sự dùng.

Còn lại:

DISABLE.

Đặc biệt:

Composer

Airflow

Dataflow

Data Transfer

lakehouse federation

BigQuery ML

graph

dbt

Dataform

không cần nằm trong agent context mặc định.

Decree

PRUNE TO TASK-ON-DEMAND.

3. Firebase — 11 skills
🔴 DISABLE ALL

ERI/ALRP không phải Firebase application.

Không có lý do để Antigravity phải mang:

Firebase Auth

Firestore

Crashlytics

Remote Config

App Hosting

Xcode setup

vào context.

DISABLE ALL.

4. Flutter — 23 skills
🔴 DISABLE ALL

Đây là một trong những nhóm dễ prune nhất.

Không liên quan đến:

ERI

ALRP

Python simulation

historical QCA

corpus

computational epistemology

DISABLE ALL.

5. Android CLI
🔴 DISABLE

Không liên quan.

DISABLE.

6. Gemini API — 4 skills

Gemini API development

Interactions API

Live API

Omni Flash

🟡 CONDITIONAL

Nếu Antigravity thực sự code against Gemini API:

KEEP LAZY.

Nếu AI Studio chỉ đang được dùng như external research interface:

DISABLE.

AI Studio session không đồng nghĩa Antigravity cần toàn bộ Gemini API engineering skill stack.

7. google-antigravity-sdk
🟢 KEEP

Đây là một trường hợp đặc biệt.

Đây là native platform capability, không phải domain distraction.

KEEP.

8. Google Maps Platform
🔴 DISABLE

Không liên quan.

DISABLE.

9. Modern Web Guidance
🔴 DISABLE

Nếu chỉ có:

chrome-extennce

thì càng không có lý do giữ trong research agent.

DISABLE.

10. SCIENCE — 37 SKILLS

Đây là đợt pruning lớn nhất.

Danh mục gồm:

AlphaFold

AlphaGenome

ChEMBL

ClinicalTrials

ClinVar

dbSNP

ENCODE

Ensembl

gnomAD

GTEx

UniProt

PubMed

OpenFDA

OpenTargets

PDB

PubChem

Reactome

STRING

UCSC

v.v.

🔴 DISABLE ALL BY DEFAULT

Điều này không có nghĩa khoa học sự sống không liên quan tới longevity research.

Nó có nghĩa:

Antigravity hiện tại không cần 37 database connectors nằm trong active agent surface để thực hiện ERI + ALRP.

Nếu sau này có một research question thực sự yêu cầu:

“Hãy query PubMed/ClinVar/UniProt...”

thì bật đúng skill đó trong đúng session.

Decree
science/*
    DEFAULT = DISABLED
    ACTIVATION = TASK-SPECIFIC

Đây chính xác là kiểu capability-on-demand mà hệ thống cần.

V. STANDALONE SKILLS
agy-customizations
🟢 KEEP

Infrastructure/meta configuration.

antigravity-guide
🟢 KEEP LAZY

Useful for operating the platform itself.

neon
🔴 DISABLE

Opera Neon hiện đã là external browser execution layer.

Không cần Antigravity thêm một abstraction layer cho Neon nếu CDP đang hoạt động ổn định.

neon-ai-gateway
🔴 DISABLE

Cùng lý do.

Opera Neon đã có các Web LLM sessions.

Không cần thêm gateway abstraction trừ khi có một workflow thực sự cần nó.

neon-postgres
🟡 KEEP LAZY

Đây là ngoại lệ quan trọng.

Nếu infrastructure của bạn thực sự dùng Neon PostgreSQL cho:

research database

experiment registry

provenance

benchmark metadata

simulation results

thì giữ.

Nếu không dùng:

DISABLE.

Nó không overlap với Opera Neon browser; Neon browser ≠ Neon Postgres.

schema-mapping
🟢 KEEP

Rất phù hợp architecture hiện tại.

Đặc biệt:

source schema
      ↓
canonical schema
      ↓
ERI / ALRP schema
      ↓
dataset

Giữ.

skill-repair
🟢 KEEP

Meta-infrastructure.

Một hệ thống đã có nhiều skill thì capability repair rất hữu ích.

humanize-text
🔴 DISABLE

Không phải strategic capability.

Không cần agent context cho ERI/ALRP.

VI. BẢNG FINAL DECREE
🟢 KEEP
google-antigravity-sdk
drive
notebooks
schema-mapping
skill-repair
agy-customizations
🟢 KEEP — LAZY
huggingface
data-agent-kit
visualization
antigravity-guide
neon-postgres       [nếu thực sự dùng]
gemini-api-docs     [nếu phát triển Gemini API]
gemini-api skills   [nếu phát triển Gemini API]
🟡 TASK-ON-DEMAND
science/*
GCP/data-agent skills
Chrome DevTools
Gemini API

Tức là không load vào strategic context, nhưng không cần xóa khỏi máy.

🔴 DISABLE
vertex-ai-search
chrome-devtools-plugin
firebase/*
flutter/*
android-cli
google-maps-platform
modern-web-guidance
neon
neon-ai-gateway
humanize-text
🔴 REMOVE

Tôi chưa ra lệnh hard-delete bất kỳ package nào ở phase 1.

Đây là chủ ý.

DISABLE trước → observe → validate → REMOVE sau.

VII. KIẾN TRÚC SAU KHI SLIMMING

Đây mới là phần quan trọng nhất.

Antigravity nên trở thành:

                    ┌──────────────────────┐
                    │      ANTIGRAVITY     │
                    │   ENGINEERING HQ     │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
         ERI ENGINE       ALRP ENGINE       ERI-X ENGINE
              │                │                │
              └────────────────┼────────────────┘
                               │
                     Python / NumPy / SciPy
                     Pandas / simulations
                     tests / CI / Git
                               │
                               ▼
                        CANONICAL DATA
                               │
                         SHA256 / diff
                               │
                               ▼
                            Google Drive
                               │
                               ▼
                          NotebookLM
                               │
                     ┌─────────┼─────────┐
                     ▼         ▼         ▼
                    ERI       ALRP     MASTER
                   Notebook  Notebook  Context

Trong khi đó:

                   OPERA NEON
                       │
              CDP :9224 / browser
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
   NotebookLM       AI Studio        Claude
       │               │                │
   Perplexity        Grok            Manus
                       │
                    DeepSeek

Hai hệ thống không cạnh tranh nhau.

VIII. QUAN TRỌNG: ĐỪNG PRUNE NOTEBOOKS

Có một điểm tôi muốn nhấn mạnh.

Nhìn inventory rất dễ nghĩ:

“NotebookLM đã có rồi → notebooks MCP là duplicate.”

Không.

Hai lớp khác nhau:

NotebookLM

Knowledge retrieval / source-grounded reasoning

Jupyter notebooks

Computational experimentation

ALRP đặc biệt cần:

raw data
↓
Python
↓
residuals
↓
bootstrap
↓
simulation
↓
chart
↓
reproducible notebook

Cho nên:

NotebookLM và Jupyter Notebook phải cùng tồn tại.

Chỉ là chúng không được phép trở thành hai “source of truth”.

IX. TƯƠNG TỰ VỚI CHROME DEVTOOLS

Opera Neon có CDP nên:

Neon = Browser Sovereign

Nhưng CDP và DevTools skill không hoàn toàn giống nhau.

Do đó tôi không ra lệnh uninstall Chrome DevTools.

Tôi ra:

DEFAULT DISABLED / EMERGENCY TOOLING

Khi Antigravity cần debug một website cụ thể:

ENABLE
↓
debug
↓
collect evidence
↓
disable

Như một specialized surgical instrument, không phải organ thường trực.

X. TOKEN BLOAT — ĐÂY MỚI LÀ TARGET

Mục tiêu không phải:

“Antigravity có ít skill nhất.”

Mà là:

Antigravity có ít skill không liên quan nhất trong active reasoning surface.

Ví dụ một agent đang xử lý:

“Kiểm tra 6 negative residual liên tiếp của ALRP”

thì context lý tưởng chỉ cần:

ALRP ontology
raw data
residual rules
statistical methods
Python
visualization
provenance
Git

Nó không cần biết:

Flutter widget testing
Firebase Auth
Android CLI
AlphaFold
ClinVar
Google Maps
Airflow
BigQuery graph
Chrome LCP

Đây là nơi pruning có thể tạo ra khác biệt rất lớn về signal-to-noise ratio, ngay cả khi không phải toàn bộ skill metadata đều được nhúng vào mỗi prompt.

XI. DELEGATION MATRIX CUỐI CÙNG
Capability	Chủ quyền
Browser automation	Opera Neon / CDP
Web LLM sessions	Opera Neon
Source-grounded research	NotebookLM
Corpus	Obsidian + Git
Canonical data	Git repository
Validation	CI / Antigravity
Numerical computation	Python / NumPy / SciPy
Simulation	ALRP Engine
Institutional coding	ERI Engine
Adversarial testing	Worker 4
Performance optimization	Worker 5
Engineering integration	Worker 1
Literature extraction	Worker 2
Infrastructure	Worker 3
Visualization	Antigravity, lazy
Cloud transport	Drive
Database	Neon Postgres, only if actually used
XII. LỆNH THI HÀNH CHO ANTIGRAVITY

PHASE 1 — SAFE PRUNING

1. Export current MCP/plugin/skill manifest.
2. Snapshot configuration.
3. Disable, do not delete, all RED items.
4. Convert EAGER non-core tools to LAZY where possible.
5. Preserve Drive, notebooks, HF, visualization.
6. Preserve google-antigravity-sdk.
7. Preserve schema/provenance/repair infrastructure.
8. Do not modify ERI-H canonical data.
9. Do not modify ALRP raw data.
10. Run full ERI + ALRP test suite.
11. Compare agent behavior before/after pruning.
12. Record token/context footprint.
13. Produce pruning diff.
14. Only after validation consider permanent removal.
Và một rule mới:

Không được để Antigravity tự tiện “clean up” MCP/skills bằng cách xóa package trực tiếp.

Mọi removal phải có:

OLD
NEW
REASON
DEPENDENCIES
IMPACT
ROLLBACK
TEST RESULT
TIMESTAMP

Cùng một triết lý với ERI Locked Baseline và ALRP Raw Residual Rule.

🏛️ PHÁN QUYẾT CUỐI

Tôi PHÊ CHUẨN việc slimming.

Nhưng architecture cuối cùng không phải là:

“Antigravity càng ít tool càng tốt.”

Mà là:

Antigravity chỉ giữ những capability thuộc về vai trò của chính nó.

Opera Neon = sensory/browser apparatus.
NotebookLM = epistemic/corpus apparatus.
Obsidian + Git = institutional memory + source of truth.
Antigravity = computational/engineering apparatus.

Và bên trong Antigravity:

ERI + ALRP + ERI-X + provenance + computation + testing = core.

Mọi thứ khác trở thành on-demand capability, không được phép chen vào chiến tuyến chính.

Đây là cấu hình tôi sẽ dùng làm baseline architecture cho phase pruning.