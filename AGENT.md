# Upstage: Autonomous Agent & Developer Guide (`AGENT.md`)

This guide outlines the architectural contracts, execution protocols, prompt envelope specifications, and self-healing mechanisms governing the **Upstage** framework. Autonomous agents and LLM developers operating within this repository must adhere to the conventions defined below.

---

## 1\. System Mission & Agent Mandate

The primary objective of **Upstage** is executing **cross-play dramatic character transplantation** with high historical-literary fidelity.

### Core Invariants:

1. **Mathematical Actantial Matching:** Never transplant a character into an incompatible structural role. Centrality Gap \$\\Delta\_{\\text{centrality}} \= |C\_{\\text{deg}}(D) \- C\_{\\text{deg}}(T)| \+ \\lambda |C\_{\\text{bet}}(D) \- C\_{\\text{bet}}(T)|\$ must satisfy \$\\Delta\_{\\text{centrality}} \\le 0.15\$.  
2. **Strict Epistemic Isolation:** The transplanted character must never exhibit awareness of their native donor plot, future events, or unrevealed target plot secrets. Narrative leakage \$L\_{\\text{leak}}\$ must strictly equal **\$0.0%\$**.  
3. **Socio-Pragmatic Register Integrity:** Early Modern English (EME) pronominal address rules must be observed. Lower-to-higher status interactions require formal \$V\$-forms (*you/your*); higher-to-lower, intimate, or licensed fools require informal \$T\$-forms (*thou/thee/thy*).  
4. **Zero External Dependencies:** Core engines must use Python standard library modules (`sqlite3`, `http.server`, `math`, `re`, `json`). Do not introduce runtime pip/npm dependencies.

---

## 2\. Architecture & Data Contracts

### 2.1 Database Schema (`dracor_shakespeare.db`)

The SQLite database contains all 37 canonical Shakespeare plays extracted from DraCor TEI-XML corpora:

\-- Play metadata

CREATE TABLE plays (

    id TEXT PRIMARY KEY,           \-- e.g. "hamlet", "king-lear"

    title TEXT NOT NULL,          \-- e.g. "The Tragedy of Hamlet"

    genre TEXT NOT NULL,          \-- "Tragedy", "Comedy", "History", "Romance"

    year INTEGER,                 \-- Approximate composition year

    word\_count INTEGER,

    speaker\_count INTEGER,

    network\_density REAL,

    clustering\_coeff REAL

);

\-- Character metadata & network metrics

CREATE TABLE characters (

    id TEXT PRIMARY KEY,           \-- e.g. "falstaff\_1h4", "fool\_lear"

    play\_id TEXT NOT NULL,

    name TEXT NOT NULL,

    degree\_centrality REAL,

    betweenness\_centrality REAL,

    word\_count INTEGER,

    speech\_count INTEGER,

    FOREIGN KEY(play\_id) REFERENCES plays(id)

);

\-- Dialogue speeches

CREATE TABLE speeches (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    play\_id TEXT NOT NULL,

    act INTEGER,

    scene INTEGER,

    speaker\_id TEXT NOT NULL,

    speaker\_name TEXT NOT NULL,

    text TEXT NOT NULL,

    verse\_type TEXT,              \-- "verse", "prose"

    FOREIGN KEY(play\_id) REFERENCES plays(id)

);

\-- Social co-presence graph edges

CREATE TABLE co\_occurrences (

    play\_id TEXT NOT NULL,

    character\_a TEXT NOT NULL,

    character\_b TEXT NOT NULL,

    weight INTEGER DEFAULT 1,     \-- Number of shared scenes

    PRIMARY KEY(play\_id, character\_a, character\_b)

);

---

## 3\. The 4-Tier Prompt Envelope

When generating counterfactual turns, the LLM must be wrapped in a structured 4-tier prompt envelope (`dialogue_generator.py`):

\+-----------------------------------------------------------------------+

| TIER 1: SYSTEM PERSONA (Voice DNA)                                    |

| \- Lexical profile, rhetorical devices, prose/verse habit              |

| \- Idiomatic tropes, sociolect, rhythmic tendencies                     |

\+-----------------------------------------------------------------------+

| TIER 2: EPISTEMIC ISOLATION (Boundary & Ban-List)                     |

| \- Strict temporal horizon: Act X, Scene Y of Target Play             |

| \- FORBIDDEN ENTITIES (Negative Ban-List B\_D): Specific names/events   |

|   from donor play that MUST NOT be mentioned under any circumstances  |

\+-----------------------------------------------------------------------+

| TIER 3: PRECEDING DIALOGUE CONTEXT                                    |

| \- Last N turns of the scene leading up to the target slot             |

| \- Direct cue lines and interlocutor speaker identity                  |

\+-----------------------------------------------------------------------+

| TIER 4: ACTANTIAL & SOCIOLINGUISTIC DIRECTIVES                        |

| \- Immediate scene objective A(T, s) (e.g. counsel, deflect, woo)      |

| \- Prescribed EME Address Mode: T-form (thou) vs V-form (you)           |

| \- Verse constraint: Blank verse (iambic pentameter) or rhythmic prose |

\+-----------------------------------------------------------------------+

### Template Format:

\[SYSTEM: PERSONA DEFINITION\]

You are embodying the dramatic persona of {donor\_name} from {donor\_play}.

Voice DNA: {voice\_summary}

