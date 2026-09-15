from django.db import models
from django.conf import settings


class ResearchProject(models.Model):
    """
    科研项目申报表（对应 research_projects）
    """
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]

    title = models.CharField(max_length=255, verbose_name='项目名称')
    category = models.CharField(max_length=100, verbose_name='项目类型')
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name='申报人'
    )
    college = models.CharField(max_length=100, verbose_name='所属学院')
    budget = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='经费（元）')
    description = models.TextField(verbose_name='项目描述')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='审核状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申报时间')

    class Meta:
        db_table = 'research_projects'
        verbose_name = '科研项目'
        verbose_name_plural = '科研项目管理'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title}（{self.get_status_display()}）'


class ProjectReview(models.Model):
    """
    项目审核记录表（对应 project_reviews）
    """
    RESULT_CHOICES = [
        ('approved', '通过'),
        ('rejected', '拒绝'),
    ]

    project = models.ForeignKey(
        ResearchProject,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='关联项目'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='审核专家'
    )
    comment = models.TextField(verbose_name='审核意见')
    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        verbose_name='审核结果'
    )
    reviewed_at = models.DateTimeField(auto_now_add=True, verbose_name='审核时间')

    class Meta:
        db_table = 'project_reviews'
        verbose_name = '审核记录'
        verbose_name_plural = '审核记录管理'
        ordering = ['-reviewed_at']

    def __str__(self):
        return f'{self.project.title} - {self.get_result_display()} by {self.reviewer.username}'
