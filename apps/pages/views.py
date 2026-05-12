from django.shortcuts import render


def home_view(request):
    context = {
        "page_name": "home",
        "feature_cards": [
            {
                "icon": "01",
                "title": "Phan loai bang anh upload",
                "description": "Sinh vien tai anh len, web goi service va nhan ket qua du doan tu package machine learning.",
                "meta": "Upload -> Service -> Predictor",
            },
            {
                "icon": "02",
                "title": "Mo phong pipeline xu ly",
                "description": "Trang rieng de giai thich cac buoc: tien xu ly, trich rut dac trung, nap model va tra ve nhan.",
                "meta": "Hoc de hieu luong ML",
            },
            {
                "icon": "03",
                "title": "Trinh bay dataset",
                "description": "Minh hoa cau truc tap du lieu va phan bo lop de sinh vien lien ket giua du lieu va ket qua mo hinh.",
                "meta": "Dataset co cau truc ro rang",
            },
        ],
        "stats": [
            {"number": "4", "label": "Trang chinh", "description": "Trang home, about, pipeline, dataset."},
            {"number": "1", "label": "App classifier", "description": "Noi xu ly upload va hien thi ket qua."},
            {"number": "1", "label": "ML package", "description": "Package Python doc lap de Django goi ham predict()."},
        ],
    }
    return render(request, "pages/home.html", context)


def about_view(request):
    context = {
        "page_name": "about",
        "architecture_points": [
            "Django app pages quan ly cac trang gioi thieu va minh hoa.",
            "Django app classifier phu trach form upload, render ket qua va service.",
            "Package ml/ chua code machine learning doc lap de giu views gon gang.",
        ],
    }
    return render(request, "pages/about.html", context)


def pipeline_view(request):
    context = {
        "page_name": "pipeline",
        "pipeline_steps": [
            {
                "step_number": "01",
                "title": "Nhan anh tu nguoi dung",
                "description": "Anh duoc upload thong qua form trong app classifier.",
            },
            {
                "step_number": "02",
                "title": "Tien xu ly",
                "description": "Package ml/ co the resize, normalize va chuan bi du lieu dau vao.",
            },
            {
                "step_number": "03",
                "title": "Trich rut va du doan",
                "description": "Model loader nap file trong ml_models/ va predictor tra ket qua cho Django.",
            },
            {
                "step_number": "04",
                "title": "Hien thi ket qua",
                "description": "Classifier app nhan output va render giao dien cho nguoi dung.",
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
