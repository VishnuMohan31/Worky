"""
Intent Classification Service for Chat Assistant

This service analyzes user queries to determine intent type, extract entities,
and provide confidence scoring. It uses regex patterns for common cases and
falls back to LLM for ambiguous queries.
"""

import re
import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from app.schemas.chat import IntentType, EntityType
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEntity:
    """Represents an extracted entity from user query"""
    entity_type: EntityType
    entity_id: Optional[str] = None
    entity_name: Optional[str] = None
    raw_text: Optional[str] = None


@dataclass
class Intent:
    """Represents classified intent with entities and confidence"""
    intent_type: IntentType
    entities: List[ExtractedEntity]
    confidence: float  # 0.0 to 1.0
    raw_query: str
    normalized_query: str
    temporal_context: Optional[Dict[str, Any]] = None
    requires_llm: bool = False


class IntentClassifier:
    """Service for classifying user intents and extracting entities"""
    
    # Entity ID patterns
    PATTERNS = {
        'project_id': re.compile(r'\b(PRJ-\d+)\b', re.IGNORECASE),
        'task_id': re.compile(r'\b(TSK-\d+)\b', re.IGNORECASE),
        'subtask_id': re.compile(r'\b(SUB-\d+)\b', re.IGNORECASE),
        'bug_id': re.compile(r'\b(BUG-\d+)\b', re.IGNORECASE),
        'story_id': re.compile(r'\b(STY-\d+)\b', re.IGNORECASE),
        'usecase_id': re.compile(r'\b(USC-\d+)\b', re.IGNORECASE),
        'test_case_id': re.compile(r'\b(TST-\d+)\b', re.IGNORECASE),
        'program_id': re.compile(r'\b(PRG-\d+)\b', re.IGNORECASE),
    }
    
    # Date patterns
    DATE_PATTERNS = {
        'today': re.compile(r'\btoday\b', re.IGNORECASE),
        'tomorrow': re.compile(r'\btomorrow\b', re.IGNORECASE),
        'yesterday': re.compile(r'\byesterday\b', re.IGNORECASE),
        'this_week': re.compile(r'\bthis\s+week\b', re.IGNORECASE),
        'last_week': re.compile(r'\blast\s+week\b', re.IGNORECASE),
        'next_week': re.compile(r'\bnext\s+week\b', re.IGNORECASE),
        'this_month': re.compile(r'\bthis\s+month\b', re.IGNORECASE),
        'last_month': re.compile(r'\blast\s+month\b', re.IGNORECASE),
        'specific_date': re.compile(
            r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b'
        ),
    }
    
    # Intent keyword patterns
    INTENT_KEYWORDS = {
        IntentType.QUERY: [
            r'\b(show|list|find|get|what|which|who|when|where|how many|count|search)\b',
            r'\b(tell me|give me|display)\b',
        ],
        IntentType.ACTION: [
            r'\b(set|create|add|update|change|modify|assign|link|attach)\b',
            r'\b(remind|reminder|schedule)\b',
            r'\b(comment|note)\b',
        ],
        IntentType.NAVIGATION: [
            r'\b(open|view|show me|go to|navigate to|take me to)\b',
            r'\b(details|detail page)\b',
        ],
        IntentType.REPORT: [
            r'\b(report|summary|overview|statistics|stats|metrics|analytics)\b',
            r'\b(distribution|breakdown|analysis|trend)\b',
            r'\b(how is|how are|status of)\b',
        ],
        IntentType.CLARIFICATION: [
            r'\b(what do you mean|can you explain|clarify|more details)\b',
            r'\b(huh|what|pardon|sorry)\b',
            r'^(yes|no|yeah|nope|ok|okay)$',
        ],
    }
    
    # Status values
    STATUS_VALUES = [
        'not started', 'in progress', 'completed', 'blocked', 'on hold',
        'pending', 'approved', 'rejected', 'cancelled', 'archived'
    ]
    
    # Priority values
    PRIORITY_VALUES = ['low', 'medium', 'high', 'critical', 'urgent']
    
    def __init__(self):
        """Initialize the intent classifier"""
        self.llm_service = None  # Will be injected when LLM service is available
    
    def set_llm_service(self, llm_service):
        """Set LLM service for fallback classification"""
        self.llm_service = llm_service
    
    async def classify(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Intent:
        """
        Classify user query and extract entities
        
        Args:
            query: User's natural language query
            context: Optional conversation context
            
        Returns:
            Intent object with classification results
        """
        # Normalize query
        normalized_query = self._normalize_query(query)
        
        # Extract entities
        entities = self._extract_entities(normalized_query)
        
        # Extract temporal context
        temporal_context = self._extract_temporal_context(normalized_query)
        
        # Classify intent type
        intent_type, confidence = self._classify_intent_type(
            normalized_query,
            entities,
            context
        )
        
        # Determine if LLM fallback is needed
        requires_llm = confidence < 0.7 or self._is_complex_query(normalized_query)
        
        intent = Intent(
            intent_type=intent_type,
            entities=entities,
            confidence=confidence,
            raw_query=query,
            normalized_query=normalized_query,
            temporal_context=temporal_context,
            requires_llm=requires_llm
        )
        
        logger.debug(
            f"Classified intent: type={intent_type.value}, "
            f"confidence={confidence:.2f}, entities={len(entities)}, "
            f"requires_llm={requires_llm}"
        )
        
        return intent
    
    def _normalize_query(self, query: str) -> str:
        """
        Normalize query text
        
        Args:
            query: Raw query string
            
        Returns:
            Normalized query string
        """
        # Strip whitespace
        normalized = query.strip()
        
        # Remove extra spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Ensure ends with punctuation for better parsing
        if normalized and normalized[-1] not in '.!?':
            normalized += '.'
        
        return normalized
    
    def _extract_entities(self, query: str) -> List[ExtractedEntity]:
        """
        Extract entities from query using regex patterns
        
        Args:
            query: Normalized query string
            
        Returns:
            List of extracted entities
        """
        entities = []
        
        # Extract entity IDs
        entity_type_map = {
            'project_id': EntityType.PROJECT,
            'task_id': EntityType.TASK,
            'subtask_id': EntityType.SUBTASK,
            'bug_id': EntityType.BUG,
            'story_id': EntityType.USER_STORY,
            'usecase_id': EntityType.USECASE,
            'test_case_id': EntityType.TEST_CASE,
            'program_id': EntityType.PROGRAM,
        }
        
        for pattern_name, pattern in self.PATTERNS.items():
            matches = pattern.findall(query)
            if matches:
                entity_type = entity_type_map.get(pattern_name)
                if entity_type:
                    for match in matches:
                        entities.append(ExtractedEntity(
                            entity_type=entity_type,
                            entity_id=match.upper(),
                            raw_text=match
                        ))
        
        # Extract entity names (quoted strings or capitalized phrases)
        # e.g., "Project Alpha" or Project Alpha
        name_patterns = [
            re.compile(r'"([^"]+)"'),  # Quoted strings
            re.compile(r"'([^']+)'"),  # Single quoted strings
        ]
        
        for pattern in name_patterns:
            matches = pattern.findall(query)
            for match in matches:
                # Try to infer entity type from context
                entity_type = self._infer_entity_type_from_context(match, query)
                if entity_type:
                    entities.append(ExtractedEntity(
                        entity_type=entity_type,
                        entity_name=match,
                        raw_text=match
                    ))
        
        # Extract status values
        query_lower = query.lower()
        for status in self.STATUS_VALUES:
            if status in query_lower:
                # Status is metadata, not a primary entity
                # We'll include it in temporal_context instead
                pass
        
        # Extract priority values
        for priority in self.PRIORITY_VALUES:
            if priority in query_lower:
                # Priority is metadata, not a primary entity
                pass
        
        return entities
    
    def _infer_entity_type_from_context(
        self,
        entity_name: str,
        query: str
    ) -> Optional[EntityType]:
        """
        Infer entity type from surrounding context
        
        Args:
            entity_name: Name of the entity
            query: Full query string
            
        Returns:
            EntityType if inferred, None otherwise
        """
        query_lower = query.lower()
        
        # Look for type keywords near the entity name
        type_keywords = {
            EntityType.PROJECT: ['project', 'projects'],
            EntityType.TASK: ['task', 'tasks'],
            EntityType.BUG: ['bug', 'bugs', 'issue', 'issues'],
            EntityType.USER_STORY: ['story', 'stories', 'user story', 'user stories'],
            EntityType.USECASE: ['usecase', 'usecases', 'use case', 'use cases'],
            EntityType.SUBTASK: ['subtask', 'subtasks', 'sub-task', 'sub-tasks'],
            EntityType.PROGRAM: ['program', 'programs'],
            EntityType.TEST_CASE: ['test case', 'test cases', 'test'],
        }
        
        # Find the position of entity name in query
        entity_pos = query_lower.find(entity_name.lower())
        if entity_pos == -1:
            return None
        
        # Check words before and after entity name
        context_window = 50  # characters
        start = max(0, entity_pos - context_window)
        end = min(len(query_lower), entity_pos + len(entity_name) + context_window)
        context = query_lower[start:end]
        
        for entity_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in context:
                    return entity_type
        
        return None
    
    def _extract_temporal_context(self, query: str) -> Dict[str, Any]:
        """
        Extract temporal information from query
        
        Args:
            query: Normalized query string
            
        Returns:
            Dictionary with temporal context
        """
        temporal_context = {}
        
        # Check for relative dates
        today = datetime.now().date()
        
        if self.DATE_PATTERNS['today'].search(query):
            temporal_context['date_filter'] = 'today'
            temporal_context['start_date'] = today
            temporal_context['end_date'] = today
        
        elif self.DATE_PATTERNS['tomorrow'].search(query):
            tomorrow = today + timedelta(days=1)
            temporal_context['date_filter'] = 'tomorrow'
            temporal_context['start_date'] = tomorrow
            temporal_context['end_date'] = tomorrow
        
        elif self.DATE_PATTERNS['yesterday'].search(query):
            yesterday = today - timedelta(days=1)
            temporal_context['date_filter'] = 'yesterday'
            temporal_context['start_date'] = yesterday
            temporal_context['end_date'] = yesterday
        
        elif self.DATE_PATTERNS['this_week'].search(query):
            # Start of week (Monday)
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            temporal_context['date_filter'] = 'this_week'
            temporal_context['start_date'] = start_of_week
            temporal_context['end_date'] = end_of_week
        
        elif self.DATE_PATTERNS['last_week'].search(query):
            start_of_last_week = today - timedelta(days=today.weekday() + 7)
            end_of_last_week = start_of_last_week + timedelta(days=6)
            temporal_context['date_filter'] = 'last_week'
            temporal_context['start_date'] = start_of_last_week
            temporal_context['end_date'] = end_of_last_week
        
        elif self.DATE_PATTERNS['next_week'].search(query):
            start_of_next_week = today + timedelta(days=(7 - today.weekday()))
            end_of_next_week = start_of_next_week + timedelta(days=6)
            temporal_context['date_filter'] = 'next_week'
            temporal_context['start_date'] = start_of_next_week
            temporal_context['end_date'] = end_of_next_week
        
        elif self.DATE_PATTERNS['this_month'].search(query):
            start_of_month = today.replace(day=1)
            # Last day of month
            if today.month == 12:
                end_of_month = today.replace(day=31)
            else:
                end_of_month = (today.replace(month=today.month + 1, day=1) - timedelta(days=1))
            temporal_context['date_filter'] = 'this_month'
            temporal_context['start_date'] = start_of_month
            temporal_context['end_date'] = end_of_month
        
        elif self.DATE_PATTERNS['last_month'].search(query):
            if today.month == 1:
                start_of_last_month = today.replace(year=today.year - 1, month=12, day=1)
            else:
                start_of_last_month = today.replace(month=today.month - 1, day=1)
            end_of_last_month = today.replace(day=1) - timedelta(days=1)
            temporal_context['date_filter'] = 'last_month'
            temporal_context['start_date'] = start_of_last_month
            temporal_context['end_date'] = end_of_last_month
        
        # Check for specific dates
        specific_date_match = self.DATE_PATTERNS['specific_date'].search(query)
        if specific_date_match:
            date_str = specific_date_match.group(1)
            try:
                # Try different date formats
                for fmt in ['%Y-%m-%d', '%m-%d-%Y', '%d-%m-%Y', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y']:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt).date()
                        temporal_context['date_filter'] = 'specific'
                        temporal_context['start_date'] = parsed_date
                        temporal_context['end_date'] = parsed_date
                        break
                    except ValueError:
                        continue
            except Exception as e:
                logger.warning(f"Failed to parse date '{date_str}': {e}")
        
        # Extract status filter
        query_lower = query.lower()
        for status in self.STATUS_VALUES:
            if status in query_lower:
                temporal_context['status_filter'] = status
                break
        
        # Extract priority filter
        for priority in self.PRIORITY_VALUES:
            if priority in query_lower:
                temporal_context['priority_filter'] = priority
                break
        
        return temporal_context
    
    def _classify_intent_type(
        self,
        query: str,
        entities: List[ExtractedEntity],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[IntentType, float]:
        """
        Classify the intent type of the query
        
        Args:
            query: Normalized query string
            entities: Extracted entities
            context: Optional conversation context
            
        Returns:
            Tuple of (IntentType, confidence_score)
        """
        query_lower = query.lower()
        scores = {intent_type: 0.0 for intent_type in IntentType}
        
        # Score based on keyword patterns
        for intent_type, patterns in self.INTENT_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    scores[intent_type] += 0.3
        
        # Adjust scores based on entities and structure
        
        # NAVIGATION: Single entity with "open", "view", "show me"
        if len(entities) == 1 and any(
            word in query_lower for word in ['open', 'view', 'show me', 'go to', 'navigate']
        ):
            scores[IntentType.NAVIGATION] += 0.5
        
        # ACTION: Contains action verbs and specific entities
        action_verbs = ['set', 'create', 'add', 'update', 'change', 'assign', 'link', 'remind']
        if any(verb in query_lower for verb in action_verbs):
            scores[IntentType.ACTION] += 0.4
            if entities:
                scores[IntentType.ACTION] += 0.2
        
        # QUERY: Question words or list/show commands
        question_words = ['what', 'which', 'who', 'when', 'where', 'how']
        if any(word in query_lower for word in question_words):
            scores[IntentType.QUERY] += 0.4
        
        if any(word in query_lower for word in ['show', 'list', 'find', 'get', 'display']):
            scores[IntentType.QUERY] += 0.3
        
        # REPORT: Aggregate or analytical queries
        report_keywords = ['report', 'summary', 'statistics', 'distribution', 'breakdown', 'trend']
        if any(keyword in query_lower for keyword in report_keywords):
            scores[IntentType.REPORT] += 0.5
        
        # Check for aggregate functions
        if any(word in query_lower for word in ['count', 'total', 'average', 'sum', 'how many']):
            scores[IntentType.REPORT] += 0.3
        
        # CLARIFICATION: Very short queries or yes/no responses
        if len(query.split()) <= 3 and any(
            word in query_lower for word in ['yes', 'no', 'what', 'huh', 'ok', 'yeah']
        ):
            scores[IntentType.CLARIFICATION] += 0.5
        
        # Context-based adjustments
        if context:
            last_intent = context.get('last_intent')
            
            # If last intent was CLARIFICATION, current is likely the actual intent
            if last_intent == IntentType.CLARIFICATION:
                scores[IntentType.CLARIFICATION] -= 0.3
            
            # If we have mentioned entities in context and query uses pronouns
            if context.get('mentioned_entities') and any(
                pronoun in query_lower for pronoun in ['it', 'this', 'that', 'them']
            ):
                # Likely continuing previous conversation
                if last_intent:
                    scores[last_intent] += 0.2
        
        # Find intent with highest score
        max_score = max(scores.values())
        
        # If no clear winner, default to QUERY
        if max_score < 0.3:
            return IntentType.QUERY, 0.5
        
        # Get intent with highest score
        best_intent = max(scores.items(), key=lambda x: x[1])[0]
        
        # Normalize confidence to 0-1 range
        # Max possible score is around 1.5, so normalize
        confidence = min(max_score / 1.5, 1.0)
        
        return best_intent, confidence
    
    def _is_complex_query(self, query: str) -> bool:
        """
        Determine if query is complex and requires LLM processing
        
        Args:
            query: Normalized query string
            
        Returns:
            True if query is complex, False otherwise
        """
        # Long queries are likely complex
        if len(query.split()) > 20:
            return True
        
        # Multiple clauses (and, or, but)
        clause_connectors = ['and', 'or', 'but', 'however', 'also', 'additionally']
        connector_count = sum(1 for word in clause_connectors if f' {word} ' in query.lower())
        if connector_count >= 2:
            return True
        
        # Nested questions
        if query.count('?') > 1:
            return True
        
        # Conditional statements
        if any(word in query.lower() for word in ['if', 'when', 'unless', 'provided that']):
            return True
        
        # Comparison queries
        if any(word in query.lower() for word in ['compare', 'difference', 'versus', 'vs', 'better']):
            return True
        
        return False
    
    async def classify_with_llm_fallback(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Intent:
        """
        Classify intent with LLM fallback for ambiguous queries
        
        Args:
            query: User's natural language query
            context: Optional conversation context
            
        Returns:
            Intent object with classification results
        """
        # First try rule-based classification
        intent = await self.classify(query, context)
        
        # If confidence is low or query is complex, use LLM
        if intent.requires_llm and self.llm_service:
            try:
                logger.info(f"Using LLM fallback for query: {query[:50]}...")
                llm_intent = await self._classify_with_llm(query, context)
                
                # Merge LLM results with rule-based results
                # Prefer LLM for intent type, but keep rule-based entities
                if llm_intent:
                    intent.intent_type = llm_intent.intent_type
                    intent.confidence = max(intent.confidence, llm_intent.confidence)
                    
                    # Merge entities (LLM might find additional ones)
                    existing_entity_ids = {e.entity_id for e in intent.entities if e.entity_id}
                    for llm_entity in llm_intent.entities:
                        if llm_entity.entity_id not in existing_entity_ids:
                            intent.entities.append(llm_entity)
                    
                    intent.requires_llm = False
                    logger.info(f"LLM classification: {llm_intent.intent_type.value}, confidence: {llm_intent.confidence:.2f}")
            
            except Exception as e:
                logger.error(f"LLM fallback failed: {e}")
                # Continue with rule-based classification
        
        return intent
    
    async def _classify_with_llm(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Intent]:
        """
        Use LLM to classify intent for ambiguous queries
        
        Args:
            query: User's natural language query
            context: Optional conversation context
            
        Returns:
            Intent object if successful, None otherwise
        """
        if not self.llm_service:
            logger.warning("LLM service not available for fallback classification")
            return None
        
        # Build prompt for LLM
        prompt = self._build_classification_prompt(query, context)
        
        try:
            # Call LLM service
            response = await self.llm_service.classify_intent(prompt)
            
            # Parse LLM response
            intent = self._parse_llm_classification(response, query)
            return intent
        
        except Exception as e:
            logger.error(f"Failed to classify with LLM: {e}")
            return None
    
    def _build_classification_prompt(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build prompt for LLM intent classification
        
        Args:
            query: User's natural language query
            context: Optional conversation context
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Classify the following user query for a project management system.

Query: "{query}"

Intent Types:
- QUERY: Information retrieval (e.g., "Show me tasks for Project X")
- ACTION: Perform operation (e.g., "Set reminder for task TSK-123")
- NAVIGATION: Request deep link (e.g., "Open bug BUG-456")
- REPORT: Generate insights (e.g., "Show task distribution by status")
- CLARIFICATION: Follow-up or ambiguous query (e.g., "What?", "Can you explain?")

Entity Types:
- PROJECT, TASK, SUBTASK, BUG, USER_STORY, USECASE, TEST_CASE, PROGRAM, USER

"""
        
        if context:
            prompt += f"\nConversation Context:\n"
            if context.get('last_intent'):
                prompt += f"- Last Intent: {context['last_intent']}\n"
            if context.get('mentioned_entities'):
                prompt += f"- Recently Mentioned: {context['mentioned_entities']}\n"
        
        prompt += """
Please respond in JSON format:
{
  "intent_type": "QUERY|ACTION|NAVIGATION|REPORT|CLARIFICATION",
  "confidence": 0.0-1.0,
  "entities": [
    {
      "entity_type": "TASK",
      "entity_id": "TSK-123",
      "entity_name": "Task Name"
    }
  ],
  "reasoning": "Brief explanation"
}
"""
        
        return prompt
    
    def _parse_llm_classification(
        self,
        llm_response: str,
        original_query: str
    ) -> Optional[Intent]:
        """
        Parse LLM classification response
        
        Args:
            llm_response: JSON response from LLM
            original_query: Original user query
            
        Returns:
            Intent object if parsing successful, None otherwise
        """
        try:
            import json
            
            # Parse JSON response
            data = json.loads(llm_response)
            
            # Extract intent type
            intent_type_str = data.get('intent_type', 'QUERY').upper()
            try:
                intent_type = IntentType(intent_type_str.lower())
            except ValueError:
                logger.warning(f"Invalid intent type from LLM: {intent_type_str}")
                intent_type = IntentType.QUERY
            
            # Extract confidence
            confidence = float(data.get('confidence', 0.7))
            confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
            
            # Extract entities
            entities = []
            for entity_data in data.get('entities', []):
                try:
                    entity_type_str = entity_data.get('entity_type', '').upper()
                    entity_type = EntityType(entity_type_str.lower())
                    
                    entities.append(ExtractedEntity(
                        entity_type=entity_type,
                        entity_id=entity_data.get('entity_id'),
                        entity_name=entity_data.get('entity_name'),
                        raw_text=entity_data.get('entity_id') or entity_data.get('entity_name')
                    ))
                except (ValueError, KeyError) as e:
                    logger.warning(f"Failed to parse entity from LLM: {e}")
                    continue
            
            # Create Intent object
            intent = Intent(
                intent_type=intent_type,
                entities=entities,
                confidence=confidence,
                raw_query=original_query,
                normalized_query=self._normalize_query(original_query),
                temporal_context={},
                requires_llm=False
            )
            
            return intent
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse LLM classification response: {e}")
            return None
    
    def extract_action_parameters(
        self,
        query: str,
        intent: Intent
    ) -> Dict[str, Any]:
        """
        Extract action-specific parameters from query
        
        Args:
            query: User's natural language query
            intent: Classified intent
            
        Returns:
            Dictionary of action parameters
        """
        if intent.intent_type != IntentType.ACTION:
            return {}
        
        params = {}
        query_lower = query.lower()
        
        # Extract reminder time
        if 'remind' in query_lower or 'reminder' in query_lower:
            params['action_type'] = 'SET_REMINDER'
            
            # Extract time from temporal context
            if intent.temporal_context:
                if 'start_date' in intent.temporal_context:
                    params['remind_at'] = intent.temporal_context['start_date']
        
        # Extract status update
        if 'status' in query_lower or 'update' in query_lower or 'change' in query_lower:
            for status in self.STATUS_VALUES:
                if status in query_lower:
                    params['action_type'] = 'UPDATE_STATUS'
                    params['new_status'] = status
                    break
        
        # Extract comment
        if 'comment' in query_lower or 'note' in query_lower:
            params['action_type'] = 'CREATE_COMMENT'
            # Extract comment text (text after "comment:" or in quotes)
            comment_match = re.search(r'comment[:\s]+["\']?([^"\']+)["\']?', query_lower)
            if comment_match:
                params['comment_text'] = comment_match.group(1).strip()
        
        # Extract commit/PR link
        if 'link' in query_lower or 'commit' in query_lower or 'pr' in query_lower:
            params['action_type'] = 'LINK_COMMIT'
            # Extract PR/commit ID
            pr_match = re.search(r'\b(pr|pull request|commit)[:\s#]+(\w+)', query_lower)
            if pr_match:
                params['commit_id'] = pr_match.group(2)
        
        return params


# Singleton instance
_intent_classifier: Optional[IntentClassifier] = None


def get_intent_classifier() -> IntentClassifier:
    """Get or create the intent classifier singleton"""
    global _intent_classifier
    if _intent_classifier is None:
        _intent_classifier = IntentClassifier()
    return _intent_classifier
