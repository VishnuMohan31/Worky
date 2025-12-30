# Chat Assistant Architecture - Knowledge Transfer Document

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Module Details](#module-details)
4. [Data Flow](#data-flow)
5. [External Dependencies](#external-dependencies)
6. [Configuration](#configuration)
7. [Database Schema](#database-schema)
8. [API Endpoints](#api-endpoints)
9. [Security & RBAC](#security--rbac)
10. [Monitoring & Metrics](#monitoring--metrics)
11. [Troubleshooting](#troubleshooting)
12. [Development Guide](#development-guide)

---

## Overview

The Worky Chat Assistant is an AI-powered natural language interface that enables users to:
- Query project data using natural language
- Execute safe write operations (reminders, status updates, comments)
- Navigate to entities via deep links
- Generate reports and analytics
- Maintain conversation context across sessions

**Key Features:**
- Intent classification with LLM fallback
- Strict RBAC enforcement at data layer
- Session management with Redis
- Comprehensive audit logging with PII masking
- Prometheus metrics for observability
- Graceful degradation when LLM unavailable

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│                   HTTP/REST API Calls                        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   API Layer (FastAPI)                        │
│              /api/v1/chat/* endpoints                        │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              ChatService (Orchestrator)                      │
│  - Coordinates all sub-services                              │
│  - Manages request lifecycle                                 │
│  - Error handling & fallback                                 │
└──┬────────┬────────┬────────┬────────┬────────┬────────────┘
   │        │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Session│ │Intent│ │ Data │ │ LLM  │ │Action│ │Audit │
│Service│ │Class.│ │Retr. │ │Serv. │ │Handlr│ │Serv. │
└───┬───┘ └──────┘ └───┬──┘ └───┬──┘ └───┬──┘ └───┬──┘
    │                  │        │        │        │
    ▼                  ▼        ▼        ▼        ▼
┌───────┐         ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Redis │         │PostgreSQL│ │OpenAI API│ │PostgreSQL│
│Session│         │  (Data)  │ │   (LLM)  │ │ (Audit)  │
└───────┘         └──────────┘ └──────────┘ └──────────┘
```

### Component Responsibilities

| Component | Responsibility | Storage |
|-----------|---------------|---------|
| **API Layer** | HTTP endpoints, auth, validation | N/A |
| **ChatService** | Orchestration, error handling | N/A |
| **SessionService** | Conversation context, history | Redis |
| **IntentClassifier** | Intent detection, entity extraction | N/A |
| **DataRetriever** | RBAC-enforced data queries | PostgreSQL |
| **LLMService** | Natural language generation | OpenAI API |
| **ActionHandler** | Safe write operations | PostgreSQL |
| **AuditService** | Compliance logging, PII masking | PostgreSQL |
| **MetricsService** | Observability metrics | Prometheus |

---

## Module Details

### 1. API Layer
**File:** `api/app/api/v1/endpoints/chat.py`

**Endpoints:**

```python
POST   /api/