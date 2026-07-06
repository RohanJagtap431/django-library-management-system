const coverInput = document.getElementById("id_book_cover");
const coverPreview = document.getElementById("coverPreview");

if (coverInput && coverPreview) {
    coverInput.addEventListener("change", function () {
        const file = this.files[0];

        if (file) {
            coverPreview.src = URL.createObjectURL(file);
        }
    });
}