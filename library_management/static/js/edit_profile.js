document.getElementById("id_profile_photo").addEventListener("change", function(e){

    const file = e.target.files[0];

    if(file){

        document.getElementById("previewImage").src =
            URL.createObjectURL(file);

    }

});