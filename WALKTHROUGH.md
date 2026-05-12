# WALKTHROUGH - Hướng Dẫn Hiểu Project VeggiClassify

## 1. Project này là gì?

VeggiClassify là một web Django dùng để minh họa bài toán phân loại rau củ bằng ảnh đầu vào. Điểm quan trọng của project là phần giao diện web và phần machine learning được tách trách nhiệm rõ ràng:

- Django lo giao diện, form upload, điều hướng trang và render kết quả.
- Package `ml/` lo preprocessing, feature extraction, train model, load model và dự đoán.

Nhờ cách tách này, người học có thể đọc riêng phần web hoặc phần machine learning mà không bị lẫn logic.

## 2. Luồng hoạt động tổng quát

Flow hiện tại của project:

```text
Người dùng mở trang /classify/
    ↓
Tải lên ảnh rau củ
    ↓
Django nhận request POST
    ↓
apps/classifier/services.py lưu ảnh vào media/uploads/
    ↓
services.py gọi ml.predictor.predict(image_path)
    ↓
predictor load VegetableGMMModel từ ml_models/vegetable_model.pkl
    ↓
model.predict(image_path) trả về dictionary kết quả
    ↓
Django chuẩn hóa dữ liệu hiển thị
    ↓
Render kết quả ngay trên trang classify và lưu session cho trang result
```

Nói ngắn gọn:

```text
Web Django nhận ảnh -> gọi predict(image_path) -> ML trả kết quả -> giao diện hiển thị lại
```

## 3. Cây thư mục quan trọng

```text
vegetable_classifier_web/
├── config/
├── apps/
│   ├── pages/
│   └── classifier/
├── ml/
├── ml_models/
├── templates/
├── static/
├── media/
├── manage.py
├── requirements.txt
├── README.md
├── WALKTHROUGH.md
└── ML_WALKTHROUGH.md
```

Giải thích nhanh:

- `config/`: cấu hình Django.
- `apps/pages/`: các trang giới thiệu, pipeline, dataset.
- `apps/classifier/`: upload ảnh và hiển thị kết quả phân loại.
- `ml/`: toàn bộ logic machine learning.
- `ml_models/`: nơi lưu artifact model sau train.
- `media/uploads/`: ảnh người dùng upload.

## 4. Vai trò của app `pages`

App `pages` chịu trách nhiệm cho các trang nội dung:

- `home`
- `about`
- `pipeline`
- `dataset`

File `apps/pages/views.py` chuẩn bị context cho các trang này. Điểm đáng chú ý trong project hiện tại:

- Trang `dataset` không dùng list cứng nữa.
- Dữ liệu label và số lượng lớp được lấy từ dataset thật.
- Tên hiển thị trên UI là tiếng Việt thông qua `ml/label_mapping.py`.

## 5. Vai trò của app `classifier`

App `classifier` là nơi nối web với machine learning.

### `apps/classifier/views.py`

- Render form upload ở `classify_view()`.
- Gọi `classify_uploaded_image()` khi người dùng submit ảnh.
- Đưa danh sách rau hỗ trợ lên UI từ `get_dataset_label_items()`.

### `apps/classifier/services.py`

Đây là lớp trung gian giữa Django và ML:

1. Lưu ảnh vào `media/uploads/`
2. Gọi `ml.predictor.predict(image_path)`
3. Chuẩn hóa output để giao diện dùng được:
   - `image_url`
   - `confidence_percent`
   - `processing_time`
   - `model_name`

Nhờ vậy, phần view Django không cần biết chi tiết bên trong model.

## 6. Vai trò của package `ml/`

Package `ml/` là phần machine learning độc lập.

Các file chính:

- `ml/config/config.json`: cấu hình feature, transform, GMM, Mahalanobis.
- `ml/helper.py`: scan dataset, load config, helper GMM và Mahalanobis.
- `ml/preprocessing.py`: đọc ảnh, resize hoặc letterbox.
- `ml/feature_extraction.py`: trích đặc trưng HSV + LBP và transform feature.
- `ml/model.py`: class `VegetableGMMModel` với `train()`, `evaluate()`, `predict()`.
- `ml/model_loader.py`: tạo model từ config và load model đã train từ `ml_models/vegetable_model.pkl`.
- `ml/predictor.py`: public entrypoint `predict(image_path)` mà Django gọi.
- `ml/train_model.py`: script train model và lưu artifact.
- `ml/label_mapping.py`: map label nội bộ sang tên tiếng Việt.

