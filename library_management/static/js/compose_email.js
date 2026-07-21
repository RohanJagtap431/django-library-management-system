const memberDiv = document.getElementById("member-dropdown");
const subjectDiv = document.getElementById("subject-div");

selectedMember.addEventListener("change", function () {
    memberDiv.style.display = "block";

    subjectDiv.classList.remove("col-md-12");
    subjectDiv.classList.add("col-md-6");
});

allMembers.addEventListener("change", function () {
    memberDiv.style.display = "none";

    subjectDiv.classList.remove("col-md-6");
    subjectDiv.classList.add("col-md-12");
});


ClassicEditor
    .create(document.querySelector("#editor"), {
        toolbar: [
            "heading",
            "|",
            "bold",
            "italic",
            "underline",
            "|",
            "bulletedList",
            "numberedList",
            "|",
            "link",
            "blockQuote",
            "|",
            "undo",
            "redo"
        ]
    })
    .catch(error => {
        console.error(error);
    });