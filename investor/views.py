from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Investor
from .serializers import InvestorSerializer

# Create your views here.
class InvestorListCreateView(generics.ListCreateAPIView):
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InvestorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Investor.objects.all()
    serializer_class = InvestorSerializer
    permission_classes = [permissions.IsAuthenticated]