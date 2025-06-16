from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Association, Farmer
from .serializers import AssociationSerializer, FarmerSerializer
from django.shortcuts import get_object_or_404

# Association Views

class AssociationListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated]

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

class FarmerListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        farmers = Farmer.objects.all()
        serializer = FarmerSerializer(farmers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FarmerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FarmerRetrieveUpdateDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        farmer = self.get_object(pk)
        farmer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
