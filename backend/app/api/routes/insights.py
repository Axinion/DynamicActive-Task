"""
API routes for teacher insights and misconception analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from ...db.session import get_db
from ...db.models import User, Class
from ...core.security import get_current_user
from ...services.insights import get_misconception_insights

router = APIRouter()


@router.get("/misconceptions")
async def get_misconception_insights_api(
    class_id: int = Query(..., description="Class ID is required"),
    period: str = Query("week", description="Time period: 'week' or 'month'"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get misconception insights for a class within a time period (teacher only).
    
    Analyzes low-scoring and incorrect responses to identify common misconceptions
    using clustering analysis on student answer embeddings.
    
    Args:
        class_id: ID of the class to analyze
        period: Time period for analysis ('week' for last 7 days, 'month' for last 30 days)
    """
    # Verify user is a teacher
    if current_user["role"] != "teacher":
        raise HTTPException(
            status_code=403, 
            detail="Only teachers can access misconception insights"
        )
    
    # Verify the class exists and teacher owns it
    class_ = db.query(Class).filter(
        Class.id == class_id,
        Class.teacher_id == current_user["id"]
    ).first()
    
    if not class_:
        raise HTTPException(
            status_code=404, 
            detail="Class not found or access denied"
        )
    
    # Validate period parameter
    if period not in ["week", "month"]:
        raise HTTPException(
            status_code=422,
            detail="Period must be 'week' or 'month'"
        )
    
    try:
        # Get misconception insights
        insights = get_misconception_insights(class_id, db, period)
        
        # Add metadata about the request
        insights.update({
            'requested_by': {
                'id': current_user["id"],
                'name': current_user["name"],
                'role': current_user["role"]
            },
            'analysis_timestamp': insights.get('analysis_timestamp', 'N/A')
        })
        
        return insights
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating misconception insights: {str(e)}"
        )


@router.get("/health")
async def insights_health_check():
    """
    Health check endpoint for the insights service.
    """
    return {
        "status": "ok",
        "message": "Insights service is operational",
        "features": [
            "misconception_clustering",
            "response_analysis",
            "keyword_extraction",
            "skill_tag_suggestions"
        ]
    }
