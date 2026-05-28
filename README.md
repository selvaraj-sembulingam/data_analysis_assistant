# 🔮 Data Analysis Assistant

An enterprise-grade conversational analytics system that transforms natural language business questions into explainable SQL workflows with full row-level lineage tracking, session memory, and auditable execution artifacts.

---

# Overview

This project demonstrates how Large Language Models (LLMs) can be combined with analytical databases to build a trustworthy AI-powered data assistant for enterprise environments.

The assistant allows users to:

* Upload CSV or Excel datasets
* Ask analytical questions in natural language
* Automatically generate SQL queries
* Execute analytics against DuckDB
* Produce conversational answers
* Generate full lineage and audit trails
* Persist session-aware conversational context
* Export intermediate reporting artifacts into a sandboxed virtual file system

The architecture emphasizes:

* **Explainability**
* **Auditability**
* **Data provenance**
* **LLM safety controls**
* **Session continuity**
* **Enterprise governance**

---

# Problem This Solves

Traditional BI systems require users to know SQL, table structures, and reporting tools.

Modern LLM systems can generate SQL, but most fail in enterprise environments because they lack:

* Data lineage
* Audit logs
* Query explainability
* Provenance tracking
* Hallucination prevention
* Stateful conversation memory

This project addresses those gaps by building a fully auditable conversational analytics engine.

---

# High-Level Architecture

```text
User Question
      ↓
Routing + Validation Agent
      ↓
SQL Translation Agent
      ↓
DuckDB Execution Engine
      ↓
Lineage & Provenance Tracker
      ↓
Natural Language Synthesis Agent
      ↓
Virtual File System Storage
      ↓
Interactive Streamlit Dashboard
```

---

# Core Components

# 1. Virtual File System (VFS)

## Purpose

Implements an in-memory sandboxed file storage layer for session artifacts.

## Responsibilities

* Store generated CSV outputs
* Store lineage manifests
* Isolate user sessions
* Simulate enterprise reporting storage

## Key Features

* Session-scoped storage
* No disk dependency for audit assets
* Lightweight and fast

```python
class VirtualFileSystem:
```

---

# 2. Stateful Auditable Assistant

This is the core orchestration engine.

```python
class StatefulAuditableAssistant:
```

It combines:

* LLM orchestration
* SQL generation
* Query execution
* Data provenance
* Conversational memory
* Audit logging

---

# 3. DuckDB Analytical Warehouse

## Why DuckDB?

DuckDB was selected because it provides:

* Fast analytical queries
* In-memory execution
* Pandas interoperability
* Zero infrastructure setup
* Excellent CSV ingestion

## Warehouse Initialization

Uploaded datasets are automatically transformed into relational tables.

Each row receives a synthetic lineage key:

```sql
row_number() OVER () - 1 AS __lineage_row_id
```

This enables deterministic provenance tracking.

---

# 4. Schema Intelligence Layer

During ingestion, the engine automatically builds metadata catalogs:

## Captured Metadata

### Schema Fields

```json
"schema_fields": [...]
```

### Categorical Values

```json
"valid_categorical_values": {...}
```

### Numeric Ranges

```json
"valid_numeric_ranges": {...}
```

This metadata becomes the grounding context for the LLM.

---

# 5. Routing & Validation Agent

## Goal

Prevent hallucinations before SQL generation.

The routing agent determines whether a question:

| Route State       | Meaning                                     |
| ----------------- | ------------------------------------------- |
| CAN_ANSWER        | Query can be answered from available schema |
| META_CONVERSATION | Conversational/history request              |
| ABSTAIN           | Unsupported or hallucination-prone query    |

---

## Example

### Valid Question

> "Which stores sold the highest quantity last quarter?"

→ `CAN_ANSWER`

### Unsupported Question

> "What is the customer sentiment score?"

→ `ABSTAIN`

because no such metric exists in the schema catalog.

---

# 6. SQL Translation Agent

This component converts natural language into executable DuckDB SQL.

## Important Design Decision

The SQL generator intentionally avoids aggregation functions.

Instead of:

```sql
SUM(revenue)
GROUP BY region
```

the assistant fetches raw rows first.

Why?

Because enterprise lineage systems require:

* Exact source rows
* Traceable transformations
* Reproducibility

Aggregations are computed later in Python where provenance remains observable.

---

# 7. Lineage Tracking System

This is the most important architectural feature.

## What Gets Tracked?

* Source files
* Source columns
* Row offsets
* Query execution plans
* Intermediate outputs
* Transformation logic

---

## Lineage Modes

### Point Lineage

Tracks exact cell-level origins.

Example:

```text
Revenue value originated from:
sales.csv → row 42 → column "Revenue"
```

---

### Execution Recipe Lineage

Used when outputs derive from multiple rows or tables.

Example:

```text
Derived from rows [14, 18, 29]
across sales.csv and stores.csv
```

---

# 8. Logical Query Plan Extraction

The assistant also captures simplified DuckDB execution plans.

```python
EXPLAIN <query>
```

This provides transparency into:

* Table scans
* Filters
* Joins
* Projections

---

# 9. Conversational Memory

Each session maintains persistent state:

```python
self.session_memory
```

This allows follow-up questions like:

> "What about only the west region?"

without restating previous context.

---

# 10. Natural Language Synthesis

After SQL execution:

1. Result rows are converted to JSON
2. Gemini synthesizes a professional answer
3. Responses remain grounded strictly in verified rows

This prevents unsupported claims.

---

# Streamlit Frontend

The Streamlit layer provides an enterprise-style conversational dashboard.

