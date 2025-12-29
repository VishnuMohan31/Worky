from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Date, Numeric, Boolean, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Program(Base):
    __tablename__ = "programs"

    id = Column(String(20), primary_key=True, server_default=text("generate_string_id('PRG', 'programs_id_seq')"))
    client_id = Column(String(20), ForeignKey("clients.id"), nullable=False)
    name = Column(String(255), nullable=False)
    short_description = Column(String(500))
    long_description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(50), default="Planning")
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="programs")
    projects = relationship("Project", back_populates="program", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(20), primary_key=True, server_default=text("generate_string_id('PRJ', 'projects_id_seq')"))
    program_id = Column(String(20), ForeignKey("programs.id"), nullable=False)
    name = Column(String(255), nullable=False)
    short_description = Column(String(500))
    long_description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(50), default="Planning")
    repository_url = Column(String(500))
    # Sprint configuration (project-level)
    sprint_length_weeks = Column(String(10), default="2")  # "1" or "2"
    sprint_starting_day = Column(String(20), default="Monday")  # Monday, Tuesday, Wednesday, etc.
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    program = relationship("Program", back_populates="projects")
    usecases = relationship("Usecase", back_populates="project", cascade="all, delete-orphan")
    sprints = relationship("Sprint", back_populates="project", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="project", cascade="all, delete-orphan")


class Usecase(Base):
    __tablename__ = "usecases"

    id = Column(String(20), primary_key=True, server_default=text("generate_string_id('USC', 'usecases_id_seq')"))
    project_id = Column(String(20), ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    short_description = Column(String(500))
    long_description = Column(Text)
    priority = Column(String(20), default="Medium")
    status = Column(String(50), default="Draft")
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="usecases")
    user_stories = relationship("UserStory", back_populates="usecase", cascade="all, delete-orphan")


class UserStory(Base):
    __tablename__ = "user_stories"

    id = Column(String(20), primary_key=True, server_default=text("generate_string_id('UST', 'user_stories_id_seq')"))
    usecase_id = Column(String(20), ForeignKey("usecases.id"), nullable=False)
    phase_id = Column(String(20), ForeignKey("phases.id"), nullable=False)
    name = Column(String(255), nullable=False)
    short_description = Column(String(500))
    long_description = Column(Text)
    acceptance_criteria = Column(Text)
    story_points = Column(Integer)
    priority = Column(String(20), default="Medium")
    status = Column(String(50), default="Backlog")
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    usecase = relationship("Usecase", back_populates="user_stories")
    phase = relationship("Phase", back_populates="user_stories")
    tasks = relationship("Task", back_populates="user_story", cascade="all, delete-orphan")
    # bugs = relationship("Bug", back_populates="user_story")  # Disabled until Bug.user_story_id exists


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(20), primary_key=True, server_default=text("generate_string_id('TSK', 'tasks_id_seq')"))
    user_story_id = Column(String(20), ForeignKey("user_stories.id"), nullable=False)
    phase_id = Column(String(20), ForeignKey("phases.id"))
    name = Column(String(255), nullable=False)
    short_description = Column(String(500))
    long_description = Column(Text)
    status = Column(String(50), default="To Do")
    priority = Column(String(20), default="Medium")
    assigned_to = Column(String(20), ForeignKey("users.id"))
    sprint_id = Column(String(20), ForeignKey("sprints.id"))
    estimated_hours = Column(Numeric(10, 2))
    actual_hours = Column(Numeric(10, 2))
    start_date = Column(Date)
    due_date = Column(Date)
    completed_at = Column(DateTime(timezone=True))
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user_story = relationship("UserStory", back_populates="tasks")
    phase = relationship("Phase", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to])
    sprint = relationship("Sprint", foreign_keys=[sprint_id])
    subtasks = relationship("Subtask", back_populates="task", cascade="all, delete-orphan")
    commits = relationship("Commit", back_populates="task")
    # bugs = relationship("Bug", back_populates="task")  # Disabled until Bug.task_id exists
    sprint_tasks = relationship("SprintTask", back_populates="task")


class Subtask(Base):
    __tablename__ = "subtasks"

    id = Column(String(20), primary_key=True, server_default=text("generate_string_id('SUB', 'subtasks_id_seq')"))
    task_id = Column(String(20), ForeignKey("tasks.id"), nullable=False)
    phase_id = Column(String(20), ForeignKey("phases.id"))
    name = Column(String(255), nullable=False)
    short_description = Column(String(500))
    long_description = Column(Text)
    status = Column(String(50), default="To Do")
    assigned_to = Column(String(20), ForeignKey("users.id"))
    estimated_hours = Column(Numeric(10, 2))
    actual_hours = Column(Numeric(10, 2))
    duration_days = Column(Integer)
    scrum_points = Column(Numeric(5, 2))
    completed_at = Column(DateTime(timezone=True))
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    task = relationship("Task", back_populates="subtasks")
    phase = relationship("Phase", back_populates="subtasks")
    assignee = relationship("User", foreign_keys=[assigned_to])


class Phase(Base):
    __tablename__ = "phases"

    id = Column(String(20), primary_key=True, server_default=text("generate_string_id('PHS', 'phases_id_seq')"))
    name = Column(String(255), nullable=False, unique=True)
    short_description = Column(String(500))
    long_description = Column(Text)
    color = Column(String(7), nullable=False, default='#4A90E2')
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(255))
    updated_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user_stories = relationship("UserStory", back_populates="phase")
    tasks = relationship("Task", back_populates="phase")
    subtasks = relationship("Subtask", back_populates="phase")
