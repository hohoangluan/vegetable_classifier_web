document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("[data-upload-form]");
    const uploadBox = document.querySelector("[data-upload-box]");
    const dropzone = document.querySelector("[data-upload-dropzone]");
    const input = document.getElementById("id_image");
    const preview = document.getElementById("image-preview");
    const fileName = document.getElementById("file-name");
    const emptyState = document.querySelector("[data-upload-empty]");
    const previewState = document.querySelector("[data-upload-preview-state]");
    const clearButton = document.querySelector("[data-clear-preview]");
    let objectUrl = null;

    if (!form || !uploadBox || !dropzone || !input || !preview || !fileName || !emptyState || !previewState || !clearButton) {
        return;
    }

    const resetObjectUrl = () => {
        if (objectUrl) {
            URL.revokeObjectURL(objectUrl);
            objectUrl = null;
        }
    };

    const updateState = ({ previewSrc = "", fileLabel = "", hasPreview = false }) => {
        uploadBox.classList.toggle("has-preview", hasPreview);
        dropzone.classList.toggle("has-preview", hasPreview);
        emptyState.hidden = hasPreview;
        previewState.hidden = !hasPreview;
        clearButton.hidden = !hasPreview;

        if (hasPreview && previewSrc) {
            preview.src = previewSrc;
            preview.hidden = false;
            fileName.textContent = fileLabel || "Ảnh đã sẵn sàng để phân loại.";
            return;
        }

        preview.hidden = true;
        preview.removeAttribute("src");
        fileName.textContent = "Nhấn vào khung hoặc kéo thả ảnh để bắt đầu.";
    };

    const submitForm = () => {
        if (typeof form.requestSubmit === "function") {
            form.requestSubmit();
            return;
        }

        form.submit();
    };

    const showLocalPreview = (file) => {
        resetObjectUrl();
        objectUrl = URL.createObjectURL(file);
        updateState({
            previewSrc: objectUrl,
            fileLabel: file.name,
            hasPreview: true,
        });
    };

    const handleFileSelection = (file) => {
        if (!file) {
            updateState({ hasPreview: false });
            return;
        }

        showLocalPreview(file);
        window.setTimeout(submitForm, 80);
    };

    input.addEventListener("change", (event) => {
        const [file] = event.target.files;
        handleFileSelection(file);
    });

    ["dragenter", "dragover"].forEach((eventName) => {
        dropzone.addEventListener(eventName, (event) => {
            event.preventDefault();
            dropzone.classList.add("is-dragover");
        });
    });

    ["dragleave", "dragend", "drop"].forEach((eventName) => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.remove("is-dragover");
        });
    });

    dropzone.addEventListener("drop", (event) => {
        event.preventDefault();
        const [file] = event.dataTransfer.files;
        if (!file) {
            return;
        }

        if (typeof DataTransfer === "function") {
            const transfer = new DataTransfer();
            transfer.items.add(file);
            input.files = transfer.files;
        }

        handleFileSelection(file);
    });

    clearButton.addEventListener("click", (event) => {
        event.preventDefault();
        resetObjectUrl();
        input.value = "";
        updateState({ hasPreview: false });
    });

    if (preview.getAttribute("src")) {
        updateState({
            previewSrc: preview.getAttribute("src"),
            fileLabel: "Ảnh đã sẵn sàng để phân loại.",
            hasPreview: true,
        });
        return;
    }

    updateState({ hasPreview: false });
});
