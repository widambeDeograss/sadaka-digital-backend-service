from BeemAfrica import Authorize, SMS
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.api_key = getattr(settings, 'BEEM_API_KEY', 'ea6238aa30eb8eed')
        self.secret_key = getattr(settings, 'BEEM_SECRET_KEY',
                                  'NTA1MzEyOTIwMWE4ZjIyZmE1YmJhOGJlNDM1ZDdkNmE2NDY2ZjQ3M2Y0MjdiM2FjYjZiMjg1MjIyNDkyMjdkYQ==')
        self.sender_id = getattr(settings, 'BEEM_SENDER_ID', 'BMC MAKABE')

    def send_sms(self, message, phone, sender_id=None):
        """Send SMS using BeemAfrica API"""
        try:
            Authorize(self.api_key, self.secret_key)

            request = SMS.send_sms(
                message,
                phone,
                sender_id=sender_id or self.sender_id
            )

            return {
                'success': True,
                'data': request,
                'request_id': request.get('request_id') if isinstance(request, dict) else None
            }

        except Exception as e:
            logger.error(f"SMS sending failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }