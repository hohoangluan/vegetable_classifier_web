from django.shortcuts import render

from .forms import ImageUploadForm
from .services import classify_uploaded_image


SUPPORTED_VEGETABLES = [
    "Cà chua",
    "Cà rốt",
    "Khoai tây",
    "Bắp cải",
    "Ớt chuông",
    "Dưa chuột",
    "Hành tây",
    "Bí đỏ",
    "Rau bina",
    "Súp lơ xanh",
    "Cà tím",
    "Ớt",
    "Bí ngòi",
    "Đậu Hà Lan",
    "Ngô",
]


def classify_view(request):
    form = ImageUploadForm(request.POST or None, request.FILES or None)
    result = None
    preview_url = ""

    if request.method == "POST" and form.is_valid():
        result = classify_uploaded_image(form.cleaned_data["image"])
        preview_url = result.get("image_url", "")
        request.session["latest_prediction"] = result

    return render(
        request,
        "classifier/classify.html",
        {
            "page_name": "classify",
            "form": form,
            "preview_url": preview_url,
            "result": result,
            "supported_vegetables": SUPPORTED_VEGETABLES,
        },
    )


def result_view(request):
    result = request.session.get("latest_prediction")
    return render(
        request,
        "classifier/result.html",
        {
            "page_name": "classify",
            "result": result,
        },
    )
