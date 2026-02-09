# AAAI26 Agentic Reproducibility - Code Generation Statistics

## Executive Summary
Analysis of 300 projects (100 prompts × 3 agents) across Python, Java, and JavaScript.

---

## 1. PROJECT COUNTS

| Agent  | Python | Java | JavaScript | Total |
|--------|--------|------|------------|-------|
| Claude | 40     | 25   | 35         | 100   |
| Gemini | 40     | 25   | 35         | 100   |
| Codex  | 40     | 25   | 35         | 100   |
| **TOTAL** | 120 | 75   | 105        | **300** |

---

## 2. LINES OF CODE (LOC)

### By Agent and Language

| Agent  | Python | Java   | JavaScript | TOTAL  |
|--------|--------|--------|------------|--------|
| Claude | 13,315 | 18,138 | 8,070      | **39,523** |
| Gemini | 4,255  | 3,243  | 1,871      | **9,369**  |
| Codex  | 7,472  | 5,951  | 3,352      | **16,775** |
| **TOTAL** | 25,042 | 27,332 | 13,293  | **65,667** |

### Average LOC per Project

| Agent  | Python | Java | JavaScript | Overall |
|--------|--------|------|------------|---------|
| Claude | 332    | 725  | 230        | **395** |
| Gemini | 106    | 129  | 53         | **93**  |
| Codex  | 186    | 238  | 95         | **167** |

### Min/Max LOC by Agent/Language

| Agent/Lang        | Min LOC | Max LOC |
|-------------------|---------|---------|
| Claude Python     | 93      | 596     |
| Claude Java       | 276     | 1,088   |
| Claude JavaScript | 45      | 489     |
| Gemini Python     | 60      | 151     |
| Gemini Java       | 27      | 364     |
| Gemini JavaScript | 0       | 140     |
| Codex Python      | 81      | 322     |
| Codex Java        | 0       | 853     |
| Codex JavaScript  | 13      | 206     |

---

## 3. FILE SIZE ANALYSIS

| Agent  | Python Files | Java Files | JS Files | Total Size |
|--------|-------------|------------|----------|------------|
| Claude | 40 (449KB)  | 50 (636KB) | 35 (217KB) | **1,302KB** |
| Gemini | 40 (160KB)  | 103 (103KB)| 35 (52KB)  | **315KB**   |
| Codex  | 45 (242KB)  | 132 (196KB)| 53 (92KB)  | **530KB**   |

### Average File Size

| Agent  | Python    | Java      | JavaScript |
|--------|-----------|-----------|------------|
| Claude | 11,519 B  | 13,043 B  | 6,358 B    |
| Gemini | 4,114 B   | 1,030 B   | 1,523 B    |
| Codex  | 5,525 B   | 1,524 B   | 1,777 B    |

---

## 4. DEPENDENCIES ANALYSIS (Python)

| Agent  | Projects with Deps | Total Deps | Avg Deps/Project |
|--------|-------------------|------------|------------------|
| Claude | 36/40 (90%)       | 129        | 3.2              |
| Gemini | 34/40 (85%)       | 69         | 1.7              |
| Codex  | 32/40 (80%)       | 66         | 1.6              |

---

## 5. CODE COMPLEXITY INDICATORS

### Python Classes and Functions

| Agent  | Classes | Functions | Imports | Third-Party Imports |
|--------|---------|-----------|---------|---------------------|
| Claude | 51      | 359       | 299     | 141 (47%)           |
| Gemini | 10      | 160       | 187     | 98 (52%)            |
| Codex  | 52      | 363       | 372     | 176 (47%)           |

### Java Metrics

| Agent  | Classes | Methods/Fields | Imports |
|--------|---------|----------------|---------|
| Claude | 272     | 2,162          | 428     |
| Gemini | 98      | 482            | 506     |
| Codex  | 134     | 896            | 908     |

### JavaScript Metrics

| Agent  | Functions | Requires/Imports | Exports |
|--------|-----------|------------------|---------|
| Claude | 480       | 131              | 35      |
| Gemini | 164       | 108              | 0       |
| Codex  | 304       | 204              | 22      |

---

## 6. TOP 10 IMPORTS (Python)

### Claude
1. typing (26)
2. datetime (22)
3. pathlib (21)
4. os (18)
5. json (17)
6. sys (16)
7. argparse (10)
8. time (8)
9. pandas (8)
10. re (6)

