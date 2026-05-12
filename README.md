# VeggiClassify

`VeggiClassify` là một project Django demo cho bài toán phân loại rau củ bằng ảnh đầu vào. Project tách riêng phần web và phần machine learning để dễ đọc, dễ bảo trì và thuận tiện cho việc học tập.

## Mục tiêu

- Upload ảnh rau củ trên web và trả về kết quả phân loại.
- Giữ flow Django đơn giản: nhận ảnh, gọi `ml.predictor.predict(image_path)`, render kết quả.
- Đặt toàn bộ logic machine learning trong package `ml/`, không trộn vào Django app.

## Cấu trúc chính

- `config/`: cấu hình trung tâm của Django.
- `apps/pages/`: các trang giới thiệu như home, pipeline, dataset.
- `apps/classifier/`: upload ảnh, gọi ML, hiển thị kết quả.
- `ml/`: pipeline machine learning, preprocessing, feature extraction, load model, predictor, script train.
- `ml/train_model.py`: script train `VegetableGMMModel` và lưu artifact.
- `ml_models/vegetable_model.pkl`: artifact model đã train để predictor sử dụng.
- `ml_models/vegetable_model_report.json`: báo cáo sau khi train.
- `templates/`, `static/`, `media/`: giao diện, tài nguyên tĩnh và file upload.

## Chạy project

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python ml/train_model.py
python manage.py migrate
python manage.py runserver
```

Sau khi train thành công, web sẽ dùng `ml_models/vegetable_model.pkl` để dự đoán. Nếu file này còn là placeholder hoặc chưa được tạo đúng cách, predictor sẽ báo lỗi rõ ràng.

## Dataset và label

- Dataset mặc định nằm ở `d:\Study\ML\code\dataset`.
- Cấu trúc gồm 3 split: `train`, `validation`, `test`.
- Internal label lấy trực tiếp từ tên thư mục con trong `dataset/train`.
- Tên hiển thị tiếng Việt được map trong `ml/label_mapping.py`.

## Flow ngắn gọn

```text
Người dùng upload ảnh
    -> apps/classifier/services.py lưu ảnh vào media/uploads/
    -> ml.predictor.predict(image_path)
    -> predictor load VegetableGMMModel từ ml_models/vegetable_model.pkl
    -> model.predict(image_path) trả kết quả
    -> Django render lên giao diện classify/result
```

## Tài liệu

- `README.md`: bắt đầu nhanh.
- `WALKTHROUGH.md`: toàn cảnh project Django + ML.
- `ML_WALKTHROUGH.md`: riêng phần machine learning, train, label, artifact và predict flow.
