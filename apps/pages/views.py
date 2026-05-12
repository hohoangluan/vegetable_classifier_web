from django.shortcuts import render


def home_view(request):
    context = {
        "page_name": "home",
        "hero": {
            "title": "Hệ Thống Phân Loại Rau Củ",
            "subtitle": "Sử dụng công nghệ trí tuệ nhân tạo và deep learning để tự động nhận diện và phân loại các loại rau củ một cách chính xác và nhanh chóng",
            "cta_label": "Bắt Đầu Phân Loại Ngay",
        },
        "feature_cards": [
            {
                "icon_key": "zap",
                "title": "Phân Loại Nhanh Chóng",
                "description": "Xử lý hình ảnh và đưa ra kết quả trong vài giây với độ chính xác cao",
            },
            {
                "icon_key": "badge-check",
                "title": "Độ Chính Xác Cao",
                "description": "Sử dụng mô hình deep learning được huấn luyện trên hàng nghìn mẫu dữ liệu",
            },
            {
                "icon_key": "shield",
                "title": "Đa Dạng Loại Rau Củ",
                "description": "Hỗ trợ phân loại nhiều loại rau củ phổ biến tại Việt Nam",
            },
        ],
        "usage_steps": [
            {
                "number": "1",
                "icon_key": "upload",
                "title": "Tải Hình Ảnh",
                "description": "Chọn hoặc kéo thả hình ảnh rau củ cần phân loại",
            },
            {
                "number": "2",
                "icon_key": "git-branch",
                "title": "Xem Pipeline",
                "description": "Tìm hiểu quy trình xử lý và phân loại",
            },
            {
                "number": "3",
                "icon_key": "database",
                "title": "Khám Phá Dataset",
                "description": "Xem chi tiết về dữ liệu huấn luyện",
            },
        ],
        "stats": [
            {"number": "15+", "label": "Loại Rau Củ"},
            {"number": "95%", "label": "Độ Chính Xác"},
            {"number": "5000+", "label": "Hình Ảnh"},
            {"number": "<2s", "label": "Thời Gian Xử Lý"},
        ],
    }
    return render(request, "pages/home.html", context)


def about_view(request):
    context = {
        "page_name": "about",
        "architecture_points": [
            "Django app pages quản lý các trang giới thiệu và minh họa.",
            "Django app classifier phụ trách form upload, render kết quả và service.",
            "Package ml/ chứa code machine learning độc lập để giữ views gọn gàng.",
        ],
    }
    return render(request, "pages/about.html", context)


def pipeline_view(request):
    context = {
        "page_name": "pipeline",
        "pipeline_steps": [
            {
                "step_number": "01",
                "title": "Nhận Ảnh Từ Người Dùng",
                "description": "Ảnh được upload thông qua form trong app classifier.",
            },
            {
                "step_number": "02",
                "title": "Tiền Xử Lý",
                "description": "Package ml/ có thể resize, normalize và chuẩn bị dữ liệu đầu vào.",
            },
            {
                "step_number": "03",
                "title": "Trích Rút Và Dự Đoán",
                "description": "Model loader nạp file trong ml_models/ và predictor trả kết quả cho Django.",
            },
            {
                "step_number": "04",
                "title": "Hiển Thị Kết Quả",
                "description": "Classifier app nhận output và render giao diện cho người dùng.",
            },
        ],
    }
    return render(request, "pages/pipeline.html", context)


def dataset_view(request):
    context = {
        "page_name": "dataset",
        "dataset_bars": [
            {"name": "Carrot", "count": 1000, "ratio": 92},
            {"name": "Potato", "count": 980, "ratio": 88},
            {"name": "Tomato", "count": 940, "ratio": 84},
            {"name": "Cabbage", "count": 860, "ratio": 76},
        ],
    }
    return render(request, "pages/dataset.html", context)
