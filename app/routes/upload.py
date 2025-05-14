from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import UploadedText, AnalysisResult
from app.models.share import SharedAnalysis
from app import db
from flask_wtf.csrf import validate_csrf, ValidationError
from app.utils.sentiment_utils import get_sentiment_summary
from app.utils.ngram_utils import get_multiple_ngrams
from app.utils.ner_utils import perform_ner_analysis
from app.utils.word_frequency_utils import analyze_word_frequency
import os
import re
import traceback
import requests
from datetime import datetime, timedelta

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

# Define allowed file types
ALLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/', methods=['GET', 'POST'])
@login_required
def upload():
    # For GET requests, always explicitly query the latest uploads
    if request.method == 'GET':
        # Force database query to get fresh data, regardless of session state
        if current_user and hasattr(current_user, 'id'):
            recent_uploads = UploadedText.query.filter_by(user_id=current_user.id).order_by(UploadedText.created_at.desc()).all()
        else:
            recent_uploads = []
            
        return render_template('upload.html', uploads=recent_uploads)
    
    # From here on, we're handling POST requests
    try:
        # Get title if provided
        title = request.form.get('title', '').strip() or None
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename.strip() != '':
                if not file.filename.endswith('.txt'):
                    flash('Only .txt files are supported!', 'danger')
                    return redirect(url_for('upload.upload'))
                
                # Read and process the file content
                try:
                    file_content = file.read().decode('utf-8')
                except UnicodeDecodeError:
                    flash('File encoding not supported. Please use UTF-8 encoded text files.', 'danger')
                    return redirect(url_for('upload.upload'))
                
                if len(file_content.strip()) == 0:
                    flash('Uploaded file is empty!', 'danger')
                    return redirect(url_for('upload.upload'))
                  # Create the UploadedText entry
                new_upload = UploadedText(
                    user_id=current_user.id,
                    title=title or secure_filename(file.filename),
                    content=file_content,
                    filename=secure_filename(file.filename),
                    file_type='file'
                )
                
                db.session.add(new_upload)
                db.session.commit()
                
                # Perform sentiment analysis
                sentiment_data = get_sentiment_summary(file_content)
                
                # Perform N-gram analysis
                ngram_data = get_multiple_ngrams(file_content)
                
                # Perform NER analysis
                ner_data = perform_ner_analysis(file_content)
                
                # Perform word frequency analysis
                word_freq_data = analyze_word_frequency(file_content)
                
                # Store data in session for visualization page - using a reference approach
                session['sentiment_data'] = sentiment_data
                session['ngram_data'] = ngram_data
                session['ner_data'] = ner_data
                session['word_freq_data'] = word_freq_data
                session['upload_id'] = new_upload.id
                # Store text preview in session but keep it minimal - we'll get full text from database
                session['text_content'] = file_content[:500] + "..." if len(file_content) > 500 else file_content
                  # Flash success message and redirect to analyze page
                flash('File uploaded and analyzed successfully!', 'success')
                return redirect(url_for('main.analyze'))
            else:
                flash('No file selected!', 'warning')
            
        # Handle text upload
        elif 'content' in request.form:
            text_content = request.form.get('content', '').strip()
            if text_content:
                # Create new upload
                new_upload = UploadedText(
                    user_id=current_user.id,
                    title=title or 'Text Upload',
                    content=text_content,
                    filename='text_input.txt',
                    file_type='text'
                )
                db.session.add(new_upload)
                db.session.commit()
                
                # Perform sentiment analysis
                sentiment_data = get_sentiment_summary(text_content)
                
                # Perform N-gram analysis
                ngram_data = get_multiple_ngrams(text_content)
                
                # Perform NER analysis
                ner_data = perform_ner_analysis(text_content)
                  # Perform word frequency analysis
                word_freq_data = analyze_word_frequency(text_content)
                
                # Store data in session for visualization page - using a reference approach
                session['sentiment_data'] = sentiment_data
                session['ngram_data'] = ngram_data
                session['ner_data'] = ner_data
                session['word_freq_data'] = word_freq_data
                session['upload_id'] = new_upload.id
                # Store text preview in session but keep it minimal - we'll get full text from database
                session['text_content'] = text_content[:500] + "..." if len(text_content) > 500 else text_content
                  # Flash success message and redirect to analyze page
                flash('Text content uploaded and analyzed successfully!', 'success')
                return redirect(url_for('main.analyze'))
            else:
                flash('No content provided!', 'danger')
        
        else:
            flash('No data submitted!', 'danger')
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Upload error: {str(e)}")
        flash(f'Error: {str(e)}', 'danger')
    
    # If we get here, it means there was an error or invalid submission
    # Redirect back to the upload page (this prevents form resubmission on refresh)
    return redirect(url_for('upload.upload'))

