from django.db.models import QuerySet
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework.views import APIView # type: ignore

from .authentication import EmailBackend
from .serializer import *
from django.contrib.auth import authenticate, login, update_session_auth_hash, get_user_model
from .models import *
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.authtoken.models import Token # type: ignore
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
import logging


logger = logging.getLogger(__name__)


class RegisterUser(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# class RegisterUser(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self, request):
#         data = request.data
#
#         serializer = UserSerializer(data=data)
#         if serializer.is_valid():
#             email = data["email"]
#             user = User.objects.filter(email=email)
#             if user:
#                 message = {"success": False, "message": "username or email already exists"}
#                 return Response(message)
#             serializer.save()
#             return Response({"success": True})
#         return Response({"success": False, "message": serializer.errors})
#
#     @staticmethod
#     def get(request):
#         users = User.objects.all()
#         return Response(UserGetSerializer(instance=users, many=True).data)


# {
#     "username":"mike",
#     "email":"mike@gmail.com",
#     "firstname":"Michael",
#     "lastname":"Cyril",
#     "user_role":"ADMIN",
#     "password":"123"
# }


# class LoginView(TokenObtainPairView):
#     permission_classes = [AllowAny]


class LoginView(APIView):
    permission_classes = [AllowAny]
    User = get_user_model()
    model = User

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        logger.info(f"Login attempt for email: {email}")

        if not email or not password:
            logger.warning("Login failed: Email and password are required.")
            return Response({
                "success": False,
                "message": "Email and password are required."
            }, status=400)


        user = authenticate(request, email=email, password=password, backend=EmailBackend)
        logger.info(f"User authenticated: {user}")

        if user is not None:
            if not user.user_active:
                logger.warning(f"Login failed: Inactive account for email: {email}")
                return Response({
                    "success": False,
                    "message": "Your account is inactive. Please contact support."
                }, status=403)

            login(request, user)

            user_info = UserGetSerializer(instance=user, many=False).data

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            logger.info(f"Login successful for email: {email}")

            response = {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user_info,
            }

            return Response(response, status=200)
        else:
            return Response({
                "success": False,
                "message": "Invalid email or password."
            }, status=401)

# {
#     "email":"michael@gmail.com",
#     "password":"12345"
# }


class GetUsersView(APIView):
    permission_classes = [AllowAny, ]
    @staticmethod
    def get(request):
        query_type = request.GET.get("query_type")
        queryset = User.objects.all()
        logger.info(f"Query type: {query_type}")
        if query_type == "sp_admins":
            # institute_id = request.GET.get('institute_id')
            queryset = queryset.filter(is_sp_admin=True)
            return Response(UserGetSerializer(instance=queryset, many=True).data)
        
        if query_type == "active_staff":
            queryset = queryset.filter(user_active=True, user_deleted=False)
            return Response(UserGetSerializer(instance=queryset, many=True))
        
        if query_type == "inactive_staff":
            queryset = queryset.filter(user_active=False, user_deleted=False)
            return Response(UserGetSerializer(instance=queryset, many=True))
        logger.info("No specific query type provided, returning all users.")
        return Response([])



class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, ]
    @staticmethod
    def post(request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            logger.info(f"Password change attempt for user: {user.email}")
            if user.check_password(serializer.data.get("old_password")):
                user.set_password(serializer.data.get("new_password"))
                user.save()
                update_session_auth_hash(
                    request, user
                )
                return Response(
                    {"message": "Password changed successfully.", "success": True}
                )
            logger.warning(f"Password change failed for user: {user.email} - Incorrect old password.")
            return Response(
                {"error": "Incorrect old password.", "success": False}
            )
        return Response(serializer.errors)

# {
#     "old_password": "123",
#     "new_password": "456"
# }


class ActivateDeactivateStaff(APIView):
    permission_classes = [IsAuthenticated]  # Replace DjangoModelPermissionsOrAnonReadOnly with IsAuthenticated

    @staticmethod
    def get(request):
        data = request.data
        logger.info(f"Activate/Deactivate staff attempt: {data}")
        try:
            id = request.GET.get('id')
            user = User.objects.get(id=id)
            user.user_active = not user.user_active
            user.save()
            logger.info(f"Staff {'activated' if user.user_active else 'deactivated'} successfully: {user.email}")
            return Response(
                {
                    "success": True,
                    "message": "Staff activated successfully" if user.user_active else "Staff deactivated successfully"
                },
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            logger.warning(f"Activate/Deactivate staff failed: User not found.")
            return Response(
                {
                    "success": False,
                    "message": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
    

class DeleteStaffView(APIView):
    @staticmethod
    def get(request):
        data = request.data
        logger.info(f"Delete staff attempt: {data}")
        try:

            id = request.GET.get('id')
            user = User.objects.get(id=id)
            user.user_deleted = True
            user.save()
            logger.info(f"Staff deleted successfully: {user.email}")
            return Response({"success": True, "message": "Staff deleted successfully."})
        except User.DoesNotExist:
            logger.warning(f"Delete staff failed: User not found.")
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        if isinstance(serializer.validated_data, list):
            # Bulk create
            SystemPermission.objects.bulk_create([
                SystemPermission(**item) for item in serializer.validated_data
            ])
        else:
            # Single create
            serializer.save()


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

