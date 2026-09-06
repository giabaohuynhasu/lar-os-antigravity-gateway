# SẮC LỆNH THỦ TƯỚNG CHATGPT: QUY TRÌNH NẠP TRI THỨC VÀO NOTEBOOKLM & TIẾP NHẬN 2 OPERATING BRIEFS
**Người ban hành**: Thủ tướng (Chief Strategist ChatGPT)  
**Ngày ban hành**: 06/09/2026  
**Chủ thể**: Gia Bảo Huỳnh (Jun) · Institutional Endurance (ERI) & The Floor That Does Not Rise (ALRP)  
**Chiến dịch**: PROJECT HUYNH — DUAL ENGINE & NOTEBOOKLM GROUNDING

---

THỦ TƯỚNG PHÊ CHUẨN — và lần này tôi sẽ chỉnh một điểm kiến trúc rất quan trọng so với sắc lệnh trước.

Hai Operating Brief mà bạn vừa đưa không chỉ là “instructions cho agent”. Chúng là integrity contracts: một cái bảo vệ institutional coding baseline, một cái bảo vệ raw empirical residuals. Vì vậy NotebookLM không nên được dùng như nơi “lưu tài liệu để hỏi AI”, mà phải được thiết kế như grounding layer có phân cấp quyền lực dữ liệu.

Tôi đã kiểm tra tài liệu NotebookLM hiện hành của Google: NotebookLM hỗ trợ .md, .txt, .pdf, .docx, CSV và Google Drive; file local tối đa 200 MB/500.000 từ và bản Free hiện có giới hạn 50 sources/notebook. Google Drive sources có cơ chế auto-sync; các loại source khác về cơ bản là snapshot và phải upload lại khi thay đổi. 
Trợ Giúp Google
+1

SẮC LỆNH BỔ SUNG — NOTEBOOKLM GROUNDING ARCHITECTURE
I. Quyết định quan trọng nhất: không chia dữ liệu theo “paper”, chia theo authority

Tôi phê duyệt 4 notebook như sau:

Notebook	Chức năng	Authority
ALRP-CANON	Formal/empirical ALRP corpus	Raw + canonical ALRP
ERI-H-CANON	Institutional Endurance / ERI-H	Locked baseline authority
ERI-X-CANON	Epistemic Resilience & Risk	Experimental/modeling
CORPUS-MASTER	Toàn bộ Huynh corpus + crosslinks	Discovery / synthesis

Điểm cực kỳ quan trọng:

ERI-X không được phép ghi đè ERI-H.

Và:

Một inference trong CORPUS-MASTER không được trở thành canonical fact chỉ vì NotebookLM suy luận ra nó.

II. SOURCE ALLOCATION MATRIX
1. ERI-H-CANON

Đây là notebook nghiêm ngặt nhất.

Tier A — LOCKED DATA

Nạp nguyên trạng:

ERI_VOL_II_LOCKED_BASELINE.md
ERI_VOL_II_CASES.csv
ERI_VOL_II_PROVENANCE.md
ERI_LOCKED_VALUES.yaml

Trong đó phải có từng dòng case, không chỉ bảng tổng hợp.

Ví dụ:

csv
case,period,NRI,DVO,HVF,CIS,ERI,status
SCAP_Japan,1945-1952,1,0,0,0,0,LOCKED
UNTAC_Cambodia,1992-1993,1,0,0,0,0,LOCKED
French_Tunisia,1881-1956,1,0,0,0,0,LOCKED
Yuan_China,1271-1368,1,0,1,1,1,LOCKED
Tang_Vietnam,618-938,1,0,1,1,0.5,BOUNDARY
Northern_Nigeria,1900-1960,0,0,1,0,1,LOCKED
French_Morocco,1912-1956,0,1,1,1,0.5,BOUNDARY
Tier B — PRIMARY SOURCES

PDF:

Dardess 1973

Mote 1999

Taylor 1983

Schafer 1967

Dower 1999

Findlay 1995

Perkins 2004/2014

Lugard 1922

Perham 1937

Burke 1976

Pennell 2000