# Added new route to display sentiment analysis and N-gram analysis results
@upload_bp.route('/test-page', methods=['GET'])
@login_required
def test_page():
    # Get analysis data from session
    sentiment_data = session.get('sentiment_data')
    ngram_data = session.get('ngram_data')
    ner_data = session.get('ner_data')
    word_freq_data = session.get('word_freq_data')
    text_content = session.get('text_content')
    upload_id = session.get('upload_id')
    
    # Render test_page template and pass analysis results
    return render_template('test_page.html', 
                          sentiment_data=sentiment_data,
                          ngram_data=ngram_data,
                          ner_data=ner_data,
                          word_freq_data=word_freq_data,
                          text_content=text_content,
                          upload_id=upload_id)

@upload_bp.route('/text', methods=['POST'])
@login_required
def upload_text():
    try:
        content = request.form.get('content')
        if not content or len(content.strip()) == 0:
            return jsonify({'error': 'No content provided'}), 400
            
        new_upload = UploadedText(
            user_id=current_user.id,
            content=content,
            filename='text_input.txt',
            file_type='text'
        )
        
        db.session.add(new_upload)
        db.session.commit()
        
        # Perform text analysis
        sentiment_data = get_sentiment_summary(content)
        ngram_data = get_multiple_ngrams(content)
        ner_data = perform_ner_analysis(content)
        word_freq_data = analyze_word_frequency(content)
        
        return jsonify({
            'success': True,
            'message': 'Content uploaded successfully!',
            'sentiment_data': sentiment_data,
            'ngram_data': ngram_data,
            'ner_data': ner_data,
            'word_freq_data': word_freq_data,
            'upload_id': new_upload.id
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/file', methods=['POST'])
@login_required
def upload_file():
    """Handle file upload."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not file.filename.endswith('.txt'):
            return jsonify({'error': 'Only .txt files are allowed'}), 400
        
        try:
            file_content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return jsonify({'error': 'File encoding not supported. Please use UTF-8 encoded text files.'}), 400
            
        if len(file_content.strip()) == 0:
            return jsonify({'error': 'File is empty'}), 400
            
        new_upload = UploadedText(
            user_id=current_user.id,
            content=file_content,
            filename=secure_filename(file.filename),
            file_type='file'
        )
        
        db.session.add(new_upload)
        db.session.commit()
        
        # Perform text analysis
        sentiment_data = get_sentiment_summary(file_content)
        ngram_data = get_multiple_ngrams(file_content)
        ner_data = perform_ner_analysis(file_content)
        word_freq_data = analyze_word_frequency(file_content)
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'upload_id': new_upload.id,
            'sentiment_data': sentiment_data,
            'ngram_data': ngram_data,
            'ner_data': ner_data,
            'word_freq_data': word_freq_data,
            'content': file_content  # Storing full content without truncation
        }), 200
        
    except Exception as e:
        db.session.rollback()
        error_details = traceback.format_exc()
        current_app.logger.error(f"File upload error: {str(e)}\n{error_details}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@upload_bp.route('/list', methods=['GET'])
@login_required
def list_uploads():
    """Get list of user's uploads."""
    try:
        uploads = UploadedText.query.filter_by(user_id=current_user.id).order_by(UploadedText.created_at.desc()).all()
        
        upload_list = [{
            'id': upload.id,
            'filename': upload.filename,
            'created_at': upload.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'preview': upload.content[:100] + '...' if len(upload.content) > 100 else upload.content,
            'file_type': upload.file_type
        } for upload in uploads]
        
        return jsonify({
            'success': True,
            'uploads': upload_list
        }), 200
        
    except Exception as e:
        error_details = traceback.format_exc()
        current_app.logger.error(f"List uploads error: {str(e)}\n{error_details}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@upload_bp.route('/history', methods=['GET'])
@login_required
def get_upload_history():
    try:
        # Check if current_user is authenticated and has an id
        if not current_user or not hasattr(current_user, 'id'):
            current_app.logger.error("User not properly authenticated for upload history")
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
            
        uploads = UploadedText.query.filter_by(user_id=current_user.id).order_by(UploadedText.created_at.desc()).all()
        
        uploads_list = []
        for upload in uploads:
            # Handle possible None values in content
            content = upload.content or ""
            preview = content[:100] + '...' if len(content) > 100 else content
            
            uploads_list.append({
                'id': upload.id,
                'title': getattr(upload, 'title', None) or 'Untitled',
                'filename': getattr(upload, 'filename', None) or 'text_input.txt',
                'created_at': upload.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'preview': preview,
                'file_type': getattr(upload, 'file_type', 'text')
            })
        
        return jsonify({
            'success': True,
            'uploads': uploads_list
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in upload history: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Could not retrieve upload history: {str(e)}'
        }), 500

@upload_bp.route('/view/<int:upload_id>', methods=['GET'])
@login_required
def view_upload(upload_id):
    try:
        upload = UploadedText.query.get_or_404(upload_id)
        
        # Security check - ensure user can only see their own uploads
        if upload.user_id != current_user.id:
            return render_template('error.html', message="You don't have permission to view this upload"), 403
        
        # Instead of rendering view_upload.html, set up session variables and redirect to visualization
        # Retrieve content and set it in the session
        content = upload.content
        
        # Perform sentiment analysis
        sentiment_data = get_sentiment_summary(content)
        
        # Perform N-gram analysis
        ngram_data = get_multiple_ngrams(content)
        
        # Perform NER analysis
        ner_data = perform_ner_analysis(content)
        
        # Perform word frequency analysis
        word_freq_data = analyze_word_frequency(content)
        
        # Store data in session for visualization page
        session['sentiment_data'] = sentiment_data
        session['ngram_data'] = ngram_data
        session['ner_data'] = ner_data
        session['word_freq_data'] = word_freq_data
        session['upload_id'] = upload.id
        session['text_content'] = content[:500] + "..." if len(content) > 500 else content
          # Flash a message to the user
        flash('Content loaded for analysis', 'success')
        
        # Redirect to the analysis page
        return redirect(url_for('main.analyze'))
        
    except Exception as e:
        current_app.logger.error(f"Error viewing upload: {str(e)}")
        return render_template('error.html', message=f"An error occurred: {str(e)}"), 500

@upload_bp.route('/delete/<int:upload_id>', methods=['DELETE'])
@login_required
def delete_upload(upload_id):
    """Delete a user's upload."""
    try:
        # Get the CSRF token from the header
        csrf_token = request.headers.get('X-CSRFToken')
        
        # Validate CSRF token
        try:
            validate_csrf(csrf_token)
        except ValidationError:
            return jsonify({
                'success': False,
                'error': 'Invalid CSRF token. Please refresh the page and try again.'
            }), 400
            
        upload = UploadedText.query.get_or_404(upload_id)
          # Security check - ensure user can only delete their own uploads
        if upload.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': "You don't have permission to delete this upload"
            }), 403
        
        # Delete the upload itself
        db.session.delete(upload)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Upload deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        error_details = traceback.format_exc()
        current_app.logger.error(f"Delete upload error: {str(e)}\n{error_details}")
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

# New route for searching online news
@upload_bp.route('/search-news', methods=['GET'])
@login_required
def search_news():
    try:
        query = request.args.get('query', '')
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
            
        # Using NewsAPI for real data
        api_key = current_app.config.get('NEWS_API_KEY', '')
        
        # Check if we have a valid API key
        if not api_key or api_key == 'your-news-api-key-here':
            return jsonify({
                'success': False,
                'error': 'No valid News API key configured. Please add your News API key to the configuration or environment variables.',
                'articles': []
            })
        
        # Calculate date for last 7 days
        current_date = datetime.now()
        from_date = (current_date - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Make request to News API
        url = f'https://newsapi.org/v2/everything'
        params = {
            'q': query,
            'from': from_date,
            'sortBy': 'relevancy',
            'language': 'en',
            'apiKey': api_key,
            'pageSize': 10  # Limit to 10 results
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200 and data.get('articles'):
            # Format the results
            articles = []
            for article in data.get('articles', []):
                # Make sure we don't have future dates
                publish_date = article.get('publishedAt', '')
                try:
                    # Parse and validate the date
                    pub_date_obj = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
                    if pub_date_obj > current_date:
                        publish_date = current_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                except (ValueError, TypeError):
                    publish_date = current_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                
                # Get full content
                content = article.get('content', '')
                
                # If content is truncated, try to fetch full article if URL exists
                url = article.get('url')
                if url and (not content or len(content) < 500 or '[+' in content):
                    try:
                        full_article = requests.get(url, timeout=5)  # Increased timeout for better reliability
                        if full_article.status_code == 200:
                            # Extract article content - improved approach for better content extraction
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(full_article.text, 'html.parser')
                            
                            # Try multiple approaches to find article content
                            article_content = None
                            
                            # Check for common article containers
                            selectors = [
                                'article', '.article-content', '.story-body', '.entry-content',
                                '.article-body', '.story-content', '.post-content', '.news-content',
                                '[itemprop="articleBody"]', '[property="content:encoded"]',
                                '.main-content', '.blog-post-content', '.node-content'
                            ]
                            
                            for selector in selectors:
                                if selector.startswith('.'):
                                    article_content = soup.find(class_=selector[1:])
                                elif selector.startswith('['):
                                    # Extract attribute name and value
                                    attr = selector[1:-1].split('=')
                                    if len(attr) == 2:
                                        attr_name = attr[0]
                                        attr_value = attr[1].strip('"\'')
                                        article_content = soup.find(attrs={attr_name: attr_value})
                                else:
                                    article_content = soup.find(selector)
                                    
                                if article_content:
                                    break
                            
                            # If no specific content container found, use the main content area
                            if not article_content:
                                article_content = soup.find('main') or soup.find(id='main') or soup.find('body')
                            
                            if article_content:
                                # Get all paragraphs and combine
                                paragraphs = article_content.find_all('p')
                                full_content = '\n\n'.join([p.text.strip() for p in paragraphs if len(p.text.strip()) > 20])
                                
                                if full_content and len(full_content) > 100:
                                    content = full_content
                                    current_app.logger.info(f"Successfully extracted full content: {len(content)} chars")
                    except Exception as e:
                        current_app.logger.error(f"Error fetching full article: {str(e)}")
                
                # Ensure we have substantial content
                if not content or len(content.strip()) < 200:
                    # Try to get a better fallback by combining title, description, and any content we have
                    title = article.get('title', '')
                    description = article.get('description', '')
                    
                    # Combine all available text
                    combined_text = []
                    if title:
                        combined_text.append(title)
                    if description:
                        combined_text.append(description)
                    if content:
                        combined_text.append(content)
                        
                    # If we still don't have enough, repeat what we have
                    content = '\n\n'.join(combined_text)
                    if len(content.strip()) < 200:
                        content = content * 3  # Triple the content as fallback
                
                # Remove "[+XXXX chars]" that NewsAPI adds
                content = re.sub(r'\[\+\d+ chars\]$', '', content).strip()
                
                articles.append({
                    'title': article.get('title', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': url,
                    'publishedAt': publish_date,
                    'description': article.get('description', ''),
                    'content': content,
                    'urlToImage': article.get('urlToImage', '')
                })
                
            return jsonify({
                'success': True,
                'articles': articles
            })
        else:
            # If API request failed, return error with more details
            error_message = data.get('message', 'Unknown error')
            current_app.logger.error(f"NewsAPI error: {error_message}")
            return jsonify({
                'success': False,
                'error': f"News API error: {error_message}",
                'articles': []
            })
            
    except Exception as e:
        current_app.logger.error(f"News search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}',
            'articles': []
        })

# New route for fetching latest news headlines
@upload_bp.route('/latest-news', methods=['GET'])
@login_required
def latest_news():
    try:
        # Get optional category parameter
        category = request.args.get('category', 'general')
        
        # Using NewsAPI for real data
        api_key = current_app.config.get('NEWS_API_KEY', '')
        current_date = datetime.now()
        
        # Check if we have a valid API key
        if not api_key or api_key == 'your-news-api-key-here':
            return jsonify({
                'success': False,
                'error': 'No valid News API key configured. Please add your News API key to the configuration or environment variables.',
                'articles': []
            })
        
        # Make request to News API
        if category == 'general':
            url = f'https://newsapi.org/v2/top-headlines'
            params = {
                'country': 'us',
                'apiKey': api_key,
                'pageSize': 3  # Limit to 3 results as requested
            }
        else:
            url = f'https://newsapi.org/v2/top-headlines'
            params = {
                'category': category,
                'country': 'us',
                'apiKey': api_key,
                'pageSize': 3  # Limit to 3 results as requested
            }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200 and data.get('articles'):
            # Format the results
            articles = []
            for article in data.get('articles', [])[:3]:  # Double ensure we only get 3
                # Make sure we don't have future dates
                publish_date = article.get('publishedAt', '')
                try:
                    # Parse and validate the date
                    pub_date_obj = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
                    if pub_date_obj > current_date:
                        publish_date = current_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                except (ValueError, TypeError):
                    publish_date = current_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                
                # Get full content
                content = article.get('content', '')
                
                # If content is truncated, try to fetch full article if URL exists
                url = article.get('url')
                if url and (not content or len(content) < 500 or '[+' in content):
                    try:
                        full_article = requests.get(url, timeout=5)  # Increased timeout for better reliability
                        if full_article.status_code == 200:
                            # Extract article content - improved approach for better content extraction
                            from bs4 import BeautifulSoup
                            soup = BeautifulSoup(full_article.text, 'html.parser')
                            
                            # Try multiple approaches to find article content
                            article_content = None
                            
                            # Check for common article containers
                            selectors = [
                                'article', '.article-content', '.story-body', '.entry-content',
                                '.article-body', '.story-content', '.post-content', '.news-content',
                                '[itemprop="articleBody"]', '[property="content:encoded"]',
                                '.main-content', '.blog-post-content', '.node-content'
                            ]
                            
                            for selector in selectors:
                                if selector.startswith('.'):
                                    article_content = soup.find(class_=selector[1:])
                                elif selector.startswith('['):
                                    # Extract attribute name and value
                                    attr = selector[1:-1].split('=')
                                    if len(attr) == 2:
                                        attr_name = attr[0]
                                        attr_value = attr[1].strip('"\'')
                                        article_content = soup.find(attrs={attr_name: attr_value})
                                else:
                                    article_content = soup.find(selector)
                                    
                                if article_content:
                                    break
                            
                            # If no specific content container found, use the main content area
                            if not article_content:
                                article_content = soup.find('main') or soup.find(id='main') or soup.find('body')
                            
                            if article_content:
                                # Get all paragraphs and combine
                                paragraphs = article_content.find_all('p')
                                full_content = '\n\n'.join([p.text.strip() for p in paragraphs if len(p.text.strip()) > 20])
                                
                                if full_content and len(full_content) > 100:
                                    content = full_content
                                    current_app.logger.info(f"Successfully extracted full content: {len(content)} chars")
                    except Exception as e:
                        current_app.logger.error(f"Error fetching full article: {str(e)}")
                
                # Ensure we have substantial content
                if not content or len(content.strip()) < 200:
                    # Try to get a better fallback by combining title, description, and any content we have
                    title = article.get('title', '')
                    description = article.get('description', '')
                    
                    # Combine all available text
                    combined_text = []
                    if title:
                        combined_text.append(title)
                    if description:
                        combined_text.append(description)
                    if content:
                        combined_text.append(content)
                        
                    # If we still don't have enough, repeat what we have
                    content = '\n\n'.join(combined_text)
                    if len(content.strip()) < 200:
                        content = content * 3  # Triple the content as fallback
                
                # Remove "[+XXXX chars]" that NewsAPI adds
                content = re.sub(r'\[\+\d+ chars\]$', '', content).strip()
                
                articles.append({
                    'title': article.get('title', ''),
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': url,
                    'publishedAt': publish_date,
                    'description': article.get('description', ''),
                    'content': content,
                    'urlToImage': article.get('urlToImage', '')
                })
                
            return jsonify({
                'success': True,
                'articles': articles
            })
        else:
            # If API request failed, return error with more details
            error_message = data.get('message', 'Unknown error')
            current_app.logger.error(f"NewsAPI error: {error_message}")
            return jsonify({
                'success': False,
                'error': f"News API error: {error_message}",
                'articles': []
            })
            
    except Exception as e:
        current_app.logger.error(f"Latest news error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}',
            'articles': []
        })