from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from notification.models import NotificationTemplate
from notification.api.v1.serializers import NotificationTemplateModelSerializer, UserDataSerializer
from notification.api.v1.services import get_users_by_role


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateModelSerializer


@extend_schema(
    parameters=[
        OpenApiParameter('role', type=str, location=OpenApiParameter.QUERY, description='User role or "all_users"'),
        OpenApiParameter('page', type=int, location=OpenApiParameter.QUERY, description='Page number'),
        OpenApiParameter('page_size', type=int, location=OpenApiParameter.QUERY, description='Records per page')
    ],
    responses={200: UserDataSerializer(many=True)}
)
@api_view(['GET'])
def get_user_data(request):
    role = request.query_params.get('role')
    page = request.query_params.get('page', 1)
    page_size = request.query_params.get('page_size', 50)

    if role is None:
        return Response({'error': "Parameter 'role' is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        page = int(page)
        page_size = int(page_size)
    except ValueError:
        return Response(
            {'error': "Parameters 'page' and 'page_size' must be integers."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if page < 1 or page_size < 1:
        return Response(
            {'error': "Parameters 'page' and 'page_size' must be greater than zero."},
            status=status.HTTP_400_BAD_REQUEST
        )

    rows = get_users_by_role(role, page, page_size)

    result = [
        {
            'id': row[0],
            'email': row[1],
            'first_name': row[2],
            'last_name': row[3]
        }
        for row in rows
    ]

    serializer = UserDataSerializer(data=result, many=True)
    serializer.is_valid(raise_exception=True)

    return Response({
        'current_page': page,
        'page_size': page_size,
        'results': serializer.data
    })
