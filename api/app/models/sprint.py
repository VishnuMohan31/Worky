from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Date, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(String(20), primary_key=True, server_default=text("generate_sprint_id()"))
    project_id = Column(String(20), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    goal = Column(Text)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(50), default="Planning")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="sprints")
    sprint_tasks = relationship("SprintTask", back_populates="sprint", cascade="all, delete-orphan")
    tasks = relationship("Task", foreign_keys="Task.sprint_id", back_populates="sprint")


class SprintTask(Base):
    __tablename__ = "sprint_tasks"

    sprint_id = Column(String(20), ForeignKey("sprints.id"), primary_key=True)
    task_id = Column(String(20), ForeignKey("tasks.id"), primary_key=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sprint = relationship("Sprint", back_populates="sprint_tasks")
    task = relationship("Task", back_populates="sprint_tasks")