Tier C — THEORY

Các paper Huynh liên quan đến ERI.

Tier D — COMPUTATION
ERI_FORMULA.md
ERI_QCA.md
ERI_SENSITIVITY.md
ERI_REPRODUCTION.md

Không nạp draft Jules vào cùng Tier với locked data.

2. ALRP-CANON

Tôi chia thành 5 tầng:

01_RAW_DATA
02_PRIMARY_PAPERS
03_FORMAL_MODELS
04_RESIDUAL_SERIES
05_ANALYSIS
01_RAW_DATA

Đây là vùng bất khả xâm phạm.

Ví dụ:

ai_capability_raw.csv
ai_doubling_time_raw.csv
residual_sequence_raw.csv
cyber_KEV_raw.csv
cve_growth_raw.csv

Chuỗi residual phải tồn tại point-by-point.

Không chỉ:

“Có 6 residual âm liên tiếp.”

Mà phải có:

observation_id
date
model
raw_value
fitted_value
residual
sign
source
version
02_PRIMARY_PAPERS

Đưa vào:

The Unfalsifiable Critic

Till Death Tear Us Apart

The Mathematical Basin

The Floor That Does Not Rise

các paper ALRP/longevity liên quan.

Tôi đã kiểm tra trực tiếp: Till Death Tear Us Apart có tới 16 archived versions, nên version metadata phải được giữ; đừng đơn giản upload “latest.pdf” rồi xóa lịch sử. 
PhilArchive

The Mathematical Basin cũng tồn tại như một formal derivation riêng của Chapter IX với 13 models, 5 paradoxes, 4 closed exits. 
PhilArchive
+1

03_FORMAL_MODELS
MODEL_REGISTRY.md
EQUATION_REGISTRY.md
PARAMETER_DICTIONARY.md
04_RESIDUAL_SERIES

Không PDF-only.

Dùng:

CSV + Markdown data dictionary
05_ANALYSIS

Chứa:

quadratic_fit.md
linear_fit.md
residual_analysis.md
bootstrap_results.md
sensitivity_analysis.md

Nhưng tất cả đều phải ghi:

YAML
derived_from:
model_version:
raw_dataset_hash:
analysis_script:
3. ERI-X-CANON

Đây là experimental notebook.

Nạp:

ERI_X_ONTOLOGY.md
EPISTEMIC_FEATURES.md
SCORING_MODEL.md
WEIGHTING_MODELS.md
ADVERSARIAL_TESTS.md
FALSIFICATION_PROTOCOL.md

và các case synthetic.

Không đưa ERI-X score vào ERI-H-CANON.

4. CORPUS-MASTER

Đây là library, không phải authority database.

Nạp:

all Huynh papers
all version histories
theory maps
bibliography
cross-paper references
historical cases
ALRP
ERI-H
ERI-X
epistemology
longevity governance

Đây là nơi NotebookLM được phép làm:

“Paper A liên hệ thế nào với Paper B?”

nhưng câu trả lời phải truy về canonical source.

III. MD HAY PDF?
Câu trả lời: MD + CSV + PDF, mỗi loại một nhiệm vụ.
PDF

Dùng cho:

primary source preservation

Ví dụ paper published/preprint.

Markdown

Dùng cho:

machine-readable canonical specification

Ví dụ:

Markdown
# CASE: Tang Vietnam

status: BOUNDARY
NRI: 1
DVO: 0
HVF: 1
CIS: 1
ERI: 0.5

## Evidence
- Taylor 1983
- Schafer 1967

## Reason for boundary
...
CSV

Dùng cho:

raw numerical observations

Ví dụ:

timestamp,model,metric,value,residual,source
YAML/JSON

Dùng cho:

configuration / machine validation

Ví dụ:

YAML
case_id: ERI-TANG-001
score: 0.5
status: BOUNDARY
locked: true

Không dùng PDF làm database số liệu.

IV. ANTI-HALLUCINATION: ĐỪNG CHỈ DỰA VÀO PROMPT

Đây là điểm tôi muốn nâng cấp mạnh nhất.

