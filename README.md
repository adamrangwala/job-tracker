# Job Application Tracker

A Python application that scans Gmail for job application emails, classifies them using AI, and allows user feedback to improve classification over time.

## Features
- Gmail integration to scan emails for job-related content
- AI classification of emails into job application confirmations, rejections, and interview invitations
- User feedback system to improve classification accuracy
- Spreadsheet export with key job application details
- Web interface for review and manual entry

## Setup

### Prerequisites
- Python 3.8+
- MongoDB
- Google API credentials
- OpenAI API key

### Installation
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up Google API credentials:
   - Create a project in Google Developer Console
   - Enable Gmail API
   - Create OAuth credentials
   - Download credentials as JSON to `credentials/credentials.json`
4. Set environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `MONGODB_URI`: MongoDB connection string (default: mongodb://localhost:27017/)
   - `SECRET_KEY`: Flask session secret key

### Running the application

## Usage
1. Navigate to http://localhost:5000
2. Authorize the application to access your Gmail
3. Use "Scan New Emails" to scan your inbox
4. Review classifications and provide feedback
5. Download spreadsheet of job applications

## Contributing
Contributions welcome! Please feel free to submit a Pull Request.