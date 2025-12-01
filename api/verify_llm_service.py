"""
Verification script for LLM Service implementation

This script tests the core functionality of the LLM service without requiring
an actual API key or making real API calls.
"""

import asyncio
import sys
from app.services.llm_service import LLMService, get_llm_service
from app.schemas.chat import IntentType, EntityType


async def test_llm_service():
    """Test LLM service functionality"""
    print("=" * 60)
    print("LLM Service Verification")
    print("=" * 60)
    
    # Test 1: Service initialization
    print("\n1. Testing service initialization...")
    service = get_llm_service()
    assert service is not None, "Service should be initialized"
    print(f"   ✓ Service initialized")
    print(f"   ✓ Model: {service.model}")
    print(f"   ✓ Temperature: {service.temperature}")
    print(f"   ✓ Max tokens: {service.max_tokens}")
    print(f"   ✓ Timeout: {service.timeout}s")
    print(f"   ✓ Provider: {service.provider}")
    
    # Test 2: Token counting
    print("\n2. Testing token counting...")
    test_text = "This is a test message for token counting."
    token_count = service.count_tokens(test_text)
    assert token_count > 0, "Token count should be positive"
    print(f"   ✓ Text: '{test_text}'")
    print(f"   ✓ Token count: {token_count}")
    
    # Test 3: System prompt generation
    print("\n3. Testing system prompt generation...")
    system_prompt = service._build_system_prompt()
    assert len(system_prompt) > 0, "System prompt should not be empty"
    assert "Worky" in system_prompt, "System prompt should mention Worky"
    assert "project management" in system_prompt, "System prompt should mention project management"
    print(f"   ✓ System prompt generated ({len(system_prompt)} chars)")
    print(f"   ✓ Token count: {service.count_tokens(system_prompt)}")
    
    # Test 4: User prompt generation
    print("\n4. Testing user prompt generation...")
    query = "Show me all tasks for Project Alpha"
    retrieved_data = {
        "tasks": [
            {"id": "TSK-001", "title": "Task 1", "status": "in_progress"},
            {"id": "TSK-002", "title": "Task 2", "status": "completed"}
        ],
        "project": {"id": "PRJ-001", "name": "Project Alpha"}
    }
    user_prompt = service._build_user_prompt(
        query=query,
        retrieved_data=retrieved_data,
        intent_type=IntentType.QUERY
    )
    assert len(user_prompt) > 0, "User prompt should not be empty"
    assert query in user_prompt, "User prompt should contain the query"
    assert "TSK-001" in user_prompt, "User prompt should contain retrieved data"
    print(f"   ✓ User prompt generated ({len(user_prompt)} chars)")
    print(f"   ✓ Token count: {service.count_tokens(user_prompt)}")
    
    # Test 5: User prompt with conversation context
    print("\n5. Testing user prompt with conversation context...")
    conversation_context = [
        {"role": "user", "content": "What projects do I have?"},
        {"role": "assistant", "content": "You have Project Alpha and Project Beta."},
        {"role": "user", "content": "Show me tasks for the first one"}
    ]
    user_prompt_with_context = service._build_user_prompt(
        query="Show me tasks for the first one",
        retrieved_data=retrieved_data,
        intent_type=IntentType.QUERY,
        conversation_context=conversation_context
    )
    assert "Previous conversation:" in user_prompt_with_context, "Should include conversation context"
    print(f"   ✓ User prompt with context generated ({len(user_prompt_with_context)} chars)")
    
    # Test 6: Fallback response generation
    print("\n6. Testing fallback response generation...")
    fallback_response = service._generate_fallback_response(
        query=query,
        retrieved_data=retrieved_data,
        intent_type=IntentType.QUERY
    )
    assert len(fallback_response) > 0, "Fallback response should not be empty"
    assert "found" in fallback_response.lower(), "Fallback should mention found data"
    print(f"   ✓ Fallback response generated ({len(fallback_response)} chars)")
    print(f"   Preview: {fallback_response[:100]}...")
    
    # Test 7: Fallback response with no data
    print("\n7. Testing fallback response with no data...")
    fallback_no_data = service._generate_fallback_response(
        query="Show me something that doesn't exist",
        retrieved_data={},
        intent_type=IntentType.QUERY
    )
    assert "couldn't find" in fallback_no_data.lower(), "Should indicate no data found"
    print(f"   ✓ No-data fallback generated")
    print(f"   Preview: {fallback_no_data[:100]}...")
    
    # Test 8: Entity card extraction
    print("\n8. Testing entity card extraction...")
    cards = service._extract_entity_cards(retrieved_data)
    assert len(cards) > 0, "Should extract entity cards"
    assert cards[0]["entity_type"] == EntityType.TASK.value, "Should identify task entity type"
    assert cards[0]["entity_id"] == "TSK-001", "Should extract entity ID"
    print(f"   ✓ Extracted {len(cards)} entity cards")
    for card in cards:
        print(f"     - {card['entity_type']}: {card['title']} ({card['entity_id']})")
    
    # Test 9: Suggested actions extraction
    print("\n9. Testing suggested actions extraction...")
    response_text = "Here are your tasks. You might want to set a reminder for Task 1."
    actions = service._extract_suggested_actions(response_text, retrieved_data)
    assert len(actions) > 0, "Should extract suggested actions"
    print(f"   ✓ Extracted {len(actions)} suggested actions")
    for action in actions:
        print(f"     - {action['action_type']}: {action['label']}")
    
    # Test 10: Table data extraction
    print("\n10. Testing table data extraction...")
    large_data = {
        "tasks": [
            {"id": f"TSK-{i:03d}", "title": f"Task {i}", "status": "open", "assignee_name": f"User {i % 3}"}
            for i in range(1, 11)
        ]
    }
    table = service._extract_table_data(large_data)
    assert table is not None, "Should extract table data for large lists"
    assert len(table["columns"]) > 0, "Table should have columns"
    assert len(table["rows"]) > 0, "Table should have rows"
    print(f"   ✓ Extracted table with {len(table['columns'])} columns and {len(table['rows'])} rows")
    print(f"   ✓ Columns: {', '.join(table['columns'])}")
    
    # Test 11: Structured output parsing
    print("\n11. Testing structured output parsing...")
    response_text = "I found 2 tasks for Project Alpha. Task 1 is in progress and Task 2 is completed."
    structured = service.parse_structured_output(response_text, retrieved_data)
    assert "text" in structured, "Should have text field"
    assert "actions" in structured, "Should have actions field"
    assert "cards" in structured, "Should have cards field"
    assert structured["text"] == response_text, "Should preserve response text"
    print(f"   ✓ Structured output parsed")
    print(f"     - Text length: {len(structured['text'])} chars")
    print(f"     - Cards: {len(structured['cards'])}")
    print(f"     - Actions: {len(structured['actions'])}")
    print(f"     - Table: {'Yes' if structured['table'] else 'No'}")
    
    # Test 12: Singleton pattern
    print("\n12. Testing singleton pattern...")
    service2 = get_llm_service()
    assert service is service2, "Should return same instance"
    print(f"   ✓ Singleton pattern working correctly")
    
    print("\n" + "=" * 60)
    print("✓ All LLM Service tests passed!")
    print("=" * 60)
    
    # Note about actual LLM calls
    print("\nNote: Actual LLM API calls require LLM_API_KEY to be configured.")
    print("The service will use fallback responses when the API is unavailable.")
    print("\nTo test with real API calls:")
    print("1. Set LLM_API_KEY in your .env file")
    print("2. Call service.generate_response() with your query and data")
    
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_llm_service())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
