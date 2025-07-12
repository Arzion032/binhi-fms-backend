import rest_framework.permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Association, Farmer
from .serializers import AssociationSerializer, FarmerSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

# Association Views

class AssociationListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        associations = Association.objects.all()
        serializer = AssociationSerializer(associations, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AssociationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssociationRetrieveUpdateDeleteView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return get_object_or_404(Association, pk=pk)

    def get(self, request, pk):
        association = self.get_object(pk)
        serializer = AssociationSerializer(association)
        return Response(serializer.data)

    def patch(self, request, pk):
        association = self.get_object(pk)
        serializer = AssociationSerializer(association, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        association = self.get_object(pk)
        association.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Farmer Views
@authentication_classes([])  # Disable authentication
@permission_classes([AllowAny])  # Allow any
class FarmerListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        association_id = request.query_params.get('association_id')

        if association_id:
            farmers = Farmer.objects.filter(association_id=association_id)
        else:
            farmers = Farmer.objects.all()

        serializer = FarmerSerializer(farmers, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = FarmerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print("POST error:", serializer.errors)  # 👈 Add this line
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([])  # Disable authentication
@permission_classes([AllowAny])  # Allow any
class FarmerRetrieveUpdateDeleteView(APIView):

    def get_object(self, pk):
        return get_object_or_404(Farmer, pk=pk)

    def get(self, request, pk):
        farmer = self.get_object(pk)
        serializer = FarmerSerializer(farmer)
        return Response(serializer.data)

    def patch(self, request, pk):
        farmer = self.get_object(pk)
        serializer = FarmerSerializer(farmer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        print("PATCH error:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        farmer = self.get_object(pk)
        farmer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
