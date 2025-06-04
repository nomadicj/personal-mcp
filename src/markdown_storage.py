import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
from .models import StaffMember, Note, Reminder, Goal, CallTranscript

class MarkdownStorage:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.staff_dir = self.data_dir / "staff"
        self.reminders_file = self.data_dir / "reminders.md"
        self.transcripts_dir = self.data_dir / "transcripts"
        
        # Create directories
        self.staff_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize reminders file if not exists
        if not self.reminders_file.exists():
            self._create_reminders_file()
    
    def _create_reminders_file(self):
        """Create initial reminders markdown file"""
        content = """# Team Management Reminders

## Pending Tasks

<!-- Tasks will be automatically added here -->

## Completed Tasks

<!-- Completed tasks will be moved here -->
"""
        self.reminders_file.write_text(content)
    
    def _sanitize_filename(self, name: str) -> str:
        """Convert name to safe filename"""
        # Remove special characters, replace spaces with hyphens
        safe_name = re.sub(r'[^\w\s-]', '', name)
        safe_name = re.sub(r'[-\s]+', '-', safe_name)
        return safe_name.lower().strip('-')
    
    def _parse_frontmatter(self, content: str) -> tuple[Dict, str]:
        """Parse YAML frontmatter from markdown content"""
        if not content.startswith('---\n'):
            return {}, content
        
        try:
            end_marker = content.find('\n---\n', 4)
            if end_marker == -1:
                return {}, content
            
            frontmatter = content[4:end_marker]
            body = content[end_marker + 5:]
            
            metadata = yaml.safe_load(frontmatter) or {}
            return metadata, body
        except:
            return {}, content
    
    def _create_staff_markdown(self, staff: StaffMember) -> str:
        """Generate markdown content for a staff member"""
        metadata = {
            'id': staff.id,
            'name': staff.name,
            'email': staff.email,
            'role': staff.role,
            'department': staff.department,
            'hire_date': staff.hire_date.isoformat() if staff.hire_date else None,
            'manager': staff.manager,
            'last_one_on_one': staff.last_one_on_one.isoformat() if staff.last_one_on_one else None,
            'next_review': staff.next_review.isoformat() if staff.next_review else None,
            'created_at': staff.created_at.isoformat(),
            'updated_at': staff.updated_at.isoformat(),
        }
        
        # Remove None values
        metadata = {k: v for k, v in metadata.items() if v is not None}
        
        content = f"""---
{yaml.dump(metadata, default_flow_style=False)}---

# {staff.name}

## Overview
- **Role:** {staff.role or 'Not specified'}
- **Department:** {staff.department or 'Not specified'}
- **Email:** {staff.email or 'Not specified'}
- **Manager:** {staff.manager or 'Not specified'}

## Skills
{chr(10).join(f'- {skill}' for skill in staff.skills) if staff.skills else '- No skills listed yet'}

## Current Goals
{chr(10).join(f'- {goal}' for goal in staff.goals) if staff.goals else '- No current goals'}

## Notes
{chr(10).join(f'- {note}' for note in staff.notes) if staff.notes else '- No notes yet'}

## Achievements
{chr(10).join(f'- {achievement}' for achievement in staff.achievements) if staff.achievements else '- No achievements recorded yet'}

## Concerns
{chr(10).join(f'- {concern}' for concern in staff.concerns) if staff.concerns else '- No concerns noted'}

---
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        return content
    
    def save_staff(self, staff: StaffMember):
        """Save staff member as markdown file"""
        staff.updated_at = datetime.now()
        filename = f"{self._sanitize_filename(staff.name)}.md"
        file_path = self.staff_dir / filename
        
        content = self._create_staff_markdown(staff)
        file_path.write_text(content)
    
    def get_staff_by_id(self, staff_id: str) -> Optional[StaffMember]:
        """Get staff member by ID"""
        for file_path in self.staff_dir.glob("*.md"):
            content = file_path.read_text()
            metadata, _ = self._parse_frontmatter(content)
            
            if metadata.get('id') == staff_id:
                return self._markdown_to_staff(content)
        return None
    
    def get_staff_by_name(self, name: str) -> Optional[StaffMember]:
        """Get staff member by name"""
        filename = f"{self._sanitize_filename(name)}.md"
        file_path = self.staff_dir / filename
        
        if file_path.exists():
            content = file_path.read_text()
            return self._markdown_to_staff(content)
        return None
    
    def get_all_staff(self) -> List[StaffMember]:
        """Get all staff members"""
        staff_list = []
        for file_path in self.staff_dir.glob("*.md"):
            try:
                content = file_path.read_text()
                staff = self._markdown_to_staff(content)
                if staff:
                    staff_list.append(staff)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        return staff_list
    
    def _markdown_to_staff(self, content: str) -> Optional[StaffMember]:
        """Convert markdown content to StaffMember object"""
        metadata, body = self._parse_frontmatter(content)
        
        if not metadata.get('id'):
            return None
        
        # Parse lists from markdown body
        skills = self._extract_list_from_section(body, "## Skills")
        goals = self._extract_list_from_section(body, "## Current Goals") 
        notes = self._extract_list_from_section(body, "## Notes")
        achievements = self._extract_list_from_section(body, "## Achievements")
        concerns = self._extract_list_from_section(body, "## Concerns")
        
        try:
            return StaffMember(
                id=metadata['id'],
                name=metadata['name'],
                email=metadata.get('email'),
                role=metadata.get('role'),
                department=metadata.get('department'),
                hire_date=datetime.fromisoformat(metadata['hire_date']) if metadata.get('hire_date') else None,
                manager=metadata.get('manager'),
                last_one_on_one=datetime.fromisoformat(metadata['last_one_on_one']) if metadata.get('last_one_on_one') else None,
                next_review=datetime.fromisoformat(metadata['next_review']) if metadata.get('next_review') else None,
                created_at=datetime.fromisoformat(metadata['created_at']),
                updated_at=datetime.fromisoformat(metadata['updated_at']),
                skills=skills,
                goals=goals,
                notes=notes,
                achievements=achievements,
                concerns=concerns
            )
        except Exception as e:
            print(f"Error parsing staff member: {e}")
            return None
    
    def _extract_list_from_section(self, content: str, section_header: str) -> List[str]:
        """Extract list items from a markdown section"""
        items = []
        lines = content.split('\n')
        in_section = False
        
        for line in lines:
            if line.strip() == section_header:
                in_section = True
                continue
            elif line.startswith('## ') and in_section:
                break
            elif in_section and line.strip().startswith('- '):
                item = line.strip()[2:].strip()
                if item and not item.startswith('No ') and not item.startswith('*'):
                    items.append(item)
        
        return items
    
    def delete_staff(self, staff_id: str) -> bool:
        """Delete staff member"""
        staff = self.get_staff_by_id(staff_id)
        if staff:
            filename = f"{self._sanitize_filename(staff.name)}.md"
            file_path = self.staff_dir / filename
            if file_path.exists():
                file_path.unlink()
                return True
        return False
    
    def add_note_to_staff(self, staff_id: str, note_content: str, category: str = None, source: str = None):
        """Add a note to staff member's markdown file"""
        staff = self.get_staff_by_id(staff_id)
        if staff:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            note_with_meta = f"{note_content}"
            if category or source:
                note_with_meta += f" *({category or 'general'}"
                if source:
                    note_with_meta += f", from {source}"
                note_with_meta += f", {timestamp})*"
            else:
                note_with_meta += f" *({timestamp})*"
            
            staff.notes.append(note_with_meta)
            self.save_staff(staff)
    
    def save_reminder_to_markdown(self, reminder: Reminder):
        """Add reminder to markdown file"""
        if not self.reminders_file.exists():
            self._create_reminders_file()
        
        content = self.reminders_file.read_text()
        
        # Format reminder
        priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴", "urgent": "🚨"}
        emoji = priority_emoji.get(reminder.priority.value, "⚪")
        
        reminder_line = f"- {emoji} **{reminder.title}** (Due: {reminder.due_date.strftime('%Y-%m-%d')})"
        if reminder.description:
            reminder_line += f"\n  - {reminder.description}"
        if reminder.staff_id:
            staff = self.get_staff_by_id(reminder.staff_id)
            if staff:
                reminder_line += f"\n  - Related to: {staff.name}"
        reminder_line += f"\n  - ID: `{reminder.id}`\n"
        
        # Add to pending section
        lines = content.split('\n')
        pending_index = -1
        for i, line in enumerate(lines):
            if line.strip() == "## Pending Tasks":
                pending_index = i
                break
        
        if pending_index != -1:
            # Find insertion point (after the header and comment)
            insert_index = pending_index + 1
            while insert_index < len(lines) and (lines[insert_index].strip() == "" or lines[insert_index].strip().startswith("<!--")):
                insert_index += 1
            
            lines.insert(insert_index, reminder_line)
            self.reminders_file.write_text('\n'.join(lines))
    
    def get_all_reminders(self) -> List[Reminder]:
        """Parse all reminders from markdown file"""
        reminders = []
        if not self.reminders_file.exists():
            return reminders
        
        content = self.reminders_file.read_text()
        lines = content.split('\n')
        
        current_reminder = None
        in_pending = False
        in_completed = False
        
        for line in lines:
            line = line.strip()
            
            if line == "## Pending Tasks":
                in_pending = True
                in_completed = False
                continue
            elif line == "## Completed Tasks":
                in_pending = False
                in_completed = True
                continue
            elif line.startswith("## "):
                in_pending = False
                in_completed = False
                continue
            
            # Parse reminder line
            if (in_pending or in_completed) and line.startswith("- ") and "**" in line:
                # Finalize previous reminder first
                if current_reminder:
                    try:
                        from .models import Priority, ReminderStatus
                        import uuid as uuid_module
                        reminder = Reminder(
                            id=current_reminder['id'] or str(uuid_module.uuid4()),
                            title=current_reminder['title'],
                            description=current_reminder['description'],
                            due_date=current_reminder['due_date'],
                            priority=Priority(current_reminder['priority']),
                            status=ReminderStatus(current_reminder['status']),
                            staff_id=current_reminder['staff_id']
                        )
                        reminders.append(reminder)
                    except Exception as e:
                        print(f"Error parsing previous reminder: {e}")
                
                # Parse: - 🔴 **Title** (Due: 2024-06-15) or - ✅ **Title** (Completed: 2024-06-15)
                import re
                due_match = re.search(r'- [🟢🟡🔴🚨⚪] \*\*(.*?)\*\* \(Due: ([\d-]+)\)', line)
                completed_match = re.search(r'- ✅ \*\*(.*?)\*\* \(Completed: ([\d-]+)\)', line)
                
                if due_match:
                    title = due_match.group(1)
                    due_date_str = due_match.group(2)
                    
                    # Map emoji to priority
                    priority_map = {"🟢": "low", "🟡": "medium", "🔴": "high", "🚨": "urgent", "⚪": "medium"}
                    emoji = line.split()[1] if len(line.split()) > 1 else "⚪"
                    priority = priority_map.get(emoji, "medium")
                    
                    try:
                        due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                        current_reminder = {
                            'title': title,
                            'due_date': due_date,
                            'priority': priority,
                            'status': 'pending',
                            'description': '',
                            'staff_id': None,
                            'id': None
                        }
                    except ValueError:
                        continue
                elif completed_match:
                    title = completed_match.group(1)
                    completed_date_str = completed_match.group(2)
                    
                    try:
                        completed_date = datetime.strptime(completed_date_str, '%Y-%m-%d')
                        current_reminder = {
                            'title': title,
                            'due_date': completed_date,  # Use completed date as due date
                            'priority': 'medium',
                            'status': 'completed',
                            'description': '',
                            'staff_id': None,
                            'id': None
                        }
                    except ValueError:
                        continue
            
            # Parse description and metadata
            elif current_reminder and line.startswith("  - "):
                detail = line[4:].strip()
                if detail.startswith("Related to:"):
                    # Find staff by name
                    name = detail.replace("Related to:", "").strip()
                    staff = self.get_staff_by_name(name)
                    if staff:
                        current_reminder['staff_id'] = staff.id
                elif detail.startswith("ID:"):
                    # Extract ID from backticks
                    id_match = re.search(r'`([^`]+)`', detail)
                    if id_match:
                        current_reminder['id'] = id_match.group(1)
                else:
                    current_reminder['description'] = detail
            
            # Empty line or end of reminder - do nothing, we handle completion in the main parse loop
        
        # Handle last reminder if file doesn't end with empty line
        if current_reminder:
            try:
                from .models import Priority, ReminderStatus
                import uuid as uuid_module
                reminder = Reminder(
                    id=current_reminder['id'] or str(uuid_module.uuid4()),
                    title=current_reminder['title'],
                    description=current_reminder['description'],
                    due_date=current_reminder['due_date'],
                    priority=Priority(current_reminder['priority']),
                    status=ReminderStatus(current_reminder['status']),
                    staff_id=current_reminder['staff_id']
                )
                reminders.append(reminder)
            except Exception as e:
                print(f"Error parsing final reminder: {e}")
        
        return reminders
    
    def complete_reminder(self, reminder: Reminder):
        """Move reminder from pending to completed section"""
        if not self.reminders_file.exists():
            return
        
        content = self.reminders_file.read_text()
        lines = content.split('\n')
        
        # Find and remove the reminder from pending section
        reminder_found = False
        new_lines = []
        skip_next_lines = 0
        
        for i, line in enumerate(lines):
            if skip_next_lines > 0:
                skip_next_lines -= 1
                continue
                
            # Look for our reminder by ID
            if f"ID: `{reminder.id}`" in line:
                # Remove this line and the previous reminder lines
                # Go back to find the start of this reminder
                j = len(new_lines) - 1
                while j >= 0 and not new_lines[j].strip().startswith("- "):
                    j -= 1
                if j >= 0:
                    new_lines = new_lines[:j]  # Remove the reminder and its details
                reminder_found = True
                continue
            else:
                new_lines.append(line)
        
        if reminder_found:
            # Add to completed section
            completed_index = -1
            for i, line in enumerate(new_lines):
                if line.strip() == "## Completed Tasks":
                    completed_index = i
                    break
            
            if completed_index != -1:
                # Create completed reminder entry
                priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴", "urgent": "🚨"}
                emoji = priority_emoji.get(reminder.priority.value, "⚪")
                
                completed_line = f"- ✅ **{reminder.title}** (Completed: {datetime.now().strftime('%Y-%m-%d')})"
                if reminder.description:
                    completed_line += f"\n  - {reminder.description}"
                if reminder.staff_id:
                    staff = self.get_staff_by_id(reminder.staff_id)
                    if staff:
                        completed_line += f"\n  - Related to: {staff.name}"
                completed_line += f"\n  - ID: `{reminder.id}`\n"
                
                # Insert after completed header
                insert_index = completed_index + 1
                while insert_index < len(new_lines) and (new_lines[insert_index].strip() == "" or new_lines[insert_index].strip().startswith("<!--")):
                    insert_index += 1
                
                new_lines.insert(insert_index, completed_line)
                self.reminders_file.write_text('\n'.join(new_lines))
    
    def get_goals_for_staff(self, staff_id: str) -> List[Goal]:
        """Extract goals from staff member's markdown file"""
        staff = self.get_staff_by_id(staff_id)
        if not staff:
            return []
        
        # For now, convert the simple goal strings to Goal objects
        # In a full implementation, we'd store goals with more metadata
        goals = []
        for i, goal_text in enumerate(staff.goals):
            goal = Goal(
                id=f"{staff_id}-goal-{i}",
                staff_id=staff_id,
                title=goal_text,
                description="",
                target_date=None,
                status="in_progress",
                progress_notes=[]
            )
            goals.append(goal)
        
        return goals
    
    def save_goal(self, goal: Goal):
        """Save/update goal in staff member's markdown file"""
        staff = self.get_staff_by_id(goal.staff_id)
        if not staff:
            return
        
        # Update or add goal to staff member's goals list
        goal_found = False
        for i, existing_goal in enumerate(staff.goals):
            if f"{goal.staff_id}-goal-{i}" == goal.id:
                staff.goals[i] = goal.title
                goal_found = True
                break
        
        if not goal_found:
            staff.goals.append(goal.title)
        
        self.save_staff(staff)
    
    def save_transcript(self, transcript: CallTranscript):
        """Save call transcript as markdown file"""
        filename = f"{datetime.now().strftime('%Y-%m-%d')}-{self._sanitize_filename(transcript.title or 'transcript')}.md"
        file_path = self.transcripts_dir / filename
        
        content = f"""# {transcript.title or 'Call Transcript'}

**Date:** {transcript.created_at.strftime('%Y-%m-%d %H:%M')}
**Participants:** {', '.join(transcript.participants) if transcript.participants else 'Not specified'}

## Transcript Content

{transcript.content}

## Extracted Items

"""
        
        if hasattr(transcript, 'extracted_items') and transcript.extracted_items:
            for item in transcript.extracted_items:
                content += f"- **{item.get('type', 'item').title()}:** {item.get('content', '')}\n"
                if item.get('participants'):
                    content += f"  - Participants: {', '.join(item['participants'])}\n"
        else:
            content += "No items extracted yet.\n"
        
        content += f"\n---\n*Processed: {transcript.processed}*\n*ID: {transcript.id}*\n"
        
        file_path.write_text(content)
    
    def get_notes_for_staff(self, staff_id: str) -> List[Note]:
        """Get all notes for a staff member"""
        staff = self.get_staff_by_id(staff_id)
        if not staff:
            return []
        
        # Convert staff notes to Note objects
        notes = []
        for i, note_text in enumerate(staff.notes):
            # Parse timestamp and metadata from note text
            import re
            timestamp_match = re.search(r'\*\(.*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}).*?\)\*', note_text)
            if timestamp_match:
                try:
                    timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M')
                except:
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()
            
            # Extract category
            category_match = re.search(r'\*\((.*?),', note_text)
            category = category_match.group(1) if category_match else 'general'
            
            # Clean content
            clean_content = re.sub(r'\s*\*\(.*?\)\*\s*$', '', note_text).strip()
            
            note = Note(
                id=f"{staff_id}-note-{i}",
                staff_id=staff_id,
                content=clean_content,
                category=category,
                timestamp=timestamp
            )
            notes.append(note)
        
        return notes