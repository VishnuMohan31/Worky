"""
LLM Service for Chat Assistant

This service handles integration with Large Language Models (OpenAI API or compatible endpoints)
for generating natural language responses based on retrieved data.
"""

import logging
import asyncio
import json
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import tiktoken
from openai import AsyncOpenAI, APIError, APITimeoutError, RateLimitError

from app.core.config import settings
from app.schemas.chat import (
    IntentType,
    EntityType,
    UIAction,
    ActionType,
    EntityCard,
    DataTable
)
from app.services.chat_metrics import get_chat_metrics

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM integration with OpenAI API"""
    
    def __init__(self):
        """Initialize OpenAI client and configuration"""
        self.client: Optional[AsyncOpenAI] = None
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.timeout = settings.LLM_TIMEOUT
        self.provider = settings.LLM_PROVIDER
        self.metrics = get_chat_metrics()
        
        # Initialize token counter
        try:
            self.encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            # Fallback to cl100k_base for unknown models
            self.encoding = tiktoken.get_encoding("cl100k_base")
            logger.warning(f"Unknown model {self.model}, using cl100k_base encoding")
    
    async def connect(self) -> None:
        """Initialize OpenAI client connection"""
        if not settings.LLM_API_KEY:
            logger.warning("LLM_API_KEY not configured, LLM service will use fallback responses")
            return
        
        try:
            self.client = AsyncOpenAI(
                api_key=settings.LLM_API_KEY,
                timeout=self.timeout
            )
            logger.info(f"LLM service initialized with provider: {self.provider}, model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in a text string
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.warning(f"Failed to count tokens: {e}")
            # Rough estimate: 1 token ≈ 4 characters
            return len(text) // 4
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt for the LLM
        
        Returns:
            System prompt string
        """
        return """You are a helpful AI assistant for the Worky project management platform.

Your role is to help users find information about their projects, tasks, bugs, user stories, and team members.

Guidelines:
- Answer based ONLY on the provided data from the database
- If the data is insufficient or missing, clearly state that and ask for clarification
- Format responses clearly with bullet points or numbered lists when appropriate
- Suggest relevant actions when appropriate (view details, set reminders, update status)
- Be concise but informative
- Do not make up information or assume data that wasn't provided
- Respect the user's access permissions - only discuss data they can access
- Use professional but friendly language
- When showing dates, use clear formats (e.g., "January 15, 2024")
- When showing lists, limit to the most relevant items and mention if there are more

Important:
- NEVER suggest destructive actions like deleting projects or changing user roles
- ALWAYS base your response on the retrieved data provided
- If you're unsure, ask clarifying questions"""
    
    def _build_user_prompt(
        self,
        query: str,
        retrieved_data: Dict[str, Any],
        intent_type: Optional[IntentType] = None,
        conversation_context: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Build the user prompt with query and retrieved data
        
        Args:
            query: User's natural language query
            retrieved_data: Data retrieved from database
            intent_type: Detected intent type
            conversation_context: Previous messages for context
            
        Returns:
            Formatted user prompt
        """
        prompt_parts = []
        
        # Add conversation context if available
        if conversation_context:
            prompt_parts.append("Previous conversation:")
            for msg in conversation_context[-3:]:  # Last 3 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt_parts.append(f"{role.capitalize()}: {content}")
            prompt_parts.append("")
        
        # Add current query
        prompt_parts.append(f"User Query: {query}")
        prompt_parts.append("")
        
        # Add intent type if detected
        if intent_type:
            prompt_parts.append(f"Detected Intent: {intent_type.value}")
            prompt_parts.append("")
        
        # Add retrieved data
        prompt_parts.append("Retrieved Data from Database:")
        
        if not retrieved_data or all(not v for v in retrieved_data.values()):
            prompt_parts.append("No relevant data found in the database.")
        else:
            # Format retrieved data as JSON for clarity
            prompt_parts.append(json.dumps(retrieved_data, indent=2, default=str))
        
        prompt_parts.append("")
        prompt_parts.append("Instructions:")
        prompt_parts.append("- Provide a clear, helpful response based on the retrieved data")
        prompt_parts.append("- If suggesting actions, be specific about what the user can do")
        prompt_parts.append("- If data is missing or unclear, ask for clarification")
        prompt_parts.append("- Format your response in a user-friendly way")
        
        return "\n".join(prompt_parts)
    
    async def generate_response(
        self,
        query: str,
        retrieved_data: Dict[str, Any],
        intent_type: Optional[IntentType] = None,
        conversation_context: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, int]:
        """
        Generate a natural language response using the LLM
        
        Args:
            query: User's natural language query
            retrieved_data: Data retrieved from database
            intent_type: Detected intent type
            conversation_context: Previous messages for context
            
        Returns:
            Tuple of (response_text, tokens_used)
            
        Raises:
            APITimeoutError: If LLM request times out
            APIError: If LLM API returns an error
        """
        if not self.client:
            await self.connect()
        
        # If no API key, use fallback
        if not self.client:
            return self._generate_fallback_response(query, retrieved_data, intent_type), 0
        
        try:
            # Build prompts
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(
                query, retrieved_data, intent_type, conversation_context
            )
            
            # Count input tokens
            input_tokens = self.count_tokens(system_prompt) + self.count_tokens(user_prompt)
            logger.debug(f"LLM request with {input_tokens} input tokens")
            
            # Make API call with timeout and track duration
            start_time = datetime.utcnow()
            
            with self.metrics.track_llm_call_duration():
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=self.temperature,
                        max_tokens=self.max_tokens
                    ),
                    timeout=self.timeout
                )
            
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Extract response
            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else input_tokens
            
            logger.info(
                f"LLM response generated in {duration_ms}ms, "
                f"tokens: {tokens_used}, "
                f"finish_reason: {response.choices[0].finish_reason}"
            )
            
            return response_text, tokens_used
            
        except asyncio.TimeoutError:
            logger.error(f"LLM request timed out after {self.timeout} seconds")
            self.metrics.record_error("llm_timeout")
            raise APITimeoutError("LLM request timed out")
            
        except RateLimitError as e:
            logger.error(f"LLM rate limit exceeded: {e}")
            self.metrics.record_error("llm_rate_limit")
            return self._generate_fallback_response(
                query, retrieved_data, intent_type,
                error_msg="The AI service is currently at capacity. Please try again in a moment."
            ), 0
            
        except APIError as e:
            logger.error(f"LLM API error: {e}")
            self.metrics.record_error("llm_unavailable")
            return self._generate_fallback_response(
                query, retrieved_data, intent_type,
                error_msg="The AI service encountered an error. Here's what I found in the database:"
            ), 0
            
        except Exception as e:
            logger.error(f"Unexpected error in LLM service: {e}")
            self.metrics.record_error("llm_error")
            return self._generate_fallback_response(
                query, retrieved_data, intent_type,
                error_msg="I encountered an issue processing your request. Here's the raw data:"
            ), 0
    
    def _generate_fallback_response(
        self,
        query: str,
        retrieved_data: Dict[str, Any],
        intent_type: Optional[IntentType] = None,
        error_msg: Optional[str] = None
    ) -> str:
        """
        Generate a fallback response when LLM is unavailable
        
        Args:
            query: User's query
            retrieved_data: Retrieved data
            intent_type: Detected intent
            error_msg: Optional error message to include
            
        Returns:
            Formatted fallback response
        """
        response_parts = []
        
        if error_msg:
            response_parts.append(error_msg)
            response_parts.append("")
        
        # Check if we have data
        if not retrieved_data or all(not v for v in retrieved_data.values()):
            response_parts.append("I couldn't find any relevant data for your query.")
            response_parts.append("")
            response_parts.append("Try:")
            response_parts.append("- Being more specific about what you're looking for")
            response_parts.append("- Checking if you have access to the project or entity")
            response_parts.append("- Using entity IDs (e.g., TSK-123, PRJ-456)")
            return "\n".join(response_parts)
        
        # Format data based on what we found
        response_parts.append("Here's what I found:")
        response_parts.append("")
        
        for key, value in retrieved_data.items():
            if not value:
                continue
                
            if isinstance(value, list):
                if len(value) > 0:
                    response_parts.append(f"{key.replace('_', ' ').title()}: {len(value)} items")
                    # Show first few items
                    for item in value[:3]:
                        if isinstance(item, dict):
                            title = item.get('title') or item.get('name') or item.get('id', 'Unknown')
                            response_parts.append(f"  - {title}")
                    if len(value) > 3:
                        response_parts.append(f"  ... and {len(value) - 3} more")
            elif isinstance(value, dict):
                response_parts.append(f"{key.replace('_', ' ').title()}:")
                for k, v in list(value.items())[:5]:  # Show first 5 fields
                    response_parts.append(f"  {k}: {v}")
            else:
                response_parts.append(f"{key.replace('_', ' ').title()}: {value}")
            
            response_parts.append("")
        
        return "\n".join(response_parts)
    
    def parse_structured_output(
        self,
        response_text: str,
        retrieved_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse LLM response and extract structured data for UI
        
        Args:
            response_text: LLM generated response
            retrieved_data: Original retrieved data
            
        Returns:
            Dictionary with structured output including actions and cards
        """
        structured_output = {
            "text": response_text,
            "actions": [],
            "cards": [],
            "table": None
        }
        
        # Extract entity cards from retrieved data
        cards = self._extract_entity_cards(retrieved_data)
        if cards:
            structured_output["cards"] = cards
        
        # Extract suggested actions
        actions = self._extract_suggested_actions(response_text, retrieved_data)
        if actions:
            structured_output["actions"] = actions
        
        # Extract table data if present
        table = self._extract_table_data(retrieved_data)
        if table:
            structured_output["table"] = table
        
        return structured_output
    
    def _extract_entity_cards(self, retrieved_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract entity cards from retrieved data"""
        cards = []
        
        # Map data keys to entity types
        entity_mappings = {
            "tasks": EntityType.TASK,
            "bugs": EntityType.BUG,
            "projects": EntityType.PROJECT,
            "user_stories": EntityType.USER_STORY,
            "subtasks": EntityType.SUBTASK,
        }
        
        for data_key, entity_type in entity_mappings.items():
            if data_key in retrieved_data and isinstance(retrieved_data[data_key], list):
                for item in retrieved_data[data_key][:5]:  # Limit to 5 cards
                    if isinstance(item, dict):
                        card = {
                            "entity_type": entity_type.value,
                            "entity_id": item.get("id", ""),
                            "title": item.get("title") or item.get("name", "Untitled"),
                            "status": item.get("status"),
                            "assignee": item.get("assignee_name") or item.get("assigned_to"),
                            "due_date": item.get("due_date"),
                            "priority": item.get("priority"),
                            "deep_link": f"/{entity_type.value}s/{item.get('id')}",
                            "metadata": {
                                k: v for k, v in item.items()
                                if k not in ["id", "title", "name", "status", "assignee_name", "due_date", "priority"]
                            }
                        }
                        cards.append(card)
        
        return cards
    
    def _extract_suggested_actions(
        self,
        response_text: str,
        retrieved_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract suggested actions from response and data"""
        actions = []
        
        # If we have single entity results, suggest view action
        for key in ["task", "bug", "project", "user_story"]:
            if key in retrieved_data and isinstance(retrieved_data[key], dict):
                entity = retrieved_data[key]
                entity_type = EntityType(key.replace("_", "_"))
                actions.append({
                    "action_type": ActionType.VIEW_ENTITY.value,
                    "label": f"View {key.replace('_', ' ').title()}",
                    "entity_type": entity_type.value,
                    "entity_id": entity.get("id"),
                    "deep_link": f"/{key}s/{entity.get('id')}",
                    "parameters": {}
                })
        
        # Check for reminder suggestions in response
        if any(word in response_text.lower() for word in ["remind", "reminder", "follow up"]):
            # Find first task or bug in data
            for key in ["tasks", "bugs"]:
                if key in retrieved_data and isinstance(retrieved_data[key], list) and len(retrieved_data[key]) > 0:
                    entity = retrieved_data[key][0]
                    actions.append({
                        "action_type": ActionType.SET_REMINDER.value,
                        "label": "Set Reminder",
                        "entity_type": EntityType.TASK.value if key == "tasks" else EntityType.BUG.value,
                        "entity_id": entity.get("id"),
                        "parameters": {}
                    })
                    break
        
        return actions
    
    def _extract_table_data(self, retrieved_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract table data from retrieved data"""
        # Look for list data that should be displayed as table
        for key, value in retrieved_data.items():
            if isinstance(value, list) and len(value) > 3:  # Use table for 4+ items
                if len(value) > 0 and isinstance(value[0], dict):
                    # Extract common columns
                    all_keys = set()
                    for item in value:
                        all_keys.update(item.keys())
                    
                    # Prioritize important columns
                    priority_columns = ["id", "title", "name", "status", "assignee_name", "due_date", "priority"]
                    columns = [col for col in priority_columns if col in all_keys]
                    
                    # Add remaining columns (up to 8 total)
                    remaining = [col for col in sorted(all_keys) if col not in columns]
                    columns.extend(remaining[:8 - len(columns)])
                    
                    # Build rows
                    rows = []
                    for item in value[:20]:  # Limit to 20 rows
                        row = [item.get(col, "") for col in columns]
                        rows.append(row)
                    
                    return {
                        "columns": [col.replace("_", " ").title() for col in columns],
                        "rows": rows,
                        "total_count": len(value),
                        "has_more": len(value) > 20
                    }
        
        return None
    
    async def health_check(self) -> bool:
        """
        Check if LLM service is available
        
        Returns:
            True if service is healthy, False otherwise
        """
        if not self.client:
            try:
                await self.connect()
            except Exception:
                return False
        
        if not self.client:
            return False
        
        try:
            # Simple test request with short timeout
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                ),
                timeout=5
            )
            return response is not None
        except Exception as e:
            logger.warning(f"LLM health check failed: {e}")
            return False


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
