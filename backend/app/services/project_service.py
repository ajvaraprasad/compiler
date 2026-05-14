from sqlalchemy.orm import Session
from app.models.models import Project, ProjectFile, ExecutionHistory
from typing import List, Optional
from datetime import datetime


def get_projects_by_user(db: Session, user_id: int) -> List[Project]:
    return db.query(Project).filter(Project.owner_id == user_id).all()


def get_project_by_id(db: Session, project_id: int, user_id: Optional[int] = None) -> Optional[Project]:
    query = db.query(Project).filter(Project.id == project_id)
    if user_id:
        query = query.filter(Project.owner_id == user_id)
    return query.first()


def create_project(db: Session, owner_id: int, name: str, language: str, code: str = "", description: str = None, is_public: bool = False) -> Project:
    project = Project(
        name=name,
        description=description,
        language=language,
        code=code,
        owner_id=owner_id,
        is_public=is_public
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project_id: int, **kwargs) -> Optional[Project]:
    project = get_project_by_id(db, project_id)
    if not project:
        return None
    
    for key, value in kwargs.items():
        if hasattr(project, key):
            setattr(project, key, value)
    
    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int) -> bool:
    project = get_project_by_id(db, project_id)
    if not project:
        return False
    
    db.delete(project)
    db.commit()
    return True


# Project File operations
def get_project_files(db: Session, project_id: int) -> List[ProjectFile]:
    return db.query(ProjectFile).filter(ProjectFile.project_id == project_id).all()


def get_project_file_by_id(db: Session, file_id: int) -> Optional[ProjectFile]:
    return db.query(ProjectFile).filter(ProjectFile.id == file_id).first()


def create_project_file(db: Session, project_id: int, name: str, content: str = "") -> ProjectFile:
    file = ProjectFile(
        name=name,
        content=content,
        project_id=project_id
    )
    db.add(file)
    db.commit()
    db.refresh(file)
    return file


def update_project_file(db: Session, file_id: int, content: str) -> Optional[ProjectFile]:
    file = get_project_file_by_id(db, file_id)
    if not file:
        return None
    
    file.content = content
    db.commit()
    db.refresh(file)
    return file


def delete_project_file(db: Session, file_id: int) -> bool:
    file = get_project_file_by_id(db, file_id)
    if not file:
        return False
    
    db.delete(file)
    db.commit()
    return True


# Execution History operations
def create_execution_history(
    db: Session, 
    user_id: int, 
    language: str, 
    code: str, 
    input_data: str = None,
    project_id: int = None
) -> ExecutionHistory:
    execution = ExecutionHistory(
        user_id=user_id,
        project_id=project_id,
        language=language,
        code=code,
        input_data=input_data,
        status="pending"
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution


def update_execution_history(
    db: Session, 
    execution_id: int, 
    output: str = None, 
    error: str = None, 
    status: str = None,
    execution_time: int = None
) -> Optional[ExecutionHistory]:
    execution = db.query(ExecutionHistory).filter(ExecutionHistory.id == execution_id).first()
    if not execution:
        return None
    
    if output is not None:
        execution.output = output
    if error is not None:
        execution.error = error
    if status is not None:
        execution.status = status
    if execution_time is not None:
        execution.execution_time = execution_time
    
    db.commit()
    db.refresh(execution)
    return execution


def get_execution_history_by_user(db: Session, user_id: int, limit: int = 20) -> List[ExecutionHistory]:
    return db.query(ExecutionHistory).filter(
        ExecutionHistory.user_id == user_id
    ).order_by(ExecutionHistory.created_at.desc()).limit(limit).all()
