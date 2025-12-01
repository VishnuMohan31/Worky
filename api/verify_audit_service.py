"""
Verification script for Audit Service implementation

This script tests the core functionality of the audit service including
PII masking, batch logging, and querying capabilities.
"""

import sys
from app.services.audit_service import AuditService, get_audit_service


def test_audit_service():
    """Test audit service functionality"""
    print("=" * 60)
    print("Audit Service Verification")
    print("=" * 60)
    
    # Test 1: Service initialization
    print("\n1. Testing service initialization...")
    service = get_audit_service()
    assert service is not None, "Service should be initialized"
    print(f"   ✓ Service initialized")
    print(f"   ✓ Batch size: {service._batch_size}")
    print(f"   ✓ Batch timeout: {service._batch_timeout}s")
    
    # Test 2: Email masking
    print("\n2. Testing email PII masking...")
    test_cases = [
        ("Contact john.doe@example.com for details", "Contact [EMAIL] for details"),
        ("Email: admin@company.org", "Email: [EMAIL]"),
        ("Multiple emails: user1@test.com and user2@test.com", "Multiple emails: [EMAIL] and [EMAIL]"),
    ]
    
    for original, expected in test_cases:
        masked = service.mask_pii(original)
        assert masked == expected, f"Expected '{expected}', got '{masked}'"
        print(f"   ✓ '{original}' → '{masked}'")
    
    # Test 3: Phone number masking
    print("\n3. Testing phone number PII masking...")
    test_cases = [
        ("Call me at 555-123-4567", "Call me at [PHONE]"),
        ("Phone: (555) 123-4567", "Phone: [PHONE]"),
        ("Contact: 5551234567", "Contact: [PHONE]"),
        ("+1-555-123-4567", "[PHONE]"),  # Entire phone with country code is masked
    ]
    
    for original, expected in test_cases:
        masked = service.mask_pii(original)
        assert masked == expected, f"Expected '{expected}', got '{masked}'"
        print(f"   ✓ '{original}' → '{masked}'")
    
    # Test 4: SSN masking
    print("\n4. Testing SSN PII masking...")
    test_cases = [
        ("SSN: 123-45-6789", "SSN: [SSN]"),
        ("Social security number 987-65-4321", "Social security number [SSN]"),
    ]
    
    for original, expected in test_cases:
        masked = service.mask_pii(original)
        assert masked == expected, f"Expected '{expected}', got '{masked}'"
        print(f"   ✓ '{original}' → '{masked}'")
    
    # Test 5: Credit card masking
    print("\n5. Testing credit card PII masking...")
    test_cases = [
        ("Card: 1234-5678-9012-3456", "Card: [CREDIT_CARD]"),
        ("CC: 1234 5678 9012 3456", "CC: [CREDIT_CARD]"),
        ("Card number: 1234567890123456", "Card number: [CREDIT_CARD]"),
    ]
    
    for original, expected in test_cases:
        masked = service.mask_pii(original)
        assert masked == expected, f"Expected '{expected}', got '{masked}'"
        print(f"   ✓ '{original}' → '{masked}'")
    
    # Test 6: Name masking
    print("\n6. Testing name PII masking...")
    test_cases = [
        ("Contact Dr. John Smith", "Contact [NAME]"),
        ("Ask Mr. Robert Johnson", "Ask [NAME]"),
        ("Email Mrs. Sarah Williams", "Email [NAME]"),
        ("Call Ms. Emily Davis", "Call [NAME]"),
        ("Meet Prof. Michael Brown", "Meet [NAME]"),
    ]
    
    for original, expected in test_cases:
        masked = service.mask_pii(original)
        assert masked == expected, f"Expected '{expected}', got '{masked}'"
        print(f"   ✓ '{original}' → '{masked}'")
    
    # Test 7: Multiple PII types in one text
    print("\n7. Testing multiple PII types in one text...")
    original = "Contact Dr. John Smith at john.smith@example.com or call 555-123-4567"
    masked = service.mask_pii(original)
    
    assert "[NAME]" in masked, "Should mask name"
    assert "[EMAIL]" in masked, "Should mask email"
    assert "[PHONE]" in masked, "Should mask phone"
    assert "john.smith@example.com" not in masked, "Should not contain original email"
    assert "555-123-4567" not in masked, "Should not contain original phone"
    
    print(f"   ✓ Original: '{original}'")
    print(f"   ✓ Masked:   '{masked}'")
    
    # Test 8: Text without PII
    print("\n8. Testing text without PII...")
    original = "Show me all tasks for Project Alpha"
    masked = service.mask_pii(original)
    assert masked == original, "Text without PII should remain unchanged"
    print(f"   ✓ Text without PII unchanged: '{masked}'")
    
    # Test 9: Empty and None text
    print("\n9. Testing empty and None text...")
    assert service.mask_pii("") == "", "Empty string should remain empty"
    assert service.mask_pii(None) == None, "None should remain None"
    print(f"   ✓ Empty and None handled correctly")
    
    # Test 10: Text truncation
    print("\n10. Testing text truncation...")
    long_text = "A" * 1000
    truncated = service._truncate_text(long_text, max_length=100)
    assert len(truncated) == 100, f"Should truncate to 100 chars, got {len(truncated)}"
    assert truncated.endswith("..."), "Should end with ellipsis"
    print(f"   ✓ Long text truncated: {len(long_text)} → {len(truncated)} chars")
    
    short_text = "Short text"
    not_truncated = service._truncate_text(short_text, max_length=100)
    assert not_truncated == short_text, "Short text should not be truncated"
    print(f"   ✓ Short text not truncated: '{not_truncated}'")
    
    none_text = service._truncate_text(None)
    assert none_text is None, "None should remain None"
    print(f"   ✓ None handled correctly")
    
    # Test 11: Singleton pattern
    print("\n11. Testing singleton pattern...")
    service2 = get_audit_service()
    assert service is service2, "Should return same instance"
    print(f"   ✓ Singleton pattern working correctly")
    
    # Test 12: Complex real-world example
    print("\n12. Testing complex real-world example...")
    complex_query = """
    I need to update task TSK-123 and notify Dr. Jane Doe at jane.doe@company.com.
    Her phone is 555-987-6543. The payment card ending in 1234-5678-9012-3456 should
    be charged. SSN for verification: 123-45-6789.
    """
    
    masked_complex = service.mask_pii(complex_query)
    
    # Verify all PII is masked
    assert "jane.doe@company.com" not in masked_complex, "Email should be masked"
    assert "555-987-6543" not in masked_complex, "Phone should be masked"
    assert "1234-5678-9012-3456" not in masked_complex, "Credit card should be masked"
    assert "123-45-6789" not in masked_complex, "SSN should be masked"
    assert "Dr. Jane Doe" not in masked_complex, "Name should be masked"
    
    # Verify task ID is preserved
    assert "TSK-123" in masked_complex, "Task ID should be preserved"
    
    print(f"   ✓ Complex query masked successfully")
    print(f"   Original length: {len(complex_query)} chars")
    print(f"   Masked length: {len(masked_complex)} chars")
    print(f"   Preview: {masked_complex[:100]}...")
    
    # Test 13: Batch queue operations
    print("\n13. Testing batch queue operations...")
    assert len(service._batch_queue) == 0, "Batch queue should start empty"
    print(f"   ✓ Batch queue initialized empty")
    print(f"   ✓ Batch size configured: {service._batch_size}")
    print(f"   ✓ Batch timeout configured: {service._batch_timeout}s")
    
    print("\n" + "=" * 60)
    print("✓ All Audit Service tests passed!")
    print("=" * 60)
    
    # Note about database operations
    print("\nNote: Database operations require an active database connection.")
    print("The following methods require a database session:")
    print("- create_audit_log()")
    print("- get_audit_logs()")
    print("- get_audit_log_by_request_id()")
    print("- get_audit_statistics()")
    print("- flush_batch()")
    print("\nTo test with database:")
    print("1. Ensure PostgreSQL is running")
    print("2. Run database migrations")
    print("3. Use the service with a valid AsyncSession")
    
    return True


if __name__ == "__main__":
    try:
        result = test_audit_service()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
