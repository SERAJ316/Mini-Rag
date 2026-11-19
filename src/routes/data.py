from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
import aiofiles
import logging
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
from models import (
    ResponseSignal,
    ProcessRequest,
    ProjectModel,
    DataChunkModel,
    DataChunk,
    AssetModel,
    Asset,
    AssetTypeEnum,
)

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):

    data_controller = DataController()

    # 1. فحص مواصفات الملف (النوع والحجم)
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": result_signal
            }
        )

    # 2. إنشاء المسار الفريد للملف وتنضيف اسمه
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )

    # 3. كتابة الملف على الهارد بشكل غير معطل (Async Chunks)
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )

    # 4. حفظ أو جلب المشروع من قاعدة البيانات (مع تجهيز الفهارس)
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)

    # 5. تخزين بيانات الملف المرفوع في جدول الـ assets
    asset_model = await AssetModel.create_instance(
        db_client=request.app.db_client
    )

    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path)
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)

    # 6. رد بالنجاح مع معرّف الـ Asset المسجل ومعرّف المشروع في الداتابيز
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id": str(asset_record.id),
            "project_id": str(project.id)
        }
    )

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):

    process_controller = ProcessController(project_id=project_id)

    # 1. قراءة محتويات الملف (اللوادر وقراءة الصفحات)
    file_content = process_controller.get_file_content(file_id=process_request.file_id)

    if file_content is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_ID_ERROR.value
            }
        )

    # 2. تقطيع الملف لتشانكس متناسقة مع التداخل
    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=process_request.file_id,
        chunk_size=process_request.chunk_size,
        overlap_size=process_request.overlap_size
    )

    # 3. التحقق من نجاح التقطيع
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESSING_FAILED.value
            }
        )

    # 4. جلب أو التأكد من وجود المشروع في الداتابيز (مع تجهيز الفهارس)
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)

    # 5. تجهيز موديل قطع النصوص (مع تجهيز الفهارس)
    data_chunk_model = await DataChunkModel.create_instance(
        db_client=request.app.db_client
    )

    # 6. إذا طلب المستخدم do_reset = 1 نقوم بمسح القطع القديمة للمشروع
    if process_request.do_reset == 1:
        _ = await data_chunk_model.delete_chunks_by_project_id(project_id=project.id)

    # 7. تحويل الـ Chunks إلى كائنات DataChunk متوافقة مع الـ Schema
    data_chunks = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i + 1,
            chunk_project_id=project.id
        )
        for i, chunk in enumerate(file_chunks)
    ]

    # 8. حفظ القطع النصية في الداتابيز بنظام الـ Bulk Write
    no_records = await data_chunk_model.insert_many_chunks(chunks=data_chunks)

    # 9. الرد بنجاح المعالجة مع عدد الـ Chunks التي تم حفظها فعلياً
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records
        }
    )
