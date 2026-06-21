"""
Reports API — Historical data retrieval endpoints.

  GET /api/vessels           — List vessels the current user has reports for (admin: all).
  GET /api/reports          — Query daily reports by vessel and date range.
  GET /api/reports/summary  — Aggregate summary of user-scoped ingested data (admin: all).
"""

import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.vessel import Vessel
from app.models.daily_report import DailyReport
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api", tags=["Reports"])


@router.get("/vessels")
def list_vessels(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return vessels visible to the current user.

    - Admin: all registered vessels.
    - Regular user: only vessels that have at least one daily report owned
      by this user.
    """
    if current_user.role == "admin":
        vessels = db.query(Vessel).order_by(Vessel.vessel_name.asc()).all()
    else:
        # Subquery: vessel IDs that have at least one report by this user
        vessel_ids_subquery = (
            db.query(DailyReport.vessel_id)
            .filter(DailyReport.user_id == current_user.id)
            .distinct()
            .subquery()
        )
        vessels = (
            db.query(Vessel)
            .filter(Vessel.id.in_(vessel_ids_subquery))
            .order_by(Vessel.vessel_name.asc())
            .all()
        )

    return {
        "success": True,
        "data": [
            {
                "id": v.id,
                "vesselName": v.vessel_name,
                "technicalManager": v.technical_manager,
            }
            for v in vessels
        ],
    }


@router.get("/reports")
def get_reports(
    vesselName: str = Query(..., description="Vessel name to filter by"),
    startDate: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve daily reports for a vessel, optionally filtered by date range.

    Query Parameters:
      - vesselName (required)
      - startDate (optional, YYYY-MM-DD)
      - endDate (optional, YYYY-MM-DD)
    """
    # Look up vessel
    vessel = db.query(Vessel).filter(Vessel.vessel_name == vesselName).first()
    if vessel is None:
        return {
            "success": True,
            "data": {
                "vesselName": vesselName,
                "reportCount": 0,
                "reports": [],
            },
        }

    # Build query
    query = db.query(DailyReport).filter(
        DailyReport.vessel_id == vessel.id
    )
    if current_user.role != "admin":
        query = query.filter(DailyReport.user_id == current_user.id)

    # Apply date filters
    if startDate:
        try:
            start = datetime.date.fromisoformat(startDate)
            query = query.filter(DailyReport.report_date >= start)
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": f"Invalid startDate format: {startDate}. Expected YYYY-MM-DD.",
                },
            )

    if endDate:
        try:
            end = datetime.date.fromisoformat(endDate)
            query = query.filter(DailyReport.report_date <= end)
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": f"Invalid endDate format: {endDate}. Expected YYYY-MM-DD.",
                },
            )

    # Order by date ascending
    reports = query.order_by(DailyReport.report_date.asc()).all()

    # Format response
    report_list = []
    for r in reports:
        report_list.append({
            "reportDate": r.report_date.isoformat(),
            "utcTime": r.utc_time,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "latitudeDecimal": r.latitude_decimal,
            "longitudeDecimal": r.longitude_decimal,
            "vesselCondition": r.vessel_condition,
            "remarks": r.remarks,
            "sourceFileName": r.source_file_name,
            "ingestedAt": r.ingested_at.isoformat() + "Z" if r.ingested_at else None,
            "details": r.raw_json,
        })

    return {
        "success": True,
        "data": {
            "vesselName": vessel.vessel_name,
            "reportCount": len(report_list),
            "reports": report_list,
        },
    }


@router.get("/reports/summary")
def get_reports_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return an aggregate summary of ingested data.

    - Admin: platform-wide totals.
    - Regular user: totals scoped to their own reports.
    """
    if current_user.role == "admin":
        # Platform-wide totals
        total_vessels = db.query(func.count(Vessel.id)).scalar() or 0
        total_reports = db.query(func.count(DailyReport.id)).scalar() or 0
        date_min = db.query(func.min(DailyReport.report_date)).scalar()
        date_max = db.query(func.max(DailyReport.report_date)).scalar()
    else:
        # User-scoped totals
        user_reports = db.query(DailyReport).filter(
            DailyReport.user_id == current_user.id
        )
        total_reports = user_reports.count()

        # Count distinct vessels the user has reports for
        total_vessels = (
            db.query(func.count(func.distinct(DailyReport.vessel_id)))
            .filter(DailyReport.user_id == current_user.id)
            .scalar()
            or 0
        )

        date_min = (
            db.query(func.min(DailyReport.report_date))
            .filter(DailyReport.user_id == current_user.id)
            .scalar()
        )
        date_max = (
            db.query(func.max(DailyReport.report_date))
            .filter(DailyReport.user_id == current_user.id)
            .scalar()
        )

    return {
        "success": True,
        "data": {
            "totalVessels": total_vessels,
            "totalReports": total_reports,
            "dateRange": {
                "start": date_min.isoformat() if date_min else None,
                "end": date_max.isoformat() if date_max else None,
            },
        },
    }