## Features

### Multi-file Upload

Supports:

* CSV
* Excel workbooks
* Multi-sheet extraction

---

### Conversational Chat Interface

Users interact naturally with the warehouse.

---

### Lineage Explorer

Displays:

* Source files
* Row offsets
* SQL plans
* Dataframe previews
* Provenance summaries

---

### Virtual File Inspector

Allows inspection of:

* Generated CSV outputs
* Audit manifests
* Session artifacts

---

# Example Workflow

## User Input

> "Show total sales for electronics products in California"

## Data Source
https://www.kaggle.com/datasets/amangarg08/apple-retail-sales-dataset

This dataset contains over 1 million rows of Apple Retail Sales data. It includes information on products, stores, sales transactions, and warranty claims across various Apple retail locations worldwide.

The dataset is designed to reflect real-world business scenarios — including multiple product categories, regional sales variations, and customer service data — making it suitable for end-to-end data analytics and machine learning projects.

---

## System Pipeline

### Step 1 — Routing

Validate whether:

* `sales`
* `products`
* `California`
* `electronics`

exist in metadata.

---

### Step 2 — SQL Translation

Generate filtered SQL.

---

### Step 3 — Query Execution

Run against DuckDB.

---

### Step 4 — Provenance Extraction

Track:

* Source rows
* Source files
* Involved columns

---

### Step 5 — Natural Language Synthesis

Generate business-readable answer.

---

### Step 6 — Artifact Generation

Create:

* CSV snapshot
* JSON manifest
* Execution trace

inside VFS storage.

---

# Enterprise Design Principles

# 1. Explainable AI

Every number can be traced back to source rows.

---

# 2. Hallucination Resistance

The router abstains when schema support is missing.

---

# 3. Governance-First Architecture

All outputs generate audit metadata automatically.

---

# 4. Stateless Infrastructure with Stateful Sessions

Backend remains lightweight while preserving user context.

---

# 5. Data-Centric LLM Design

The LLM never operates without schema grounding.

---

# Technical Stack

| Component       | Technology       |
| --------------- | ---------------- |
| LLM             | Gemini 2.5 Flash |
| Query Engine    | DuckDB           |
| UI Layer        | Streamlit        |
| Data Processing | Pandas           |
| Storage         | In-memory VFS    |
| Language        | Python           |

---

# Why This Project Is Interesting

This project goes beyond a basic “chat with CSV” demo.

It introduces enterprise-grade capabilities including:

* Provenance tracking
* Query explainability
* Auditable analytics
* Conversational memory
* Safe routing logic
* Multi-source joins
* Artifact persistence

It demonstrates understanding of:

* LLM orchestration
* Analytical databases
* AI governance
* Stateful systems
* Enterprise software architecture
* Human-AI interaction patterns

---

# Future Improvements

## Potential Enhancements


### Vector Retrieval Layer

* Semantic schema search
* Documentation grounding

### Column-Level Access Governance

* PII masking
* Compliance enforcement

### Visualization Layer

* Automatic chart generation
* Dashboard synthesis

### Multi-Agent Orchestration

Dedicated agents for:

* SQL optimization
* Risk detection
* Data quality validation

---

# How to Run

## Install Dependencies

```bash
pip install streamlit duckdb pandas google-generativeai openpyxl
```

---

## Start the Application

```bash
streamlit run app.py
```

---

# Sample Questions

```text
What is the total quantity of 'MacBook Air (M1)' sold across all sales records?
```

```text
What is the total quantity of all products sold across all stores located in the United States?
```

```text
Which store names in the United Kingdom have sold the 'MacBook Pro', and what was the total quantity sold across those stores?
```

```text
What is the net profit margin performance and customer satisfaction score for Android smartphones in 2025?
```

---

# Key Takeaways

This project showcases how to build trustworthy AI systems for enterprise analytics by combining:

* LLM reasoning
* Relational query engines
* Data lineage
* Audit systems
* Stateful conversational UX

The result is a conversational BI platform that is not only intelligent, but also explainable and governable.



# Coreworks AI 
Honestly, as an AI engineer who spends all day worrying about non-deterministic outputs, spending 15 minutes with Coreworks was incredibly refreshing. Most conversational BI prototypes out there are built like hand-wavy wrappers that dump a whole spreadsheet into a context window, cross their fingers, and pray the LLM does the math right—which, surprise, it rarely does at scale. Coreworks feels like it was actually designed by engineers who understand production realities. The separation of concerns between intent routing, data pulling, and document compilation is exactly how you have to build these things if you care about latency and token budgets. I love that it doesn't try to force the model to play calculator; instead, it uses the LLM as an orchestrator and lets a proper structured layer do the heavy lifting. The focus on ironclad row-level citations and programmatic abstention instead of letting the AI guess or extrapolate is the exact type of engineering discipline needed to make business users actually trust these systems.

### 📊 Extending to PPT and Report Generation

Because the engine functions strictly as an **Artifact Factory**, it decouples calculation from document formatting. On every turn, the system dumps a static, verified output pair into the Virtual File System workspace: `query_txn_..._data.csv` (the filtered data matrix) and `query_txn_..._manifest.json` (the exact generation recipe). 

```text
[ VFS Sandbox Vault ]
   ├── query_txn_A1B2_data.csv      ──► [ Native PPTX Chart Engine ] ──► (Generates Bar/Line Charts)
   └── query_txn_A1B2_manifest.json ──► [ Layout Templates Builder ] ──► (Paints Slide Titles & Audit Footnotes)
