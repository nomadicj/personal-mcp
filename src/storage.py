import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from .models import StaffMember, Note, Reminder, Goal, CallTranscript

class JSONStorage:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.staff_file = self.data_dir / "staff.json"
        self.notes_file = self.data_dir / "notes.json"
        self.reminders_file = self.data_dir / "reminders.json"
        self.goals_file = self.data_dir / "goals.json"
        self.transcripts_file = self.data_dir / "transcripts.json"
        
        self._init_files()
    
    def _init_files(self):
        for file_path in [self.staff_file, self.notes_file, self.reminders_file, 
                         self.goals_file, self.transcripts_file]:
            if not file_path.exists():
                file_path.write_text("[]")
    
    def _load_json(self, file_path: Path) -> List[Dict]:
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_json(self, file_path: Path, data: List[Dict]):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # Staff operations
    def get_all_staff(self) -> List[StaffMember]:
        data = self._load_json(self.staff_file)
        return [StaffMember(**item) for item in data]
    
    def get_staff_by_id(self, staff_id: str) -> Optional[StaffMember]:
        staff_list = self.get_all_staff()
        for staff in staff_list:
            if staff.id == staff_id:
                return staff
        return None
    
    def save_staff(self, staff: StaffMember):
        staff_list = self.get_all_staff()
        staff.updated_at = datetime.now()
        
        for i, existing in enumerate(staff_list):
            if existing.id == staff.id:
                staff_list[i] = staff
                break
        else:
            staff_list.append(staff)
        
        data = [s.model_dump() for s in staff_list]
        self._save_json(self.staff_file, data)
    
    def delete_staff(self, staff_id: str) -> bool:
        staff_list = self.get_all_staff()
        original_length = len(staff_list)
        staff_list = [s for s in staff_list if s.id != staff_id]
        
        if len(staff_list) < original_length:
            data = [s.model_dump() for s in staff_list]
            self._save_json(self.staff_file, data)
            return True
        return False
    
    # Notes operations
    def get_notes_for_staff(self, staff_id: str) -> List[Note]:
        data = self._load_json(self.notes_file)
        notes = [Note(**item) for item in data]
        return [note for note in notes if note.staff_id == staff_id]
    
    def save_note(self, note: Note):
        data = self._load_json(self.notes_file)
        notes = [Note(**item) for item in data]
        
        for i, existing in enumerate(notes):
            if existing.id == note.id:
                notes[i] = note
                break
        else:
            notes.append(note)
        
        data = [n.model_dump() for n in notes]
        self._save_json(self.notes_file, data)
    
    # Reminders operations
    def get_all_reminders(self) -> List[Reminder]:
        data = self._load_json(self.reminders_file)
        return [Reminder(**item) for item in data]
    
    def get_pending_reminders(self) -> List[Reminder]:
        reminders = self.get_all_reminders()
        return [r for r in reminders if r.status.value == "pending"]
    
    def save_reminder(self, reminder: Reminder):
        data = self._load_json(self.reminders_file)
        reminders = [Reminder(**item) for item in data]
        
        for i, existing in enumerate(reminders):
            if existing.id == reminder.id:
                reminders[i] = reminder
                break
        else:
            reminders.append(reminder)
        
        data = [r.model_dump() for r in reminders]
        self._save_json(self.reminders_file, data)
    
    # Goals operations
    def get_goals_for_staff(self, staff_id: str) -> List[Goal]:
        data = self._load_json(self.goals_file)
        goals = [Goal(**item) for item in data]
        return [goal for goal in goals if goal.staff_id == staff_id]
    
    def save_goal(self, goal: Goal):
        data = self._load_json(self.goals_file)
        goals = [Goal(**item) for item in data]
        goal.updated_at = datetime.now()
        
        for i, existing in enumerate(goals):
            if existing.id == goal.id:
                goals[i] = goal
                break
        else:
            goals.append(goal)
        
        data = [g.model_dump() for g in goals]
        self._save_json(self.goals_file, data)
    
    # Transcript operations
    def save_transcript(self, transcript: CallTranscript):
        data = self._load_json(self.transcripts_file)
        transcripts = [CallTranscript(**item) for item in data]
        
        for i, existing in enumerate(transcripts):
            if existing.id == transcript.id:
                transcripts[i] = transcript
                break
        else:
            transcripts.append(transcript)
        
        data = [t.model_dump() for t in transcripts]
        self._save_json(self.transcripts_file, data)