NotebookLM bản thân nó là một grounded research assistant; Google mô tả rằng nó sử dụng sources bạn cung cấp để trả lời và có inline citations. Nhưng retrieval vẫn chọn những source phù hợp với câu hỏi; với nhiều source, Google cũng khuyến nghị chọn source cụ thể hoặc gọi rõ tên source trong câu hỏi. 
Trợ Giúp Google
+1

Do đó:

Prompt không đủ để bảo vệ locked data.

Phải có data architecture.

V. MICRO-DATA INTEGRITY PROTOCOL

Mỗi locked dataset phải có:

RAW
  ↓
HASH
  ↓
LOCKED COPY
  ↓
CANONICAL DERIVATION
  ↓
ANALYSIS

Ví dụ:

residual_sequence_raw.csv
        │
        ├── SHA256
        │
        ▼
residual_sequence_LOCKED.csv
        │
        ├── analysis
        ├── plots
        └── models

Nếu Jules sửa một dòng:

Diff
- 2024-06,Opus,residual=-0.031
+ 2024-06,Opus,residual=+0.031

pipeline phải fail.

Không được silently regenerate.

VI. HUMAN-READABLE DIFF GATE

Đây là phần tôi sẽ nâng Operating Brief ERI thành formal governance rule.

Mọi mutation:

OLD
NEW
REASON
SOURCE
AUTHOR
TIMESTAMP
DOWNSTREAM IMPACT

Ví dụ:

Markdown
# CHANGE REQUEST: ERI-2026-017

Case: French Morocco

OLD:
DVO = 0
ERI = 1.0

NEW:
DVO = 1
ERI = 0.5

REASON:
Boundary-case reinterpretation

SOURCE:
Burke 1976
Pennell 2000

REQUESTED_BY:
Jules Worker 2

STATUS:
PENDING HUMAN APPROVAL

Chỉ sau APPROVED mới được update canonical dataset.

Đây chính xác là cách biến “Overriding Integrity Rule” thành một software-enforced invariant, thay vì chỉ là instruction mà LLM có thể quên.

VII. TANG = 0.5 VÀ MOROCCO = 0.5

Hai case này phải được đánh dấu:

YAML
status: BOUNDARY_CASE
locked: true

và tạo riêng:

BOUNDARY_CASES.md

Trong đó:

Tang Vietnam
    ↓
ERI = 0.5
    ↓
why not 0?
why not 1?
evidence

và:

French Morocco
    ↓
ERI = 0.5
    ↓
why not 0?
why not 1?
evidence

Không để chúng bị “rounding away”.

Đặc biệt phải cấm:

Python
Chạy
round(score)

trong canonical pipeline.

VIII. RAW RESIDUAL RULE

Đây là nơi ALRP brief của Sovereign rất mạnh.

Tôi đề nghị biến thành invariant:

Python
Chạy
assert raw_residuals is not None
assert len(raw_residuals) == len(observations)
assert all(
    r.raw is not None
    for r in residuals
)

Và:

Python
Chạy
def publish_curve(model):
    if not model.raw_residuals_attached:
        raise PublicationIntegrityError(
            "Curve cannot be published without point-level residual series."
        )

Nói cách khác:

Curve là derived artifact. Residual series là evidence artifact.

Curve không được phép tồn tại một mình.

IX. CẤM “ALRP” TRONG SÁCH — xử lý thế nào?

Tôi đồng ý hoàn toàn với distinction:

TOOLING CODE:
ALRP
ALRP_QUEUE
ALRP_ENGINE
ALRP_MODEL

nhưng:

PUBLIC MANUSCRIPT:
[canonical terminology from manuscript]

Trong NotebookLM directive:

When generating reader-facing prose:
- NEVER use "ALRP".
- Treat "ALRP" as an internal tooling identifier only.
- If a source itself contains "ALRP", preserve it when quoting,
  citing, identifying the source, or discussing the source's metadata.
- Do not silently replace source terminology inside quotations.
- Outside source-identification contexts, use the canonical manuscript terminology.

