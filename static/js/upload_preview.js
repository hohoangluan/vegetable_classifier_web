document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("id_image");
    const preview = document.getElementById("image-preview");
    const fileName = document.getElementById("file-name");

    if (!input || !preview || !fileName) {
        return;
    }

    input.addEventListener("change", (event) => {
        const [file] = event.target.files;
        if (!file) {
            preview.hidden = true;
            preview.removeAttribute("src");
            fileName.textContent = "Chưa có ảnh nào được chọn.";
            return;
        }

        preview.src = URL.createObjectURL(file);
        preview.hidden = false;
        fileName.textContent = file.name;
    });
});
