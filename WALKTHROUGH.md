# WALKTHROUGH - Hướng Dẫn Hiểu Project VeggiClassify

## 1. Project này là gì?

VeggiClassify là một web demo dùng Django để minh họa bài toán phân loại rau củ bằng ảnh đầu vào.

Ý tưởng rất đơn giản:

- Người dùng mở website.
- Người dùng tải lên một ảnh rau củ.
- Django nhận ảnh đó.
- Django gọi sang module machine learning.
- Module ML trả về kết quả dự đoán.
- Website hiển thị lại kết quả trên giao diện.

Project này phù hợp cho sinh viên học:

- Django cơ bản
- Cách tổ chức project web rõ ràng
- Cách tách phần web và phần machine learning
- Cách gọi model ML từ Django

Điểm quan trọng của project là: phần Django và phần ML được tách trách nhiệm rõ ràng để dễ đọc, dễ sửa, dễ mở rộng.

## 2. Tổng quan luồng hoạt động

Sơ đồ luồng tổng quát:

```text
Người dùng mở website
    ↓
Vào trang /classify/
    ↓
Upload ảnh rau củ
    ↓
Django nhận request POST
    ↓
Form kiểm tra dữ liệu ảnh
    ↓
Ảnh được lưu vào media/uploads/
    ↓
apps/classifier/services.py gọi ml/predictor.py
    ↓
predict(image_path) xử lý ảnh và dự đoán
    ↓
ML trả về dictionary kết quả
    ↓
Django nhận output
    ↓
Render ra giao diện result.html
```

Nếu nói ngắn gọn hơn thì project hoạt động theo công thức:

```text
Web Django nhận ảnh -> gọi hàm predict() -> nhận kết quả -> hiển thị cho người dùng
```

## 3. Cây thư mục tổng quan

