from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.request import Request
from rest_framework.views import Response as DRFResponse

from notification.models import NotificationTemplate
from notification.api.v1.serializers import NotificationTemplateModelSerializer, UserDataSerializer
from notification.api.v1.services import get_users_by_role


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateModelSerializer


@extend_schema(
    parameters=[
        OpenApiParameter('role', type=str, location=OpenApiParameter.QUERY,
                         description='Роль пользователя или "all_users"'),
        OpenApiParameter('page', type=int, location=OpenApiParameter.QUERY,
                         description='Номер страницы'),
        OpenApiParameter('page_size', type=int, location=OpenApiParameter.QUERY,
                         description='Количество записей на странице')
    ],
    responses={200: UserDataSerializer(many=True)}
)
@api_view(['GET'])
def get_user_data(request: Request) -> DRFResponse:
    role: str | None = request.query_params.get('role')
    page: str | int = request.query_params.get('page', 1)
    page_size: str | int = request.query_params.get('page_size', 50)

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

    result: list[dict[str, str]] = [
        {'email': row[0], 'first_name': row[1], 'last_name': row[2]}
        for row in rows
    ]

    serializer: UserDataSerializer = UserDataSerializer(data=result, many=True)
    serializer.is_valid(raise_exception=True)

    return Response({
        'current_page': page,
        'page_size': page_size,
        'results': serializer.data
    })
