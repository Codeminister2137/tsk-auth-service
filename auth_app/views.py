from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, request
from rest_framework.generics import ListAPIView

from .models import CustomUser
from .serializers import UserSerializer
from .permissions import IsOwnerOrAdmin, IsAdminUser, IsAuthenticatedAndHasSpecialRole


class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckLoginView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Jeśli użytkownik jest zalogowany, zwróci status 200
        return Response({"message": "User is authenticated"}, status=status.HTTP_200_OK)

class ProfileView(viewsets.ModelViewSet):
    """Allows users to retrieve and edit their own profile."""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'list':  # /api/users/
            permission_classes = [IsAdminUser]  # Only Admins
        elif self.action in ['retrieve', 'update', 'create', 'partial_update', 'destroy']:  # /api/users/<id>/
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]  # Owner user or Admin
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]


    def get_object(self):
        """Retrieve and return a profile instance."""
        self.get_permissions()
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj



class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def post(self, request, *args, **kwargs):

        data = request.data
        user = request.user
        if user.check_password(data['old_password']):
            user.set_password(data['new_password'])
            user.save()
            return Response({"message": "Password successfully changed"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Wrong password"}, status=status.HTTP_400_BAD_REQUEST)


class SpecialResourceView(ListAPIView):
    """Allows editors to retrieve special resources."""
    permission_classes = [IsAuthenticatedAndHasSpecialRole]
    def get(self, request, *args, **kwargs):
        data = []
        return Response(data, status=status.HTTP_200_OK)


