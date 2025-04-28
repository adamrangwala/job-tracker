import os
from flask import Flask, request, redirect, render_template, session, send_file, url_for
from utils.gmail_service import get_gmail_service, get_emails
from utils.email_processor import extract_email_data, classify_emails
from utils.database import connect_to_db
from utils.spreadsheet import create_spreadsheet
from google_auth_oauthlib.flow import InstalledAppFlow

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key')
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

@app.route('/')
def index():
    """Home page - start OAuth flow"""
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    flow.redirect_uri = url_for('oauth_callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth_callback')
def oauth_callback():
    """Handle OAuth callback"""
    state = session['state']
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    flow.redirect_uri = url_for('oauth_callback', _external=True)
    
    # Use the authorization server's response to fetch the OAuth 2.0 tokens
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    
    # Save credentials
    with open('token.json', 'w') as token:
        token.write(credentials.to_json())
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Display dashboard with emails needing review"""
    db = connect_to_db()
    # Find unverified job emails
    job_emails = list(db.job_emails.find(
        {'user_verified': False}
    ).sort('date_processed', -1).limit(20))
    
    return render_template('dashboard.html', job_emails=job_emails)

@app.route('/scan_emails')
def scan_emails():
    """Scan and process new emails"""
    try:
        service = get_gmail_service()
        db = connect_to_db()
        
        emails = get_emails(service)
        classify_emails(emails, db)
        
        return redirect(url_for('dashboard'))
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/feedback/<id>', methods=['POST'])
def feedback(id):
    """Process user feedback on email classification"""
    is_correct = request.form.get('is_correct') == 'true'
    correct_category = request.form.get('correct_category')
    correct_company = request.form.get('correct_company')
    correct_job_title = request.form.get('correct_job_title')
    
    db = connect_to_db()
    
    # Find the email
    job_email = db.job_emails.find_one({'_id': id})
    if not job_email:
        return "Email not found", 404
    
    # Update with user feedback
    db.job_emails.update_one(
        {'_id': id},
        {'$set': {
            'user_verified': True,
            'is_correct': is_correct,
            'correct_category': correct_category or job_email.get('original_category'),
            'correct_company': correct_company or job_email.get('original_company'),
            'correct_job_title': correct_job_title or job_email.get('original_job_title')
        }}
    )
    
    # If correction provided, add to training samples
    if not is_correct:
        db.training_samples.insert_one({
            'subject': job_email.get('subject'),
            'from': job_email.get('from'),
            'body': job_email.get('body'),
            'original_category': job_email.get('original_category'),
            'correct_category': correct_category,
            'correct_company': correct_company,
            'correct_job_title': correct_job_title,
            'date_added': datetime.datetime.now()
        })
    
    return redirect(url_for('dashboard'))

@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    """Add job application manually"""
    if request.method == 'POST':
        job_title = request.form.get('job_title')
        company = request.form.get('company')
        date_applied = request.form.get('date_applied')
        status = request.form.get('status')
        
        db = connect_to_db()
        db.job_emails.insert_one({
            'job_title': job_title,
            'company': company,
            'date_applied': date_applied,
            'status': status,
            'ai_classified': False,
            'user_verified': True,
            'date_processed': datetime.datetime.now()
        })
        
        return redirect(url_for('dashboard'))
    
    return render_template('add_job.html')

@app.route('/download')
def download():
    """Generate and download spreadsheet"""
    db = connect_to_db()
    job_applications = list(db.job_emails.find({'user_verified': True}))
    
    filename = create_spreadsheet(job_applications)
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)