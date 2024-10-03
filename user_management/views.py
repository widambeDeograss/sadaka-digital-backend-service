from django.db.models import QuerySet
from rest_framework.permissions import AllowAny, IsAuthenticated # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.views import APIView # type: ignore
from .serializer import *
from django.contrib.auth import authenticate, login, update_session_auth_hash
from .models import *
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.authtoken.models import Token # type: ignore
from rest_framework.decorators import api_view, permission_classes # type: ignore



class RegisterUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            email = data["email"]
            user = User.objects.filter(email=email)
            if user:
                message = {"success": False, "message": "username or email already exists"}
                return Response(message)
            serializer.save()
            return Response({"success": True})
        return Response({"success": False, "message": serializer.errors})

    @staticmethod
    def get(request):
        users = User.objects.all()
        return Response(UserGetSerializer(instance=users, many=True).data)


# {
#     "username":"mike",
#     "email":"mike@gmail.com",
#     "firstname":"Michael",
#     "lastname":"Cyril",
#     "user_role":"ADMIN",
#     "password":"123"
# }


class LoginView(APIView):
    permission_classes = [AllowAny]
    model = User

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)
        print(user)
        if user is not None:
            login(request, user)
            user_id = User.objects.get(email=email)
            user_info = UserGetSerializer(instance=user_id, many=False).data
            token, created = Token.objects.get_or_create(user=user)
            response = {"success": True, "token": token.key, "user": user_info}
            return Response(response)
        if user is None:
            response = {
                "success": False,
                "message": "User doesnot exist",
            }
            return Response(response)
        else:
            response = {
                "success": False,
                "message": "Invalid username or password",
            }
            return Response(response)


# {
#     "email":"mike@gmail.com",
#     "password":"123"
# }


# class GetUsersView(APIView):
#     permission_classes = [IsAuthenticated, ]
#     @staticmethod
#     def get(request, query_type):
#         queryset = User.objects.all()
#         if query_type == "institute_staff":
#             institute_id = request.GET.get('institute_id')
#             queryset = queryset.filter(institution=institute_id, user_deleted=False)
#             return Response(UserGetSerializer(instance=queryset, many=True))
        
#         if query_type == "active_staff":
#             queryset = queryset.filter(user_active=True, user_deleted=False)
#             return Response(UserGetSerializer(instance=queryset, many=True))
        
#         if query_type == "inactive_staff":
#             queryset = queryset.filter(user_active=False, user_deleted=False)
#             return Response(UserGetSerializer(instance=queryset, many=True))
        
#         return Response([])



class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, ]
    @staticmethod
    def post(request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get("old_password")):
                user.set_password(serializer.data.get("new_password"))
                user.save()
                update_session_auth_hash(
                    request, user
                )
                return Response(
                    {"message": "Password changed successfully.", "success": True}
                )
            return Response(
                {"error": "Incorrect old password.", "success": False}
            )
        return Response(serializer.errors)

# {
#     "old_password": "123",
#     "new_password": "456"
# }


class ActivateDeactivateStaff(APIView):
    @staticmethod
    def get(request):
        data = request.data
        try:
            id = request.GET.get('id')
            user = User.objects.get(id=id)
            user.user_active = not user.user_active
            user.save()
            return Response({"success": True, "message": "Staff activated successfully" if user.user_active else "Staff deactivated successfully."})
        except User.DoesNotExist:
            return Response({"success": False, "message": "User not found."})
    

class DeleteStaffView(APIView):
    @staticmethod
    def get(request):
        data = request.data
        try:
            id = request.GET.get('id')
            user = User.objects.get(id=id)
            user.user_deleted = True
            user.save()
            return Response({"success": True, "message": "Staff deleted successfully."})
        except User.DoesNotExist:
            return Response({"success": False, "message": "User not found."})


class SystemRoleListCreateView(ListCreateAPIView):
    queryset = SystemRole.objects.all()
    serializer_class = SystemRoleSerializer
    permission_classes = [AllowAny]


class SystemRoleRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = SystemRole.objects.all()
    serializer_class = SystemRoleSerializer
    permission_classes = [AllowAny]


class SystemPermissionListCreateView(ListCreateAPIView):
    queryset = SystemPermission.objects.all()
    serializer_class = SystemPermissionSerializer
    permission_classes = [AllowAny]


class SystemPermissionRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = SystemPermission.objects.all()
    serializer_class = SystemPermissionSerializer
    permission_classes = [AllowAny]


class NotificationListCreateView(ListCreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]


class NotificationRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