Rhetorical traits: {rhetorical\_devices}

\[EPISTEMIC BOUNDARY CONSTRAINTS\]

You are physically and narratively situated inside {target\_play}, Act {act}, Scene {scene}.

Knowledge Horizon: You only know what has transpired in this play up to this scene.

NEGATIVE BAN-LIST: You have NEVER heard of, and MUST NEVER mention:

{negative\_ban\_list}

\[PRECEDING DIALOGUE\]

{preceding\_turns}

\[ACTANTIAL & SOCIOLINGUISTIC DIRECTIVES\]

Role in scene: {actantial\_intent}

Interlocutor: {interlocutor\_name} (Social Rank: {interlocutor\_rank})

Pronominal Address: You MUST address the interlocutor using {address\_mode}.

Output ONLY the spoken dialogue turn. Do not break character.

---

## 4\. The Critic-Reflection Self-Healing Protocol

Draft utterances \$u^{(0)}\$ must pass an automated multi-stage audit before final emission (`critic_reflection.py`).

### 4.1 Audit Verification Stages

1. **Epistemic Leakage Check (\$L\_{\\text{leak}}\$):**  
   * Scans text for token matches or semantic equivalents in negative ban-list \$\\mathcal{B}\_D\$.  
   * *Threshold:* Strict \$0\$ matches permitted.  
2. **Anachronism Lexical Filter:**  
   * Curated dictionary of post-Shakespearean concepts (e.g., *psychology, modern, society, complex, subjective, stress*).  
   * *Threshold:* \$0\$ anachronisms permitted.  
3. **Sociolinguistic Pronoun Audit (\$\\rho\_{T/V}\$):**  
   * Computes ratio \$\\rho\_{T/V} \= \\frac{\\sum T\\text{-forms}}{\\sum V\\text{-forms} \+ \\epsilon}\$.  
   * If formal deference is required (\$V\$-mode) and \$\\rho\_{T/V} \> 0.20\$, violation is flagged.  
   * If intimacy or condescension is required (\$T\$-mode) and \$\\rho\_{T/V} \< 1.00\$, violation is flagged.

### 4.2 Reflection Feedback Loop

When violations are detected, the Critic Agent appends a structured critique to the prompt envelope and requests a self-correction pass (\$u^{(k+1)}\$):

\[CRITIC AUDIT FAILURE \- REFLECTION REQUIRED\]

Your previous response contained the following violations:

1\. EPISTEMIC LEAKAGE: Mentioned forbidden donor entity "{forbidden\_entity}". Remove all references to {donor\_play}.

2\. ANACHRONISM: Used non-period word "{anachronism}". Replace with Early Modern English equivalent.

3\. SOCIOLINGUISTIC MISMATCH: Addressed a superior using informal "thou/thee". Replace with deferential "you/your".

Rewrite your response immediately, eliminating every violation while preserving the rhetorical voice of {donor\_name}.

---

## 5\. Stylometric Metrics Specification

To verify stylometric fidelity, agents must utilize the mathematical implementations in `stylometrics.py`:

### Burrows' Delta (\$\\Delta\$)

Measures function-word frequency divergence across the top \$n=100\$ Most Frequent Words (MFW) normalized by canon-wide \$z\$-scores: \$\$\\Delta(u, \\mathcal{V}*D) \= \\frac{1}{n} \\sum*{i=1}^n \\left| \\frac{f\_i(u) \- \\mu\_i}{\\sigma\_i} \- \\frac{f\_i(\\mathcal{V}\_D) \- \\mu\_i}{\\sigma\_i} \\right|\$\$

* **Authorial / Idiolectal Target:** \$\\Delta \\le 0.80\$.  
* **Target Role Separation:** \$\\Delta(u, \\mathcal{V}\_T) \\ge 1.20\$.

---

## 6\. Extending Upstage

### 6.1 Adding a New Benchmark Pair

To register a new transplantation benchmark in `benchmark_experiments.py`:

1. Define donor play and target play in `dracor_shakespeare.db`.  
2. Extract the donor's speech corpus to establish baseline MFW frequencies.  
3. Define the target scene number, replaced speaker ID, and preceding turns.  
4. Construct the negative ban-list \$\\mathcal{B}\_D\$ (all proper nouns, locations, and unique historical events from donor play).  
5. Specify the actantial goal and target \$T/V\$ address mode.

### 6.2 Adding Live LLM API Keys

To connect real-time LLM inference (e.g. Gemini 1.5 Pro) in `upstage_ui.py`:

1. Set the environment variable: `export GEMINI_API_KEY="your-api-key"`.  
2. Update the `simulate_llm_turn()` handler in `upstage_ui.py` to route compiled 4-tier prompt envelopes to the live model endpoint.  
3. Stream the raw draft through `CriticAgent.audit()` and execute the reflection loop if violations occur.

---

## 7\. Quality Assurance Checklist for Autonomous Agents

Before committing changes or deploying simulated scenes, verify:

- [ ] Database queries use parameterized SQL to avoid syntax errors.  
- [ ] All 4 canonical benchmarks pass evaluation via `python3 run_full_evaluation.py`.  
- [ ] Unit tests pass: `python3 test_ui_server.py`, `python3 test_stylometrics.py`.  
- [ ] No local filesystem paths are leaked in user-facing responses.  
- [ ] Any generated documentation or academic papers are compiled and stored in the Google Drive project folder.