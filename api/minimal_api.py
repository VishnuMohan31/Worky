from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from pydantic import BaseModel
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.schemas.user import UserResponse
from datetime import timedelta
import os

# Create FastAPI app
app = FastAPI(title="Worky API - Minimal")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3007", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5437/worky"
engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Schemas
class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "worky-api-minimal", "version": "1.0.0"}

@app.get("/api/v1/clients")
async def list_clients(db: AsyncSession = Depends(get_db)):
    """List all clients"""
    try:
        result = await db.execute(text("SELECT id, name, description, is_active FROM clients ORDER BY name"))
        clients = []
        for row in result:
            clients.append({
                "id": str(row[0]),
                "name": row[1],
                "description": row[2],
                "is_active": row[3]
            })
        return {"clients": clients, "total": len(clients)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/v1/clients/statistics/dashboard")
async def client_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics for clients"""
    try:
        # Get basic counts
        clients_result = await db.execute(text("SELECT COUNT(*) FROM clients"))
        programs_result = await db.execute(text("SELECT COUNT(*) FROM programs"))
        projects_result = await db.execute(text("SELECT COUNT(*) FROM projects"))
        
        clients_count = clients_result.scalar() or 0
        programs_count = programs_result.scalar() or 0
        projects_count = projects_result.scalar() or 0
        
        return {
            "total_clients": clients_count,
            "total_programs": programs_count,
            "total_projects": projects_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard stats error: {str(e)}")

@app.post("/api/v1/auth/login")
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password"""
    try:
        # Get user by email
        result = await db.execute(
            select(User).where(User.email == credentials.email)
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        # Create user response manually
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "client_id": str(user.client_id),
            "primary_role": user.primary_role or user.role,
            "secondary_roles": user.secondary_roles or [],
            "is_contact_person": user.is_contact_person or False,
            "language": user.language,
            "theme": user.theme,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)