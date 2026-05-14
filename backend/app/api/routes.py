from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta

from app.db.database import get_db
from app.schemas.schemas import (
    UserCreate, UserResponse, UserLogin, Token, 
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ExecutionRequest, ExecutionResponse, ExecutionHistoryResponse
)
from app.services import user_service, project_service
from app.core.security import create_access_token, authenticate_user, decode_access_token
from app.core.config import settings
from app.services.executor_service import executor

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = user_service.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    
    return user


# Authentication endpoints
@router.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = user_service.get_user_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = user_service.get_user_by_username(db, username=user_data.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create user
    user = user_service.create_user(
        db=db,
        email=user_data.email,
        username=user_data.username,
        password=user_data.password
    )
    
    return user


@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    return current_user


# Project endpoints
@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = project_service.get_projects_by_user(db, user_id=current_user.id)
    return projects


@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = project_service.create_project(
        db=db,
        owner_id=current_user.id,
        name=project_data.name,
        language=project_data.language,
        code=project_data.code,
        description=project_data.description,
        is_public=project_data.is_public
    )
    return project


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = project_service.get_project_by_id(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check ownership or public access
    if project.owner_id != current_user.id and not project.is_public:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = project_service.get_project_by_id(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = project_data.dict(exclude_unset=True)
    project = project_service.update_project(db, project_id=project_id, **update_data)
    return project


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project = project_service.get_project_by_id(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = project_service.delete_project(db, project_id=project_id)
    if success:
        return {"message": "Project deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete project")


# Execution endpoints
@router.post("/execute", response_model=ExecutionResponse)
async def execute_code(
    execution_request: ExecutionRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Create execution history
    execution = project_service.create_execution_history(
        db=db,
        user_id=current_user.id,
        language=execution_request.language,
        code=execution_request.code,
        input_data=execution_request.input_data
    )
    
    # Execute code
    result = await executor.execute_code(
        language=execution_request.language,
        code=execution_request.code,
        input_data=execution_request.input_data
    )
    
    # Update execution history
    project_service.update_execution_history(
        db=db,
        execution_id=execution.id,
        output=result["output"],
        error=result["error"],
        status=result["status"],
        execution_time=result["execution_time"]
    )
    
    return ExecutionResponse(**result)


@router.websocket("/ws/execute/{language}")
async def websocket_execute(websocket: WebSocket, language: str):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            code = data.get("code", "")
            input_data = data.get("input_data", "")
            
            await executor.stream_execution(
                language=language,
                code=code,
                input_data=input_data,
                websocket=websocket
            )
    
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})


# Execution history
@router.get("/history", response_model=List[ExecutionHistoryResponse])
async def get_execution_history(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = project_service.get_execution_history_by_user(db, user_id=current_user.id)
    return history
