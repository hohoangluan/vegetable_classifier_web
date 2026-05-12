# ML_WALKTHROUGH - Hướng Dẫn Phần Machine Learning

## 1. Mục tiêu của package `ml/`

Package `ml/` chứa toàn bộ logic machine learning của project. Django không train model, không trực tiếp xử lý feature và cũng không biết chi tiết nội bộ của GMM. Tầng web chỉ làm một việc đơn giản:

```python
from ml.predictor import predict
predict(image_path)
```

Nhờ cách này:

- web dễ đọc hơn
- ML dễ thay đổi hơn
- predictor trở thành contract ổn định giữa Django và model

## 2. Flow machine learning hiện tại

### Flow train

```text
dataset/
    -> helper.scan_dataset()
    -> DataFrame train / validation / test
    -> create_model_from_json()
    -> VegetableGMMModel.train()
    -> VegetableGMMModel.evaluate() nếu có test split
    -> joblib.dump(model, ml_models/vegetable_model.pkl)
    -> lưu ml_models/vegetable_model_report.json
```

### Flow predict

```text
Ảnh người dùng upload
    -> apps/classifier/services.py nhận đường dẫn ảnh
    -> ml.predictor.predict(image_path)
    -> load_trained_model()
    -> VegetableGMMModel.predict(image_path)
    -> predictor chuẩn hóa output
    -> Django render label_vi + confidence lên UI
```

## 3. Các file chính trong `ml/`

### `ml/config/config.json`

Chứa cấu hình cho pipeline ML:

- `feature`: resize, mode preprocess, số bin HSV, tham số LBP
- `transform`: có dùng scaler và LDA hay không
- `gmm`: tham số cho Gaussian Mixture Model
- `mahalanobis`: cách tính threshold OOD

File này phải là strict JSON, không được để comment trực tiếp trong file.

### `ml/helper.py`

Vai trò:

- `scan_dataset()` quét dataset và trả về DataFrame gồm `split`, `class`, `path`
- `load_config()` đọc và validate config
- nhóm hàm GMM:
  - `fit_gmm_classifier()`
  - `predict_gmm_proba()`
  - `predict_gmm_class()`
- nhóm hàm Mahalanobis:
  - `compute_mahalanobis_batch()`
  - `compute_mahalanobis_threshold()`

### `ml/preprocessing.py`

Vai trò:

- `read_image()` đọc ảnh từ path
- `preprocess_image()` resize hoặc letterbox
- `prepare_image()` là entrypoint gọn cho bước chuẩn hóa đầu vào

### `ml/feature_extraction.py`

Đây là nơi biến ảnh thành vector feature.

Pipeline hiện tại:

1. Đọc ảnh
2. Preprocess về kích thước theo config
3. Trích histogram HSV
4. Trích histogram LBP
5. Ghép 2 phần thành vector feature cuối cùng

Ngoài ra file này còn có:

- `build_feature_matrix()` để tạo ma trận feature từ DataFrame
- `fit_feature_transformer()` để fit scaler/LDA
- `transform_features()` để transform feature khi predict/evaluate

### `ml/model.py`

Chứa class `VegetableGMMModel`, là lõi của mô hình.

Ba API chính:

- `train()`
- `evaluate()`
- `predict()`

`predict()` trả về metadata quan trọng như:

- `prediction`
- `class_prediction`
- `confidence`
- `is_ood`
- `mahalanobis`
- `threshold_maha`
- `proba`

### `ml/model_loader.py`

Vai trò:

- `create_model_from_json()` tạo một `VegetableGMMModel` chưa train từ config
- `load_trained_model()` load artifact đã train từ `ml_models/vegetable_model.pkl`

Artifact chuẩn bây giờ là một object `VegetableGMMModel` hoàn chỉnh, không phải ghép model/scaler/encoder rời như flow cũ.

### `ml/predictor.py`

Đây là public entrypoint mà Django gọi.

Nó làm các bước:

1. Kiểm tra file ảnh tồn tại
2. Gọi `load_trained_model()`
3. Gọi `model.predict(image_path)`
4. Chuẩn hóa output thành dict ổn định cho web

Output tối thiểu mà Django dùng:

- `label`
- `label_vi`
- `confidence`

### `ml/train_model.py`

Đây là script train model cho project hiện tại.

Nó chịu trách nhiệm:

- parse CLI args
- đọc dataset
- validate label mapping
- train model
- evaluate nếu có test split
- lưu `vegetable_model.pkl`
- lưu `vegetable_model_report.json`

### `ml/label_mapping.py`

Chứa mapping từ internal label sang tên tiếng Việt hiển thị trên UI.

Internal label lấy từ tên thư mục dataset, ví dụ:

- `Capsicum`
- `Carrot`
- `Tomato`

Tên hiển thị:

- `Ớt chuông`
- `Cà rốt`
- `Cà chua`

## 4. Dataset và label

Dataset mặc định của project:

```text
d:\Study\ML\code\dataset
```

Ba split:

- `train`
- `validation`
- `test`

### Quy tắc label

- Internal label = tên thư mục con trong `dataset/train`
- Tên tiếng Việt = `get_vietnamese_label(internal_label)`

### 15 lớp hiện có

| Internal label | Tên hiển thị |
|---|---|
| `Bean` | Đậu que |
| `Bitter_Gourd` | Khổ qua |
| `Bottle_Gourd` | Bầu |
| `Brinjal` | Cà tím |
| `Broccoli` | Súp lơ xanh |
| `Cabbage` | Bắp cải |
| `Capsicum` | Ớt chuông |
| `Carrot` | Cà rốt |
| `Cauliflower` | Súp lơ trắng |
| `Cucumber` | Dưa chuột |
| `Papaya` | Đu đủ |
| `Potato` | Khoai tây |
| `Pumpkin` | Bí đỏ |
| `Radish` | Củ cải |
| `Tomato` | Cà chua |