Project chính có cấu trúc như sau:

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
└── WALKTHROUGH.md
```

Giải thích ngắn gọn:

- `config/`: nơi chứa cấu hình chung của Django project.
- `apps/`: nơi chứa các Django app.
- `apps/pages/`: các trang thông tin như home, about, pipeline, dataset.
- `apps/classifier/`: phần upload ảnh và gọi module ML để phân loại.
- `ml/`: package Python chứa logic machine learning.
- `ml_models/`: nơi lưu file model đã train.
- `templates/`: HTML dùng chung cho toàn project.
- `static/`: CSS, JS, hình ảnh giao diện.
- `media/`: nơi lưu file do người dùng upload.
- `manage.py`: file lệnh chính để chạy Django.
- `requirements.txt`: danh sách thư viện cần cài.
- `README.md`: mô tả nhanh project.
- `WALKTHROUGH.md`: file hướng dẫn chi tiết này.

## 4. Vai trò của thư mục config/

Thư mục `config/` là trung tâm cấu hình của Django project.

Các file quan trọng:

- `config/settings.py`: cấu hình project, app, template, static, media, database.
- `config/urls.py`: nơi nối URL tổng cho toàn bộ website.
- `config/asgi.py`: dùng khi chạy hoặc deploy theo chuẩn ASGI.
- `config/wsgi.py`: dùng khi chạy hoặc deploy theo chuẩn WSGI.

### `config/settings.py` dùng để làm gì?

Đây là file mà người mới sẽ gặp rất nhiều khi học Django. Trong project này, file đó đang đảm nhiệm:

- Khai báo `INSTALLED_APPS`
- Cấu hình thư mục `templates/`
- Cấu hình `STATIC_URL`, `STATICFILES_DIRS`
- Cấu hình `MEDIA_URL`, `MEDIA_ROOT`
- Cấu hình database SQLite

Ví dụ: vì app nằm trong thư mục `apps/`, project đang import theo dạng:

```python
"apps.pages.apps.PagesConfig"
"apps.classifier.apps.ClassifierConfig"
```

Nhờ vậy Django biết cần nạp app nào khi chạy.

### `config/urls.py` dùng để làm gì?

Đây là nơi gắn các app vào project.

Ví dụ trong project này:

- URL gốc `/` sẽ đi vào app `pages`
- URL `/classify/` sẽ đi vào app `classifier`

Nói dễ hiểu:

```text
config/urls.py giống như bảng điều phối giao thông của cả website
```

### `asgi.py` và `wsgi.py`

Người mới học chưa cần chỉnh nhiều hai file này.

Bạn chỉ cần nhớ:

- Chúng phục vụ việc chạy và deploy project.
- Thường để nguyên mặc định.
- Chỉ sửa khi bạn thật sự hiểu quá trình triển khai ứng dụng.

## 5. Vai trò của app pages/

App `pages` dùng cho các trang thông tin.

Điểm quan trọng:

- App này không xử lý machine learning.
- App này chủ yếu render các trang để giới thiệu project và giải thích pipeline.

Các file chính:

- `apps/pages/views.py`: chứa các hàm render trang.
- `apps/pages/urls.py`: định nghĩa URL cho app `pages`.
- `apps/pages/templates/pages/home.html`: trang chủ.
- `apps/pages/templates/pages/about.html`: trang giới thiệu.
- `apps/pages/templates/pages/pipeline.html`: trang mô tả pipeline.
- `apps/pages/templates/pages/dataset.html`: trang mô tả dataset.

### `pages/views.py` làm gì?

File này chứa các hàm như:

- `home_view()`
- `about_view()`
- `pipeline_view()`
- `dataset_view()`

Các hàm này thường chỉ làm việc nhẹ:

- Nhận request
- Tạo context nếu cần
- Render template HTML

Ví dụ tư duy:

```text
Người dùng vào /about/ -> Django gọi about_view() -> about_view() render about.html
```

### Nếu muốn sửa nội dung trang giới thiệu thì chỉnh file nào?

Bạn thường sẽ chỉnh:

- `apps/pages/templates/pages/about.html`

Nếu muốn sửa dữ liệu context được truyền sang template thì chỉnh thêm:

- `apps/pages/views.py`

### Nếu muốn thêm một trang mới trong app pages thì sửa gì?

Bạn cần làm 4 việc:

1. Tạo file template mới trong `apps/pages/templates/pages/`
2. Thêm view mới trong `apps/pages/views.py`
3. Thêm URL mới trong `apps/pages/urls.py`
4. Nếu muốn hiện trên menu thì thêm link trong `templates/components/navbar.html`

## 6. Vai trò của app classifier/

App `classifier` là phần quan trọng nhất của project, vì đây là nơi xử lý chức năng phân loại ảnh.

App này phụ trách:

- Hiển thị form upload ảnh
- Nhận ảnh từ người dùng
- Gọi service trung gian
- Service gọi module ML
- Nhận kết quả và hiển thị lên giao diện

Các file chính:

- `apps/classifier/views.py`: nhận request, kiểm tra form, render trang.
- `apps/classifier/forms.py`: định nghĩa form upload ảnh.
- `apps/classifier/models.py`: nơi có thể tạo model database nếu muốn lưu lịch sử sau này.
- `apps/classifier/services.py`: xử lý logic trung gian, gọi ML.
- `apps/classifier/urls.py`: định nghĩa URL của phần classify.
- `apps/classifier/templates/classifier/classify.html`: trang upload ảnh.
- `apps/classifier/templates/classifier/result.html`: trang hiển thị kết quả.

### `classifier/views.py` làm gì?

Trong project này, `views.py` chủ yếu làm đúng tinh thần Django:

- Nhận request GET hoặc POST
- Tạo form
- Kiểm tra form hợp lệ hay không
- Nếu hợp lệ thì gọi `services.py`
- Lấy kết quả từ service
- Render giao diện cho người dùng

Điều rất quan trọng:

```text
Không nên viết toàn bộ logic machine learning trong views.py
```

Lý do:

- `views.py` sẽ rất dài và khó đọc
- Khó tái sử dụng code
- Khó bảo trì khi thay model
- Trộn lẫn trách nhiệm của web và ML

### `classifier/forms.py` làm gì?

File này định nghĩa form upload ảnh.

Form giúp:

- Kiểm tra request có file ảnh hay không
- Quản lý trường nhập liệu sạch hơn
- Giúp giao diện render form dễ hơn

### `classifier/models.py` làm gì?

Hiện tại file này đang để dạng khung cơ bản.

Trong tương lai, bạn có thể dùng file này để tạo các model database như:

- lịch sử phân loại
- thông tin ảnh đã upload
- thời gian dự đoán
- người dùng nào đã dự đoán

Nếu project chỉ là demo đơn giản thì chưa nhất thiết phải dùng database cho phần classifier.

### `classifier/services.py` làm gì?

Đây là file rất đáng chú ý.

Nhiệm vụ của `services.py`:

- Lưu ảnh upload vào `media/uploads/`
- Tạo đường dẫn của ảnh
- Gọi `ml.predictor.predict(image_path)`
- Nhận kết quả từ ML
- Trả kết quả lại cho view

Nói dễ hiểu:

```text
services.py là chiếc cầu nối giữa Django và machine learning
```

### Nguyên tắc quan trọng của app classifier

- `views.py` chỉ nên điều phối request/response.
- `services.py` nên chứa logic trung gian.
- `ml/` mới là nơi xử lý machine learning.

Đây là cách tổ chức rất tốt cho project học tập lẫn project thật.

## 7. Vai trò của thư mục ml/

Thư mục `ml/` không phải là Django app.

Đây chỉ là một Python package bình thường, dùng để chứa logic machine learning độc lập.

Ý tưởng quan trọng:

```text
Django không cần biết bên trong model ML phức tạp ra sao.
Django chỉ cần gọi predict(image_path) và nhận output.
```

Các file chính:

- `ml/predictor.py`: chứa hàm `predict(image_path)`, đây là đầu vào chính mà Django gọi.
- `ml/preprocessing.py`: xử lý ảnh đầu vào, ví dụ đọc ảnh, resize, normalize.
- `ml/feature_extraction.py`: trích xuất đặc trưng nếu dùng HOG, HSV, LBP hoặc đặc trưng thủ công.
- `ml/model_loader.py`: load model, scaler, label encoder.
- `ml/label_mapping.py`: ánh xạ nhãn từ tiếng Anh sang tiếng Việt.

### `ml/predictor.py` là file quan trọng nhất

Trong project hiện tại, Django đang gọi:

```python
from ml.predictor import predict
```

Sau đó service sẽ chạy:

```python
predict(image_path)
```

Hiện tại `predict()` đang là hàm giả lập để demo luồng hoạt động.

Ví dụ output mẫu:

```python
{
    "label": "carrot",
    "label_vi": "Cà rốt",
    "confidence": 0.92
}
```

### `ml/preprocessing.py`

Nếu dùng model thật, đây là nơi bạn có thể viết các bước như:

- đọc ảnh từ đường dẫn
- resize ảnh về kích thước model yêu cầu
- chuyển màu RGB/BGR
- normalize pixel
- chuyển ảnh thành tensor hoặc vector

### `ml/feature_extraction.py`

Nếu bạn dùng machine learning kiểu truyền thống thay vì deep learning, đây là nơi có thể trích xuất:

- HOG
- HSV histogram
- LBP
- color features
- shape features

Nếu sau này bạn dùng CNN end-to-end thì file này có thể đơn giản hơn hoặc chỉ làm bước trung gian.

### `ml/model_loader.py`

Đây là nơi tập trung việc load tài nguyên ML.

Ví dụ:

- model chính
- scaler
- label encoder

Tách riêng việc load model ra file này giúp:

- code gọn hơn
- dễ thay model
- dễ cache model
- dễ debug lỗi load file

### `ml/label_mapping.py`

File này giúp ánh xạ:

- `carrot` -> `Cà rốt`
- `potato` -> `Khoai tây`
- `tomato` -> `Cà chua`

Nhờ vậy giao diện có thể hiển thị thân thiện hơn thay vì chỉ dùng label tiếng Anh.

## 8. Vai trò của thư mục ml_models/

Thư mục `ml_models/` dùng để chứa các file model đã train.

Hiện tại project đang chuẩn bị sẵn chỗ cho:

- `vegetable_model.pkl`
- `scaler.pkl`
- `label_encoder.pkl`

Nếu bạn dùng TensorFlow hoặc Keras thì có thể thay bằng:

- `vegetable_model.h5`
- `vegetable_model.keras`

Nếu bạn dùng PyTorch thì có thể thay bằng:

- `vegetable_model.pt`
- `vegetable_model.pth`

### Khi thay model thật thì thường phải chỉnh các file nào?

- `ml/model_loader.py`
- `ml/preprocessing.py`
- `ml/predictor.py`

Lý do:

- model mới có cách load khác
- model mới có input khác
- model mới có cách trả nhãn và độ tin cậy khác

## 9. Vai trò của templates/

Thư mục `templates/` chứa layout và component dùng chung cho toàn project.

Các file chính:

- `templates/base.html`: layout gốc của toàn bộ website.
- `templates/layouts/main_layout.html`: layout phụ nếu muốn tái sử dụng thêm.
- `templates/components/navbar.html`: thanh điều hướng.
- `templates/components/footer.html`: footer.
- `templates/components/page_header.html`: tiêu đề đầu trang.
- `templates/components/feature_card.html`: card tính năng.
- `templates/components/stat_card.html`: card thống kê.
- `templates/components/pipeline_step.html`: card từng bước pipeline.
- `templates/components/upload_box.html`: khung upload ảnh.
- `templates/components/result_panel.html`: khung hiển thị kết quả.
- `templates/components/dataset_bar.html`: thanh hiển thị phân bố dữ liệu.

### `base.html` có vai trò gì?

Đây là khung HTML chung cho các trang.

Nó thường chứa:

- thẻ `<head>`
- link CSS
- navbar
- footer
- block nội dung như `{% block content %}`

Nhờ `base.html`, các trang con chỉ cần tập trung vào phần nội dung chính.

### Cách chỉnh navbar

Nếu muốn sửa menu, tên web, thêm link:

- Chỉnh `templates/components/navbar.html`

Nếu muốn đổi style navbar:

- Chỉnh `static/css/components.css`

### Cách chỉnh card và tiêu đề trang

Nếu muốn sửa cấu trúc card:

- `templates/components/feature_card.html`
- `templates/components/stat_card.html`
- `templates/components/pipeline_step.html`

Nếu muốn sửa phần header đầu trang:

- `templates/components/page_header.html`

## 10. Vai trò của static/

Thư mục `static/` chứa tài nguyên giao diện.

Đây là nơi bạn sẽ chỉnh nhiều nếu muốn thay đổi giao diện web.

### `static/css/`

Các file chính:

- `static/css/variables.css`: biến màu, font, shadow, bo góc.
- `static/css/base.css`: style nền tảng.
- `static/css/layout.css`: container, grid, khoảng cách, bố cục.
- `static/css/components.css`: style của navbar, card, upload box, button.
- `static/css/pages.css`: style riêng cho từng trang.
- `static/css/responsive.css`: responsive cho mobile và tablet.

### Chỉnh file nào trong các trường hợp hay gặp?

Nếu muốn đổi màu chủ đạo:

- Chỉnh `static/css/variables.css`

Nếu muốn sửa card, navbar, upload box:

- Chỉnh `static/css/components.css`

Nếu muốn sửa layout trang dataset hoặc pipeline:

- Chỉnh `static/css/pages.css`

Nếu muốn sửa cách hiển thị trên điện thoại:

- Chỉnh `static/css/responsive.css`

### `static/js/`

Các file chính:

- `static/js/main.js`: JS chung cho toàn site.
- `static/js/upload_preview.js`: xem trước ảnh trước khi upload.
- `static/js/active_nav.js`: highlight menu hiện tại.

### `static/images/`

Các thư mục con:

- `static/images/logo/`: logo web.
- `static/images/icons/`: icon giao diện.
- `static/images/dataset_samples/`: ảnh minh họa dataset.
- `static/images/pipeline/`: ảnh minh họa pipeline.
- `static/images/ui/`: ảnh placeholder hoặc empty state.

## 11. Vai trò của media/

Thư mục `media/` là nơi chứa file do người dùng upload trong lúc dùng web.

Ở project này, ảnh upload được lưu tại:

- `media/uploads/`

Điểm rất quan trọng cần phân biệt:

- `static/`: file cố định của hệ thống
- `media/`: file phát sinh từ người dùng

Ví dụ:

- logo web nên để trong `static/images/logo/`
- ảnh người dùng vừa upload để dự đoán nên nằm trong `media/uploads/`

## 12. Luồng xử lý phân loại ảnh chi tiết

Phần này đi chậm từng bước để người mới nhìn được “đường đi” của dữ liệu.

### Bước 1: Người dùng vào `/classify/`

URL này được khai báo trong:

- `apps/classifier/urls.py`

### Bước 2: `classify.html` hiển thị form upload ảnh

Template chính là:

- `apps/classifier/templates/classifier/classify.html`

Trong template này có form để chọn file ảnh.

### Bước 3: Người dùng chọn ảnh và submit

Khi người dùng bấm nút gửi:

- trình duyệt gửi request `POST`
- file ảnh đi kèm trong `request.FILES`

### Bước 4: `classifier/views.py` nhận request POST

View phụ trách:

- tạo `ImageUploadForm`
- kiểm tra request có hợp lệ không

### Bước 5: `forms.py` kiểm tra dữ liệu ảnh

`forms.py` giúp đảm bảo:

- trường upload tồn tại
- dữ liệu đi vào đúng kiểu ảnh

### Bước 6: Ảnh được lưu vào `media/uploads/`

Việc này đang được xử lý trong:

- `apps/classifier/services.py`

### Bước 7: `views.py` gọi `classifier/services.py`

View không trực tiếp làm ML.

Thay vào đó:

- view gọi service
- service xử lý bước trung gian

### Bước 8: `services.py` gọi `ml/predictor.py`

Service chạy hàm:

```python
predict(image_path)
```

### Bước 9: `predictor.py` gọi `preprocessing.py`

Nếu dùng model thật, đây là lúc ảnh được:

- đọc
- resize
- normalize
- chuyển về đúng format đầu vào

### Bước 10: `predictor.py` load model từ `ml_models/` và dự đoán

Thông thường:

- `model_loader.py` load model
- `predictor.py` gọi model để dự đoán

### Bước 11: Kết quả trả về dạng dictionary

Ví dụ:

```python
{
    "label": "carrot",
    "label_vi": "Cà rốt",
    "confidence": 0.92
}
```

### Bước 12: Django render kết quả ra giao diện

Project hiện tại đang dùng:

- `result.html`

View sẽ nhận output rồi render lại cho người dùng xem.

## 13. Cách chỉnh sửa giao diện

Đây là phần sinh viên thường đụng vào nhiều nhất.

### Muốn sửa navbar

Chỉnh:

- `templates/components/navbar.html`
- `static/css/components.css`

### Muốn sửa trang chủ

Chỉnh:

- `apps/pages/templates/pages/home.html`

Nếu cần style riêng:

- `static/css/pages.css`

### Muốn sửa trang phân loại

Chỉnh:

- `apps/classifier/templates/classifier/classify.html`
- `templates/components/upload_box.html`
- `templates/components/result_panel.html`

Nếu cần sửa style:

- `static/css/components.css`
- `static/css/pages.css`

### Muốn sửa trang pipeline

Chỉnh:

- `apps/pages/templates/pages/pipeline.html`

Nếu muốn sửa giao diện từng bước:

- `templates/components/pipeline_step.html`

### Muốn sửa trang dataset

Chỉnh:

- `apps/pages/templates/pages/dataset.html`

Nếu muốn đổi card hoặc thanh thống kê:

- `templates/components/stat_card.html`
- `templates/components/dataset_bar.html`

## 14. Cách thêm một trang mới

Ví dụ muốn thêm trang `Contact`.

### Bước 1: Tạo template mới

Tạo file:

```text
apps/pages/templates/pages/contact.html
```

### Bước 2: Thêm view trong `apps/pages/views.py`

```python
from django.shortcuts import render


