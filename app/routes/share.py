from app import db
from app.models import User, SharedAnalysis, AnalysisResult
from flask import Blueprint, render_template, session, request, redirect, url_for
from flask_login import login_required, current_user

# Define blueprint
share_bp = Blueprint('share', __name__, url_prefix='/share')

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
    # Get all users except current user for the share form
    users = User.query.filter(User.id != current_user.id).all()
    
    # Get analysis results owned by current user
    my_results = AnalysisResult.query.filter_by(owner_id=current_user.id).all()
    
    # Get results shared with current user
    shared_results = db.session.query(AnalysisResult)\
        .join(SharedAnalysis)\
        .filter(SharedAnalysis.user_id == current_user.id)\
        .all()
    
    return render_template('share.html',
                         users=users,
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

