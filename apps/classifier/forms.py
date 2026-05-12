from django import forms


class ImageUploadForm(forms.Form):
    image = forms.ImageField(
        label="Anh rau cu",
        help_text="Tai len mot anh de demo quy trinh phan loai.",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "file-input",
                "accept": "image/*",
                "id": "id_image",
            }
        ),
    )
