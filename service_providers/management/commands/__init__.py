from django.core.management.base import BaseCommand
from django.conf import settings
from service_providers.sms_queue_service import SMSQueueService
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process SMS queue with delays'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--delay',
            type=int,
            default=4,
            help='Delay between SMS sends in seconds (default: 4)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of SMS to process in one batch (default: 50)'
        )
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run continuously (daemon mode)'
        )
    
    def handle(self, *args, **options):
        delay = options['delay']
        batch_size = options['batch_size']
        continuous = options['continuous']
        
        sms_service = SMSQueueService()
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting SMS queue processor (delay: {delay}s, batch: {batch_size})')
        )
        
        if continuous:
            self.stdout.write('Running in continuous mode. Press Ctrl+C to stop.')
            
        try:
            while True:
                waiting_sms = sms_service.get_waiting_sms(limit=batch_size)
                total_sms = waiting_sms.count()
                
                if total_sms == 0:
                    if not continuous:
                        self.stdout.write('No SMS in queue to process.')
                        break
                    else:
                        self.stdout.write('No SMS in queue. Waiting 30 seconds...')
                        time.sleep(30)
                        continue
                
                self.stdout.write(f'Processing {total_sms} SMS from queue...')
                
                for index, sms in enumerate(waiting_sms, 1):
                    self.stdout.write(f'Processing record {index}/{total_sms}:')
                    self.stdout.write(f'Name: {sms.recipient_name}')
                    self.stdout.write(f'Original Phone: {sms.phone}')
                    self.stdout.write(f'Formatted Phone: {sms.format_phone()}')
                    
                    success = sms_service.process_sms(sms)
                    
                    # Add delay between sends (except for the last one)
                    if index < total_sms:
                        self.stdout.write(f'Waiting {delay} seconds before next SMS...')
                        time.sleep(delay)
                
                if not continuous:
                    break
                else:
                    self.stdout.write('Batch complete. Waiting 60 seconds before next batch...')
                    time.sleep(60)
                    
        except KeyboardInterrupt:
            self.stdout.write('\nStopping SMS queue processor...')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error processing SMS queue: {str(e)}')
            )
