from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes import DataChunk
from bson.objectid import ObjectId
from pymongo import InsertOne

class DataChunkModel(BaseDataModel):

    def __init__(self, db_client: object):
        # 1. تمرير مفتاح اتصال الداتابيز للأب BaseDataModel
        super().__init__(db_client=db_client)
        
        # 2. مسك جدول قطع النصوص (chunks) باستخدام الـ Enum
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        # دالة وسيطة لإنشاء الكائن وتجهيز الفهارس بشكل غير متزامن
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        # التحقق من وجود جدول قطع النصوص وإنشاء الفهارس لأول مرة فقط
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
            indexes = DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def create_chunk(self, chunk: DataChunk):
        # 3. تحويل كائن القطعة لقاموس وحفظه في مونجو
        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        
        # 4. حفظ المعرّف الفريد الذي أنشأته مونجو
        chunk.id = result.inserted_id
        
        # 5. إرجاع كائن القطعة النصية مكتملاً
        return chunk

    async def get_chunk(self, chunk_id: str):
        # 6. البحث في مونجو مع تحويل النص لـ ObjectId
        result = await self.collection.find_one({
            "_id": ObjectId(chunk_id)
        })

        if result is None:
            return None

        # 7. فك القاموس وتحويله لكائن DataChunk محمي بـ Pydantic
        return DataChunk(**result)

    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):
        # 8. التكرار على القطع بنظام الدفعات (Batches)
        for i in range(0, len(chunks), batch_size):
            # أخذ شريحة بحجم batch_size (مثلاً من 0 لـ 100)
            batch = chunks[i : i + batch_size]

            # تجهيز كروت العمليات InsertOne لكل قطعة في الدفعة
            operations = []
            for chunk in batch:
                operations.append(
                    InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                )

            # تنفيذ الكتابة الجماعية السريعة للدفعة في مونجو
            await self.collection.bulk_write(operations)

        # 9. إرجاع إجمالي عدد القطع التي تم حفظها بنجاح
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        # 10. حذف جميع القطع النصية التابعة لمشروع معين
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })
        return result.deleted_count

