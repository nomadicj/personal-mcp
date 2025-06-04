from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ReminderStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"

class StaffMember(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    team: Optional[str] = None
    hire_date: Optional[datetime] = None
    manager: Optional[str] = None
    notes: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    last_one_on_one: Optional[datetime] = None
    next_review: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Note(BaseModel):
    id: str
    staff_id: str
    content: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    timestamp: datetime = Field(default_factory=datetime.now)
    source: Optional[str] = None  # e.g., "call_transcript", "one_on_one", "manual"

class Reminder(BaseModel):
    id: str
    staff_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    due_date: datetime
    priority: Priority = Priority.MEDIUM
    status: ReminderStatus = ReminderStatus.PENDING
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

class Goal(BaseModel):
    id: str
    staff_id: str
    title: str
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    progress_notes: List[str] = Field(default_factory=list)
    status: str = "active"  # active, completed, paused, cancelled
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class CallTranscript(BaseModel):
    id: str
    title: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    content: str
    date: datetime = Field(default_factory=datetime.now)
    extracted_items: List[Dict[str, Any]] = Field(default_factory=list)
    processed: bool = False