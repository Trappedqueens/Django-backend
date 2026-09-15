from rest_framework import serializers
from .models import ResearchProject, ProjectReview
from apps.users.serializers import UserInfoSerializer


class ProjectReviewSerializer(serializers.ModelSerializer):
    """审核记录序列化器"""
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)

    class Meta:
        model = ProjectReview
        fields = [
            'id', 'reviewer_name', 'result', 'result_display',
            'comment', 'reviewed_at'
        ]


class ResearchProjectSerializer(serializers.ModelSerializer):
    """项目列表/详情序列化器"""
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)
    applicant_college = serializers.CharField(source='applicant.college', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reviews = ProjectReviewSerializer(many=True, read_only=True)

    class Meta:
        model = ResearchProject
        fields = [
            'id', 'title', 'category', 'applicant', 'applicant_name',
            'applicant_college', 'college', 'budget', 'description',
            'status', 'status_display', 'created_at', 'reviews'
        ]
        read_only_fields = ['applicant', 'status', 'created_at']


class ProjectCreateSerializer(serializers.ModelSerializer):
    """项目创建序列化器（教师提交申报时使用）"""

    class Meta:
        model = ResearchProject
        fields = ['title', 'category', 'college', 'budget', 'description']

    def create(self, validated_data):
        # 自动将当前登录用户设为申报人
        request = self.context['request']
        validated_data['applicant'] = request.user
        return super().create(validated_data)


class AuditSerializer(serializers.Serializer):
    """审核提交序列化器"""
    comment = serializers.CharField(min_length=1, error_messages={'blank': '审核意见不能为空'})
    result = serializers.ChoiceField(
        choices=['approved', 'rejected'],
        error_messages={'invalid_choice': '审核结果只能是 approved 或 rejected'}
    )
