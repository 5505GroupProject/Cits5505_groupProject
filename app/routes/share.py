from app import db
from app.models.user import User, UserConnection
from app.models.share import SharedAnalysis, AnalysisResult
from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from sqlalchemy import and_, inspect
from datetime import datetime

# Define blueprint
share_bp = Blueprint('share', __name__, url_prefix='/share')

# Function to check if a table exists
def table_exists(table_name):
    try:
        inspector = inspect(db.engine)
        return table_name in inspector.get_table_names()
    except Exception as e:
        print(f"Error checking if table exists: {e}")
        return False

@share_bp.route('/submit', methods=['POST'])
@login_required
def share_results():
    if request.is_json:
        data = request.get_json()
        selected_ids = data.get('analysis_ids', [])
        user_ids = data.get('user_ids', [])
        message = data.get('message', '')
        permission = data.get('permission', 'view-only')
    else:
        selected_ids = request.form.getlist('analysis_ids')
        user_ids = request.form.getlist('user_ids')
        message = request.form.get('message', '')
        permission = request.form.get('permission', 'view-only')

    # Validate inputs
    if not selected_ids:
        return "Error: No analysis results selected", 400
    if not user_ids:
        return "Error: No users selected", 400

    try:
        # Validate all users exist
        for user_id in user_ids:
            user = User.query.get(user_id)
            if not user:
                return f"Error: User ID {user_id} not found", 400

        # Validate all analysis results exist and belong to current user
        for result_id in selected_ids:
            result = AnalysisResult.query.get(result_id)
            if not result:
                return f"Error: Analysis result {result_id} not found", 400
            if result.owner_id != current_user.id:
                return f"Error: You don't own analysis result {result_id}", 403        # Create share entries
        for user_id in user_ids:
            for result_id in selected_ids:
                # Check if already shared
                existing = SharedAnalysis.query.filter_by(
                    user_id=user_id,
                    analysis_id=result_id
                ).first()
                
                # Get the full analysis result data
                result = AnalysisResult.query.get(result_id)
                
                if existing:
                    # Update existing share
                    existing.permission = permission
                    existing.message = message
                    existing.sharer_id = current_user.id  # Set current user as sharer
                    # Update all the duplicated fields 
                    existing.title = result.title
                    existing.content = result.content
                    existing.original_owner_id = result.owner_id
                    existing.upload_id = result.upload_id
                    existing.analysis_created_at = result.created_at
                    existing.url_path = result.url_path
                    existing.sentiment_data = result.sentiment_data
                    existing.ngram_data = result.ngram_data
                    existing.ner_data = result.ner_data
                    existing.word_freq_data = result.word_freq_data
                else:
                    # Create new share with all analysis data
                    entry = SharedAnalysis(
                        user_id=user_id,
                        analysis_id=result_id,
                        sharer_id=current_user.id,  # Set current user as sharer
                        permission=permission,
                        message=message,
                        # Add all the duplicated fields
                        title=result.title,
                        content=result.content,
                        original_owner_id=result.owner_id,
                        upload_id=result.upload_id,
                        analysis_created_at=result.created_at,
                        url_path=result.url_path,
                        sentiment_data=result.sentiment_data,
                        ngram_data=result.ngram_data,
                        ner_data=result.ner_data,
                        word_freq_data=result.word_freq_data
                    )
                    db.session.add(entry)

        db.session.commit()
        return "Analysis results shared successfully!", 200

    except Exception as e:
        db.session.rollback()
        return f"Error sharing results: {str(e)}", 500

