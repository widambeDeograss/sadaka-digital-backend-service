from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from service_providers.models import Wahumini
from service_providers.operations.message import pushMessage


class SendDedicatedMessage(APIView):
    permission_classes = []

    def post(self, request):
        """
        Handles POST requests to send a dedicated message.

        Args:
            request (Request): The request object containing:
                - 'message' (required): The message to send
                - 'phone' (optional): Specific phone number to send to
                - 'jumuiya_id' (optional): ID of jumuiya to send to all members
                - 'all' (optional): Boolean to send to all wahumini

        Returns:
            Response: A response indicating success or failure of the message sending process.
        """
        # Validate required fields in the request data
        phone = request.data.get('phone')
        message = request.data.get('message')
        jumuiya_id = request.data.get('jumuiya_id')  # Fixed typo from your original code
        wahumini_wote = request.data.get("all", False)

        if not message:
            return Response(
                {'message': 'Message is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Case 1: Send to all wahumini
            if wahumini_wote:
                waumini = Wahumini.objects.filter(is_active=True)
                results = []
                for muumini in waumini:
                    if not muumini.phone_number:
                        continue

                    result = pushMessage(message, muumini.phone_number)
                    results.append({
                        'phone': muumini.phone_number,
                        'result': result
                    })
                return Response(
                    {'message': f'Message sent to all {len(results)} wahumini', 'results': results},
                    status=status.HTTP_200_OK
                )

            # Case 2: Send to specific jumuiya
            elif jumuiya_id:
                waumini = Wahumini.objects.filter(jumuiya__id=jumuiya_id)
                if not waumini.exists():
                    return Response(
                        {'message': 'No wahumini found for the specified jumuiya'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                results = []
                for muumini in waumini:
                    if not muumini.phone_number:
                        continue

                    result = pushMessage(message, muumini.phone_number)
                    results.append({
                        'phone': muumini.phone_number,
                        'result': result
                    })
                return Response(
                    {'message': f'Message sent to {len(results)} wahumini in jumuiya {jumuiya_id}', 'results': results},
                    status=status.HTTP_200_OK
                )

            # Case 3: Send to specific phone number
            elif phone:
                result = pushMessage(message, phone)
                return Response(
                    {'message': 'Message sent successfully', 'result': result},
                    status=status.HTTP_200_OK
                )

            # No valid recipient specified
            else:
                return Response(
                    {'message': 'Either phone, jumuiya_id, or all=true must be specified'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            # Log the error for debugging purposes
            print(f"Error sending message: {e}")

            # Return a generic error response
            return Response(
                {'message': 'Failed to send message. Please try again later.', 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )