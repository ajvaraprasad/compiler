from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    language: str = "python"
    code: str = ""
    is_public: bool = False


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    code: Optional[str] = None
    is_public: Optional[bool] = None


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Project File schemas
class ProjectFileBase(BaseModel):
    name: str
    content: str = ""


class ProjectFileCreate(ProjectFileBase):
    project_id: int


class ProjectFileResponse(ProjectFileBase):
    id: int
    project_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Execution schemas
class ExecutionRequest(BaseModel):
    language: str
    code: str
    input_data: Optional[str] = ""


class ExecutionResponse(BaseModel):
    output: Optional[str] = None
    error: Optional[str] = None
    status: str
    execution_time: Optional[int] = None


class ExecutionHistoryResponse(BaseModel):
    id: int
    user_id: int
    project_id: Optional[int] = None
    language: str
    code: str
    input_data: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    status: str
    execution_time: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
