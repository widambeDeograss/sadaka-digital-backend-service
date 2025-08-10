from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from service_providers.models import Wahumini
from ..sms_queue_service import SMSQueueService
import logging

logger = logging.getLogger(__name__)

class SendDedicatedMessage(APIView):
    permission_classes = []
    sms_service = SMSQueueService()
    def post(self, request):
        """
        Handles POST requests to send a dedicated message.

        Args:
            request (Request): The request object containing 'phone' and 'message' in the body.

        Returns:
            Response: A response indicating success or failure of the message sending process.
        """
        # Validate required fields in the request data
        phone = request.data.get('phone')
        message = request.data.get('message')
        jumuiya_id = request.data.get('message')
        wahumini_wote =  request.data.get("all")

        if not message:
            return Response(
                {'message': 'Both "phone" and "message" are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        else:
            try:
                if bool(wahumini_wote):
                    waumini =  Wahumini.objects.all()

                    for muumini in waumini:
                        # Attempt to send the message
                        result = self.sms_service.add_to_queue(message, muumini.phone_number, muumini.first_name + " " + muumini.last_name)
                        logger.info(f"SMS notification queued for Waumini: {muumini.id}")


                    # Return success response with the result
                    return Response(
                        {'message': 'Message sent successfully', 'result': result},
                        status=status.HTTP_200_OK
                    )

            except Exception as e:
                # Log the error for debugging purposes
                print(f"Error sending message: {e}")

                # Return a generic error response
                return Response(
                    {'message': 'Failed to send message. Please try again later.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )