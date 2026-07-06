const profileInput = document.getElementById("id_profile_photo");
const profilePreview = document.getElementById("profilePreview");

if (profileInput && profilePreview) {
    profileInput.addEventListener("change", function () {
        const file = this.files[0];

        if (file) {
            profilePreview.src = URL.createObjectURL(file);
        }
    });
}