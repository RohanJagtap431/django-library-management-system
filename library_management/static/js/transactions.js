const memberSearch = document.getElementById("member-search");
const memberResults = document.getElementById("member-results");

const bookSearch = document.getElementById("book-search");
const bookResults = document.getElementById("book-results");

memberSearch.addEventListener("keyup", function () {
    const query = memberSearch.value.trim();
    if (query === ""){
        memberResults.innerHTML = "";
        memberResults.style.display = "none";
        return;
    }

    fetch(`/transactions/search-member/?q=${query}`)
        .then(response => response.json())
        .then(data => {
            memberResults.innerHTML = "";

            if (data.members.length === 0) {
                memberResults.style.display = "none";
                return;
            }

            memberResults.style.display = "block";


            data.members.forEach(member => {
                const div = document.createElement("div");

                div.classList.add("member-item");

                div.textContent = `${member.member_id} - ${member.full_name}`;


                memberResults.appendChild(div);

                div.addEventListener("click", function () {

                    memberSearch.value = `${member.member_id} - ${member.full_name}`;

                    document.getElementById("selected-member-id").value = member.id;
                    
                    document.getElementById("summary-member-id").textContent = member.member_id;

                    document.getElementById("summary-member-name").textContent = member.full_name;

                    document.getElementById("summary-phone").textContent = member.phone;

                    document.getElementById("summary-member-type").textContent = member.member_type;

                    document.getElementById("summary-status").textContent = member.status;

                    memberResults.innerHTML = "";
                    memberResults.style.display = "none";


                });
            });
        });
});



bookSearch.addEventListener("keyup", function () {
    const query = bookSearch.value.trim();
    if (query === ""){
        bookResults.innerHTML = "";
        bookResults.style.display = "none";
        return;
    }

    fetch(`/transactions/search-book/?q=${query}`)
        .then(response => response.json())
        .then(data => {
            bookResults.innerHTML = "";

            if (data.books.length === 0) {
                bookResults.style.display = "none";
                return;
            }

            bookResults.style.display = "block";


            data.books.forEach(book => {
                const div = document.createElement("div");

                div.classList.add("book-item");

                div.textContent = `${book.isbn} - ${book.title}`;


                bookResults.appendChild(div);

                div.addEventListener("click", function () {

                    bookSearch.value = `${book.isbn} - ${book.title}`;

                    document.getElementById("selected-book-id").value = book.id;
                    
                    document.getElementById("summary-book-id").textContent = book.isbn;

                    document.getElementById("summary-book-title").textContent = book.title;

                    document.getElementById("summary-category").textContent = book.category;

                    document.getElementById("summary-author").textContent = book.author;

                    document.getElementById("summary-available-copies").textContent = book.available_copies;

                    document.getElementById("issue-available-copies").textContent = book.available_copies;

                    bookResults.innerHTML = "";
                    bookResults.style.display = "none";


                    const today = new Date();

                    const issueDate = today.toLocaleDateString("en-GB", {
                        day: "2-digit",
                        month: "short",
                        year: "numeric"
                    });

                    document.getElementById("issue-date").textContent = issueDate;
                    document.getElementById("left-issue-date").textContent = issueDate;


                    const loanPeriod = 3;

                    document.getElementById("loan-period").textContent = `${loanPeriod} Days`;
                    document.getElementById("left-loan-period").textContent = `${loanPeriod} Days`;

                    const dueDate = new Date(today);

                    dueDate.setDate(today.getDate() + loanPeriod);

                    const dueDateText = dueDate.toLocaleDateString("en-GB", {
                        day: "2-digit",
                        month: "short",
                        year: "numeric"
                    });

                    document.getElementById("due-date").textContent = dueDateText;
                    document.getElementById("left-due-date").textContent = dueDateText;


                });
            });
        });
});

document.querySelectorAll('.toast').forEach(toastEl => {
    new bootstrap.Toast(toastEl).show();
});

console.log(typeof bootstrap);