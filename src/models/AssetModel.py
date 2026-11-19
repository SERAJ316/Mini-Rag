from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes import Asset
from bson import ObjectId

class AssetModel(BaseDataModel):

    def __init__(self, db_client: object):
        # 1. تمرير مفتاح اتصال الداتابيز للأب BaseDataModel
        super().__init__(db_client=db_client)

        # 2. مسك جدول الـ assets من الداتابيز
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        # دالة وسيطة لإنشاء الكائن وتجهيز الفهارس بشكل غير متزامن
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        # التحقق من وجود جدول الـ assets وإنشاء الفهارس لأول مرة فقط
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def create_asset(self, asset: Asset):
        # تحويل كائن الـ Asset إلى قاموس وحفظه في MongoDB (exclude_none يستثني _id=None ويحافظ على asset_pushed_at)
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_none=True))
        asset.id = result.inserted_id
        return asset

    async def get_all_project_assets(self, asset_project_id: str):
        # جلب جميع الـ assets التابعة لمشروع معين
        return await self.collection.find({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
        }).to_list(length=None)
