"""
Admin API — admin-only endpoints for platform management.

  GET /admin/stats              — Platform-wide totals (users, reports, vessels, recent uploads)
  GET /admin/users              — List all registered users with report counts
  GET /admin/users/{id}         — Single user detail
  GET /admin/users/{id}/reports — Reports uploaded by a specific user
"""

import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.daily_report import DailyReport
from app.models.vessel import Vessel
from app.services.auth_service import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Platform Stats ────────────────────────────────────────────────────────────

@router.get("/stats")
def get_platform_stats(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Return platform-wide aggregate statistics."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_reports = db.query(func.count(DailyReport.id)).scalar() or 0
    total_vessels = db.query(func.count(Vessel.id)).scalar() or 0

    # Recent uploads: last 7 days
    seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    recent_uploads = (
        db.query(func.count(DailyReport.id))
        .filter(DailyReport.ingested_at >= seven_days_ago)
        .scalar()
        or 0
    )

    # Recent upload activity: last 10 ingested reports
    recent_reports = (
        db.query(DailyReport, User, Vessel)
        .outerjoin(User, DailyReport.user_id == User.id)
        .join(Vessel, DailyReport.vessel_id == Vessel.id)
        .order_by(DailyReport.ingested_at.desc())
        .limit(10)
        .all()
    )

    recent_list = []
    for report, user, vessel in recent_reports:
        recent_list.append({
            "reportId": report.id,
            "reportDate": report.report_date.isoformat() if report.report_date else None,
            "sourceFileName": report.source_file_name,
            "vesselName": vessel.vessel_name,
            "uploadedBy": user.username if user else "Unknown",
            "ingestedAt": report.ingested_at.isoformat() + "Z" if report.ingested_at else None,
        })

    return {
        "success": True,
        "data": {
            "totalUsers": total_users,
            "totalReports": total_reports,
            "totalVessels": total_vessels,
            "recentUploads": recent_uploads,
            "recentActivity": recent_list,
        },
    }


# ── User Management ───────────────────────────────────────────────────────────

@router.get("/users")
def list_users(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Return all registered users with their report counts."""
    # Subquery: count reports per user
    report_counts = (
        db.query(DailyReport.user_id, func.count(DailyReport.id).label("count"))
        .group_by(DailyReport.user_id)
        .subquery()
    )

    results = (
        db.query(User, report_counts.c.count)
        .outerjoin(report_counts, User.id == report_counts.c.user_id)
        .order_by(User.created_at.desc())
        .all()
    )

    users = []
    for user, count in results:
        users.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "reportCount": count or 0,
            "createdAt": user.created_at.isoformat() + "Z" if user.created_at else None,
        })

    return {"success": True, "data": users}


@router.get("/users/{user_id}")
def get_user_detail(
    user_id: int = Path(..., description="User ID to retrieve"),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Return detail for a single user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": f"User {user_id} not found."},
        )

    report_count = db.query(func.count(DailyReport.id)).filter(
        DailyReport.user_id == user_id
    ).scalar() or 0

    return {
        "success": True,
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "reportCount": report_count,
            "createdAt": user.created_at.isoformat() + "Z" if user.created_at else None,
            "updatedAt": user.updated_at.isoformat() + "Z" if user.updated_at else None,
        },
    }


@router.get("/users/{user_id}/reports")
def get_user_reports(
    user_id: int = Path(..., description="User ID"),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Return all reports uploaded by a specific user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": f"User {user_id} not found."},
        )

    query = (
        db.query(DailyReport, Vessel)
        .join(Vessel, DailyReport.vessel_id == Vessel.id)
        .filter(DailyReport.user_id == user_id)
    )

    if startDate:
        try:
            query = query.filter(DailyReport.report_date >= datetime.date.fromisoformat(startDate))
        except ValueError:
            return JSONResponse(status_code=400, content={"success": False, "message": "Invalid startDate"})

    if endDate:
        try:
            query = query.filter(DailyReport.report_date <= datetime.date.fromisoformat(endDate))
        except ValueError:
            return JSONResponse(status_code=400, content={"success": False, "message": "Invalid endDate"})

    results = query.order_by(DailyReport.report_date.desc()).all()

    reports = []
    for report, vessel in results:
        reports.append({
            "id": report.id,
            "reportDate": report.report_date.isoformat() if report.report_date else None,
            "vesselName": vessel.vessel_name,
            "sourceFileName": report.source_file_name,
            "vesselCondition": report.vessel_condition,
            "ingestedAt": report.ingested_at.isoformat() + "Z" if report.ingested_at else None,
        })

    return {
        "success": True,
        "data": {
            "userId": user_id,
            "username": user.username,
            "reportCount": len(reports),
            "reports": reports,
        },
    }
