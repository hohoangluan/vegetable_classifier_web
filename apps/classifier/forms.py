from django import forms


class ImageUploadForm(forms.Form):
    image = forms.ImageField(
        label="Ảnh rau củ",
        help_text="Tải lên một ảnh để demo quy trình phân loại.",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "file-input",
                "accept": "image/*",
                "id": "id_image",
            }
        ),
    )