@share_bp.route('/')
@login_required
def shared_page():
    # Get connected users for the current user using ORM
    if table_exists('user_connection'):
        # Use ORM query to get user connections
        connections = UserConnection.query.filter_by(user_id=current_user.id).all()
        connected_users = [conn.connected_user for conn in connections]
    else:
        # Fallback to all users if table doesn't exist
        connected_users = User.query.filter(User.id != current_user.id).all()
    
    # Direct query to get ONLY the newest result per upload_id where title is correctly formatted
    # This approach eliminates the issues with multiple entries being displayed
    from sqlalchemy import func, desc
    
    # Use a simpler approach that's more reliable
    # Get a list of all upload_id values for the current user
    upload_ids = db.session.query(AnalysisResult.upload_id).filter(
        AnalysisResult.owner_id == current_user.id,
        AnalysisResult.upload_id.isnot(None)
    ).distinct().all()
    upload_ids = [id[0] for id in upload_ids]  # Convert from [(id1,), (id2,)] to [id1, id2]
    
    # Get the newest result for each upload_id that is explicitly an analysis result
    # and not just a copy of the original upload title
    my_results = []
    for upload_id in upload_ids:
        # For each upload_id, find results that have "Analysis" in the title
        analysis_results = AnalysisResult.query.filter(
            AnalysisResult.owner_id == current_user.id,
            AnalysisResult.upload_id == upload_id,
            (AnalysisResult.title.startswith("Analysis Result:") | AnalysisResult.title.startswith("Analysis of "))
        ).order_by(desc(AnalysisResult.created_at)).all()
        
        # If we found analysis results, use the newest one
        if analysis_results:
            newest = analysis_results[0]
            # Standardize the title format if needed
            if newest.title.startswith("Analysis of "):
                newest.title = newest.title.replace("Analysis of ", "Analysis Result: ")
                db.session.commit()
            my_results.append(newest)
        else:
            # Check if there's any result at all for this upload_id
            regular_result = AnalysisResult.query.filter(
                AnalysisResult.owner_id == current_user.id,
                AnalysisResult.upload_id == upload_id
            ).order_by(desc(AnalysisResult.created_at)).first()
            
            # If there is a result but without "Analysis" in the title, fix it
            if regular_result:
                regular_result.title = f"Analysis Result: {regular_result.title}"
                db.session.commit()
                my_results.append(regular_result)
      # Get results shared with current user directly from the SharedAnalysis table
    # This now contains all the duplicated analysis data
    from sqlalchemy import func, desc
    
    # Get all shared analyses for the current user
    shared_analyses = SharedAnalysis.query.filter(
        SharedAnalysis.user_id == current_user.id
    ).all()
    
    # Organize by upload_id to find the newest for each
    shared_by_upload = {}
    
    # Group by upload_id and keep only the newest
    for shared_analysis in shared_analyses:
        if shared_analysis.upload_id is not None:
            # Group by upload_id
            if shared_analysis.upload_id not in shared_by_upload or shared_analysis.analysis_created_at > shared_by_upload[shared_analysis.upload_id].analysis_created_at:
                shared_by_upload[shared_analysis.upload_id] = shared_analysis
    
    # Convert to list and fix titles if needed
    shared_results = list(shared_by_upload.values())
    
    # Standardize titles if needed
    for result in shared_results:
        if not result.title.startswith("Analysis Result:"):
            if result.title.startswith("Analysis of "):
                result.title = result.title.replace("Analysis of ", "Analysis Result: ")
            else:
                result.title = f"Analysis Result: {result.title}"
            db.session.commit()
    
    # Filter out any results that do not start with 'Analysis Result:'
    my_results = [result for result in my_results if result.title.startswith('Analysis Result:')]

    # Also ensure all shared results have proper titles
    shared_results = [result for result in shared_results if result.title.startswith('Analysis Result:')]

    return render_template('share.html',
        users=connected_users,
        my_results=my_results,
        shared_results=shared_results)

@share_bp.route('/search-user', methods=['POST'])
@login_required
def search_user():
    """Search for users by username"""
    if not request.is_json:
        return jsonify({"error": "Invalid request format"}), 400
        
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({"error": "Username is required"}), 400
        
    # Search for users with similar usernames, excluding current user
    users = User.query.filter(
        and_(
            User.username.ilike(f"%{username}%"),
            User.id != current_user.id
        )
    ).limit(10).all()
    
    # Format user data for response
    user_list = [{
        "id": user.id,
        "username": user.username
    } for user in users]
    
    return jsonify({"users": user_list})

