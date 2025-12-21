import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.user import User
from app.core.config import settings
from app.core.security import verify_password, create_access_token
from datetime import timedelta

async def test_login():
    try:
        # Create engine and session
        engine = create_async_engine(settings.database_url)
        async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session_maker() as session:
            # Get user by email
            result = await session.execute(
                select(User).where(User.email == 'admin@datalegos.com')
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("User not found")
                return False
                
            print(f"User found: {user.email}")
            
            # Verify password
            password_valid = verify_password('password', user.hashed_password)
            print(f"Password valid: {password_valid}")
            
            if not password_valid:
                print("Invalid password")
                return False
                
            # Check if user is active
            print(f"User active: {user.is_active}")
            
            # Create access token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(user.id)},
                expires_delta=access_token_expires
            )
            
            print(f"Access token created: {access_token[:50]}...")
            print("Login test successful!")
            return True
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_login())