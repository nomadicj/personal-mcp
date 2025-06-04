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

def _analyze_transcript_content(content: str, participants: list, title: str) -> dict:
    """
    Comprehensive transcript analysis providing:
    1. Action items for manager and participants
    2. Call briefing and summary
    3. HBS-style management coaching
    """
    lines = content.split('\n')
    
    # Extract action items
    action_items = []
    concerns = []
    decisions = []
    
    for line in lines:
        line_lower = line.lower()
        line_clean = line.strip()
        
        if any(word in line_lower for word in ['action', 'todo', 'follow up', 'next steps', 'will do', 'should do']):
            action_items.append({
                "type": "action_item",
                "content": line_clean,
                "assignee": _extract_assignee(line_clean, participants)
            })
        elif any(word in line_lower for word in ['concern', 'issue', 'problem', 'challenge', 'worried', 'risk']):
            concerns.append({
                "type": "concern", 
                "content": line_clean,
                "severity": _assess_concern_severity(line_clean)
            })
        elif any(word in line_lower for word in ['decided', 'agreed', 'conclusion', 'resolution']):
            decisions.append({
                "type": "decision",
                "content": line_clean
            })
    
    # Generate call briefing
    briefing = _generate_call_briefing(content, participants, title, action_items, concerns, decisions)
    
    # Generate management coaching
    coaching = _generate_management_coaching(content, participants)
    
    # Extract manager actions vs participant actions
    manager_actions, participant_actions = _categorize_actions(action_items, participants)
    
    return {
        "briefing": briefing,
        "manager_actions": manager_actions,
        "participant_actions": participant_actions,
        "concerns": concerns,
        "decisions": decisions,
        "management_coaching": coaching,
        "participants": participants,
        "processed_at": datetime.now().isoformat()
    }

def _extract_assignee(action_text: str, participants: list) -> str:
    """Extract who is assigned to perform an action"""
    action_lower = action_text.lower()
    
    # Look for explicit assignments
    for participant in participants:
        if participant.lower() in action_lower:
            return participant
    
    # Look for "I will", "I'll", etc. patterns
    if any(phrase in action_lower for phrase in ["i will", "i'll", "i need to", "i should"]):
        return "Manager"
    
    return "Unassigned"

def _assess_concern_severity(concern_text: str) -> str:
    """Assess the severity of a concern"""
    concern_lower = concern_text.lower()
    
    if any(word in concern_lower for word in ['critical', 'urgent', 'serious', 'major', 'blocking']):
        return "High"
    elif any(word in concern_lower for word in ['problem', 'issue', 'challenge', 'difficulty']):
        return "Medium"
    else:
        return "Low"

def _generate_call_briefing(content: str, participants: list, title: str, actions: list, concerns: list, decisions: list) -> dict:
    """Generate a structured briefing of the call"""
    word_count = len(content.split())
    
    # Identify key topics discussed
    topics = _extract_key_topics(content)
    
    # Assess overall sentiment
    sentiment = _assess_call_sentiment(content)
    
    return {
        "title": title,
        "participants": participants,
        "duration_estimate": f"{max(5, word_count // 150)} minutes",
        "key_topics": topics,
        "sentiment": sentiment,
        "summary": f"Meeting with {len(participants)} participants covering {len(topics)} main topics. Generated {len(actions)} action items, {len(concerns)} concerns, and {len(decisions)} decisions.",
        "action_items_count": len(actions),
        "concerns_count": len(concerns),
        "decisions_count": len(decisions)
    }

def _extract_key_topics(content: str) -> list:
    """Extract key topics from conversation"""
    # Simple keyword-based topic extraction
    business_keywords = {
        "project management": ["project", "timeline", "milestone", "deadline", "deliverable"],
        "performance": ["performance", "metrics", "goals", "targets", "results"],
        "team dynamics": ["team", "collaboration", "communication", "conflict", "working together"],
        "technical issues": ["technical", "system", "bug", "error", "implementation"],
        "strategy": ["strategy", "plan", "direction", "vision", "objectives"],
        "resources": ["budget", "resources", "hiring", "staffing", "capacity"]
    }
    
    content_lower = content.lower()
    topics = []
    
    for topic, keywords in business_keywords.items():
        if any(keyword in content_lower for keyword in keywords):
            topics.append(topic)
    
    return topics[:5]  # Return top 5 topics

def _assess_call_sentiment(content: str) -> str:
    """Assess overall sentiment of the call"""
    content_lower = content.lower()
    
    positive_indicators = ["great", "excellent", "good", "positive", "success", "achievement", "happy", "pleased"]
    negative_indicators = ["concern", "problem", "issue", "worry", "challenge", "difficult", "frustrated", "disappointed"]
    
    positive_count = sum(1 for word in positive_indicators if word in content_lower)
    negative_count = sum(1 for word in negative_indicators if word in content_lower)
    
    if positive_count > negative_count * 1.5:
        return "Positive"
    elif negative_count > positive_count * 1.5:
        return "Concerning"
    else:
        return "Neutral"

