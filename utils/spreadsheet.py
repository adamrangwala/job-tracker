import pandas as pd

def create_spreadsheet(job_applications, filename='job_applications.xlsx'):
    """Create Excel spreadsheet with job applications"""
    df = pd.DataFrame(job_applications)
    
    # Create hyperlinks for dates
    def create_hyperlink(row):
        email_id = row['email_id']
        date = row['date_applied']
        url = f"https://mail.google.com/mail/u/0/#inbox/{email_id}"
        return f'=HYPERLINK("{url}", "{date}")'
    
    if 'email_id' in df.columns:
        df['date_applied'] = df.apply(create_hyperlink, axis=1)
    
    # Select and reorder columns
    columns = ['job_title', 'company', 'date_applied', 'thread_id', 'status']
    df = df[columns]
    
    # Rename columns for display
    df.columns = ['Job Title', 'Company', 'Date Applied', 'Thread ID', 'Job Status']
    
    # Save to Excel
    df.to_excel(filename, index=False)
    return filename
