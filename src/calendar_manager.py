import os
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import Config
from models import CalendarEvent

class CalendarManager:
    """Handles Google Calendar integration for event creation"""
    
    def __init__(self):
        """Initialize the calendar manager with Google Calendar API"""
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Calendar API"""
        try:
            creds = None
            
            # Check if token file exists
            if os.path.exists(Config.GOOGLE_TOKEN_FILE):
                creds = Credentials.from_authorized_user_file(
                    Config.GOOGLE_TOKEN_FILE, 
                    Config.GOOGLE_SCOPES
                )
            
            # If no valid credentials available, let user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
                        raise FileNotFoundError(
                            f"Google credentials file not found: {Config.GOOGLE_CREDENTIALS_FILE}\n"
                            "Please download your credentials.json from Google Cloud Console"
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        Config.GOOGLE_CREDENTIALS_FILE, 
                        Config.GOOGLE_SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(Config.GOOGLE_TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=creds)
            print("Successfully authenticated with Google Calendar API")
            
        except Exception as e:
            print(f"Error authenticating with Google Calendar: {str(e)}")
            raise
    
    def create_event(self, event: CalendarEvent) -> Dict[str, Any]:
        """
        Create a calendar event
        
        Args:
            event: CalendarEvent object
            
        Returns:
            Created event data
        """
        try:
            if not self.service:
                raise Exception("Calendar service not initialized")
            
            # Prepare event data
            event_data = {
                'summary': event.summary,
                'description': event.description,
                'start': {
                    'dateTime': event.start_time.isoformat(),
                    'timeZone': Config.GOOGLE_CALENDAR_TIMEZONE,
                },
                'end': {
                    'dateTime': event.end_time.isoformat(),
                    'timeZone': Config.GOOGLE_CALENDAR_TIMEZONE,
                },
                'reminders': event.reminders,
            }
            
            # Add attendees if provided and valid
            if event.attendees:
                valid_attendees = [email for email in event.attendees if isinstance(email, str) and '@' in email]
                if valid_attendees:
                    event_data['attendees'] = [
                        {'email': email} for email in valid_attendees
                    ]
            
            # Add location if provided
            if event.location:
                event_data['location'] = event.location
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event_data,
                sendUpdates='all'  # Send invitations to attendees
            ).execute()
            
            print(f"Calendar event created: {created_event.get('htmlLink')}")
            return created_event
            
        except HttpError as error:
            print(f"Error creating calendar event: {error}")
            raise
        except Exception as e:
            print(f"Unexpected error creating calendar event: {str(e)}")
            raise
    
    def create_events(self, events: List[CalendarEvent]) -> List[Dict[str, Any]]:
        """
        Create multiple calendar events
        
        Args:
            events: List of CalendarEvent objects
            
        Returns:
            List of created event data
        """
        created_events = []
        
        for event in events:
            try:
                created_event = self.create_event(event)
                created_events.append(created_event)
            except Exception as e:
                print(f"Failed to create event '{event.summary}': {str(e)}")
                continue
        
        print(f"Successfully created {len(created_events)} out of {len(events)} events")
        return created_events
    
    def list_events(self, time_min: Optional[datetime] = None, 
                   time_max: Optional[datetime] = None, 
                   max_results: int = 10) -> List[Dict[str, Any]]:
        """
        List calendar events
        
        Args:
            time_min: Start time for event search
            time_max: End time for event search
            max_results: Maximum number of events to return
            
        Returns:
            List of event data
        """
        try:
            if not self.service:
                raise Exception("Calendar service not initialized")
            
            # Set default time range if not provided
            if not time_min:
                time_min = datetime.utcnow()
            if not time_max:
                time_max = time_min + timedelta(days=7)
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z',
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return events
            
        except HttpError as error:
            print(f"Error listing calendar events: {error}")
            raise
        except Exception as e:
            print(f"Unexpected error listing calendar events: {str(e)}")
            raise
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event
        
        Args:
            event_id: ID of the event to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.service:
                raise Exception("Calendar service not initialized")
            
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            print(f"Event {event_id} deleted successfully")
            return True
            
        except HttpError as error:
            print(f"Error deleting calendar event: {error}")
            return False
        except Exception as e:
            print(f"Unexpected error deleting calendar event: {str(e)}")
            return False
    
    def update_event(self, event_id: str, event: CalendarEvent) -> Dict[str, Any]:
        """
        Update a calendar event
        
        Args:
            event_id: ID of the event to update
            event: Updated CalendarEvent object
            
        Returns:
            Updated event data
        """
        try:
            if not self.service:
                raise Exception("Calendar service not initialized")
            
            # Prepare event data
            event_data = {
                'summary': event.summary,
                'description': event.description,
                'start': {
                    'dateTime': event.start_time.isoformat(),
                    'timeZone': Config.GOOGLE_CALENDAR_TIMEZONE,
                },
                'end': {
                    'dateTime': event.end_time.isoformat(),
                    'timeZone': Config.GOOGLE_CALENDAR_TIMEZONE,
                },
                'reminders': event.reminders,
            }
            
            # Add attendees if provided
            if event.attendees:
                event_data['attendees'] = [
                    {'email': email} for email in event.attendees
                ]
            
            # Add location if provided
            if event.location:
                event_data['location'] = event.location
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event_data,
                sendUpdates='all'
            ).execute()
            
            print(f"Calendar event updated: {updated_event.get('htmlLink')}")
            return updated_event
            
        except HttpError as error:
            print(f"Error updating calendar event: {error}")
            raise
        except Exception as e:
            print(f"Unexpected error updating calendar event: {str(e)}")
            raise
    
    def check_availability(self, start_time: datetime, end_time: datetime) -> bool:
        """
        Check if the time slot is available
        
        Args:
            start_time: Start time to check
            end_time: End time to check
            
        Returns:
            True if available, False if conflicting events exist
        """
        try:
            events = self.list_events(start_time, end_time, max_results=1)
            return len(events) == 0
            
        except Exception as e:
            print(f"Error checking availability: {str(e)}")
            return False 