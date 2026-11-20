import os

def test_app_sanity():
    """اختبار أولي سريع للتأكد من أن بيئة بايثون تعمل بنجاح"""
    project_name = "mini-RAG"
    assert project_name == "mini-RAG"
    assert 10 * 2 == 20

def test_project_files_exist():
    """التأكد من أن ملفات المشروع الأساسية موجودة وغير مفقودة"""
    assert os.path.exists("src")
    assert os.path.exists("requirements.txt")
    assert os.path.exists("README.md")
