from typing import Dict, Any
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from ..config import settings

logger = logging.getLogger(__name__)

class GoogleSheetsArchiver:
    def __init__(self):
        self.spreadsheet_id = settings.GOOGLE_SHEETS_SPREADSHEET_ID
        self.credentials = None
        self.service = None
        
    async def initialize(self):
        """Initialize Google Sheets service"""
        try:
            self.credentials = Credentials.from_authorized_user_info(
                info={
                    "token": settings.GOOGLE_SHEETS_TOKEN,
                    "refresh_token": settings.GOOGLE_SHEETS_REFRESH_TOKEN,
                    "client_id": settings.GOOGLE_SHEETS_CLIENT_ID,
                    "client_secret": settings.GOOGLE_SHEETS_CLIENT_SECRET,
                }
            )
            self.service = build('sheets', 'v4', credentials=self.credentials)
            logger.info("Google Sheets service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets service: {str(e)}")
            raise

    async def archive_job(self, job: Dict[str, Any]) -> bool:
        """Archive a job to Google Sheets"""
        if not self.service:
            await self.initialize()
            
        try:
            # Prepare job data for sheets
            row_data = [
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                job.get("salary", ""),
                job.get("created_at", "").isoformat(),
                job.get("archived_at", "").isoformat(),
                str(job.get("_id", "")),
                job.get("url", "")
            ]
            
            # Append to sheet
            body = {
                'values': [row_data]
            }
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range='Archive!A:H',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            logger.info(f"Successfully archived job {job['_id']} to Google Sheets")
            return True
            
        except HttpError as e:
            logger.error(f"Google Sheets API error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to archive job to Google Sheets: {str(e)}")
            return False

# Create singleton instance
sheets_archiver = GoogleSheetsArchiver() 