def contact_view(request):
    return render(request, "pages/contact.html")
```

### Bước 3: Thêm URL trong `apps/pages/urls.py`

```python
path("contact/", views.contact_view, name="contact")
```

### Bước 4: Thêm link trong navbar

Chỉnh:

- `templates/components/navbar.html`

Tóm lại, khi thêm trang mới bạn thường đụng vào:

- template
- view
- url
- navbar

## 15. Cách thay model giả lập bằng model thật

Hiện tại `ml/predictor.py` đang có thể trả kết quả giả lập để minh họa luồng hoạt động.

Muốn thay bằng model thật, bạn có thể làm theo các bước sau.

### Bước 1: Đưa file model đã train vào `ml_models/`

Ví dụ:

- `vegetable_model.pkl`
- `vegetable_model.h5`
- `vegetable_model.pt`

### Bước 2: Chỉnh `ml/model_loader.py`

Ở đây bạn viết code để load:

- model
- scaler
- label encoder

Ví dụ:

- dùng `joblib.load()` cho `.pkl`
- dùng `tensorflow.keras.models.load_model()` cho `.h5`
- dùng `torch.load()` cho `.pt`

### Bước 3: Chỉnh `ml/preprocessing.py`

Bạn phải xử lý ảnh đúng theo yêu cầu model:

- kích thước bao nhiêu
- chuẩn hóa thế nào
- RGB hay BGR
- cần tensor hay vector

### Bước 4: Chỉnh `ml/predictor.py`

Tại đây bạn sẽ:

- gọi `prepare_image()`
- load model bằng `model_loader.py`
- chạy `model.predict()`
- lấy nhãn dự đoán
- đổi sang tiếng Việt nếu cần

### Bước 5: Giữ nguyên format output

Điều rất quan trọng là dù thay model bên trong, đầu ra vẫn nên giữ dạng:

```python
{
    "label": "...",
    "label_vi": "...",
    "confidence": ...
}
```

Lý do:

- Django không phải sửa quá nhiều
- template `result.html` vẫn dùng lại được
- project ổn định hơn

## 16. Cách chạy project local

Các lệnh cơ bản:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Sau đó mở trình duyệt:

```text
http://127.0.0.1:8000/
```

Gợi ý thực tế:

- Nếu project chưa có model database riêng thì `makemigrations` có thể chưa tạo gì mới, điều đó là bình thường.
- `migrate` vẫn nên chạy để Django tạo các bảng hệ thống mặc định.

## 17. Những file người mới thường chỉnh

Đây là nhóm file thân thiện với người mới học và thường là nơi nên bắt đầu.

- `apps/pages/templates/pages/home.html`
- `apps/pages/templates/pages/about.html`
- `apps/pages/templates/pages/pipeline.html`
- `apps/pages/templates/pages/dataset.html`
- `apps/classifier/templates/classifier/classify.html`
- `templates/components/navbar.html`
- `templates/components/upload_box.html`
- `templates/components/result_panel.html`
- `static/css/variables.css`
- `static/css/components.css`
- `static/css/pages.css`
- `ml/predictor.py`
- `ml/preprocessing.py`

Vì sao nên bắt đầu ở đây?

- Dễ thấy kết quả ngay trên giao diện
- Ít rủi ro làm hỏng cấu trúc project
- Giúp hiểu rõ luồng hoạt động hơn

## 18. Những file không nên chỉnh tùy tiện

Người mới không nên sửa lung tung các file sau nếu chưa hiểu rõ:

- `config/settings.py`
- `config/urls.py`
- `manage.py`
- `config/asgi.py`
- `config/wsgi.py`
- các file migration nếu sau này project có tạo migrations

Giải thích:

- `settings.py`: sai một dòng có thể làm project không chạy.
- `urls.py`: sai route có thể làm mất đường dẫn của cả app.
- `manage.py`: gần như không cần sửa.
- `asgi.py`, `wsgi.py`: chủ yếu phục vụ deploy.
- migration files: không nên sửa tay nếu chưa hiểu cách Django quản lý database schema.

## 19. Nguyên tắc thiết kế project

Project này được tổ chức dựa trên một số nguyên tắc rất thực tế.

- Tách Django và ML rõ ràng.
- `views.py` không chứa toàn bộ logic xử lý model.
- `services.py` làm trung gian giữa web và ML.
- `ml/` chỉ tập trung vào xử lý dự đoán.
- `templates/components/` giúp tái sử dụng giao diện.
- `static/css/` được chia nhỏ để dễ chỉnh sửa.
- `media/` chỉ dùng cho file người dùng upload.

Nếu nhớ được các nguyên tắc này, bạn sẽ dễ giữ project sạch khi mở rộng thêm tính năng.

## 20. Tóm tắt cho người mới

Nếu muốn sửa nội dung trang:

- vào `templates`

Nếu muốn sửa giao diện:

- vào `static/css`

Nếu muốn sửa logic upload và predict:

- vào `apps/classifier`

Nếu muốn sửa thuật toán machine learning:

- vào `ml/`

Nếu muốn đổi model:

- vào `ml_models/` và `ml/model_loader.py`

Nếu muốn thêm URL:

- chỉnh `urls.py`

Nếu muốn thêm trang:

- thêm template
- thêm view
- thêm url
- thêm link ở navbar nếu cần

Nếu bạn là người mới, cách học tốt nhất với project này là:

1. Mở `home.html`, `about.html`, `classify.html` để xem phần giao diện.
2. Đọc `apps/classifier/views.py` để hiểu request đi đâu.
3. Đọc `apps/classifier/services.py` để hiểu Django gọi ML thế nào.
4. Đọc `ml/predictor.py` để hiểu đầu ra của model cần có dạng gì.
5. Chỉnh màu trong `static/css/variables.css` để thấy thay đổi giao diện ngay.

Nhìn toàn bộ project theo một câu rất ngắn:

```text
pages lo phần nội dung web,
classifier lo phần upload và điều phối,
ml lo phần dự đoán,
templates lo HTML dùng chung,
static lo giao diện,
media lo file upload.
```

Nếu hiểu được câu trên, bạn đã nắm được phần cốt lõi của VeggiClassify.
