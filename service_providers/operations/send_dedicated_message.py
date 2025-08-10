from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
import logging

from service_providers.models import Wahumini
from ..sms_queue_service import SMSQueueService

# Configure logger
logger = logging.getLogger(__name__)


class SendDedicatedMessage(APIView):
    permission_classes = []
    BATCH_SIZE = 100
    sms_service = SMSQueueService()

    def post(self, request):
        message = request.data.get('message')
        phone = request.data.get('phone')
        jumuiya_id = request.data.get('jumuiya_id')
        wahumini_wote = request.data.get("all", False)

        if not message:
            return Response(
                {'message': 'Message is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Single recipient case
            if phone:
                if not phone.strip():
                    return Response(
                        {'message': 'Phone number cannot be empty'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                return self.handle_single_recipient(message, phone)

            # Batch processing cases
            if wahumini_wote:
                queryset = Wahumini.objects.filter(is_active=True)
                target_name = "all active wahumini"
            elif jumuiya_id:
                queryset = Wahumini.objects.filter(jumuiya__id=jumuiya_id)
                if not queryset.exists():
                    return Response(
                        {'message': 'No wahumini found for the specified jumuiya'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                target_name = f"jumuiya {jumuiya_id}"
            else:
                return Response(
                    {'message': 'Specify phone, jumuiya_id, or all=true'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return self.process_large_batch(queryset, message, target_name)

        except Exception as e:
            logger.exception("Critical error in message sending")
            return Response(
                {'message': 'System error during message processing', 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def handle_single_recipient(self, message, phone):
        """Process single recipient with detailed error handling"""
        try:
            self.sms_service.add_to_queue(message, phone, "Individual Recipient")
            logger.info(f"SMS notification queued for phone: {phone}")
            return Response(
                {'message': 'Message sent successfully', 'result': "queued"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Failed to send to {phone}: {str(e)}")
            return Response(
                {
                    'message': 'Failed to send to individual number',
                    'phone': phone,
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def process_large_batch(self, queryset, message, target_name):
        """Process large batches with optimized database access and error handling"""
        # Get count before filtering to include skipped numbers in stats
        total_recipients = queryset.count()

        # Optimize query - only get phone numbers
        phone_numbers = queryset.exclude(phone_number__isnull=True) \
            .exclude(phone_number='') \
            .values_list('phone_number', flat=True)

        valid_phones = [p for p in phone_numbers if p.strip()]
        skipped = total_recipients - len(valid_phones)

        # Process in batches to prevent memory/timeout issues
        results = self.process_batches(valid_phones, message)

        # Compile statistics
        success_count = results['success_count']
        error_count = results['error_count']
        error_details = results['error_details']

        response_data = {
            'message': f"Batch processing completed for {target_name}",
            'stats': {
                'total_recipients': total_recipients,
                'valid_phones': len(valid_phones),
                'success': success_count,
                'errors': error_count,
                'skipped': skipped,
                }
        }


        return Response(response_data, status=status.HTTP_200_OK)

    def process_batches(self, phone_numbers, message):
        """Process phone numbers in manageable batches"""
        success_count = 0
        error_count = 0
        error_details = []

        for i in range(0, len(phone_numbers), self.BATCH_SIZE):
            batch = phone_numbers[i:i + self.BATCH_SIZE]
            batch_results = self.process_batch(batch, message)

            success_count += batch_results['success_count']
            error_count += batch_results['error_count']
            error_details.extend(batch_results['error_details'])

        return {
            'success_count': success_count,
            'error_count': error_count,
            'error_details': error_details
        }

    def process_batch(self, phone_batch, message):
        """Process a single batch of phone numbers"""
        success_count = 0
        error_count = 0
        error_details = []

        for phone in phone_batch:
            try:
                # Use atomic transactions to ensure database integrity
                with transaction.atomic():
                    self.sms_service.add_to_queue(message, phone, "Individual Recipient")
                success_count += 1
            except Exception as e:
                error_count += 1
                error_details.append({
                    'phone': phone,
                    'error': str(e)
                })
                logger.warning(f"Message failed for {phone}: {str(e)}")

        return {
            'success_count': success_count,
            'error_count': error_count,
            'error_details': error_details
        }