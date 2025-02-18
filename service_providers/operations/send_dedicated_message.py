from rest_framework.views import APIView
from rest_framework.response import Response
from service_providers.operations.message import pushMessage


class SendDedicatedMessage(APIView):
    def post(self, request):
        try:
            print(request.data)
            phone =  request.data['phone']
            message =  request.data['message']

            res = pushMessage(message, phone)

            return Response({'message': res})

        except Exception as e:
            return Response(status=400, data={'message':"message failed"})