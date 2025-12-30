"""
Report Service
Handles report generation, data aggregation, and export to PDF/CSV
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from io import BytesIO
import csv
import io

# PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: reportlab not installed. PDF generation will not work.")

from app.models.hierarchy import Task, Subtask, UserStory, Usecase, Project
from app.models.bug import Bug
from app.models.sprint import Sprint, SprintTask
from app.models.user import User


class ReportService:
    """Service for generating various reports"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_utilization_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate utilization report data"""
        
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Query tasks with estimated vs actual hours
        query = self.db.query(
            Task.assigned_to,
            User.full_name,
            func.sum(Task.estimated_hours).label('total_estimated'),
            func.sum(Task.actual_hours).label('total_actual'),
            func.count(Task.id).label('task_count')
        ).join(User, Task.assigned_to == User.id, isouter=True)
        
        if start_date and end_date:
            query = query.filter(
                and_(
                    Task.created_at >= start_date,
                    Task.created_at <= end_date
                )
            )
        
        query = query.group_by(Task.assigned_to, User.full_name)
        results = query.all()
        
        # Format data
        data = {
            "title": "Utilization Report",
            "period": f"{start_date} to {end_date}",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "headers": ["User", "Tasks", "Estimated Hours", "Actual Hours", "Utilization %"],
            "rows": []
        }
        
        for row in results:
            user_name = row.full_name or "Unassigned"
            estimated = float(row.total_estimated or 0)
            actual = float(row.total_actual or 0)
            utilization = (actual / estimated * 100) if estimated > 0 else 0
            
            data["rows"].append([
                user_name,
                str(row.task_count),
                f"{estimated:.1f}",
                f"{actual:.1f}",
                f"{utilization:.1f}%"
            ])
        
        return data
    
    async def generate_engagement_report(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate engagement report data"""
        
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Query user activity
        query = self.db.query(
            User.full_name,
            func.count(Task.id).label('tasks_created'),
            func.count(Task.completed_at).label('tasks_completed')
        ).join(Task, User.id == Task.created_by, isouter=True)
        
        if start_date and end_date:
            query = query.filter(
                and_(
                    Task.created_at >= start_date,
                    Task.created_at <= end_date
                )
            )
        
        query = query.group_by(User.full_name)
        results = query.all()
        
        data = {
            "title": "Engagement Report",
            "period": f"{start_date} to {end_date}",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "headers": ["User", "Tasks Created", "Tasks Completed", "Completion Rate"],
            "rows": []
        }
        
        for row in results:
            created = row.tasks_created or 0
            completed = row.tasks_completed or 0
            rate = (completed / created * 100) if created > 0 else 0
            
            data["rows"].append([
                row.full_name,
                str(created),
                str(completed),
                f"{rate:.1f}%"
            ])
        
        return data
    
    async def generate_occupancy_forecast(
        self,
        weeks_ahead: int = 4,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate occupancy forecast data"""
        
        # Query upcoming tasks
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=weeks_ahead)
        
        query = self.db.query(
            User.full_name,
            func.count(Task.id).label('upcoming_tasks'),
            func.sum(Task.estimated_hours).label('estimated_hours')
        ).join(Task, User.id == Task.assigned_to, isouter=True).filter(
            and_(
                Task.due_date >= start_date.strftime("%Y-%m-%d"),
                Task.due_date <= end_date.strftime("%Y-%m-%d"),
                Task.status != 'Done'
            )
        ).group_by(User.full_name)
        
        results = query.all()
        
        data = {
            "title": "Occupancy Forecast",
            "period": f"Next {weeks_ahead} weeks",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "headers": ["User", "Upcoming Tasks", "Estimated Hours", "Weekly Average"],
            "rows": []
        }
        
        for row in results:
            tasks = row.upcoming_tasks or 0
            hours = float(row.estimated_hours or 0)
            weekly_avg = hours / weeks_ahead if weeks_ahead > 0 else 0
            
            data["rows"].append([
                row.full_name,
                str(tasks),
                f"{hours:.1f}",
                f"{weekly_avg:.1f}"
            ])
        
        return data
    
    async def generate_bug_density_report(
        self,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate bug density report data"""
        
        query = self.db.query(
            Project.name,
            func.count(Bug.id).label('total_bugs'),
            func.sum(func.case((Bug.severity == 'Critical', 1), else_=0)).label('critical'),
            func.sum(func.case((Bug.severity == 'High', 1), else_=0)).label('high'),
            func.sum(func.case((Bug.status == 'Closed', 1), else_=0)).label('closed')
        ).join(Project, Bug.entity_id == Project.id, isouter=True).filter(
            Bug.entity_type == 'project'
        )
        
        if project_id:
            query = query.filter(Bug.entity_id == project_id)
        
        query = query.group_by(Project.name)
        results = query.all()
        
        data = {
            "title": "Bug Density Report",
            "period": "All time",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "headers": ["Project", "Total Bugs", "Critical", "High", "Closed", "Resolution Rate"],
            "rows": []
        }
        
        for row in results:
            total = row.total_bugs or 0
            closed = row.closed or 0
            resolution_rate = (closed / total * 100) if total > 0 else 0
            
            data["rows"].append([
                row.name or "Unknown",
                str(total),
                str(row.critical or 0),
                str(row.high or 0),
                str(closed),
                f"{resolution_rate:.1f}%"
            ])
        
        return data
    
    async def generate_sprint_velocity_report(
        self,
        project_id: Optional[str] = None,
        sprint_count: int = 10,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate sprint velocity report data"""
        
        query = self.db.query(
            Sprint.name,
            Sprint.start_date,
            Sprint.end_date,
            func.count(SprintTask.task_id).label('total_tasks'),
            func.sum(func.case((Task.status == 'Done', 1), else_=0)).label('completed_tasks')
        ).join(SprintTask, Sprint.id == SprintTask.sprint_id, isouter=True).join(
            Task, SprintTask.task_id == Task.id, isouter=True
        )
        
        if project_id:
            query = query.filter(Sprint.project_id == project_id)
        
        query = query.group_by(Sprint.id, Sprint.name, Sprint.start_date, Sprint.end_date).order_by(
            Sprint.start_date.desc()
        ).limit(sprint_count)
        
        results = query.all()
        
        data = {
            "title": "Sprint Velocity Report",
            "period": f"Last {sprint_count} sprints",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "headers": ["Sprint", "Start Date", "End Date", "Total Tasks", "Completed", "Velocity %"],
            "rows": []
        }
        
        for row in results:
            total = row.total_tasks or 0
            completed = row.completed_tasks or 0
            velocity = (completed / total * 100) if total > 0 else 0
            
            data["rows"].append([
                row.name,
                row.start_date.strftime("%Y-%m-%d") if row.start_date else "N/A",
                row.end_date.strftime("%Y-%m-%d") if row.end_date else "N/A",
                str(total),
                str(completed),
                f"{velocity:.1f}%"
            ])
        
        return data
    
    async def generate_project_health_report(
        self,
        project_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate project health report data"""
        
        query = self.db.query(
            Project.name,
            func.count(Task.id).label('total_tasks'),
            func.sum(func.case((Task.status == 'Done', 1), else_=0)).label('completed_tasks'),
            func.sum(func.case((Task.status == 'Blocked', 1), else_=0)).label('blocked_tasks'),
            func.count(Bug.id).label('open_bugs')
        ).join(Usecase, Project.id == Usecase.project_id, isouter=True).join(
            UserStory, Usecase.id == UserStory.usecase_id, isouter=True
        ).join(Task, UserStory.id == Task.user_story_id, isouter=True).join(
            Bug, and_(Bug.entity_type == 'project', Bug.entity_id == Project.id), isouter=True
        )
        
        if project_id:
            query = query.filter(Project.id == project_id)
        
        query = query.group_by(Project.id, Project.name)
        results = query.all()
        
        data = {
            "title": "Project Health Report",
            "period": "Current status",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "headers": ["Project", "Total Tasks", "Completed", "Blocked", "Open Bugs", "Health Score"],
            "rows": []
        }
        
        for row in results:
            total = row.total_tasks or 0
            completed = row.completed_tasks or 0
            blocked = row.blocked_tasks or 0
            bugs = row.open_bugs or 0
            
            # Simple health score calculation
            completion_rate = (completed / total * 100) if total > 0 else 0
            health_score = completion_rate - (blocked * 5) - (bugs * 2)
            health_score = max(0, min(100, health_score))  # Clamp between 0-100
            
            data["rows"].append([
                row.name,
                str(total),
                str(completed),
                str(blocked),
                str(bugs),
                f"{health_score:.1f}"
            ])
        
        return data
    
    async def generate_project_tree_report(
        self,
        project_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate project tree report data"""
        
        # Get project with all nested entities
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        usecases = self.db.query(Usecase).filter(Usecase.project_id == project_id).all()
        
        data = {
            "title": f"Project Tree Report - {project.name}",
            "period": "Current structure",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "headers": ["Level", "Type", "Name", "Status", "Tasks", "Completion"],
            "rows": []
        }
        
        # Add project row
        total_tasks = self.db.query(func.count(Task.id)).join(
            UserStory
        ).join(Usecase).filter(Usecase.project_id == project_id).scalar() or 0
        
        completed_tasks = self.db.query(func.count(Task.id)).join(
            UserStory
        ).join(Usecase).filter(
            and_(Usecase.project_id == project_id, Task.status == 'Done')
        ).scalar() or 0
        
        completion = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        data["rows"].append([
            "0",
            "Project",
            project.name,
            project.status or "N/A",
            str(total_tasks),
            f"{completion:.1f}%"
        ])
        
        # Add use cases and their user stories
        for usecase in usecases:
            uc_tasks = self.db.query(func.count(Task.id)).join(
                UserStory
            ).filter(UserStory.usecase_id == usecase.id).scalar() or 0
            
            uc_completed = self.db.query(func.count(Task.id)).join(
                UserStory
            ).filter(
                and_(UserStory.usecase_id == usecase.id, Task.status == 'Done')
            ).scalar() or 0
            
            uc_completion = (uc_completed / uc_tasks * 100) if uc_tasks > 0 else 0
            
            data["rows"].append([
                "1",
                "Use Case",
                f"  {usecase.name}",
                usecase.status or "N/A",
                str(uc_tasks),
                f"{uc_completion:.1f}%"
            ])
            
            # Add user stories
            user_stories = self.db.query(UserStory).filter(
                UserStory.usecase_id == usecase.id
            ).all()
            
            for story in user_stories:
                story_tasks = self.db.query(func.count(Task.id)).filter(
                    Task.user_story_id == story.id
                ).scalar() or 0
                
                story_completed = self.db.query(func.count(Task.id)).filter(
                    and_(Task.user_story_id == story.id, Task.status == 'Done')
                ).scalar() or 0
                
                story_completion = (story_completed / story_tasks * 100) if story_tasks > 0 else 0
                
                data["rows"].append([
                    "2",
                    "User Story",
                    f"    {story.title}",
                    story.status or "N/A",
                    str(story_tasks),
                    f"{story_completion:.1f}%"
                ])
        
        return data
    
    def export_to_csv(self, report_data: Dict[str, Any]) -> str:
        """Export report data to CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write title and metadata
        writer.writerow([report_data["title"]])
        writer.writerow([f"Period: {report_data['period']}"])
        writer.writerow([f"Generated: {report_data['generated_at']}"])
        writer.writerow([])  # Empty row
        
        # Write headers
        writer.writerow(report_data["headers"])
        
        # Write data rows
        for row in report_data["rows"]:
            writer.writerow(row)
        
        return output.getvalue()
    
    def export_to_pdf(self, report_data: Dict[str, Any], title: str) -> bytes:
        """Export report data to PDF format"""
        if not PDF_AVAILABLE:
            raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Title
        elements.append(Paragraph(report_data["title"], title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Metadata
        meta_style = styles['Normal']
        elements.append(Paragraph(f"<b>Period:</b> {report_data['period']}", meta_style))
        elements.append(Paragraph(f"<b>Generated:</b> {report_data['generated_at']}", meta_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Table data
        table_data = [report_data["headers"]] + report_data["rows"]
        
        # Create table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        
        return buffer.getvalue()
