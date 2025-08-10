from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date, parse_datetime
from django.utils import timezone
from datetime import datetime, timedelta
from service_providers.models import SMSQueue
from service_providers.sms_queue_service import SMSQueueService
from ..models import SMSQueue
import json

@method_decorator(csrf_exempt, name='dispatch')
class AddToQueueView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            sms_service = SMSQueueService()
            
            if isinstance(data, list):
                # Bulk add
                count = sms_service.bulk_add_to_queue(data)
                return JsonResponse({
                    'success': True,
                    'message': f'{count} SMS added to queue',
                    'count': count
                })
            else:
                # Single add
                sms_queue = sms_service.add_to_queue(
                    message=data['message'],
                    phone=data['phone'],
                    recipient_name=data.get('recipient_name')
                )
                return JsonResponse({
                    'success': True,
                    'message': 'SMS added to queue',
                    'id': sms_queue.id
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class SMSTrackingView(View):
    """
    Advanced SMS tracking with filtering capabilities
    
    GET Parameters:
    - status: Filter by status (PENDING, WAITING, SUBMITTED, FAILED)
    - phone: Filter by phone number (partial match)
    - recipient_name: Filter by recipient name (partial match)  
    - date_from: Filter from date (YYYY-MM-DD)
    - date_to: Filter to date (YYYY-MM-DD)
    - sent_date_from: Filter by sent date from (YYYY-MM-DD)
    - sent_date_to: Filter by sent date to (YYYY-MM-DD)
    - page: Page number for pagination (default: 1)
    - per_page: Items per page (default: 20, max: 100)
    - order_by: Sort field (created_at, sent_at, status, phone) with optional - for desc
    - search: General search across phone and recipient name
    """
    
    def get(self, request):
        try:
            # Get query parameters
            status = request.GET.get('status')
            phone = request.GET.get('phone')
            recipient_name = request.GET.get('recipient_name')
            date_from = request.GET.get('date_from')
            date_to = request.GET.get('date_to')
            sent_date_from = request.GET.get('sent_date_from')
            sent_date_to = request.GET.get('sent_date_to')
            search = request.GET.get('search')
            page = int(request.GET.get('page', 1))
            per_page = min(int(request.GET.get('per_page', 20)), 100)  # Max 100 per page
            order_by = request.GET.get('order_by', '-created_at')
            
            # Start with base queryset
            queryset = SMSQueue.objects.all()
            
            # Apply filters
            if status:
                if status.upper() in ['PENDING', 'WAITING', 'SUBMITTED', 'FAILED']:
                    queryset = queryset.filter(status=status.upper())
            
            if phone:
                queryset = queryset.filter(phone__icontains=phone)
            
            if recipient_name:
                queryset = queryset.filter(recipient_name__icontains=recipient_name)
            
            if search:
                queryset = queryset.filter(
                    Q(phone__icontains=search) | 
                    Q(recipient_name__icontains=search)
                )
            
            # Date filters for created_at
            if date_from:
                try:
                    date_from_parsed = parse_date(date_from)
                    if date_from_parsed:
                        queryset = queryset.filter(created_at__date__gte=date_from_parsed)
                except ValueError:
                    pass
            
            if date_to:
                try:
                    date_to_parsed = parse_date(date_to)
                    if date_to_parsed:
                        queryset = queryset.filter(created_at__date__lte=date_to_parsed)
                except ValueError:
                    pass
            
            # Date filters for sent_at
            if sent_date_from:
                try:
                    sent_date_from_parsed = parse_date(sent_date_from)
                    if sent_date_from_parsed:
                        queryset = queryset.filter(sent_at__date__gte=sent_date_from_parsed)
                except ValueError:
                    pass
            
            if sent_date_to:
                try:
                    sent_date_to_parsed = parse_date(sent_date_to)
                    if sent_date_to_parsed:
                        queryset = queryset.filter(sent_at__date__lte=sent_date_to_parsed)
                except ValueError:
                    pass
            
            # Apply ordering
            valid_order_fields = ['created_at', 'sent_at', 'status', 'phone', 'recipient_name']
            if order_by.lstrip('-') in valid_order_fields:
                queryset = queryset.order_by(order_by)
            else:
                queryset = queryset.order_by('-created_at')
            
            # Get total count before pagination
            total_count = queryset.count()
            
            # Apply pagination
            paginator = Paginator(queryset, per_page)
            page_obj = paginator.get_page(page)
            
            # Serialize data
            sms_data = []
            for sms in page_obj:
                sms_data.append({
                    'id': sms.id,
                    'message': sms.message[:100] + '...' if len(sms.message) > 100 else sms.message,  # Truncate long messages
                    'phone': sms.phone,
                    'recipient_name': sms.recipient_name,
                    'status': sms.status,
                    'created_at': sms.created_at.isoformat(),
                    'updated_at': sms.updated_at.isoformat(),
                    'sent_at': sms.sent_at.isoformat() if sms.sent_at else None,
                    'request_id': sms.request_id,
                    'error_message': sms.error_message,
                })
            
            return JsonResponse({
                'success': True,
                'data': sms_data,
                'pagination': {
                    'current_page': page,
                    'per_page': per_page,
                    'total_count': total_count,
                    'total_pages': paginator.num_pages,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                },
                'filters_applied': {
                    'status': status,
                    'phone': phone,
                    'recipient_name': recipient_name,
                    'date_from': date_from,
                    'date_to': date_to,
                    'sent_date_from': sent_date_from,
                    'sent_date_to': sent_date_to,
                    'search': search,
                    'order_by': order_by,
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class SMSStatsView(View):
    """
    Get SMS statistics with optional date filtering
    """
    
    def get(self, request):
        try:
            # Get date filters
            date_from = request.GET.get('date_from')
            date_to = request.GET.get('date_to')
            
            # Start with base queryset
            queryset = SMSQueue.objects.all()
            
            # Apply date filters if provided
            if date_from:
                try:
                    date_from_parsed = parse_date(date_from)
                    if date_from_parsed:
                        queryset = queryset.filter(created_at__date__gte=date_from_parsed)
                except ValueError:
                    pass
            
            if date_to:
                try:
                    date_to_parsed = parse_date(date_to)
                    if date_to_parsed:
                        queryset = queryset.filter(created_at__date__lte=date_to_parsed)
                except ValueError:
                    pass
            
            # Get status counts
            stats = {
                'total': queryset.count(),
                'pending': queryset.filter(status='PENDING').count(),
                'waiting': queryset.filter(status='WAITING').count(),
                'submitted': queryset.filter(status='SUBMITTED').count(),
                'failed': queryset.filter(status='FAILED').count(),
            }
            
            # Calculate success rate
            if stats['total'] > 0:
                completed = stats['submitted'] + stats['failed']
                if completed > 0:
                    stats['success_rate'] = round((stats['submitted'] / completed) * 100, 2)
                else:
                    stats['success_rate'] = 0.0
            else:
                stats['success_rate'] = 0.0
            
            # Get daily stats for the last 7 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=6)
            
            daily_stats = []
            for i in range(7):
                current_date = start_date + timedelta(days=i)
                day_queryset = SMSQueue.objects.filter(created_at__date=current_date)
                
                daily_stats.append({
                    'date': current_date.isoformat(),
                    'total': day_queryset.count(),
                    'submitted': day_queryset.filter(status='SUBMITTED').count(),
                    'failed': day_queryset.filter(status='FAILED').count(),
                })
            
            return JsonResponse({
                'success': True,
                'stats': stats,
                'daily_stats': daily_stats,
                'date_range': {
                    'from': date_from,
                    'to': date_to
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

class SMSDetailView(View):
    """
    Get detailed information for a specific SMS
    """
    
    def get(self, request, sms_id):
        try:
            sms = SMSQueue.objects.get(id=sms_id)
            
            data = {
                'id': sms.id,
                'message': sms.message,
                'phone': sms.phone,
                'formatted_phone': sms.format_phone(),
                'recipient_name': sms.recipient_name,
                'status': sms.status,
                'created_at': sms.created_at.isoformat(),
                'updated_at': sms.updated_at.isoformat(),
                'sent_at': sms.sent_at.isoformat() if sms.sent_at else None,
                'request_id': sms.request_id,
                'error_message': sms.error_message,
            }
            
            return JsonResponse({
                'success': True,
                'data': data
            })
            
        except SMSQueue.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'SMS not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

class ResendFailedSMSView(View):
    """
    Resend failed SMS by changing their status back to WAITING
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            sms_ids = data.get('sms_ids', [])
            
            if not sms_ids:
                return JsonResponse({
                    'success': False,
                    'error': 'No SMS IDs provided'
                }, status=400)
            
            # Update failed SMS to WAITING status
            updated = SMSQueue.objects.filter(
                id__in=sms_ids,
                status='FAILED'
            ).update(
                status='WAITING',
                error_message=None,
                updated_at=timezone.now()
            )
            
            return JsonResponse({
                'success': True,
                'message': f'{updated} SMS marked for resending',
                'updated_count': updated
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

# Legacy view for backward compatibility
class QueueStatusView(View):
    def get(self, request):
        stats = {
            'pending': SMSQueue.objects.filter(status='PENDING').count(),
            'waiting': SMSQueue.objects.filter(status='WAITING').count(),
            'submitted': SMSQueue.objects.filter(status='SUBMITTED').count(),
            'failed': SMSQueue.objects.filter(status='FAILED').count(),
        }
        
        recent_sms = SMSQueue.objects.order_by('-created_at')[:10]
        recent_data = [{
            'id': sms.id,
            'phone': sms.phone,
            'recipient_name': sms.recipient_name,
            'status': sms.status,
            'created_at': sms.created_at.isoformat(),
            'sent_at': sms.sent_at.isoformat() if sms.sent_at else None,
        } for sms in recent_sms]
        
        return JsonResponse({
            'stats': stats,
            'recent_sms': recent_data
        })


