# Intent Classifier Service Guide

## Overview

The Intent Classifier Service is responsible for analyzing user queries to determine intent type, extract entities, and provide confidence scoring. It uses regex patterns for common cases and can fall back to LLM for ambiguous queries.

## Features

### 1. Intent Type Detection

The classifier identifies five types of user intents:

- **QUERY**: Information retrieval (e.g., "Show me tasks for Project X")
- **ACTION**: Perform operation (e.g., "Set reminder for task TSK-123")
- **NAVIGATION**: Request deep link (e.g., "Open bug BUG-456")
- **REPORT**: Generate insights (e.g., "Show task distribution by status")
- **CLARIFICATION**: Follow-up or ambiguous query (e.g., "What?", "Can you explain?")

### 2. Entity Extraction

The classifier extracts the following entity types using regex patterns:

- **Project IDs**: PRJ-xxx
- **Task IDs**: TSK-xxx
- **Subtask IDs**: SUB-xxx
- **Bug IDs**: BUG-xxx
- **User Story IDs**: STY-xxx
- **Use Case IDs**: USC-xxx
- **Test Case IDs**: TST-xxx
- **Program IDs**: PRG-xxx

Additionally, it can extract:
- Entity names from quoted strings (e.g., "Project Alpha")
- Status values (not started, in progress, completed, etc.)
- Priority values (low, medium, high, critical, urgent)

### 3. Temporal Context Extraction

The classifier recognizes temporal references:

- **Relative dates**: today, tomorrow, yesterday
- **Week references**: this week, last week, next week
- **Month references**: this month, last month
- **Specific dates**: Various formats (YYYY-MM-DD, MM/DD/YYYY, etc.)

### 4. Confidence Scoring

The classifier provides a confidence score (0.0 to 1.0) based on:
- Keyword pattern matches
- Entity presence and count
- Query structure and complexity
- Conversation context

### 5. LLM Fallback

For ambiguous or complex queries (confidence < 0.7), the classifier can fall back to LLM for improved accuracy.

## Usage

### Basic Classification

```python
from app.services.intent_classifier import get_intent_classifier

classifier = get_intent_classifier()

# Classify a query
intent = await classifier.classify(
    query="Show me all tasks for project PRJ-100",
    context=None
)

print(f"Intent Type: {intent.intent_type}")
print(f"Confidence: {intent.confidence}")
print(f"Entities: {len(intent.entities)}")
```

### With Conversation Context

```python
# Provide context for better classification
context = {
    'last_intent': IntentType.QUERY,
    'mentioned_entities': [
        {'entity_type': 'project', 'entity_id': 'PRJ-100'}
    ]
}

intent = await classifier.classify(
    query="Show me the tasks for it",
    context=context
)
```

### With LLM Fallback

```python
# Set LLM service for fallback
from app.services.llm_service import get_llm_service

classifier.set_llm_service(get_llm_service())

# Classify with automatic LLM fallback for ambiguous queries
intent = await classifier.classify_with_llm_fallback(
    query="What's the status of things we discussed?",
    context=context
)
```

### Extract Action Parameters

```python
# For ACTION intents, extract specific parameters
intent = await classifier.classify(
    query="Set a reminder for task TSK-123 tomorrow at 2pm"
)

if intent.intent_type == IntentType.ACTION:
    params = classifier.extract_action_parameters(
        query="Set a reminder for task TSK-123 tomorrow at 2pm",
        intent=intent
    )
    print(f"Action Type: {params.get('action_type')}")
    print(f"Remind At: {params.get('remind_at')}")
```

## Intent Object Structure

```python
@dataclass
class Intent:
    intent_type: IntentType          # Classified intent type
    entities: List[ExtractedEntity]  # Extracted entities
    confidence: float                # Confidence score (0.0-1.0)
    raw_query: str                   # Original query
    normalized_query: str            # Normalized query
    temporal_context: Dict           # Temporal information
    requires_llm: bool               # Whether LLM fallback is recommended
```

