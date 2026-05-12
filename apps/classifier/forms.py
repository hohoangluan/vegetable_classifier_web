from django import forms


class ImageUploadForm(forms.Form):
    image = forms.ImageField(
        label="Ảnh rau củ",
        help_text="Ảnh sẽ được tải lên và phân loại ngay sau khi bạn chọn file.",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "file-input",
                "accept": "image/jpeg,image/png,image/webp",
                "id": "id_image",
            }
        ),
    )
