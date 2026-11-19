from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes import Project
import math

class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        # 1. تمرير مفتاح اتصال الداتابيز للأب BaseDataModel
        super().__init__(db_client=db_client)
        
        # 2. تحديد ومسك جدول المشاريع (projects) من الداتابيز
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        # دالة وسيطة لإنشاء الكائن وتجهيز الفهارس بشكل غير متزامن
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        # التحقق من وجود جدول المشاريع وإنشاء الفهارس لأول مرة فقط
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def create_project(self, project: Project):
        # 3. تحويل كائن الـ Pydantic إلى قاموس (dict) وحفظه في MongoDB
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))
        
        # 4. حفظ المعرّف (ID) الذي أنشأته مونجو داخل كائن المشروع
        project.id = result.inserted_id
        
        # 5. إرجاع كائن المشروع مكتملاً
        return project

    # ========================================================
    # الكود المضاف من الدقيقة 11:03 إلى 15:38
    # ========================================================
    async def get_project_or_create_one(self, project_id: str):
        # 1. البحث في قاعدة البيانات عن المشروع
        record = await self.collection.find_one({
            "project_id": project_id
        })

        # 2. لو مش موجود (record is None)، بننشئه ونحفظه في الداتابيز
        if record is None:
            project = Project(project_id=project_id)
            project = await self.create_project(project=project)
            return project

        # 3. لو موجود، بنفك القاموس ونحوله لكائن Project منظم
        return Project(**record)

    # ========================================================
    # الكود المضاف من الدقيقة 15:39 إلى 22:05
    # ========================================================
    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        # 1. عد إجمالي المشاريع الموجودة في قاعدة البيانات
        total_documents = await self.collection.count_documents({})

        # 2. حساب إجمالي عدد الصفحات بتقريب الناتج لأعلى
        total_pages = math.ceil(total_documents / page_size)

        # 3. حساب عدد السجلات المطلوب تخطيها
        skip = (page - 1) * page_size

        # 4. إنشاء المؤشر (cursor) وتحديد الـ skip والـ limit
        cursor = self.collection.find().skip(skip).limit(page_size)

        # 5. السحب من المؤشر بشكل غير متزامن وتحويل كل سجل لكائن
        projects = []
        async for document in cursor:
            projects.append(Project(**document))

        # 6. إرجاع قائمة المشاريع وإجمالي الصفحات
        return projects, total_pages
