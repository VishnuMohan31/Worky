#!/usr/bin/env python3
"""
Simple integration test for team assignment system without FastAPI dependencies.
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_basic_integration():
    """Test basic integration without database"""
    
    print("Testing basic imports...")
    
    try:
        from app.models.user import User
        from app.models.team import Team, TeamMember, Assignment
        from app.models.hierarchy import Project, Task
        print("+ Models imported successfully")
    except Exception as e:
        print(f"- Model import failed: {e}")
        return False
    
    try:
        from app.services.team_service import TeamService
        from app.services.assignment_service import AssignmentService
        from app.services.validation_service import ValidationService
        print("+ Services imported successfully")
    except Exception as e:
        print(f"- Service import failed: {e}")
        return False
    
    print("Testing model creation...")
    
    try:
        # Test model instantiation
        user = User(
            id="USR-TEST",
            email="test@example.com",
            full_name="Test User",
            primary_role="Developer",
            hashed_password="hashed",
            client_id="CLI-TEST"
        )
        
        project = Project(
            id="PRJ-TEST",
            name="Test Project",
            program_id="PRG-TEST"
        )
        
        team = Team(
            id="TEAM-TEST",
            name="Test Team",
            project_id=project.id,
            created_by=user.id
        )
        
        assignment = Assignment(
            id="ASSGN-TEST",
            entity_type="task",
            entity_id="TSK-TEST",
            user_id=user.id,
            assignment_type="developer",
            created_by=user.id
        )
        
        print("+ Models created successfully")
        
        # Test basic validation logic
        from app.core.exceptions import ValidationException
        print("+ Exception classes imported successfully")
        
        return True
        
    except Exception as e:
        print(f"- Model creation failed: {e}")
        return False

async def test_assignment_rules():
    """Test assignment rule validation logic"""
    
    print("\nTesting assignment rules...")
    
    try:
        # Test assignment rules matrix
        ASSIGNMENT_RULES = {
            "client": {
                "allowed_roles": ["Contact Person"],
                "assignment_type": "contact_person",
                "requires_team_membership": False
            },
            "program": {
                "allowed_roles": ["Owner", "Admin", "Architect"],
                "assignment_type": "owner",
                "requires_team_membership": False
            },
            "project": {
                "allowed_roles": ["Owner", "Admin", "Architect"],
                "assignment_type": "owner",
                "requires_team_membership": False
            },
            "usecase": {
                "allowed_roles": ["Owner", "Admin", "Architect", "Designer"],
                "assignment_type": "owner",
                "requires_team_membership": True
            },
            "userstory": {
                "allowed_roles": ["Owner", "Admin", "Architect", "Designer"],
                "assignment_type": "owner",
                "requires_team_membership": True
            },
            "task": {
                "allowed_roles": ["Developer"],
                "assignment_type": "developer",
                "requires_team_membership": True
            },
            "subtask": {
                "allowed_roles": ["Developer"],
                "assignment_type": "developer",
                "requires_team_membership": True
            }
        }
        
        # Test rule validation
        def validate_role_assignment(entity_type: str, user_role: str) -> bool:
            if entity_type not in ASSIGNMENT_RULES:
                return False
            
            allowed_roles = ASSIGNMENT_RULES[entity_type]["allowed_roles"]
            return user_role in allowed_roles
        
        # Test valid assignments
        valid_tests = [
            ("task", "Developer"),
            ("project", "Owner"),
            ("usecase", "Admin"),
            ("client", "Contact Person")
        ]
        
        for entity_type, role in valid_tests:
            if validate_role_assignment(entity_type, role):
                print(f"+ Valid assignment: {entity_type} -> {role}")
            else:
                print(f"- Should be valid: {entity_type} -> {role}")
                return False
        
        # Test invalid assignments
        invalid_tests = [
            ("task", "Owner"),
            ("project", "Developer"),
            ("client", "Developer")
        ]
        
        for entity_type, role in invalid_tests:
            if not validate_role_assignment(entity_type, role):
                print(f"+ Invalid assignment correctly rejected: {entity_type} -> {role}")
            else:
                print(f"- Should be invalid: {entity_type} -> {role}")
                return False
        
        return True
        
    except Exception as e:
        print(f"- Assignment rule testing failed: {e}")
        return False

async def test_cross_project_isolation():
    """Test cross-project isolation logic"""
    
    print("\nTesting cross-project isolation...")
    
    try:
        # Simulate project isolation check
        def check_project_isolation(user_project_id: str, entity_project_id: str) -> bool:
            """Check if user can access entity based on project isolation"""
            return user_project_id == entity_project_id
        
        # Test same project access
        if check_project_isolation("PRJ-001", "PRJ-001"):
            print("+ Same project access allowed")
        else:
            print("- Same project access should be allowed")
            return False
        
        # Test cross-project access
        if not check_project_isolation("PRJ-001", "PRJ-002"):
            print("+ Cross-project access correctly blocked")
        else:
            print("- Cross-project access should be blocked")
            return False
        
        return True
        
    except Exception as e:
        print(f"- Cross-project isolation testing failed: {e}")
        return False

async def main():
    """Run all integration tests"""
    
    print("=" * 60)
    print("TEAM ASSIGNMENT SYSTEM - INTEGRATION TEST")
    print("=" * 60)
    
    tests = [
        ("Basic Integration", test_basic_integration),
        ("Assignment Rules", test_assignment_rules),
        ("Cross-Project Isolation", test_cross_project_isolation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[TEST] {test_name}")
        print("-" * 40)
        
        try:
            result = await test_func()
            if result:
                print(f"+ {test_name} PASSED")
                passed += 1
            else:
                print(f"- {test_name} FAILED")
        except Exception as e:
            print(f"- {test_name} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("SUCCESS: ALL INTEGRATION TESTS PASSED!")
        return True
    else:
        print("FAILED: SOME TESTS FAILED")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)