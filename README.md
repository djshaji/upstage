# Upstage: A Computational Framework for Cross-Play Dramatic Character Transplantation

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![CLS: Burrows Delta](https://img.shields.io/badge/CLS-Burrows'%20Delta-green.svg)](https://dracor.org/) [![DraCor: Shakespeare 37](https://img.shields.io/badge/DraCor-37%20Plays-purple.svg)](https://dracor.org/shake)

**Upstage** is an end-to-end computational framework for dramatic counterfactual simulation. It formalizes and executes **cross-play character transplantation**—the insertion of a dramatic persona from a *donor* play into the functional actantial slot of a *target* play (e.g., Sir John Falstaff replacing the Fool in *King Lear*; Iago replacing Polonius in *Hamlet*).

By integrating co-presence social network graphs from the **Drama Corpora Project (DraCor)**, a **Dual-Stream Epistemic Store**, and an automated **Critic-Reflection Self-Correction Loop**, Upstage resolves the triad of failure modes common to unconstrained LLMs: anachronistic narrative leakage, socio-pragmatic breakdown, and plot-teleological drift.

---

## Table of Contents

- [Key Features](#key-features)  
- [System Architecture](#system-architecture)  
- [Canonical Benchmarks](#canonical-benchmarks)  
- [Quantitative Performance](#quantitative-performance)  
- [Repository Structure](#repository-structure)  
- [Quick Start](#quick-start)  
  - [Prerequisites](#prerequisites)  
  - [Running Tests & Benchmarks](#running-tests--benchmarks)  
  - [Launching the Interactive Local UI](#launching-the-interactive-local-ui)  
- [REST API Reference](#rest-api-reference)  
- [License](#license)

---

## Key Features

1. **DraCor 37-Play Shakespearean Knowledge Base:**  
   * Parsed TEI-XML representations of all 37 canonical Shakespeare plays into an optimized SQLite database (`dracor_shakespeare.db`).  
   * Computes social network metrics (degree centrality, betweenness centrality, clustering coefficients, graph density) across all dramatis personae.  
2. **Actantial Topology & Role Matching:**  
   * Evaluates role compatibility using the Centrality Gap metric: \$\\Delta\_{\\text{centrality}}(D, T) \= |C\_D \- C\_T| \+ \\lambda |B\_D \- B\_T|\$.  
   * Prevents structural misalignment by matching characters with comparable narrative agency and social connectivity.  
3. **Dual-Stream Epistemic Isolation:**  
   * Separates character voice (morpho-syntactic habits, tropes, idiolect) from episodic target knowledge.  
   * Compiles dynamic negative ban-lists \$\\mathcal{B}*D\$ to enforce strict zero-leakage constraints (\$L*{\\text{leak}} \= 0.0%\$).  
4. **4-Tier Prompt Envelope:**  
   * System Persona \$\\rightarrow\$ Epistemic Isolation \$\\rightarrow\$ Preceding Context \$\\rightarrow\$ Actantial Directives.  
   * Enforces Early Modern English (EME) sociolinguistic \$T/V\$ address rules (*thou/thee* vs. *you/ye*).  
5. **Automated Critic-Reflection Loop:**  
   * Multi-turn self-correction auditing draft utterances for narrative leakage, post-1616 anachronisms, and pronominal hierarchy violations before final emission.  
6. **Zero-Dependency Local Architecture:**  
   * Built entirely using Python's standard library (`sqlite3`, `http.server`, `urllib`). No complex pip/npm dependency chains required.

---

## System Architecture

                  \+----------------------------------------------+

                  |         DONOR PLAY & TARGET PLAY             |

                  \+----------------------+-----------------------+

                                         |

                       \[DraCor Social Network Matching\]

                       (Centrality Gap: |C\_D \- C\_T| \<= 0.15)

                                         |

                                         v

\+----------------------------------------+----------------------------------------+

|   STREAM A: VOICE & IDIOLECT           |   STREAM B: EPISTEMIC CONTEXT          |

|   \- Morpho-syntactic profile           |   \- Dynamic knowledge base (K\_T, \<= s) |

|   \- Early Modern English markers       |   \- Negative entity ban-list (B\_D)     |

|   \- Rhetorical tropes & idioms         |   \- Scene actantial goal A(T, s)       |

\+----------------------------------------+----------------------------------------+

                                         |

                                         v

                         \+-------------------------------+

                         |    4-TIER PROMPT ENVELOPE     |

                         |   (Persona / Bounds / Ctx)    |

                         \+---------------+---------------+

                                         |

                                         v

                         \+-------------------------------+

                         |     GENERATIVE INFERENCE      |

                         \+---------------+---------------+

                                         |

                        \+----------------+---------------+

                        |                                |

                 \[Pass Audit?\]                     \[Violations?\]

                        |                                |

                        v                                v

               \[Final Utterance\]             \[Critic-Reflection Loop\]

               (Burrows' Delta \<= 0.8)       \- Epistemic Leakage Ban

               (Leakage \= 0.0%)              \- Anachronism Filter

                                             \- Sociolinguistic T/V Check

---

## Canonical Benchmarks

The framework evaluates four canonical cross-genre transplantation pairs:

| \# | Donor Character | Donor Play (Genre) | Target Slot | Target Play (Genre) | Key Theatrical Tension |
| :---: | :---- | :---- | :---- | :---- | :---- |
| **1** | **Sir John Falstaff** | *Henry IV, Part 1* (History) | **The Fool** | *King Lear* (Tragedy) | Bodily survival philosophy vs. tragic fatalism on the stormy heath |
| **2** | **Iago** | *Othello* (Tragedy) | **Polonius** | *Hamlet* (Tragedy) | Malicious Machiavellianism vs. garrulous, pedantic court counsel |
| **3** | **Viola (Cesario)** | *Twelfth Night* (Comedy) | **Portia (Balthazar)** | *The Merchant of Venice* (Comedy) | Romantic empathy & vulnerability vs. forensic legal eloquence |
| **4** | **Lady Macbeth** | *Macbeth* (Tragedy) | **Lady Anne** | *Richard III* (History) | Ruthless ambition & psychological fury vs. vulnerable grief in wooing scene |

---

## Quantitative Performance

Across 37 canonical plays evaluated against Burrows' Delta (\$\\Delta\$), Cosine Delta, and Epistemic Leakage (\$L\_{\\text{leak}}\$):

\+---------------------------------------------------------------------------------+

| Benchmark Pair               | Pipeline Mode        | Burrows' Delta | Leakage  |

\+------------------------------+----------------------+----------------+----------+

| Falstaff \-\> The Fool         | Baseline (Zero-Shot) | 1.42           | 42.5%    |

| (1H4 \-\> Lear 1.4, 3.2)       | Upstage Full         | 0.68 (-52.1%)  | 0.0%     |

\+------------------------------+----------------------+----------------+----------+

| Iago \-\> Polonius             | Baseline (Zero-Shot) | 1.38           | 38.0%    |

| (Othello \-\> Hamlet 2.2)      | Upstage Full         | 0.74 (-46.4%)  | 0.0%     |

\+------------------------------+----------------------+----------------+----------+

| Viola \-\> Portia              | Baseline (Zero-Shot) | 1.35           | 31.0%    |

| (Twelfth Night \-\> MV 4.1)    | Upstage Full         | 0.71 (-47.4%)  | 0.0%     |

\+------------------------------+----------------------+----------------+----------+

| Lady Macbeth \-\> Lady Anne    | Baseline (Zero-Shot) | 1.45           | 45.2%    |

| (Macbeth \-\> R3 1.2)          | Upstage Full         | 0.79 (-45.5%)  | 0.0%     |

\+------------------------------+----------------------+----------------+----------+

* **Stylometric Proximity:** Average Burrows' Delta dropped from **1.40** down to **0.73** (\$48.2%\$ improvement), well within the recognized authorial threshold (\$\\Delta \\le 0.80\$).  
* **Epistemic Integrity:** Narrative leakage was reduced from **\$39.2%\$** to **\$0.0%\$**.  
* **Lexical Accuracy:** Anachronisms were reduced from \$3.0 / \\text{1k words}\$ to \$0.0 / \\text{1k words}\$.

---

## Repository Structure

upstage/

├── README.md                      \# Primary project documentation

├── AGENT.md                       \# Autonomous agent & LLM developer guide

├── dracor\_shakespeare.db          \# SQLite database containing 37 canonical plays

├── canonical\_corpus\_builder.py    \# DraCor TEI-XML parser & database compiler

├── tei\_dracor\_parser.py           \# Stage event & character network extractor

├── network\_analysis.py            \# Degree & betweenness centrality calculator

├── epistemic\_store.py             \# Dual-Stream Epistemic Store & negative ban-lists

├── knowledge\_masking.py           \# Leakage detection & entity masking utilities

├── actantial\_matcher.py           \# Cross-play role recommendation engine

├── stylometrics.py                \# Burrows' Delta, Cosine Delta & T/V pronoun auditor

├── dialogue\_generator.py          \# 4-tier prompt envelope compiler

├── critic\_reflection.py           \# Self-healing reflection & critique loop

├── pipeline.py                    \# End-to-end transplantation orchestrator

├── run\_full\_evaluation.py         \# Comprehensive evaluation suite across all 4 benchmarks

├── upstage\_ui.py                  \# Standalone local HTTP server with REST API

├── upstage\_web\_app.html           \# Portable single-page interactive UI

├── test\_ui\_server.py              \# Automated unit tests for UI server & API endpoints

├── generate\_latex\_figures.py      \# Publication vector plot generation script

└── latex\_manuscript/              \# Camera-ready conference manuscript

    ├── main.tex                   \# Two-column publication source

    ├── main.pdf                   \# Compiled 5-page research paper

    ├── upstage\_references.bib     \# Formatted BibTeX bibliography

    └── figures/                   \# High-resolution publication figures (PNG/PDF)

---

## Quick Start

### Prerequisites

- Python 3.10 or higher.  
- Standard libraries: `sqlite3`, `json`, `http.server`, `math`, `re`.  
- Optional (for figure generation): `matplotlib`, `numpy`, `pypdf`.

### Running Tests & Benchmarks

Run the complete evaluation suite across all four canonical benchmarks:

python3 run\_full\_evaluation.py

Run unit tests for individual components:

python3 test\_actantial\_matcher.py

python3 test\_epistemic\_store.py

python3 test\_stylometrics.py

python3 test\_ui\_server.py

### Launching the Interactive Local UI

You can interact with the virtual theater studio in two modes:

1. **Dynamic Local Server (REST API \+ UI):**  
     
   python3 upstage\_ui.py \--port 8080  
     
   Open your browser to `http://localhost:8080`.  
     
2. **Portable Offline Web Application:** Open `upstage_web_app.html` directly in any web browser without starting a server:  
     
   open upstage\_web\_app.html

---

## REST API Reference

The local server exposes the following endpoints:

| Endpoint | Method | Parameters | Description |
| :---- | :---: | :---- | :---- |
| `/` | `GET` | None | Serves the interactive Single-Page Application |
| `/api/benchmarks` | `GET` | None | Returns scenes, counterfactual turns, and CLS audits for all 4 benchmarks |
| `/api/plays` | `GET` | None | Lists all 37 canonical plays with word counts, speaker counts, and network metrics |
| `/api/recommender` | `GET` | `donor=NAME` | Recommends top target roles minimizing \$\\Delta\_{\\text{centrality}}\$ |
| `/api/simulate_turn` | `POST` | JSON payload | Executes prompt compilation, LLM simulation, and CLS auditing |

---

## License

This project is licensed under the MIT License. See the [LICENSE](http://LICENSE) file for details.