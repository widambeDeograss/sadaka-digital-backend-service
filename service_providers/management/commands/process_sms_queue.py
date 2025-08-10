import time
import logging
from django.core.management.base import BaseCommand
from service_providers.sms_queue_service import SMSQueueService

logger = logging.getLogger('service_providers')

class Command(BaseCommand):
    help = 'Process SMS queue with delays'

    def add_arguments(self, parser):
        parser.add_argument('--delay', type=int, default=4, help='Delay between SMS sends in seconds (default: 4)')
        parser.add_argument('--batch-size', type=int, default=50, help='Number of SMS to process in one batch (default: 50)')
        parser.add_argument('--continuous', action='store_true', help='Run continuously (daemon mode)')

    def handle(self, *args, **options):
        delay = options['delay']
        batch_size = options['batch_size']
        continuous = options['continuous']

        sms_service = SMSQueueService()

        logger.info(f"Starting SMS queue processor (delay={delay}s, batch={batch_size})")

        if continuous:
            logger.info("Running in continuous mode. Press Ctrl+C to stop.")

        try:
            while True:
                waiting_sms = sms_service.get_waiting_sms(limit=batch_size)
                total_sms = waiting_sms.count()

                if total_sms == 0:
                    if not continuous:
                        logger.info("No SMS in queue to process.")
                        break
                    else:
                        logger.info("No SMS in queue. Waiting 30 seconds...")
                        time.sleep(30)
                        continue

                logger.info(f"Processing {total_sms} SMS from queue...")

                for index, sms in enumerate(waiting_sms, 1):
                    logger.info(f"Processing record {index}/{total_sms}: Name={sms.recipient_name}, Phone={sms.phone}, Formatted={sms.format_phone()}")

                    success = sms_service.process_sms(sms)

                    if not success:
                        logger.error(f"Failed to process SMS for {sms.phone}")

                    if index < total_sms:
                        logger.info(f"Waiting {delay} seconds before next SMS...")
                        time.sleep(delay)

                if not continuous:
                    break
                else:
                    logger.info("Batch complete. Waiting 60 seconds before next batch...")
                    time.sleep(60)

        except KeyboardInterrupt:
            logger.warning("Stopping SMS queue processor...")
        except Exception as e:
            logger.exception(f"Error processing SMS queue: {str(e)}")
