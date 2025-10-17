from rest_framework.views import APIView
from plan.models import PlanModel
from plan.serializers import PlanSerializer
from rest_framework import status
from rest_framework.response import Response


class PlanListAPIView(APIView):
    def get(self, request):
        serializer = PlanSerializer(PlanModel.objects.all(), many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


