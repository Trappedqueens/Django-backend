from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters

from .models import ResearchProject, ProjectReview
from .serializers import (
    ResearchProjectSerializer,
    ProjectCreateSerializer,
    AuditSerializer,
    ProjectReviewSerializer,
)
from apps.users.models import User


# ─── 自定义权限 ───────────────────────────────────────────────────────────────

class IsTeacher(IsAuthenticated):
    """仅教师可操作"""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'teacher'


class IsExpertOrAdmin(IsAuthenticated):
    """专家或管理员可操作"""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in ('expert', 'admin')


# ─── 过滤器 ───────────────────────────────────────────────────────────────────

class ProjectFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='exact')
    college = django_filters.CharFilter(field_name='college', lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category', lookup_expr='icontains')

    class Meta:
        model = ResearchProject
        fields = ['status', 'college', 'category']


# ─── 视图集 ───────────────────────────────────────────────────────────────────

class ProjectViewSet(viewsets.ModelViewSet):
    """
    科研项目 ViewSet

    GET    /api/projects/                  列表（支持分页、搜索、过滤）
    POST   /api/projects/                  创建（仅教师）
    GET    /api/projects/{id}/             详情
    PUT    /api/projects/{id}/             更新（仅申报人且状态为 pending）
    DELETE /api/projects/{id}/             删除（仅管理员）
    POST   /api/projects/{id}/audit/       审核（仅专家/管理员）
    """
    queryset = ResearchProject.objects.select_related('applicant').prefetch_related('reviews').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['title', 'applicant__username', 'college', 'category']
    ordering_fields = ['created_at', 'budget', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectCreateSerializer
        if self.action == 'audit':
            return AuditSerializer
        return ResearchProjectSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsTeacher()]
        if self.action == 'audit':
            return [IsExpertOrAdmin()]
        if self.action == 'destroy':
            return [IsExpertOrAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        # 教师只能看自己的项目
        if user.role == 'teacher':
            qs = qs.filter(applicant=user)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        project = serializer.save()
        return Response(
            ResearchProjectSerializer(project).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        # 只有申报人本人、且项目处于待审核状态时才允许编辑
        if project.applicant != request.user:
            return Response({'detail': '只能编辑自己的项目'}, status=status.HTTP_403_FORBIDDEN)
        if project.status != 'pending':
            return Response({'detail': '已审核的项目不可修改'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='audit')
    def audit(self, request, pk=None):
        """
        POST /api/projects/{id}/audit/
        请求体：{ "comment": "审核意见", "result": "approved" | "rejected" }
        """
        project = self.get_object()

        if project.status != 'pending':
            return Response(
                {'detail': '该项目已审核，不可重复操作'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AuditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 创建审核记录
        review = ProjectReview.objects.create(
            project=project,
            reviewer=request.user,
            comment=serializer.validated_data['comment'],
            result=serializer.validated_data['result'],
        )

        # 更新项目状态
        project.status = serializer.validated_data['result']
        project.save(update_fields=['status'])

        return Response(
            {
                'detail': '审核完成',
                'project_status': project.status,
                'review': ProjectReviewSerializer(review).data,
            },
            status=status.HTTP_200_OK
        )
