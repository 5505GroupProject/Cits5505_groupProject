"""
Utilities for handling analysis results
"""

from app import db
from app.models import AnalysisResult
from datetime import datetime

def save_or_update_analysis_result(title, content, owner_id, upload_id):
    """
    Save a new analysis result or update an existing one to prevent duplicates.
    Ensures title always starts with "Analysis Result: ".
    
    Args:
        title: The base title for the analysis result (e.g., the original upload title)
        content: The content for the analysis result
        owner_id: The user ID of the owner
        upload_id: The ID of the uploaded text
        
    Returns:
        The saved or updated AnalysisResult object
    """
    # Ensure the title always starts with "Analysis Result: "
    if title.startswith("Analysis Result: "):
        formatted_title = title
    elif title.startswith("Analysis of "):
        formatted_title = title.replace("Analysis of ", "Analysis Result: ")
    else:
        formatted_title = f"Analysis Result: {title}"
    
    # Clean up potential double prefixes, just in case
    formatted_title = formatted_title.replace("Analysis Result: Analysis Result: ", "Analysis Result: ")

    # Check if an analysis result already exists for this upload_id
    existing_results = AnalysisResult.query.filter_by(
        upload_id=upload_id,
        owner_id=owner_id
    ).all()
    
    if existing_results:
        # Use the first existing result and update it
        result = existing_results[0]
        result.title = formatted_title # Use the consistently formatted title
        result.content = content
        result.created_at = datetime.utcnow() # Update timestamp
        
        # If there are multiple results (duplicates), remove the extras
        if len(existing_results) > 1:
            for extra_result in existing_results[1:]:
                db.session.delete(extra_result)
    else:
        # Create a new result
        result = AnalysisResult(
            title=formatted_title, # Use the consistently formatted title
            content=content,
            owner_id=owner_id,
            upload_id=upload_id
        )
        db.session.add(result)
    
    # Commit changes
    db.session.commit()
    
    return result