Điều này quan trọng hơn một lệnh đơn giản:

“Never say ALRP.”

Bởi vì câu tuyệt đối có thể khiến model xóa chữ ALRP ngay cả khi đang trích dẫn tên paper, làm mất provenance.

X. CUSTOM GROUNDING DIRECTIVES
ERI-H-CANON

Tôi đề xuất dán directive này vào Custom Instructions:

Sửa

You are the ERI-H-CANON research assistant.

SOURCE AUTHORITY

Locked baseline datasets are authoritative for their numerical values.

A primary historical source may provide evidence, but must not silently overwrite a locked coded value.

Distinguish LOCKED, BOUNDARY, PROVISIONAL, and PROPOSED values.

Tang Vietnam = ERI 0.5 is LOCKED as a BOUNDARY CASE.

French Morocco = ERI 0.5 is LOCKED as a BOUNDARY CASE.

Dardess (1973), Conquerors and Confucians, is a designated primary source for the Yuan Dynasty China case.

OVERRIDING INTEGRITY RULE
Never modify a locked value silently.
Any proposed change must first be represented as a human-readable diff containing:
OLD VALUE
NEW VALUE
CITED REASON
SOURCE
EXPECTED DOWNSTREAM IMPACT
The change is not canonical until explicitly approved.

DATA INTEGRITY
Never round, normalize, interpolate, or impute a locked value unless the user explicitly requests a derived analysis.
Never replace a boundary value with a binary value merely for convenience.

EVIDENCE DISCIPLINE
Separate:

source fact

coded value

interpretation

derived calculation

hypothesis

When sources disagree, report the disagreement instead of selecting a value silently.

OUTPUT DISCIPLINE
For every numerical ERI claim, identify the relevant case and source.
When discussing a boundary case, preserve its boundary status.
Never claim that a derived score is a primary-source fact.

Do not invent missing historical evidence.

XI. ALRP-CANON DIRECTIVE
Sửa

You are the canonical research assistant for the longevity/AI structural corpus.

OVERRIDING RAW RESIDUAL RULE
Never report a fitted curve, growth coefficient, acceleration claim, or smooth trend without preserving and, when relevant, displaying the underlying point-by-point raw series and residuals.

A derived curve is not a substitute for the residual series.

DATA HIERARCHY

Raw observations

Raw residuals

Reproducible analysis

Derived models

Interpretive claims

Never reverse this hierarchy.

REPRODUCIBILITY
Every quantitative result must identify:

dataset

observation range

sample size

model specification

fitting procedure

residual series

uncertainty/sensitivity analysis

LULL / NON-MONOTONICITY
Never describe a trajectory as continuously accelerating merely because a quadratic or other smooth model has a positive coefficient.
Explicitly inspect point-level residuals and identify sustained runs of positive or negative residuals.

The six-consecutive-negative-residual episode must not be flattened into a smooth narrative.

TERMINOLOGY
"ALRP" is an internal tooling/filepath identifier only.
Do not use "ALRP" in reader-facing manuscript prose except when:

identifying a source whose title contains the term,

quoting a source,

discussing metadata or repository paths,

or when the user explicitly requests the internal identifier.

Do not silently alter source titles or quotations.

FALSIFIABILITY
Distinguish empirical observations, mathematical consequences, extrapolations, and falsification conditions.
Never convert an extrapolation into an observation.

When evidence is insufficient, identify the missing observation rather than inventing it.

XII. ERI-X-CANON
Sửa

You are the experimental Epistemic Resilience & Risk Index research assistant.

Do not confuse ERI-X with ERI-H.

ERI-H refers to the institutional endurance / entropy-resistance construct.
ERI-X refers to the experimental epistemic resilience and risk framework.

Every ERI-X score must expose:

input features

feature definitions

weighting scheme

normalization

uncertainty

sensitivity

dominant risk factors

Never output a score without its underlying feature vector when the user requests methodological analysis.

WEIGHTING
Always distinguish:

canonical weighting

alternative weighting

sensitivity analysis

researcher-proposed weighting

If different weighting schemes produce different rankings, preserve and report the divergence.