Lưu ý:

- Nếu thêm thư mục class mới vào `dataset/train` mà chưa bổ sung mapping tiếng Việt, script train sẽ dừng và báo lỗi.

## 5. Cách train model

Lệnh mặc định:

```bash
python ml/train_model.py
```

### Các tham số CLI

```bash
python ml/train_model.py ^
  --dataset-root d:\Study\ML\code\dataset ^
  --config ml/config/config.json ^
  --output-model ml_models/vegetable_model.pkl ^
  --output-report ml_models/vegetable_model_report.json
```

Ý nghĩa:

- `--dataset-root`: đường dẫn dataset gồm `train`, `validation`, `test`
- `--config`: config pipeline ML
- `--output-model`: nơi lưu model đã train
- `--output-report`: nơi lưu báo cáo train

### Flow train chi tiết

1. Validate dependency `joblib`
2. Validate `dataset-root`
3. Đọc class names từ `dataset/train`
4. Kiểm tra đủ mapping tiếng Việt
5. `scan_dataset()` để gom dữ liệu thành DataFrame
6. Tách `train_df`, `validation_df`, `test_df`
7. `create_model_from_json()`
8. `model.train(train_df, val_df=validation_df)`
9. Nếu có test split thì `model.evaluate(test_df)`
10. `joblib.dump(model, output_model_path)`
11. Load lại model vừa lưu để verify
12. Ghi report JSON

### Output sau train

- `ml_models/vegetable_model.pkl`
- `ml_models/vegetable_model_report.json`

## 6. `vegetable_model_report.json` dùng để làm gì?

Đây là báo cáo gọn sau train, giúp xem nhanh:

- dataset root
- config path
- model path
- class names
- tên hiển thị tiếng Việt
- số lượng mẫu ở từng split
- trạng thái Mahalanobis
- metric evaluate trên test split nếu có

File này không phải artifact dùng để predict; predictor chỉ cần `vegetable_model.pkl`.

## 7. Cách predict hoạt động

### Từ phía Django

`apps/classifier/services.py` làm 3 việc:

1. Lưu ảnh upload vào `media/uploads/`
2. Gọi `predict(image_path)`
3. Chuẩn hóa thêm thông tin hiển thị

### Từ phía ML

`ml.predictor.predict(image_path)`:

1. Kiểm tra ảnh tồn tại
2. `load_trained_model()`
3. `model.predict(image_path)`
4. Map `label` sang `label_vi`
5. Trả dict kết quả cho Django

Contract tối thiểu:

```python
{
    "label": "...",
    "label_vi": "...",
    "confidence": 0.93,
}
```

Có thể kèm thêm:

- `is_ood`
- `mahalanobis`
- `threshold_maha`
- `class_prediction`
- `class_prediction_vi`
- `proba`
- `model_name`

## 8. Các lỗi thường gặp

### Thiếu dependency

Ví dụ:

- `joblib`
- `scikit-learn`
- `opencv-python`
- `numpy`
- `pandas`

Cách xử lý:

```bash
pip install -r requirements.txt
```

### `vegetable_model.pkl` còn placeholder hoặc rỗng

Triệu chứng:

- predictor báo không load được model
- hoặc báo artifact rỗng / placeholder

Cách xử lý:

- chạy lại `python ml/train_model.py`

### `config.json` không phải strict JSON

Triệu chứng:

- `load_config()` báo lỗi parse JSON

Cách xử lý:

- xóa comment hoặc dữ liệu thừa khỏi file JSON

### Sai dataset root

Triệu chứng:

- train script báo không tìm thấy dataset root

Cách xử lý:

- kiểm tra lại `--dataset-root`

### Class mới chưa có mapping tiếng Việt

Triệu chứng:

- train script dừng ở bước check label mapping

Cách xử lý:

- cập nhật `ml/label_mapping.py`

## 9. Nếu muốn thay đổi model thì xem file nào trước?

Thứ tự nên đọc:

1. `ml/config/config.json`
2. `ml/feature_extraction.py`
3. `ml/model.py`
4. `ml/train_model.py`
5. `ml/label_mapping.py`
6. `ml/model_loader.py`
7. `ml/predictor.py`

Nguyên tắc quan trọng:

- Có thể đổi kiến trúc model bên trong
- nhưng nên giữ contract của `predict()` ổn định để Django không phải sửa nhiều

## 10. Quan hệ giữa ML và UI

UI hiện bám theo dataset thật:

- danh sách rau hỗ trợ trên trang classify lấy từ `label_mapping.py` + tên thư mục dataset
- trang dataset cũng dùng dữ liệu động từ dataset thật
- kết quả hiển thị là tên tiếng Việt, không hiển thị raw folder name cho người dùng cuối

Điều này có nghĩa là khi dataset thay đổi:

- bạn phải cập nhật mapping
- nên train lại model
- nên kiểm tra lại trang dataset/classify để bảo đảm UI còn đồng bộ

## 11. Kết luận

Phần machine learning của project hiện tại đã có đầy đủ các mảnh chính:

- preprocessing
- feature extraction
- GMM model
- Mahalanobis OOD
- train script
- loader
- predictor
- report

Nếu nhớ đúng ba điểm sau thì sẽ không bị lạc flow:

1. Train bằng `python ml/train_model.py`
2. Predict qua `ml.predictor.predict(image_path)`
3. Artifact chính là `ml_models/vegetable_model.pkl`
