# VeggiClassify

`VeggiClassify` la mot project Django demo cho mon hoc Machine Learning, duoc thiet ke de tach ro phan web va phan machine learning.

## Muc tieu

- Web demo phan loai rau cu bang anh upload.
- Cau truc de doc, de mo rong cho sinh vien moi hoc Django.
- App Django chi phu trach giao dien, upload anh va goi service.
- Machine learning duoc dat trong package `ml/`, khong tach thanh Django app rieng.

## Cau truc chinh

- `config/`: cau hinh trung tam cua Django.
- `apps/pages/`: cac trang thong tin nhu home, about, pipeline, dataset.
- `apps/classifier/`: upload anh, goi ML, hien thi ket qua.
- `ml/`: code machine learning doc lap, cung cap ham `predict(image_path)`.
- `ml_models/`: noi luu model da train (`.pkl`).
- `templates/components/`: cac khoi giao dien tai su dung.
- `static/css/`: tach CSS theo vai tro de de hoc va de sua.
- `static/js/`: preview anh upload, active navbar va tuong tac nho.
- `media/uploads/`: noi luu anh nguoi dung tai len.

## Chay project

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Ghi chu

- `apps/__init__.py` duoc them de viec import `apps.pages` va `apps.classifier` ro rang hon cho nguoi moi hoc.
- `ml/predictor.py` hien dang la ham gia lap, tra ve du lieu mau de demo luong xu ly.
