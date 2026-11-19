from .BaseController import BaseController
import os

class ProjectController(BaseController):
    
    def __init__(self):
        # مناداة الأب لتحميل الإعدادات ومسار files_dir
        super().__init__()

    def get_project_path(self, project_id: str):
        # 1. دمج مسار مجلد الملفات مع اسم/رقم المشروع
        project_dir = os.path.join(
            self.files_dir,
            project_id
        )

        # 2. فحص: لو المجلد مش موجود على الهارد ديسك، أنشئه فوراً
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        # 3. رجّع المسار الكامل للمجلد
        return project_dir
