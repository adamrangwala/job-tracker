import json
import datetime
import openai
import os

def classify_emails(emails, db):
    """Classify emails using LLM with feedback training"""
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    
    # Get training samples for improving prompts
    training_samples = list(db.training_samples.find())
    
    job_applications = []
    
    for email in emails:
        email_data = extract_email_data(email)
        
        # Create enhanced prompt with training examples
        prompt = f"""
        Subject: {email_data['subject']}
        From: {email_data['from']}
        Body: {email_data['body']}
        
        Based on the email above, classify it into one of these categories:
        1. Job application confirmation
        2. Job rejection
        3. Invitation for next interview step
        4. Not job-related
        
        If job-related, extract the company name and job title.
        """
        
        # Add training examples if available
        if training_samples:
            prompt += "\n\nHere are some examples of correct classifications:\n"
            
            # Group by category and take up to 3 examples of each
            for category in range(1, 5):
                examples = [s for s in training_samples if s.get('correct_category') == str(category)][:3]
                
                if examples:
                    prompt += f"\nCategory {category} examples:\n"
                    for ex in examples:
                        prompt += f"Subject: {ex.get('subject')}\n"
                        prompt += f"From: {ex.get('from')}\n"
                        prompt += f"Result: Category {ex.get('correct_category')}, "
                        prompt += f"Company: {ex.get('correct_company')}, "
                        prompt += f"Job Title: {ex.get('correct_job_title')}\n"
        
        prompt += "\nFormat your response as JSON: {\"category\": \"category_number\", \"company\": \"company_name\", \"jobTitle\": \"job_title\"}"
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            
            if result.get('category') != "4":  # If job-related
                job_app = {
                    'job_title': result.get('jobTitle'),
                    'company': result.get('company'),
                    'date_applied': email_data['date'],
                    'thread_id': email_data['thread_id'],
                    'email_id': email_data['email_id'],
                    'status': 'applied' if result.get('category') == "1" else 
                              'rejected' if result.get('category') == "2" else 'next step',
                    # For tracking user feedback
                    'ai_classified': True,
                    'user_verified': False,
                    'original_category': result.get('category'),
                    'original_company': result.get('company'),
                    'original_job_title': result.get('jobTitle')
                }
                
                # Store in database
                db.job_emails.insert_one({
                    **job_app,
                    **email_data,
                    'date_processed': datetime.datetime.now()
                })
                
                job_applications.append(job_app)
                
        except Exception as e:
            print(f"Error processing email {email_data['email_id']}: {e}")
    
    return job_applications