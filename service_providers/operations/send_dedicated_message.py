from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from service_providers.operations.message import pushMessage

class SendDedicatedMessage(APIView):
    permission_classes = []
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

        if not phone or not message:
            return Response(
                {'message': 'Both "phone" and "message" are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Attempt to send the message
            result = pushMessage(message, phone)

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