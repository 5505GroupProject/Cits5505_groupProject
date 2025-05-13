#!/usr/bin/env python3
"""
Fix duplicates script to thoroughly clean up the analysis_result table
by removing duplicate entries and ensuring consistent title formatting.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import AnalysisResult
from app.models.share import SharedAnalysis
from sqlalchemy import func
from datetime import datetime

# Create app context for database operations
app = create_app()

def fix_duplicates_and_format_titles():
    """
    Clean up the analysis_result table by:
    1. Removing entries without upload_id
    2. Ensuring all titles start with "Analysis Result:"
    3. Removing duplicates, keeping only the newest per upload_id/owner_id
    4. Update timestamps to ensure the correct entries are picked up by queries
    """
    with app.app_context():
        print("Starting database cleanup...")
        fixed_titles = 0
        deleted_orphans = 0
        deleted_duplicates = 0
        
        # 1. Fix any titles that don't use the standardized format
        results = AnalysisResult.query.all()
        for result in results:
            original_title = result.title
            
            # Standardize the title format
            if not result.title.startswith("Analysis Result:"):
                if result.title.startswith("Analysis of "):
                    result.title = result.title.replace("Analysis of ", "Analysis Result: ")
                else:
                    result.title = f"Analysis Result: {result.title}"
                
                # Remove any double prefixes
                result.title = result.title.replace("Analysis Result: Analysis Result: ", "Analysis Result: ")
                print(f"Fixed title: '{original_title}' -> '{result.title}'")
                fixed_titles += 1
        
        # Commit fixes before proceeding
        db.session.commit()
        
        # 2. Delete orphaned entries (those with no upload_id)
        orphaned = AnalysisResult.query.filter(AnalysisResult.upload_id.is_(None)).all()
        for result in orphaned:
            # First delete any shared entries
            shared = SharedAnalysis.query.filter_by(analysis_id=result.id).all()
            for shared_entry in shared:
                db.session.delete(shared_entry)
                
            # Then delete the orphaned result
            print(f"Deleting orphaned result (id={result.id}): '{result.title}'")
            db.session.delete(result)
            deleted_orphans += 1
        
        # Commit orphan deletion before proceeding
        db.session.commit()
        
        # 3. For each upload_id/owner_id combination, keep only the latest result and delete the rest
        # Get all distinct upload_id/owner_id combinations that have multiple entries
        duplicates = db.session.query(
            AnalysisResult.upload_id, 
            AnalysisResult.owner_id, 
            func.count(AnalysisResult.id).label('count')
        ).filter(
            AnalysisResult.upload_id.isnot(None)
        ).group_by(
            AnalysisResult.upload_id, AnalysisResult.owner_id
        ).having(
            func.count(AnalysisResult.id) > 1
        ).all()
        
        # For each duplicate set, keep the newest and update its timestamp to now
        for upload_id, owner_id, count in duplicates:
            results = AnalysisResult.query.filter_by(
                upload_id=upload_id, 
                owner_id=owner_id
            ).order_by(AnalysisResult.created_at.desc()).all()
            
            # Keep the first (newest) result but update its timestamp
            keep_result = results[0]
            keep_result.created_at = datetime.utcnow()
            print(f"Keeping '{keep_result.title}' (id={keep_result.id}) and updating timestamp")
            
            # Delete all others
            for result in results[1:]:
                # First delete any shared entries
                shared = SharedAnalysis.query.filter_by(analysis_id=result.id).all()
                for shared_entry in shared:
                    db.session.delete(shared_entry)
                
                # Then delete the duplicate result
                print(f"Deleting duplicate (id={result.id}): '{result.title}'")
                db.session.delete(result)
                deleted_duplicates += 1
                
        # Commit changes
        db.session.commit()
                
        print(f"Cleanup complete: Fixed {fixed_titles} titles, deleted {deleted_orphans} orphaned entries, "
              f"and removed {deleted_duplicates} duplicates.")

if __name__ == "__main__":
    fix_duplicates_and_format_titles()
