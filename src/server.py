import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Sequence
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import AnyUrl

from .markdown_storage import MarkdownStorage
from .models import StaffMember, Note, Reminder, Goal, CallTranscript, Priority

# Initialize storage
storage = MarkdownStorage()

server = Server("personal-assistant")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="add_staff_member",
            description="Add a new staff member to the team",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Staff member's full name"},
                    "email": {"type": "string", "description": "Email address"},
                    "role": {"type": "string", "description": "Job title/role"},
                    "department": {"type": "string", "description": "Department"},
                    "team": {"type": "string", "description": "Team name"},
                    "manager": {"type": "string", "description": "Manager's name"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="update_staff_member",
            description="Update an existing staff member's information",
            inputSchema={
                "type": "object",
                "properties": {
                    "staff_id": {"type": "string", "description": "Staff member ID"},
                    "name": {"type": "string", "description": "Staff member's full name"},
                    "email": {"type": "string", "description": "Email address"},
                    "role": {"type": "string", "description": "Job title/role"},
                    "department": {"type": "string", "description": "Department"},
                    "team": {"type": "string", "description": "Team name"},
                    "manager": {"type": "string", "description": "Manager's name"},
                },
                "required": ["staff_id"],
            },
        ),
        Tool(
            name="get_staff_member",
            description="Get details for a specific staff member",
            inputSchema={
                "type": "object",
                "properties": {
                    "staff_id": {"type": "string", "description": "Staff member ID"},
                    "name": {"type": "string", "description": "Staff member name (alternative to ID)"},
                },
            },
        ),
        Tool(
            name="list_all_staff",
            description="List all staff members with basic info",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="add_note",
            description="Add a note about a staff member",
            inputSchema={
                "type": "object",
                "properties": {
                    "staff_id": {"type": "string", "description": "Staff member ID"},
                    "content": {"type": "string", "description": "Note content"},
                    "category": {"type": "string", "description": "Note category (e.g., performance, personal, goals)"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for the note"},
                    "source": {"type": "string", "description": "Source of the note (e.g., one_on_one, call_transcript)"},
                },
                "required": ["staff_id", "content"],
            },
        ),
        Tool(
            name="get_staff_notes",
            description="Get all notes for a staff member",
            inputSchema={
                "type": "object",
                "properties": {
                    "staff_id": {"type": "string", "description": "Staff member ID"},
                },
                "required": ["staff_id"],
            },
        ),
        Tool(
            name="add_reminder",
            description="Add a reminder for staff-related tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Reminder title"},
                    "description": {"type": "string", "description": "Detailed description"},
                    "due_date": {"type": "string", "description": "Due date (YYYY-MM-DD or YYYY-MM-DD HH:MM)"},
                    "staff_id": {"type": "string", "description": "Related staff member ID (optional)"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Priority level"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags"},
                },
                "required": ["title", "due_date"],
            },
        ),
        Tool(
            name="list_reminders",
            description="List reminders, optionally filtered by status or staff member",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["pending", "completed", "overdue"], "description": "Filter by status"},
                    "staff_id": {"type": "string", "description": "Filter by staff member"},
                },
            },
        ),
        Tool(
            name="complete_reminder",
            description="Mark a reminder as completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "reminder_id": {"type": "string", "description": "Reminder ID"},
                },
                "required": ["reminder_id"],
            },
        ),
        Tool(
            name="add_goal",
            description="Add a goal for a staff member",
            inputSchema={
                "type": "object",
                "properties": {
                    "staff_id": {"type": "string", "description": "Staff member ID"},
                    "title": {"type": "string", "description": "Goal title"},
                    "description": {"type": "string", "description": "Goal description"},
                    "target_date": {"type": "string", "description": "Target completion date (YYYY-MM-DD)"},
                },
                "required": ["staff_id", "title"],
            },
        ),
        Tool(
            name="update_goal_progress",
            description="Update progress on a staff member's goal",
            inputSchema={
                "type": "object",
                "properties": {
                    "goal_id": {"type": "string", "description": "Goal ID"},
                    "progress_note": {"type": "string", "description": "Progress update"},
                    "status": {"type": "string", "enum": ["active", "completed", "paused", "cancelled"], "description": "Goal status"},
                },
                "required": ["goal_id", "progress_note"],
            },
        ),
        Tool(
            name="get_staff_goals",
            description="Get all goals for a staff member",
            inputSchema={
                "type": "object",
                "properties": {
                    "staff_id": {"type": "string", "description": "Staff member ID"},
                },
                "required": ["staff_id"],
            },
        ),
        Tool(
            name="process_call_transcript",
            description="Process a call transcript to extract insights and action items",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Call/meeting title"},
                    "content": {"type": "string", "description": "Transcript content"},
                    "participants": {"type": "array", "items": {"type": "string"}, "description": "List of participants"},
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="get_management_advice",
            description="Get AI-powered management advice for a staff member based on their notes and context",
            inputSchema={
                "type": "object",
                "properties": {
                    "staff_id": {"type": "string", "description": "Staff member ID"},
                    "situation": {"type": "string", "description": "Current situation or challenge"},
                },
                "required": ["staff_id"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    if arguments is None:
        arguments = {}
    
    try:
        if name == "add_staff_member":
            staff_id = str(uuid.uuid4())
            staff = StaffMember(
                id=staff_id,
                name=arguments["name"],
                email=arguments.get("email"),
                role=arguments.get("role"),
                department=arguments.get("department"),
                team=arguments.get("team"),
                manager=arguments.get("manager"),
            )
            storage.save_staff(staff)
            return [TextContent(type="text", text=f"Staff member {arguments['name']} added with ID: {staff_id}")]
        
        elif name == "get_staff_member":
            if "staff_id" in arguments:
                staff = storage.get_staff_by_id(arguments["staff_id"])
            elif "name" in arguments:
                all_staff = storage.get_all_staff()
                staff = next((s for s in all_staff if s.name.lower() == arguments["name"].lower()), None)
            else:
                return [TextContent(type="text", text="Please provide either staff_id or name")]
            
            if staff:
                return [TextContent(type="text", text=json.dumps(staff.model_dump(), indent=2, default=str))]
            else:
                return [TextContent(type="text", text="Staff member not found")]
        
        elif name == "list_all_staff":
            staff_list = storage.get_all_staff()
            summary = []
            for staff in staff_list:
                summary.append({
                    "id": staff.id,
                    "name": staff.name,
                    "role": staff.role,
                    "department": staff.department,
                    "team": staff.team,
                    "last_one_on_one": staff.last_one_on_one.isoformat() if staff.last_one_on_one else None,
                })
            return [TextContent(type="text", text=json.dumps(summary, indent=2, default=str))]
        
        elif name == "update_staff_member":
            staff = storage.get_staff_by_id(arguments["staff_id"])
            if not staff:
                return [TextContent(type="text", text="Staff member not found")]
            
            # Update only provided fields
            if "name" in arguments:
                staff.name = arguments["name"]
            if "email" in arguments:
                staff.email = arguments["email"]
            if "role" in arguments:
                staff.role = arguments["role"]
            if "department" in arguments:
                staff.department = arguments["department"]
            if "team" in arguments:
                staff.team = arguments["team"]
            if "manager" in arguments:
                staff.manager = arguments["manager"]
            
            storage.save_staff(staff)
            return [TextContent(type="text", text=f"Staff member {staff.name} updated successfully")]
        
        elif name == "add_note":
            storage.add_note_to_staff(
                staff_id=arguments["staff_id"],
                note_content=arguments["content"],
                category=arguments.get("category"),
                source=arguments.get("source")
            )
            return [TextContent(type="text", text="Note added successfully")]
        
        elif name == "get_staff_notes":
            staff = storage.get_staff_by_id(arguments["staff_id"])
            if staff:
                return [TextContent(type="text", text=json.dumps(staff.notes, indent=2, default=str))]
            else:
                return [TextContent(type="text", text="Staff member not found")]
        
        elif name == "add_reminder":
            reminder_id = str(uuid.uuid4())
            due_date = datetime.fromisoformat(arguments["due_date"])
            reminder = Reminder(
                id=reminder_id,
                staff_id=arguments.get("staff_id"),
                title=arguments["title"],
                description=arguments.get("description"),
                due_date=due_date,
                priority=Priority(arguments.get("priority", "medium")),
                tags=arguments.get("tags", []),
            )
            storage.save_reminder_to_markdown(reminder)
            return [TextContent(type="text", text=f"Reminder added with ID: {reminder_id}")]
        
        elif name == "list_reminders":
            reminders = storage.get_all_reminders()
            
            if "status" in arguments:
                reminders = [r for r in reminders if r.status.value == arguments["status"]]
            
            if "staff_id" in arguments:
                reminders = [r for r in reminders if r.staff_id == arguments["staff_id"]]
            
            # Check for overdue reminders
            now = datetime.now()
            for reminder in reminders:
                if reminder.status.value == "pending" and reminder.due_date < now:
                    reminder.status = "overdue"
                    # Note: For markdown storage, we just update the status in memory
            
            reminders_data = [reminder.model_dump() for reminder in reminders]
            return [TextContent(type="text", text=json.dumps(reminders_data, indent=2, default=str))]
        
        elif name == "complete_reminder":
            reminders = storage.get_all_reminders()
            reminder = next((r for r in reminders if r.id == arguments["reminder_id"]), None)
            if reminder:
                reminder.status = "completed"
                reminder.completed_at = datetime.now()
                storage.complete_reminder(reminder)
                return [TextContent(type="text", text="Reminder marked as completed")]
            else:
                return [TextContent(type="text", text="Reminder not found")]
        
        elif name == "add_goal":
            goal_id = str(uuid.uuid4())
            target_date = None
            if "target_date" in arguments:
                target_date = datetime.fromisoformat(arguments["target_date"])
            
            goal = Goal(
                id=goal_id,
                staff_id=arguments["staff_id"],
                title=arguments["title"],
                description=arguments.get("description"),
                target_date=target_date,
            )
            storage.save_goal(goal)
            return [TextContent(type="text", text=f"Goal added with ID: {goal_id}")]
        
        elif name == "update_goal_progress":
            all_goals = []
            for staff in storage.get_all_staff():
                all_goals.extend(storage.get_goals_for_staff(staff.id))
            
            goal = next((g for g in all_goals if g.id == arguments["goal_id"]), None)
            if goal:
                goal.progress_notes.append(f"{datetime.now().isoformat()}: {arguments['progress_note']}")
                if "status" in arguments:
                    goal.status = arguments["status"]
                storage.save_goal(goal)
                return [TextContent(type="text", text="Goal progress updated")]
            else:
                return [TextContent(type="text", text="Goal not found")]
        
        elif name == "get_staff_goals":
            goals = storage.get_goals_for_staff(arguments["staff_id"])
            goals_data = [goal.model_dump() for goal in goals]
            return [TextContent(type="text", text=json.dumps(goals_data, indent=2, default=str))]
        
        elif name == "process_call_transcript":
            transcript_id = str(uuid.uuid4())
            transcript = CallTranscript(
                id=transcript_id,
                title=arguments.get("title"),
                content=arguments["content"],
                participants=arguments.get("participants", []),
            )
            
            # Simple extraction logic (could be enhanced with NLP)
            extracted_items = []
            lines = arguments["content"].split('\n')
            for line in lines:
                line_lower = line.lower()
                if any(word in line_lower for word in ['action', 'todo', 'follow up', 'next steps']):
                    extracted_items.append({
                        "type": "action_item",
                        "content": line.strip(),
                        "participants": arguments.get("participants", [])
                    })
                elif any(word in line_lower for word in ['concern', 'issue', 'problem', 'challenge']):
                    extracted_items.append({
                        "type": "concern",
                        "content": line.strip(),
                        "participants": arguments.get("participants", [])
                    })
            
            transcript.extracted_items = extracted_items
            transcript.processed = True
            storage.save_transcript(transcript)
            
            return [TextContent(type="text", text=json.dumps({
                "transcript_id": transcript_id,
                "extracted_items": extracted_items
            }, indent=2))]
        
        elif name == "get_management_advice":
            staff = storage.get_staff_by_id(arguments["staff_id"])
            if not staff:
                return [TextContent(type="text", text="Staff member not found")]
            
            notes = storage.get_notes_for_staff(arguments["staff_id"])
            goals = storage.get_goals_for_staff(arguments["staff_id"])
            
            context = {
                "staff_info": staff.model_dump(),
                "recent_notes": [n.model_dump() for n in notes[-5:]],  # Last 5 notes
                "active_goals": [g.model_dump() for g in goals if g.status == "active"],
                "situation": arguments.get("situation", "General management guidance")
            }
            
            advice = f"""
Based on the information about {staff.name}:

Role: {staff.role or 'Not specified'}
Department: {staff.department or 'Not specified'}
Recent Notes: {len(notes)} total notes
Active Goals: {len([g for g in goals if g.status == 'active'])} goals

Management Recommendations:
1. Regular Check-ins: Schedule weekly 1:1s to maintain open communication
2. Goal Alignment: Ensure their goals align with department objectives
3. Development: Identify growth opportunities based on their interests
4. Recognition: Acknowledge achievements and progress regularly
5. Support: Address any concerns or roadblocks proactively

For specific situations, consider the context of recent notes and their current goals.
"""
            
            return [TextContent(type="text", text=advice)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    # Run the server using stdin/stdout streams
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="personal-assistant",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
                instructions="Personal assistant for team management with staff tracking, notes, goals, and reminders."
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())