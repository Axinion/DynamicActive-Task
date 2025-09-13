"""
Invite code generation service for class enrollment.
"""

import secrets
import string
from sqlalchemy.orm import Session
from ..db.models import Class


def generate_invite_code(length: int = 7, db: Session = None) -> str:
    """
    Generate a unique invite code for class enrollment.
    
    Args:
        length: Length of the invite code (default: 7)
        db: Database session for uniqueness check
        
    Returns:
        Unique invite code string
    """
    if length < 6 or length > 8:
        raise ValueError("Invite code length must be between 6 and 8 characters")
    
    # Generate invite code with uppercase letters and digits
    characters = string.ascii_uppercase + string.digits
    
    while True:
        invite_code = ''.join(secrets.choices(characters, k=length))
        
        # Check uniqueness if database session is provided
        if db is None:
            return invite_code
            
        existing_class = db.query(Class).filter(Class.invite_code == invite_code).first()
        if not existing_class:
            return invite_code


def is_invite_code_unique(invite_code: str, db: Session) -> bool:
    """
    Check if an invite code is unique in the database.
    
    Args:
        invite_code: The invite code to check
        db: Database session
        
    Returns:
        True if unique, False otherwise
    """
    existing_class = db.query(Class).filter(Class.invite_code == invite_code).first()
    return existing_class is None
