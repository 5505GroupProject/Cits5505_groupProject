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
                return f"Error: You don't own analysis result {result_id}", 403

        # Create share entries
        for user_id in user_ids:
            for result_id in selected_ids:
                # Check if already shared
                existing = SharedAnalysis.query.filter_by(
                    user_id=user_id,
                    analysis_id=result_id
                ).first()
                
                if existing:
                    # Update existing share
                    existing.permission = permission
                    existing.message = message
                else:
                    # Create new share
                    entry = SharedAnalysis(
                        user_id=user_id,
                        analysis_id=result_id,
                        permission=permission,
                        message=message
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
    
    # Get results shared with current user - only the latest per upload
    from sqlalchemy import func, desc
    
    # Get all shared analysis IDs for the current user
    shared_analysis_ids = db.session.query(SharedAnalysis.analysis_id).filter(
        SharedAnalysis.user_id == current_user.id
    ).all()
    shared_analysis_ids = [id[0] for id in shared_analysis_ids]
    
    # Get the results and organize by upload_id to find the newest for each,
    # prioritizing those with "Analysis" in the title
    shared_by_upload = {}
    
    # First pass - only consider results with "Analysis" in the title
    for analysis_id in shared_analysis_ids:
        result = AnalysisResult.query.get(analysis_id)
        if (result and result.upload_id is not None and 
            (result.title.startswith("Analysis Result:") or result.title.startswith("Analysis of "))):
            # Group by upload_id
            if result.upload_id not in shared_by_upload or result.created_at > shared_by_upload[result.upload_id].created_at:
                shared_by_upload[result.upload_id] = result
    
    # Second pass - for any upload_ids without an analysis result, use the regular one
    for analysis_id in shared_analysis_ids:
        result = AnalysisResult.query.get(analysis_id)
        if result and result.upload_id is not None and result.upload_id not in shared_by_upload:
            shared_by_upload[result.upload_id] = result
    
    # Convert to list and fix titles if needed
    shared_results = []
    for upload_id, result in shared_by_upload.items():
        if not result.title.startswith("Analysis Result:"):
            if result.title.startswith("Analysis of "):
                result.title = result.title.replace("Analysis of ", "Analysis Result: ")
            else:
                result.title = f"Analysis Result: {result.title}"
            db.session.commit()
        shared_results.append(result)
    
    # Filter out any results that do not start with 'Analysis Result:'
    my_results = [result for result in my_results if result.title.startswith('Analysis Result:')]

    # Filter out any results that do not start with 'Analysis Result:'
    shared_results = [result for result in shared_results if result.title.startswith('Analysis Result:')]

    return render_template('share.html',
        users=connected_users,
        my_results=my_results,
        shared_results=shared_results)

@share_bp.route('/view/<int:result_id>')
@login_required
def view_result(result_id):
    result = AnalysisResult.query.get_or_404(result_id)
    
    shared_entry = SharedAnalysis.query.filter_by(user_id=current_user.id, analysis_id=result_id).first()
    if shared_entry or result.owner_id == current_user.id:
        return render_template("view.html", result=result)
    
    return "Access Denied", 403

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

@share_bp.route('/view/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    """View a specific analysis result"""
    # Get the analysis result
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    
    # Check if the current user owns the analysis or has shared access
    if analysis.owner_id == current_user.id:
        # User owns the analysis
        can_view = True
    else:
        # Check if the analysis is shared with the current user
        shared = SharedAnalysis.query.filter_by(
            user_id=current_user.id,
            analysis_id=analysis_id
        ).first()
        can_view = shared is not None
    
    if not can_view:
        flash('You do not have permission to view this analysis', 'danger')
        return redirect(url_for('share.shared_page'))
        
    # If the analysis has a URL path, redirect to the cleaner URL
    if hasattr(analysis, 'url_path') and analysis.url_path:
        return redirect(url_for('main.analyze', url_path=analysis.url_path))
    
    # Parse the JSON data
    import json
    
    sentiment_data = None
    ngram_data = None
    ner_data = None
    word_freq_data = None
    
    if analysis.sentiment_data:
        sentiment_data = json.loads(analysis.sentiment_data)
    
    if analysis.ngram_data:
        ngram_data = json.loads(analysis.ngram_data)
    
    if analysis.ner_data:
        ner_data = json.loads(analysis.ner_data)
    
    if analysis.word_freq_data:
        word_freq_data = json.loads(analysis.word_freq_data)
    
    # Render the analysis template with the data
    return render_template(
        'analyze.html',
        sentiment_data=sentiment_data,
        ngram_data=ngram_data,
        ner_data=ner_data,
        word_freq_data=word_freq_data,
        analyzed_text=analysis.content,
        is_saved_analysis=True,
        analysis=analysis
    )