def _categorize_actions(action_items: list, participants: list) -> tuple:
    """Separate manager actions from participant actions"""
    manager_actions = []
    participant_actions = []
    
    for action in action_items:
        if action["assignee"] == "Manager":
            manager_actions.append(action)
        else:
            participant_actions.append(action)
    
    return manager_actions, participant_actions

def _generate_management_coaching(content: str, participants: list) -> dict:
    """Generate HBS-style management coaching based on conversation analysis"""
    content_lower = content.lower()
    
    # Analyze communication patterns
    communication_analysis = _analyze_communication_patterns(content, participants)
    
    # Assess leadership behaviors
    leadership_assessment = _assess_leadership_behaviors(content_lower)
    
    # Generate specific recommendations
    recommendations = _generate_hbs_recommendations(communication_analysis, leadership_assessment)
    
    return {
        "communication_analysis": communication_analysis,
        "leadership_assessment": leadership_assessment,
        "recommendations": recommendations,
        "hbs_principles_applied": [
            "Active listening and inquiry",
            "Psychological safety creation", 
            "Clear action-oriented follow-up",
            "Balanced directive and collaborative leadership"
        ]
    }

def _analyze_communication_patterns(content: str, participants: list) -> dict:
    """Analyze how communication flowed in the meeting"""
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # Count speaking instances per participant
    speaking_count = {}
    questions_asked = 0
    
    for line in lines:
        # Find who is speaking
        for participant in participants:
            if line.startswith(f"{participant}:"):
                speaking_count[participant] = speaking_count.get(participant, 0) + 1
                if '?' in line:
                    questions_asked += 1
                break
    
    total_statements = sum(speaking_count.values())
    
    return {
        "speaking_distribution": speaking_count,
        "questions_asked": questions_asked,
        "total_exchanges": total_statements,
        "participation_balance": "Balanced" if len(set(speaking_count.values())) <= 2 else "Imbalanced"
    }

def _assess_leadership_behaviors(content_lower: str) -> dict:
    """Assess leadership behaviors demonstrated"""
    behaviors = {
        "inquiry_mindset": {
            "score": 0,
            "indicators": ["what do you think", "how do you feel", "what's your perspective", "tell me more"]
        },
        "empathy": {
            "score": 0, 
            "indicators": ["understand", "i hear you", "that makes sense", "i can see why"]
        },
        "clarity": {
            "score": 0,
            "indicators": ["to be clear", "let me clarify", "specifically", "the goal is"]
        },
        "accountability": {
            "score": 0,
            "indicators": ["action item", "who will", "by when", "follow up", "next steps"]
        }
    }
    
    for behavior, data in behaviors.items():
        for indicator in data["indicators"]:
            if indicator in content_lower:
                data["score"] += 1
    
    return {behavior: {"score": data["score"], "level": _score_to_level(data["score"])} 
            for behavior, data in behaviors.items()}

def _score_to_level(score: int) -> str:
    """Convert score to performance level"""
    if score >= 3:
        return "Strong"
    elif score >= 1:
        return "Moderate" 
    else:
        return "Needs Development"

def _generate_hbs_recommendations(comm_analysis: dict, leadership_assessment: dict) -> list:
    """Generate specific HBS-style recommendations"""
    recommendations = []
    
    # Participation balance
    if comm_analysis.get("participation_balance") == "Imbalanced":
        recommendations.append({
            "area": "Inclusive Leadership",
            "recommendation": "Draw out quieter participants with direct questions. Try: 'Sarah, what's your take on this?' Use the 2-minute rule - no one speaks for more than 2 minutes without checking in with others.",
            "hbs_principle": "Psychological Safety & Inclusion"
        })
    
    # Inquiry assessment
    if leadership_assessment.get("inquiry_mindset", {}).get("level") == "Needs Development":
        recommendations.append({
            "area": "Inquiry Leadership",
            "recommendation": "Increase use of open-ended questions. Replace 'Do you agree?' with 'What concerns do you have?' Use the 70/30 rule: 70% questions, 30% statements.",
            "hbs_principle": "Inquiry-Based Leadership"
        })
    
    # Accountability
    if leadership_assessment.get("accountability", {}).get("level") != "Strong":
        recommendations.append({
            "area": "Action Orientation", 
            "recommendation": "End each topic with clear next steps: Who, What, When. Use the format: '[Name] will [specific action] by [date].'",
            "hbs_principle": "Results-Driven Leadership"
        })
    
    # Empathy
    if leadership_assessment.get("empathy", {}).get("level") == "Needs Development":
        recommendations.append({
            "area": "Emotional Intelligence",
            "recommendation": "Practice reflective listening: 'What I'm hearing is...' and 'Help me understand...' Acknowledge emotions before moving to solutions.",
            "hbs_principle": "Authentic Leadership"
        })
    
    return recommendations

