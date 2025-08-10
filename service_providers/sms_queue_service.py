from .models import SMSQueue
from .operations.sms_service import SMSService
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class SMSQueueService:
    def __init__(self):
        self.sms_service = SMSService()

    def add_to_queue(self, message, phone, recipient_name=None, status='WAITING'):
        """Add SMS to queue"""
        sms_queue = SMSQueue.objects.create(
            message=message,
            phone=phone,
            recipient_name=recipient_name or 'Unknown',
            status=status
        )
        logger.info(f"Added SMS to queue: {sms_queue.id} for {phone}")
        return sms_queue

    def bulk_add_to_queue(self, sms_list):
        """Bulk add SMS to queue
        sms_list should be a list of dicts with keys: message, phone, recipient_name
        """
        sms_objects = []
        for sms_data in sms_list:
            sms_objects.append(SMSQueue(
                message=sms_data['message'],
                phone=sms_data['phone'],
                recipient_name=sms_data.get('recipient_name', 'Unknown'),
                status='WAITING'
            ))

        SMSQueue.objects.bulk_create(sms_objects)
        logger.info(f"Bulk added {len(sms_objects)} SMS to queue")
        return len(sms_objects)

    def get_waiting_sms(self, limit=None):
        """Get SMS with WAITING status"""
        queryset = SMSQueue.objects.filter(status='WAITING').order_by('created_at')
        if limit:
            queryset = queryset[:limit]
        return queryset

    def process_sms(self, sms_queue):
        """Process single SMS"""
        formatted_phone = sms_queue.format_phone()

        logger.info(f"=============================================================================")
        logger.info(f"Sending SMS to {formatted_phone}")

        result = self.sms_service.send_sms(sms_queue.message, formatted_phone)

        if result['success']:
            sms_queue.status = 'SUBMITTED'
            sms_queue.sent_at = timezone.now()
            sms_queue.request_id = result.get('request_id')
            sms_queue.phone = formatted_phone  # Update with formatted phone
            sms_queue.save()

            logger.info(f"Response: {result['data']}")
            logger.info(f"✓ Successfully sent SMS to {sms_queue.recipient_name} ({formatted_phone})")

            return True
        else:
            sms_queue.status = 'FAILED'
            sms_queue.error_message = result['error']
            sms_queue.save()

            logger.error(f"✗ Failed to send SMS to {sms_queue.recipient_name} ({formatted_phone}): {result['error']}")

            return False
