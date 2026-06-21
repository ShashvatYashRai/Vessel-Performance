"""
Analytics API Router — exposes endpoints for operational analytics, trends, and timeline.

All endpoints are authenticated. Regular users see only their own data; admins see everything.
"""

import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.vessel import Vessel
from app.models.daily_report import DailyReport
from app.models.user import User
from app.services.auth_service import get_current_user
import app.services.analytics_service as service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


# ── Common Query Loader Helper ───────────────────────────────────────────────

def load_vessel_and_reports(
    db: Session,
    vessel_name: Optional[str] = None,
    vessel_id: Optional[int] = None,
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None,
    user_id: Optional[int] = None,
):
    """
    Helper to look up a vessel and fetch its DailyReport records sorted by date,
    optionally filtered by startDate, endDate, and user_id.

    When user_id is provided, only reports belonging to that user are returned.
    When user_id is None (admin), all reports for the vessel are returned.
    """
    # 1. Lookup Vessel
    if vessel_id is not None:
        vessel = db.query(Vessel).filter(Vessel.id == vessel_id).first()
    elif vessel_name is not None:
        vessel = db.query(Vessel).filter(Vessel.vessel_name == vessel_name).first()
    else:
        return None, [], "Either vesselName or vesselId must be provided."

    if not vessel:
        return None, [], None

    # 2. Build DailyReport Query
    query = db.query(DailyReport).filter(DailyReport.vessel_id == vessel.id)

    # 3. Apply user-scoped isolation (non-admin)
    if user_id is not None:
        query = query.filter(DailyReport.user_id == user_id)

    # 4. Parse and Apply Date Filters
    if start_date_str:
        try:
            start_date = datetime.date.fromisoformat(start_date_str)
            query = query.filter(DailyReport.report_date >= start_date)
        except ValueError:
            return vessel, [], f"Invalid startDate format: {start_date_str}. Expected YYYY-MM-DD."

    if end_date_str:
        try:
            end_date = datetime.date.fromisoformat(end_date_str)
            query = query.filter(DailyReport.report_date <= end_date)
        except ValueError:
            return vessel, [], f"Invalid endDate format: {end_date_str}. Expected YYYY-MM-DD."

    # Order reports chronologically
    reports = query.order_by(DailyReport.report_date.asc()).all()
    return vessel, reports, None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _resolve_user_id(current_user: User) -> Optional[int]:
    """Return user_id for scoping, or None for admins (full access)."""
    return None if current_user.role == "admin" else current_user.id


# ── API Endpoints ─────────────────────────────────────────────────────────────

@router.get("/overview")
def get_overview(
    vesselName: str = Query(..., description="Vessel name to retrieve overview for"),
    startDate: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve the general vessel overview (reporting dates and coverage)."""
    uid = _resolve_user_id(current_user)
    vessel, reports, err = load_vessel_and_reports(
        db, vessel_name=vesselName, start_date_str=startDate, end_date_str=endDate, user_id=uid,
    )
    if err:
        return JSONResponse(status_code=400, content={"success": False, "message": err})

    vessel_label = vessel.vessel_name if vessel else vesselName
    data = service.compute_vessel_overview(vessel_label, reports)

    return {"success": True, "data": data}


@router.get("/vessel/{vesselId}")
def get_vessel_dashboard(
    vesselId: int,
    startDate: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    severeWeatherThreshold: float = Query(5.0, description="Beaufort scale threshold for severe weather"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all operational analytics categories in a single comprehensive payload for dashboard view."""
    uid = _resolve_user_id(current_user)
    vessel, reports, err = load_vessel_and_reports(
        db, vessel_id=vesselId, start_date_str=startDate, end_date_str=endDate, user_id=uid,
    )
    if err:
        return JSONResponse(status_code=400, content={"success": False, "message": err})

    if not vessel:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": f"Vessel with ID {vesselId} not found."},
        )

    overview = service.compute_vessel_overview(vessel.vessel_name, reports)
    voyage = service.compute_voyage_performance(reports)
    fuel = service.compute_fuel_performance(reports)
    rob = service.compute_rob_analytics(reports)
    weather = service.compute_weather_analytics(reports, severe_threshold=severeWeatherThreshold)
    machinery = service.compute_machinery_analytics(reports)
    operations = service.compute_operational_status_analytics(reports)

    return {
        "success": True,
        "data": {
            "vesselId": vessel.id,
            "vesselName": vessel.vessel_name,
            "overview": overview,
            "voyage": voyage,
            "fuel": fuel,
            "rob": rob,
            "weather": weather,
            "machinery": machinery,
            "operations": operations,
        },
    }


@router.get("/fuel")
def get_fuel_analytics(
    vesselName: str = Query(..., description="Vessel name to retrieve fuel metrics for"),
    startDate: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve detailed fuel performance and consumption breakdown."""
    uid = _resolve_user_id(current_user)
    vessel, reports, err = load_vessel_and_reports(
        db, vessel_name=vesselName, start_date_str=startDate, end_date_str=endDate, user_id=uid,
    )
    if err:
        return JSONResponse(status_code=400, content={"success": False, "message": err})

    data = service.compute_fuel_performance(reports)
    return {"success": True, "data": data}


@router.get("/weather")
def get_weather_analytics(
    vesselName: str = Query(..., description="Vessel name to retrieve weather metrics for"),
    startDate: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    severeWeatherThreshold: float = Query(5.0, description="Beaufort scale threshold for severe weather"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve detailed weather statistics and severe weather days count."""
    uid = _resolve_user_id(current_user)
    vessel, reports, err = load_vessel_and_reports(
        db, vessel_name=vesselName, start_date_str=startDate, end_date_str=endDate, user_id=uid,
    )
    if err:
        return JSONResponse(status_code=400, content={"success": False, "message": err})

    data = service.compute_weather_analytics(reports, severe_threshold=severeWeatherThreshold)
    return {"success": True, "data": data}


@router.get("/operations")
def get_operations_analytics(
    vesselName: str = Query(..., description="Vessel name to retrieve operations metrics for"),
    startDate: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve detailed operational status breakdown (days at anchor, underway, etc.)."""
    uid = _resolve_user_id(current_user)
    vessel, reports, err = load_vessel_and_reports(
        db, vessel_name=vesselName, start_date_str=startDate, end_date_str=endDate, user_id=uid,
    )
    if err:
        return JSONResponse(status_code=400, content={"success": False, "message": err})

    data = service.compute_operational_status_analytics(reports)
    return {"success": True, "data": data}


# ── Trend Endpoints ──────────────────────────────────────────────────────────

@router.get("/trends/fuel")
def get_fuel_trend(
    vesselName: str = Query(..., description="Vessel name to retrieve fuel trends for"),
    startDate: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve day-by-day fuel consumption trend data."""
    uid = _resolve_user_id(current_user)
    vessel, reports, err = load_vessel_and_reports(
        db, vessel_name=vesselName, start_date_str=startDate, end_date_str=endDate, user_id=uid,
    )
    if err:
        return JSONResponse(status_code=400, content={"success": False, "message": err})

    data = service.extract_fuel_trend(reports)
    return {"success": True, "data": data}


@router.get("/trends/speed")
def get_speed_trend(
    vesselName: str = Query(..., description="Vessel name to retrieve speed trends for"),
    startDate: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve day-by-day speed, RPM, and slip trend data."""
    uid = _resolve_user_id(current_user)
    vessel, reports, err = load_vessel_and_reports(
        db, vessel_name=vesselName, start_date_str=startDate, end_date_str=endDate, user_id=uid,
    )
    if err:
        return JSONResponse(status_code=400, content={"success": False, "message": err})

    data = service.extract_speed_trend(reports)
    return {"success": True, "data": data}


@router.get("/trends/weather")
def get_weather_trend(
    vesselName: str = Query(..., description="Vessel name to retrieve weather trends for"),
    startDate: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve day-by-day weather Beaufort and wind speed trend data."""
    uid = _resolve_user_id(current_user)
    vessel, reports, err = load_vessel_and_reports(
        db, vessel_name=vesselName, start_date_str=startDate, end_date_str=endDate, user_id=uid,
    )
    if err:
        return JSONResponse(status_code=400, content={"success": False, "message": err})

    data = service.extract_weather_trend(reports)
    return {"success": True, "data": data}


# ── Timeline Endpoint ─────────────────────────────────────────────────────────

@router.get("/timeline")
def get_timeline(
    vesselName: str = Query(..., description="Vessel name to retrieve timeline events for"),
    startDate: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a chronological timeline of reports and activities."""
    uid = _resolve_user_id(current_user)
    vessel, reports, err = load_vessel_and_reports(
        db, vessel_name=vesselName, start_date_str=startDate, end_date_str=endDate, user_id=uid,
    )
    if err:
        return JSONResponse(status_code=400, content={"success": False, "message": err})

    data = service.extract_timeline(reports)
    return {"success": True, "data": data}


@router.get("/insights")
def get_operational_insights(
    vesselName: str = Query(..., description="Vessel name to retrieve operational insights for"),
    startDate: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    endDate: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    severeWeatherThreshold: float = Query(5.0, description="Beaufort scale threshold for severe weather"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve operational insights generated by the insights engine."""
    uid = _resolve_user_id(current_user)
    vessel, reports, err = load_vessel_and_reports(
        db, vessel_name=vesselName, start_date_str=startDate, end_date_str=endDate, user_id=uid,
    )
    if err:
        return JSONResponse(status_code=400, content={"success": False, "message": err})

    if not vessel:
        return JSONResponse(
            status_code=404,
            content={"success": False, "message": f"Vessel '{vesselName}' not found."},
        )

    # 1. Compile the payload
    overview = service.compute_vessel_overview(vessel.vessel_name, reports)
    voyage = service.compute_voyage_performance(reports)
    fuel = service.compute_fuel_performance(reports)
    rob = service.compute_rob_analytics(reports)
    weather = service.compute_weather_analytics(reports, severe_threshold=severeWeatherThreshold)
    machinery = service.compute_machinery_analytics(reports)
    operations = service.compute_operational_status_analytics(reports)

    payload = {
        "overview": overview,
        "voyage": voyage,
        "fuel": fuel,
        "rob": rob,
        "weather": weather,
        "machinery": machinery,
        "operations": operations,
    }

    # 2. Generate insights
    from app.services.insights_service import engine as insights_engine
    insights = insights_engine.generate_all(payload)

    return {"success": True, "data": insights}