Chi tiết sâu hơn về phần này nằm trong [ML_WALKTHROUGH.md](ML_WALKTHROUGH.md).

## 7. Artifact trong `ml_models/`

Thư mục `ml_models/` hiện dùng các file chính:

- `vegetable_model.pkl`: artifact chuẩn để predictor load và suy luận.
- `vegetable_model_report.json`: báo cáo sau khi train.

Luồng đúng là:

```text
python ml/train_model.py
    -> tạo vegetable_model.pkl
    -> tạo vegetable_model_report.json
    -> predictor dùng lại vegetable_model.pkl
```

Nếu `vegetable_model.pkl` còn là placeholder, rỗng hoặc không phải `VegetableGMMModel` hợp lệ, predictor sẽ fail-fast với message rõ ràng.

## 8. Dataset và label

Dataset mặc định của project nằm ngoài Django root:

```text
d:\Study\ML\code\dataset
```

Nó gồm 3 split:

- `train`
- `validation`
- `test`

Internal label của model lấy trực tiếp từ tên thư mục con trong `dataset/train`. UI không dùng tên tiếng Anh này để hiển thị trực tiếp mà map sang tiếng Việt qua `ml/label_mapping.py`.

Điều này giúp:

- ML giữ label ổn định theo dataset thật
- UI hiển thị thân thiện bằng tiếng Việt
- Trang `dataset` và trang `classify` bám đúng dữ liệu đang train

## 9. Train model trong project hiện tại

Project đã có sẵn script train:

```bash
python ml/train_model.py
```

Script này sẽ:

1. Đọc dataset root
2. Kiểm tra label mapping tiếng Việt
3. Quét dữ liệu bằng `scan_dataset()`
4. Tạo `VegetableGMMModel` từ `config.json`
5. Train trên split `train`
6. Dùng `validation` để hỗ trợ Mahalanobis threshold nếu config yêu cầu
7. Evaluate trên `test` nếu có
8. Lưu model và report vào `ml_models/`

Các tham số CLI chính:

- `--dataset-root`
- `--config`
- `--output-model`
- `--output-report`

## 10. Predict trong project hiện tại

Sau khi đã có artifact train đúng:

1. Django gọi `ml.predictor.predict(image_path)`
2. Predictor dùng `load_trained_model()`
3. Loader load `vegetable_model.pkl`
4. Model chạy `predict(image_path)`
5. Predictor chuẩn hóa output:
   - `label`
   - `label_vi`
   - `confidence`
   - metadata khác nếu có

Đây là contract quan trọng vì Django đang phụ thuộc vào nó. Nếu sửa model/predictor sau này, nên giữ nguyên format output này để không làm vỡ phần web.

## 11. Các tài liệu nên đọc tiếp

- [README.md](README.md): bắt đầu nhanh, cách chạy project.
- [ML_WALKTHROUGH.md](ML_WALKTHROUGH.md): riêng phần machine learning, training, artifact, label và flow predict.

## 12. Khi muốn sửa project thì nên bắt đầu từ đâu?

Nếu muốn sửa giao diện:

- `apps/pages/templates/pages/`
- `apps/classifier/templates/classifier/`
- `templates/components/`
- `static/css/`

Nếu muốn sửa machine learning:

- `ml/train_model.py`
- `ml/model.py`
- `ml/feature_extraction.py`
- `ml/helper.py`
- `ml/predictor.py`
- `ml/model_loader.py`
- `ml/label_mapping.py`

Nếu muốn sửa flow nối giữa web và ML:

- `apps/classifier/services.py`
- `apps/classifier/views.py`

## 13. Kết luận

Project hiện tại đã chuyển sang flow machine learning thật:

- train model bằng script riêng
- lưu artifact vào `ml_models/`
- predictor load model đã train
- Django chỉ đóng vai trò gọi predictor và hiển thị kết quả

Đó là điểm quan trọng nhất cần nhớ khi đọc project ở phiên bản hiện tại.