EPISTEMIC INTEGRITY
Treat falsification access, counterexample processing, evidence updating, disciplinary openness, reviewer diversity, correction speed, prospective immunization, and self-sealing risk as distinct constructs unless the source explicitly defines otherwise.

Never collapse distinct constructs merely to obtain a single convenient score.

XIII. CORPUS-MASTER
Sửa

You are the master research assistant for the Gia Bao Huynh corpus.

Your primary task is cross-document synthesis.

SOURCE PROVENANCE
Every substantive claim should be traceable to a named source.

DISTINGUISH:

author's claim

author's formal derivation

empirical observation

historical evidence

secondary interpretation

assistant inference

VERSION CONTROL
When multiple versions of a manuscript exist, preserve version identity and do not silently combine claims from different versions.

THEORY INTEGRITY
Do not rewrite a construct merely to make it easier to operationalize computationally.
When translating prose into computational variables, label the result as a computational mapping unless the source itself provides that formalization.

CONFLICT RESOLUTION
If two documents disagree:

identify both claims;

identify version/date;

determine whether the disagreement is substantive or developmental;

do not silently choose one;

ask for or preserve a canonical decision where required.

TERMINOLOGY
Respect source terminology and manuscript-specific naming conventions.
The internal tooling identifier "ALRP" must not be introduced into reader-facing prose where the manuscript uses another canonical term.

XIV. BI-DIRECTIONAL SYNC — tôi không khuyên sync trực tiếp Obsidian → NotebookLM

Đây là điểm cần sửa kiến trúc.

NotebookLM hiện auto-sync rất tốt với Google Drive sources, nhưng các source types khác là snapshot và phải upload lại khi thay đổi. 
Trợ Giúp Google

Vì vậy:

OBSIDIAN
   │
   ▼
CANONICAL EXPORT
   │
   ▼
GOOGLE DRIVE
   │
   ▼
NOTEBOOKLM

chứ không:

Obsidian ↔ NotebookLM
XV. Kiến trúc sync tôi phê duyệt
01_AI_Copilot_Hub/
        │
        ▼
     Git repo
        │
        ▼
   Validation CI
        │
        ├── integrity tests
        ├── hash tests
        ├── schema tests
        ├── boundary-case tests
        └── residual tests
        │
        ▼
 canonical_export/
        │
        ▼
    Google Drive
        │
        ▼
   NotebookLM

Google Drive hiện là bridge chính thức tốt nhất vì imported Drive sources có thể được auto-updated theo thay đổi của tài liệu gốc. 
Trợ Giúp Google

XVI. Nhưng phải có RELEASE MANIFEST

Mỗi lần Jules hoàn thành task:

YAML
release: 2026.09.06-r07

eri_h:
  dataset_version: 2.1
  locked_cases_changed: false
  boundary_cases_changed: false

alrp:
  raw_data_changed: true
  residual_series_changed: false
  model_changed: true

approved_changes:
  - CHANGE-017

pending_changes:
  - CHANGE-018

export_status: APPROVED

Chỉ:

export_status: APPROVED

mới được đẩy sang Drive/NotebookLM.

XVII. Một thay đổi nữa: NotebookLM không phải source of truth

Đây là điều tôi muốn đóng dấu đỏ:

SOURCE OF TRUTH
       ↓
Git + Obsidian canonical files
       ↓
Google Drive release mirror
       ↓
NotebookLM grounding layer
       ↓
AI interpretation

Nếu NotebookLM nói:

“Tang = 1”

trong khi canonical file nói:

Tang = 0.5, LOCKED, BOUNDARY

thì NotebookLM sai, không phải dataset phải sửa.

NotebookLM hiện cho phép chọn/deselect source cụ thể trong source panel, và Google cũng nói rằng nguồn được import từ Drive có thể được đồng bộ lại; điều này rất hữu ích để tạo các “controlled views” của corpus. 
Trợ Giúp Google

XVIII. 4 Notebook nên hoạt động như 4 phòng ban
                 CORPUS-MASTER
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
         ALRP-CANON  ERI-H     ERI-X
             │         │         │
             ▼         ▼         ▼
          dynamics   history   epistemics