## Extracted Entity Structure

```python
@dataclass
class ExtractedEntity:
    entity_type: EntityType          # Type of entity
    entity_id: Optional[str]         # Entity ID (e.g., TSK-123)
    entity_name: Optional[str]       # Entity name (e.g., "Project Alpha")
    raw_text: Optional[str]          # Raw text from query
```

## Examples

### Query Intent

```python
# Input: "Show me all tasks assigned to John"
# Output:
Intent(
    intent_type=IntentType.QUERY,
    entities=[],
    confidence=0.7,
    temporal_context={},
    requires_llm=False
)
```

### Navigation Intent

```python
# Input: "Open task TSK-123"
# Output:
Intent(
    intent_type=IntentType.NAVIGATION,
    entities=[
        ExtractedEntity(
            entity_type=EntityType.TASK,
            entity_id="TSK-123",
            raw_text="TSK-123"
        )
    ],
    confidence=0.9,
    temporal_context={},
    requires_llm=False
)
```

### Action Intent with Temporal Context

```python
# Input: "Set a reminder for bug BUG-456 tomorrow"
# Output:
Intent(
    intent_type=IntentType.ACTION,
    entities=[
        ExtractedEntity(
            entity_type=EntityType.BUG,
            entity_id="BUG-456",
            raw_text="BUG-456"
        )
    ],
    confidence=0.85,
    temporal_context={
        'date_filter': 'tomorrow',
        'start_date': datetime.date(2025, 11, 29),
        'end_date': datetime.date(2025, 11, 29)
    },
    requires_llm=False
)
```

### Report Intent

```python
# Input: "Show me task distribution by status this week"
# Output:
Intent(
    intent_type=IntentType.REPORT,
    entities=[],
    confidence=0.8,
    temporal_context={
        'date_filter': 'this_week',
        'start_date': datetime.date(2025, 11, 24),
        'end_date': datetime.date(2025, 11, 30)
    },
    requires_llm=False
)
```

### Complex Query Requiring LLM

```python
# Input: "Compare the progress of Project Alpha and Project Beta, 
#         and tell me which one is behind schedule"
# Output:
Intent(
    intent_type=IntentType.QUERY,  # Initial classification
    entities=[
        ExtractedEntity(
            entity_type=EntityType.PROJECT,
            entity_name="Project Alpha",
            raw_text="Project Alpha"
        ),
        ExtractedEntity(
            entity_type=EntityType.PROJECT,
            entity_name="Project Beta",
            raw_text="Project Beta"
        )
    ],
    confidence=0.6,
    temporal_context={},
    requires_llm=True  # Will trigger LLM fallback
)
```

## Configuration

The intent classifier uses settings from `app.core.config`:

```python
# Chat Configuration
CHAT_MAX_QUERY_LENGTH: int = 2000  # Maximum query length
```

## Integration with Other Services

The intent classifier is designed to work with:

1. **Session Service**: Receives conversation context for better classification
2. **LLM Service**: Falls back to LLM for ambiguous queries
3. **Data Retriever**: Provides extracted entities for data retrieval
4. **Action Handler**: Provides action parameters for execution

## Performance Considerations

- **Rule-based classification** is fast (< 10ms) and handles 70-80% of queries
- **LLM fallback** adds latency (1-3 seconds) but improves accuracy for complex queries
- **Entity extraction** uses compiled regex patterns for efficiency
- **Temporal parsing** handles common date formats without external libraries

## Error Handling

The classifier is designed to be fault-tolerant:

- Invalid queries default to `IntentType.QUERY` with confidence 0.5
- Failed entity extraction returns empty list
- LLM fallback failures fall back to rule-based classification
- All errors are logged for monitoring

## Testing

See `api/tests/services/test_intent_classifier.py` for comprehensive unit tests covering:

- Intent type classification accuracy
- Entity extraction for all entity types
- Temporal context parsing
- Confidence scoring
- LLM fallback behavior
- Edge cases and error handling