def _link_transcript_to_staff(transcript: CallTranscript, analysis: dict, storage) -> None:
    """Automatically link transcript insights to staff member profiles"""
    briefing = analysis.get('briefing', {})
    concerns = analysis.get('concerns', [])
    participant_actions = analysis.get('participant_actions', [])
    
    # Create a summary note for each participant
    for participant_name in transcript.participants:
        # Skip if participant is "James Armstrong" (manager)
        if participant_name.lower() in ['james armstrong', 'james']:
            continue
            
        # Find staff member by name
        all_staff = storage.get_all_staff()
        staff_member = None
        for staff in all_staff:
            if staff.name.lower() == participant_name.lower():
                staff_member = staff
                break
        
        if not staff_member:
            continue
            
        # Create summary note content
        meeting_title = transcript.title or "Meeting"
        key_topics = ', '.join(briefing.get('key_topics', []))
        sentiment = briefing.get('sentiment', 'Neutral')
        
        # Extract participant-specific actions
        participant_specific_actions = [
            action['content'] for action in participant_actions 
            if action.get('assignee', '').lower() == participant_name.lower()
        ]
        
        # Build note content
        note_parts = [f"{meeting_title} - {sentiment} sentiment"]
        
        if key_topics:
            note_parts.append(f"Topics: {key_topics}")
            
        if participant_specific_actions:
            note_parts.append(f"Actions: {'; '.join(participant_specific_actions)}")
            
        if concerns:
            high_concerns = [c['content'][:100] + '...' for c in concerns if c.get('severity') == 'High']
            if high_concerns:
                note_parts.append(f"High priority concerns discussed: {'; '.join(high_concerns)}")
        
        note_content = '. '.join(note_parts)
        
        # Add note to staff member
        storage.add_note_to_staff(
            staff_id=staff_member.id,
            note_content=note_content,
            category="one_on_one" if len(transcript.participants) == 2 else "team_meeting",
            source="call_transcript"
        )
    
    # Store leadership coaching feedback for manager (James Armstrong)
    _store_leadership_coaching(transcript, analysis, storage)

def _store_leadership_coaching(transcript: CallTranscript, analysis: dict, storage) -> None:
    """Store leadership coaching feedback for manager's personal development"""
    coaching = analysis.get('management_coaching', {})
    if not coaching:
        return
    
    # Find James Armstrong in staff records
    all_staff = storage.get_all_staff()
    james_staff = None
    for staff in all_staff:
        if staff.name.lower() in ['james armstrong', 'james']:
            james_staff = staff
            break
    
    if not james_staff:
        # Create James Armstrong staff record if not exists
        james_id = str(uuid.uuid4())
        james_staff = StaffMember(
            id=james_id,
            name="James Armstrong",
            role="Engineering Manager",
            department="CPQ"
        )
        storage.save_staff(james_staff)
    
    # Extract coaching insights
    meeting_context = f"Meeting: {transcript.title or 'Call'} with {', '.join([p for p in transcript.participants if p.lower() not in ['james armstrong', 'james']])}"
    
    # Communication analysis summary
    comm_analysis = coaching.get('communication_analysis', {})
    participation_balance = comm_analysis.get('participation_balance', 'Unknown')
    questions_asked = comm_analysis.get('questions_asked', 0)
    
    # Leadership skills assessment
    leadership_assessment = coaching.get('leadership_assessment', {})
    skill_scores = []
    for skill, assessment in leadership_assessment.items():
        skill_name = skill.replace('_', ' ').title()
        level = assessment.get('level', 'Unknown')
        skill_scores.append(f"{skill_name}: {level}")
    
    # Specific recommendations
    recommendations = coaching.get('recommendations', [])
    rec_summary = []
    for rec in recommendations:
        area = rec.get('area', 'General')
        principle = rec.get('hbs_principle', 'Leadership')
        rec_summary.append(f"{area} ({principle})")
    
    # Build coaching note
    coaching_parts = [meeting_context]
    coaching_parts.append(f"Communication: {participation_balance} participation, {questions_asked} questions asked")
    
    if skill_scores:
        coaching_parts.append(f"Skills Assessment: {'; '.join(skill_scores)}")
    
    if rec_summary:
        coaching_parts.append(f"Development Areas: {'; '.join(rec_summary)}")
    
    # Get detailed recommendations for full note
    detailed_recs = []
    for rec in recommendations:
        area = rec.get('area', 'General')
        recommendation = rec.get('recommendation', '')
        detailed_recs.append(f"• {area}: {recommendation}")
    
    if detailed_recs:
        coaching_parts.append(f"Specific Actions: {'; '.join(detailed_recs)}")
    
    coaching_note = '. '.join(coaching_parts)
    
    # Store as personal development note
    storage.add_note_to_staff(
        staff_id=james_staff.id,
        note_content=coaching_note,
        category="personal_development",
        source="hbs_leadership_coaching"
    )

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
            
            # Enhanced transcript analysis
            analysis = _analyze_transcript_content(
                arguments["content"],
                arguments.get("participants", []),
                arguments.get("title", "Meeting")
            )
            
            transcript.extracted_items = analysis
            transcript.processed = True
            storage.save_transcript(transcript)
            
            # Auto-link insights to staff members
            _link_transcript_to_staff(transcript, analysis, storage)
            
            return [TextContent(type="text", text=json.dumps({
                "transcript_id": transcript_id,
                "analysis": analysis,
                "staff_updates": "Automatically linked insights to participant profiles"
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