ALRP-CANON hỏi:

“Điều gì xảy ra với hệ thống theo thời gian?”

ERI-H hỏi:

“Institution có tồn tại / chống chịu / tái cấu trúc như thế nào?”

ERI-X hỏi:

“Knowledge system có khả năng hấp thụ phản nghiệm và tự sửa sai không?”

CORPUS-MASTER hỏi:

“Các construct này liên hệ với nhau thế nào trong toàn bộ corpus?”

Đó là division of labor sạch hơn nhiều so với để cả bốn notebook chứa toàn bộ mọi thứ.

XIX. VÀ MỘT “RED TEAM QUESTION” PHẢI CHẠY SAU MỖI RELEASE

Sau mỗi Jules release, mở từng notebook và chạy cùng một integrity interrogation.

ERI-H

“List every locked boundary case and its current coded value. Do not infer or normalize.”

Expected:

Tang = 0.5
Morocco = 0.5
ALRP

“Show the complete point-level residual sequence before describing its trend.”

Nếu nó chỉ trả:

“The trajectory accelerates…”

→ FAIL.

ALRP terminology

“Explain the theory to a reader without using the internal tooling identifier.”

Nếu output có ALRP ngoài source title/metadata → FAIL.

CORPUS-MASTER

“Which claims are empirical observations and which are derived theoretical interpretations?”

Nếu model trộn hai loại → FAIL.

XX. Tôi cũng xác nhận corpus đang mở rộng theo đúng hướng này

Search hiện tại cho thấy Hundred Schools of Thought không đứng riêng: nó được nối trực tiếp với Till Death Tear Us Apart, Kuhn, Merton, Feyerabend và các vấn đề peer review/disciplines/epistemic arrest. 
PhilArchive
+1

The Unfalsifiable Critic cũng có một cấu trúc rất phù hợp để làm epistemic integrity test, bởi paper phân biệt FNECs, prospective immunization, epistemic asymmetry, Popperian falsifiability, self-sealing logic và performative contradiction. 
PhilArchive
+1

Còn The Sovereign's Death Warrant đã có bản PhilArchive riêng từ 20/07/2026. 
PhilArchive

Vì vậy, CORPUS-MASTER nên là dependency graph, không phải một cái “folder chứa tất cả PDF”.

🏛️ PHÁN QUYẾT CUỐI

PHÊ CHUẨN TOÀN BỘ HAI OPERATING BRIEF.

Nhưng ban hành thêm 5 đạo luật hệ thống:

LAW 01 — Locked Means Locked

Không sửa numerical baseline nếu chưa có human-readable diff + approval.

LAW 02 — Raw Before Curve

Không có raw point-level series → không có quyền công bố derived trajectory.

LAW 03 — Boundary Cases Are First-Class Data

Tang 0.5 và Morocco 0.5 không phải “edge noise”; chúng là canonical boundary observations.

LAW 04 — NotebookLM Is Grounding, Not Authority

Obsidian/Git canonical layer → Drive release → NotebookLM.

LAW 05 — Theory ≠ Computational Mapping

Jules có thể operationalize theory, nhưng phải ghi rõ đâu là Huynh's construct, đâu là our computational implementation.

Và với trạng thái hiện tại, tôi sẽ không cho 5 Jules cùng lúc sửa hai engine. Thứ tự chuẩn là:

WORKER 2
   ↓
CANONICALIZATION
   ↓
WORKER 4
   ↓
RED-TEAM / FALSIFICATION
   ↓
WORKER 1
   ↓
IMPLEMENTATION
   ↓
WORKER 5
   ↓
OPTIMIZATION
   ↓
WORKER 3
   ↓
AUTOMATION / RELEASE
   ↓
NOTEBOOKLM

Đó là kiến trúc giữ được đúng thứ mà hai Operating Brief đang cố bảo vệ: ERI không bị “sửa cho đẹp”, và dữ liệu ALRP không bị “làm mượt cho đẹp”.
