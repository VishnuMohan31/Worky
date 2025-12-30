"""
Reports API Endpoints
Handles report generation with PDF and CSV export functionality
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
import io

from app.db.base import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.report_service import ReportService

router = APIRouter()


def export_report(report_data: Dict[str, Any], format: Optional[str], report_name: str, report_service: ReportService):
    """Helper function to export report in requested format"""
    # Return JSON if no format specified or format is json
    if not format or format == "json":
        return report_data
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{report_name}_{timestamp}.{format}"
    
    # Export based on format
    if format == "pdf":
        pdf_buffer = report_service.export_to_pdf(report_data, report_data["title"])
        return StreamingResponse(
            io.BytesIO(pdf_buffer),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else:  # csv
        csv_buffer = report_service.export_to_csv(report_data)
        return StreamingResponse(
            io.BytesIO(csv_buffer.encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )


@router.get("/utilization")
async def generate_utilization_report(
    format: Optional[str] = Query(None, regex="^(pdf|csv|json)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate Utilization Report - Resource allocation vs actual usage analysis"""
    report_service = ReportService(db)
    report_data = await report_service.generate_utilization_report(
        start_date=start_date, end_date=end_date, user_id=current_user.id
    )
    return export_report(report_data, format, "utilization_report", report_service)


@router.get("/engagement")
async def generate_engagement_report(
    format: Optional[str] = Query(None, regex="^(pdf|csv|json)$"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate Engagement Report - Developer activity and contribution metrics"""
    report_service = ReportService(db)
    report_data = await report_service.generate_engagement_report(
        start_date=start_date, end_date=end_date, user_id=current_user.id
    )
    return export_report(report_data, format, "engagement_report", report_service)


@router.get("/occupancy-forecast")
async def generate_occupancy_forecast(
    format: Optional[str] = Query(None, regex="^(pdf|csv|json)$"),
    weeks_ahead: int = Query(4, ge=1, le=52),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate Occupancy Forecast - Time booking predictions"""
    report_service = ReportService(db)
    report_data = await report_service.generate_occupancy_forecast(
        weeks_ahead=weeks_ahead, user_id=current_user.id
    )
    return export_report(report_data, format, "occupancy_forecast", report_service)


@router.get("/bug-density")
async def generate_bug_density_report(
    format: Optional[str] = Query(None, regex="^(pdf|csv|json)$"),
    project_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate Bug Density Report - Bug trends and resolution metrics"""
    report_service = ReportService(db)
    report_data = await report_service.generate_bug_density_report(
        project_id=project_id, user_id=current_user.id
    )
    return export_report(report_data, format, "bug_density_report", report_service)


@router.get("/sprint-velocity")
async def generate_sprint_velocity_report(
    format: Optional[str] = Query(None, regex="^(pdf|csv|json)$"),
    project_id: Optional[str] = None,
    sprint_count: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate Sprint Velocity Report - Team velocity and sprint completion trends"""
    report_service = ReportService(db)
    report_data = await report_service.generate_sprint_velocity_report(
        project_id=project_id, sprint_count=sprint_count, user_id=current_user.id
    )
    return export_report(report_data, format, "sprint_velocity_report", report_service)


@router.get("/project-health")
async def generate_project_health_report(
    format: Optional[str] = Query(None, regex="^(pdf|csv|json)$"),
    project_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate Project Health Report - Overall project status and risk assessment"""
    report_service = ReportService(db)
    report_data = await report_service.generate_project_health_report(
        project_id=project_id, user_id=current_user.id
    )
    return export_report(report_data, format, "project_health_report", report_service)


@router.get("/project-tree")
async def generate_project_tree_report(
    format: Optional[str] = Query(None, regex="^(pdf|csv|json)$"),
    project_id: str = Query(..., description="Project ID is required"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate Project Tree Report - Hierarchical view of project structure"""
    report_service = ReportService(db)
    report_data = await report_service.generate_project_tree_report(
        project_id=project_id, user_id=current_user.id
    )
    return export_report(report_data, format, "project_tree_report", report_service)