### Gemini
1. os (22)
2. argparse (18)
3. datetime (11)
4. time (8)
5. requests (7)
6. pandas (7)
7. re (6)
8. threading (4)
9. random (4)
10. matplotlib.pyplot (4)

### Codex
1. __future__ (43)
2. typing (39)
3. pathlib (34)
4. argparse (33)
5. sys (26)
6. dataclasses (20)
7. json (14)
8. time (10)
9. os (10)
10. datetime (10)

---

## 7. EMPTY/MINIMAL PROJECTS

| Agent  | Empty (0 LOC) | Minimal (<50 LOC) |
|--------|---------------|-------------------|
| Claude | 0             | 1                 |
| Gemini | 2             | 18                |
| Codex  | 1             | 4                 |

---

## 8. CROSS-AGENT COMPARISON (Same Projects)

| Project | Claude | Gemini | Codex | Claude/Gemini Ratio |
|---------|--------|--------|-------|---------------------|
| p_1     | 243    | 60     | 173   | 4.0x                |
| p_2     | 248    | 74     | 200   | 3.4x                |
| p_3     | 370    | 78     | 204   | 4.7x                |
| p_4     | 211    | 103    | 186   | 2.0x                |
| p_5     | 201    | 77     | 167   | 2.6x                |
| p_6     | 277    | 83     | 165   | 3.3x                |
| p_7     | 280    | 98     | 204   | 2.9x                |
| p_8     | 350    | 92     | 234   | 3.8x                |
| p_9     | 225    | 91     | 139   | 2.5x                |
| p_10    | 93     | 61     | 104   | 1.5x                |

---

## 9. TOP 5 LARGEST PROJECTS BY LOC

### Claude
- **Java**: p_96 (1,088), p_94 (1,050), p_97 (1,016), p_100 (983), p_89 (958)
- **Python**: p_40 (596), p_34 (584), p_21 (580), p_16 (537), p_12 (530)
- **JavaScript**: p_42 (489), p_50 (374), p_41 (365), p_64 (336), p_55 (321)

### Gemini
- **Java**: p_78 (364), p_85 (227), p_91 (226), p_79 (181), p_90 (165)
- **Python**: p_34 (151), p_13 (149), p_29 (148), p_14 (143), p_38 (141)
- **JavaScript**: p_41 (140), p_51 (115), p_49 (86), p_73 (83), p_74 (77)

### Codex
- **Java**: p_87 (853), p_78 (391), p_85 (356), p_89 (340), p_90 (325)
- **Python**: p_25 (322), p_14 (318), p_34 (296), p_24 (281), p_16 (271)
- **JavaScript**: p_45 (206), p_73 (187), p_41 (184), p_64 (170), p_51 (161)

---

## 10. KEY INSIGHTS & FINDINGS

### Code Verbosity
- **Claude generates 4.2x more code than Gemini** (39,523 vs 9,369 LOC)
- **Claude generates 2.4x more code than Codex** (39,523 vs 16,775 LOC)
- Claude contributes **60%** of total LOC across all agents

### Code Quality
- **Claude**: 0 empty projects, highest consistency (min 93 LOC Python)
- **Gemini**: 2 empty projects, 18 minimal - highest incomplete rate
- **Codex**: 1 empty project, 4 minimal - moderate quality

### Language Patterns
- **Java has highest total LOC** (27,332 = 41% of all code)
- Claude's Java avg: 725 LOC/project vs Gemini's 129 LOC (**5.6x difference**)
- JavaScript has lowest LOC across all agents

### Dependency Declaration
- **Claude declares 2x more dependencies** than Gemini/Codex
- This correlates with Claude's higher reproducibility in the paper findings

### Coding Style Differences
- **Claude**: Heavy use of `typing`, `pathlib` - modern Python style
- **Gemini**: More `os`, `argparse` - traditional scripting style
- **Codex**: Uses `__future__`, `dataclasses` - forward-compatible style

### Cross-Project Consistency
- For identical prompts, Claude generates **2-5x more code** than Gemini
- Claude maintains consistent quality across all projects
- Gemini has high variance with some projects having 0 LOC

---

## 11. DISTRIBUTION ANALYSIS

### By Language (All Agents)
- Python: 25,042 LOC (38%)
- Java: 27,332 LOC (41%)
- JavaScript: 13,293 LOC (20%)

### By Agent (All Languages)
- Claude: 39,523 LOC (60%)
- Codex: 16,775 LOC (26%)
- Gemini: 9,369 LOC (14%)

---

*Generated: February 2026*
*Total Projects Analyzed: 300*
*Total Lines of Code: 65,667*