@share_bp.route('/add-user', methods=['POST'])
@login_required
def add_user():
    """Add a user connection"""
    if not request.is_json:
        return jsonify({"error": "Invalid request format"}), 400
        
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    # Check if user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Check if connection already exists using ORM
    existing = UserConnection.query.filter_by(
        user_id=current_user.id, 
        connected_user_id=user_id
    ).first()
    
    if existing:
        return jsonify({"error": "User already in your connections"}), 409
    
    try:
        # Create a new connection using ORM
        new_connection = UserConnection(
            user_id=current_user.id,
            connected_user_id=user_id
        )
        db.session.add(new_connection)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Added {user.username} to your connections",
            "user": {
                "id": user.id,
                "username": user.username
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to add user: {str(e)}"}), 500

@share_bp.route('/remove-user/<int:user_id>', methods=['POST'])
@login_required
def remove_user(user_id):
    """Remove a user connection"""
    if not table_exists('user_connection'):
        return jsonify({"error": "User connections feature not available"}), 500
    
    # Find the connection using ORM
    connection = UserConnection.query.filter_by(
        user_id=current_user.id,
        connected_user_id=user_id
    ).first()
    
    if not connection:
        return jsonify({"error": "Connection not found"}), 404
    
    try:
        # Delete the connection using ORM
        db.session.delete(connection)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "User removed from your connections"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to remove user: {str(e)}"}), 500

@share_bp.route('/view-shared/<int:shared_id>')
@login_required
def view_shared_analysis(shared_id):
    """View a shared analysis using the data directly from SharedAnalysis"""
    # Get the shared analysis record
    shared = SharedAnalysis.query.get_or_404(shared_id)
    
    # Check if the current user has access
    if shared.user_id != current_user.id:
        flash('You do not have permission to view this analysis', 'danger')
        return redirect(url_for('share.shared_page'))
        
    # Parse the JSON data
    import json
    
    sentiment_data = None
    ngram_data = None
    ner_data = None
    word_freq_data = None
    
    if shared.sentiment_data:
        sentiment_data = json.loads(shared.sentiment_data)
    
    if shared.ngram_data:
        ngram_data = json.loads(shared.ngram_data)
    
    if shared.ner_data:
        ner_data = json.loads(shared.ner_data)
    
    if shared.word_freq_data:
        word_freq_data = json.loads(shared.word_freq_data)    # Create a dict to represent the original owner
    original_owner = User.query.get(shared.original_owner_id)
    owner_info = {
        "username": original_owner.username if original_owner else "Unknown User"
    }
    
    # Get sharer information
    sharer_info = None
    if shared.sharer_id:
        sharer = User.query.get(shared.sharer_id)
        sharer_info = {
            "username": sharer.username if sharer else "Unknown User"
        }
      # Render the share view template with the data
    return render_template(
        'view_share.html',
        sentiment_data=sentiment_data,
        ngram_data=ngram_data,
        ner_data=ner_data,
        word_freq_data=word_freq_data,
        analyzed_text=shared.content,
        is_saved_analysis=True,
        analysis=shared,
        shared_analysis=True,
        original_owner=owner_info,
        sharer_info=sharer_info
    )

@share_bp.route('/save-to-my-news/<int:shared_id>')
@login_required
def save_shared_to_my_news(shared_id):
    """Save a shared analysis text to the user's own UploadedText collection"""
    # Get the shared analysis record
    shared = SharedAnalysis.query.get_or_404(shared_id)
    
    # Check if the current user has access
    if shared.user_id != current_user.id:
        flash('You do not have permission to save this analysis', 'danger')
        return redirect(url_for('share.shared_page'))    # Check if the permission allows resharing
    if shared.permission != "allow-reshare":
        flash('This analysis is not allowed to be saved to your collection', 'danger')
        return redirect(url_for('share.view_shared_analysis', shared_id=shared_id))
    
    try:
        # Create a new UploadedText from the shared analysis
        from app.models import UploadedText
        
        # Check if the user already has this content saved
        existing_upload = UploadedText.query.filter_by(
            user_id=current_user.id,
            content=shared.content
        ).first()
        
        if existing_upload:
            flash('This content is already in your collection', 'info')
            return redirect(url_for('upload.upload'))
        
        # Generate a title for the saved content
        title = f"Saved: {shared.title}"
        
        # Create a new UploadedText entry
        new_upload = UploadedText(
            user_id=current_user.id,
            title=title,
            content=shared.content,
            file_type='text'
        )
        
        db.session.add(new_upload)
        db.session.commit()
        
        flash('Analysis has been saved to your collection successfully', 'success')
        
        # Redirect to the upload page to see the saved text
        return redirect(url_for('upload.upload'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving analysis: {str(e)}', 'danger')
        return redirect(url_for('share.view_shared_analysis', shared_id=shared_id))

