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
        "page_name": "pipeline-page",
        "pipeline_steps": [
            {
                "number": "1",
                "icon_key": "upload",
                "accent": "blue",
                "title": "Thu Thập Dữ Liệu",
                "description": "Người dùng tải lên hình ảnh rau củ cần phân loại",
                "details": [
                    "Hỗ trợ nhiều định dạng: JPG, PNG, WEBP",
                    "Tự động resize về kích thước chuẩn",
                    "Kiểm tra chất lượng hình ảnh",
                ],
            },
            {
                "number": "2",
                "icon_key": "image",
                "accent": "purple",
                "title": "Tiền Xử Lý Ảnh",
                "description": "Chuẩn hóa và tăng cường chất lượng hình ảnh",
                "details": [
                    "Resize về 224 x 224 pixels",
                    "Normalize pixel values [0, 1]",
                    "Data augmentation cho training",
                    "Loại bỏ nhiễu và cân bằng sáng",
                ],
            },
            {
                "number": "3",
                "icon_key": "cpu",
                "accent": "green",
                "title": "Trích Xuất Đặc Trưng",
                "description": "Sử dụng CNN để trích xuất các đặc trưng quan trọng",
                "details": [
                    "Backbone: ResNet50 pretrained",
                    "Transfer learning từ ImageNet",
                    "Trích xuất feature maps đa tầng",
                    "Giảm chiều dữ liệu với Global Average Pooling",
                ],
            },
            {
                "number": "4",
                "icon_key": "brain",
                "accent": "amber",
                "title": "Phân Loại",
                "description": "Mô hình deep learning dự đoán loại rau củ",
                "details": [
                    "Fully connected layers",
                    "Softmax activation cho đa lớp",
                    "Dropout để tránh overfitting",
                    "Batch normalization",
                ],
            },
            {
                "number": "5",
                "icon_key": "check-circle",
                "accent": "mint",
                "title": "Kết Quả",
                "description": "Trả về kết quả phân loại với độ tin cậy",
                "details": [
                    "Top-1 accuracy: 95.3%",
                    "Thời gian inference: ~1.8s",
                    "Confidence score cho mỗi dự đoán",
                    "Trực quan hóa kết quả",
                ],
            },
        ],
        "architecture_highlights": [
            {
                "accent": "blue",
                "label": "Input Layer",
                "value": "224 × 224 × 3",
            },
            {
                "accent": "purple",
                "label": "Backbone",
                "value": "ResNet50 (Pretrained)",
            },
        ],
        "architecture_layers": [
            {"label": "Conv Blocks", "value": "7 × 7 × 2048"},
            {"label": "Global Avg Pool", "value": "2048"},
            {"label": "Dense Layer", "value": "512"},
            {"label": "Dropout (0.5)", "value": "512"},
            {"label": "Output Layer", "value": "15 classes"},
        ],
        "training_details": [
            {"label": "Optimizer", "value": "Adam (lr=0.001)"},
            {"label": "Loss Function", "value": "Categorical Crossentropy"},
            {"label": "Batch Size", "value": "32"},
            {"label": "Epochs", "value": "50"},
            {"label": "Training Time", "value": "~4 hours"},
            {"label": "GPU", "value": "NVIDIA Tesla T4"},
        ],
        "performance_metrics": [
            {"label": "Accuracy", "value": "95.3%"},
            {"label": "F1-Score", "value": "94.8%"},
            {"label": "Precision", "value": "96.1%"},
            {"label": "Recall", "value": "93.5%"},
        ],
        "flow_nodes": [
            {"label": "Input Image", "accent": "blue"},
            {"label": "Preprocessing", "accent": "purple"},
            {"label": "Feature Extraction", "accent": "green"},
            {"label": "Classification", "accent": "amber"},
            {"label": "Result", "accent": "mint"},
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
