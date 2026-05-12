from django.shortcuts import redirect, render

from .forms import ImageUploadForm
from .services import classify_uploaded_image


def classify_view(request):
    form = ImageUploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        prediction = classify_uploaded_image(form.cleaned_data["image"])
        request.session["latest_prediction"] = prediction
        return redirect("classifier:result")

    return render(
        request,
        "classifier/classify.html",
        {
            "page_name": "classify",
            "form": form,
        },
    )


def result_view(request):
    result = request.session.get("latest_prediction")
    return render(
        request,
        "classifier/result.html",
        {
            "page_name": "result",
            "result": result,
        },
    )
