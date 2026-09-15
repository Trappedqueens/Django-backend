"""
初始化示例数据脚本
运行方式：python manage.py shell < init_data.py
或：python manage.py runscript init_data（需安装 django-extensions）

直接在项目根目录执行：python init_data.py
"""
import os
import sys
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.users.models import User
from apps.projects.models import ResearchProject, ProjectReview


def create_users():
    print("[*] 创建示例用户...")

    users_data = [
        {
            'username': 'admin',
            'password': 'admin123',
            'role': 'admin',
            'college': '信息学院',
            'email': 'admin@school.edu.cn',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'teacher01',
            'password': 'teacher123',
            'role': 'teacher',
            'college': '计算机学院',
            'email': 'teacher01@school.edu.cn',
        },
        {
            'username': 'teacher02',
            'password': 'teacher123',
            'role': 'teacher',
            'college': '电子工程学院',
            'email': 'teacher02@school.edu.cn',
        },
        {
            'username': 'expert01',
            'password': 'expert123',
            'role': 'expert',
            'college': '科研处',
            'email': 'expert01@school.edu.cn',
        },
    ]

    created_users = {}
    for data in users_data:
        username = data['username']
        if User.objects.filter(username=username).exists():
            print(f"  [skip] 用户 {username} 已存在，跳过")
            created_users[username] = User.objects.get(username=username)
            continue

        password = data.pop('password')
        user = User(**data)
        user.set_password(password)
        user.save()
        print(f"  [ok] 创建用户：{username}（{user.get_role_display()}）")
        created_users[username] = user

    return created_users


def create_projects(users):
    print("\n[*] 创建示例项目...")

    teacher1 = users.get('teacher01')
    teacher2 = users.get('teacher02')

    projects_data = [
        {
            'title': '基于深度学习的医学影像智能诊断系统研究',
            'category': '国家级自然科学基金',
            'applicant': teacher1,
            'college': '计算机学院',
            'budget': 500000.00,
            'description': '本项目拟研究基于卷积神经网络的医学影像自动诊断方法，重点突破小样本学习、多模态融合等关键技术，开发高精度的医学影像智能诊断系统，助力临床辅助诊断。',
            'status': 'pending',
        },
        {
            'title': '新型纳米材料在能源存储中的应用研究',
            'category': '省级科研项目',
            'applicant': teacher1,
            'college': '计算机学院',
            'budget': 200000.00,
            'description': '探索新型二维纳米材料（如 MXene）在锂离子电池电极材料中的应用，通过调控其表面化学性质来提升电化学性能，为高性能储能器件的开发提供理论和实验支撑。',
            'status': 'approved',
        },
        {
            'title': '智慧城市交通流量预测与优化算法研究',
            'category': '横向合作项目',
            'applicant': teacher2,
            'college': '电子工程学院',
            'budget': 350000.00,
            'description': '联合某市交通管理部门，基于图神经网络和时空数据融合技术，建立城市道路交通流量预测模型，并设计自适应信号配时优化算法，降低城市拥堵率。',
            'status': 'pending',
        },
        {
            'title': '基于区块链的高校科研数据可信共享平台',
            'category': '校级重点项目',
            'applicant': teacher2,
            'college': '电子工程学院',
            'budget': 80000.00,
            'description': '设计并实现一套基于区块链技术的科研数据共享系统，保证数据的不可篡改性和可追溯性，解决跨院系科研数据共享中的信任问题。',
            'status': 'rejected',
        },
    ]

    created_projects = []
    for data in projects_data:
        if ResearchProject.objects.filter(title=data['title']).exists():
            print(f"  [skip] 项目已存在，跳过：{data['title'][:25]}")
            created_projects.append(ResearchProject.objects.get(title=data['title']))
            continue
        project = ResearchProject.objects.create(**data)
        print(f"  [ok] 创建项目：{project.title[:30]}（{project.get_status_display()}）")
        created_projects.append(project)

    return created_projects


def create_reviews(users, projects):
    print("\n[*] 创建示例审核记录...")

    expert = users.get('expert01')
    if not expert:
        print("  [skip] 专家用户不存在，跳过审核记录")
        return

    reviews_data = [
        {
            'project': projects[1],  # approved 项目
            'reviewer': expert,
            'comment': '项目研究目标明确，技术路线可行，研究团队具备相应实力，建议批准立项。',
            'result': 'approved',
        },
        {
            'project': projects[3],  # rejected 项目
            'reviewer': expert,
            'comment': '项目预算偏高，研究内容与已有项目重叠较多，建议申报人修改后重新提交。',
            'result': 'rejected',
        },
    ]

    for data in reviews_data:
        project = data['project']
        if ProjectReview.objects.filter(project=project, reviewer=expert).exists():
            print(f"  [skip] 审核记录已存在：{project.title[:20]}")
            continue
        review = ProjectReview.objects.create(**data)
        print(f"  [ok] 审核记录：{review.project.title[:25]} -> {review.get_result_display()}")


def main():
    print("=" * 55)
    print("  高校科研项目管理系统 - 初始化示例数据")
    print("=" * 55)

    users = create_users()
    projects = create_projects(users)
    create_reviews(users, projects)

    print("\n" + "=" * 55)
    print("  [done] 初始化完成！")
    print()
    print("  账号信息：")
    print("    管理员  admin     / admin123")
    print("    教师    teacher01 / teacher123")
    print("    教师    teacher02 / teacher123")
    print("    专家    expert01  / expert123")
    print("=" * 55)


if __name__ == '__main__':
    main()
