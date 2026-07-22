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
            "redo",
        ]
    })
    .catch(error => {
        console.error(error);
    });