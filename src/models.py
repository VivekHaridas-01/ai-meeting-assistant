from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

class SpeakerRole(str, Enum):
    """Enum for speaker roles in the meeting"""
    PARTICIPANT = "participant"
    MODERATOR = "moderator"
    UNKNOWN = "unknown"

class Speaker(BaseModel):
    """Model for speaker information"""
    speaker_id: str
    role: SpeakerRole = SpeakerRole.PARTICIPANT
    name: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)

class TranscriptionSegment(BaseModel):
    """Model for a segment of transcribed speech"""
    start: int  # Start time in milliseconds
    end: int    # End time in milliseconds
    speaker: str
    text: str
    confidence: float = Field(ge=0.0, le=1.0)

class MeetingTranscript(BaseModel):
    """Model for the complete meeting transcript"""
    meeting_id: str
    audio_url: str
    duration: int  # Duration in milliseconds
    speakers: List[Speaker]
    segments: List[TranscriptionSegment]
    created_at: datetime = Field(default_factory=datetime.now)

class ActionItem(BaseModel):
    """Model for action items from the meeting"""
    description: str
    assignee: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = "medium"  # low, medium, high
    status: str = "pending"   # pending, in_progress, completed

class Decision(BaseModel):
    """Model for decisions made in the meeting"""
    topic: str
    decision: str
    rationale: Optional[str] = None
    impact: Optional[str] = None

class MeetingMinutes(BaseModel):
    """Model for structured meeting minutes"""
    meeting_id: str
    date: datetime
    duration: timedelta
    participants: List[str]
    key_points: List[str]
    action_items: List[ActionItem]
    decisions: List[Decision]
    next_steps: List[str]
    summary: str

class CalendarEvent(BaseModel):
    """Model for Google Calendar event creation"""
    summary: str
    description: str
    start_time: datetime
    end_time: datetime
    attendees: List[str] = []
    location: Optional[str] = None
    reminders: Dict[str, Any] = {
        "useDefault": False,
        "overrides": [
            {"method": "email", "minutes": 24 * 60},
            {"method": "popup", "minutes": 30},
        ]
    }

class ProcessingStatus(str, Enum):
    """Enum for processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingResult(BaseModel):
    """Model for processing results"""
    status: ProcessingStatus
    meeting_id: str
    transcript: Optional[MeetingTranscript] = None
    minutes: Optional[MeetingMinutes] = None
    calendar_events: List[CalendarEvent] = []
    error_message: Optional[str] = None
    processing_time: Optional[float] = None  # in seconds 