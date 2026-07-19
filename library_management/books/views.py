from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Book, CATEGORY_CHOICES
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from notifications.models import Notification
from settings_app.models import NotificationSettings
from django.contrib.auth.decorators import login_required



@login_required(login_url="login")
def books_list(request):
    books = Book.objects.all().order_by("-created_at")
    search = request.GET.get("search", "")
    category = request.GET.get("category")
    status = request.GET.get("status")
    if search:
        books = books.filter(
            Q(title__icontains=search) | Q(author__icontains=search) |  Q(isbn__icontains=search) |  Q(category__icontains=search) |  Q(publisher__icontains=search) |  Q(publication_year__icontains=search) | Q(shelf_location__icontains=search)
        )
    
    if category:
        books = books.filter(category = category)
        
    if status:
        if status == "available":
            books = books.filter(available_copies__gt=0)
        elif status == "out_of_stock":
            books = books.filter(available_copies=0)
    
    query_params = request.GET.copy()
    query_params.pop("page", None)
        
    paginator = Paginator(books, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'books/book_list.html', {
        'page_obj': page_obj,
        'categories': CATEGORY_CHOICES,
        'search': search,
        'category': category,
        'status': status,
        "query_params": query_params.urlencode(),
    })

@login_required(login_url="login")
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'books/book_details.html', {'book': book})

@login_required(login_url="login")
def book_edit(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()
        category = request.POST.get("category", "").strip()
        isbn = request.POST.get("isbn", "").strip()
        publisher = request.POST.get("publisher", "").strip()
        publication_year = request.POST.get("publication_year")
        total_copies = request.POST.get("total_copies")
        available_copies = request.POST.get("available_copies")
        shelf_location = request.POST.get("shelf_location", "").strip()
        description = request.POST.get("description", "").strip()
        
        
        errors = {}

        if not title:
            errors["title"] = "Book Title is required."

        if not author:
            errors["author"] = "Author is required."

        if not category:
            errors["category"] = "Category is required."

        if not isbn:
            errors["isbn"] = "ISBN is required."

        if not publisher:
            errors["publisher"] = "Publisher is required."

        if not publication_year:
            errors["publication_year"] = "Publication Year is required."

        if not total_copies:
            errors["total_copies"] = "Total Copies is required."

        if not available_copies:
            errors["available_copies"] = "Available Copies is required."


        if errors:
            for error in errors.values():
                messages.error(request, error)
                
            return render(request, "books/edit_book.html", {
                "book": book,
                "errors": errors,
                "categories": CATEGORY_CHOICES,
            })
        
        
        
        
        if Book.objects.exclude(id=book.id).filter(isbn=isbn).exists():
            errors["isbn"] = "ISBN already exists."
        
        current_year = timezone.now().year
        
        try:
            publication_year = int(publication_year)
            total_copies = int(total_copies)
            available_copies = int(available_copies)
        except ValueError:
            errors["publication_year"] = "Please enter a valid publication year."
            errors["total_copies"] = "Please enter a valid total copies."
            errors["available_copies"] = "Please enter a valid available copies."
            
        if errors:
            return render(request, "books/add_book.html", {
                "book": book,
                "errors": errors,
                "categories": CATEGORY_CHOICES,
            })
        
        if publication_year > current_year:
            errors["publication_year"] = "Publication year cannot be in the future."
        
        if total_copies < 0 or available_copies < 0:
            errors["total_copies"] = "Copies cannot be negative."

        if available_copies > total_copies:
            errors["available_copies"] = "Available copies cannot be greater than total copies."
        
        if errors:
            return render(request, "books/edit_book.html", {
                "book": book,
                "errors": errors,
                "categories": CATEGORY_CHOICES,
            })
        
        book.title = title
        book.author = author
        book.category = category
        book.isbn = isbn
        book.publisher = publisher
        book.publication_year = publication_year
        book.total_copies = total_copies
        book.available_copies = available_copies
        book.shelf_location = shelf_location
        book.description = description
            
        
        book_cover = request.FILES.get("book_cover")
        if book_cover:
            if book.book_cover:
                book.book_cover.delete(save=False)
            book.book_cover = book_cover
        
        book.save()
        messages.success(request, "Book updated successfully.")
        return redirect("books_list")
    return render(request, "books/edit_book.html", {
        "book":book,
        'categories': CATEGORY_CHOICES
    })

@login_required(login_url="login")
def book_delete(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        if book.available_copies != book.total_copies:
            messages.error(
                request,
                "This book cannot be deleted because it is currently issued to a member"
            )
            return redirect("book_delete", book_id)
        
        if book.book_cover:
            book.book_cover.delete(save=False)
            
        title = book.title
        book.delete()
        
        messages.success(
            request,
            f'"{title}" has been deleted successfully.'
        )
        
        return redirect("books_list")
    return render(request, "books/delete_book.html", {"book": book})
  
@login_required(login_url="login")
def book_add(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()
        category = request.POST.get("category", "").strip()
        isbn = request.POST.get("isbn", "").strip()
        publisher = request.POST.get("publisher", "").strip()
        publication_year = request.POST.get("publication_year")
        total_copies = request.POST.get("total_copies")
        available_copies = request.POST.get("available_copies")
        shelf_location = request.POST.get("shelf_location", "").strip()
        description = request.POST.get("description", "").strip()
        book_cover = request.FILES.get("book_cover")

        errors = {}

        if not title:
            errors["title"] = "Book Title is required."

        if not author:
            errors["author"] = "Author is required."

        if not category:
            errors["category"] = "Category is required."

        if not isbn:
            errors["isbn"] = "ISBN is required."

        if not publisher:
            errors["publisher"] = "Publisher is required."

        if not publication_year:
            errors["publication_year"] = "Publication Year is required."

        if not total_copies:
            errors["total_copies"] = "Total Copies is required."

        if not available_copies:
            errors["available_copies"] = "Available Copies is required."

        if errors:
            for error in errors.values():
                messages.error(request, error)
                
            return render(request, "books/add_book.html", {
                "errors": errors,
                "categories": CATEGORY_CHOICES,
            })

        
        if Book.objects.filter(isbn=isbn).exists():
            errors["isbn"] = "ISBN already exists."
            

        current_year = timezone.now().year

        try:
            publication_year = int(publication_year)
            total_copies = int(total_copies)
            available_copies = int(available_copies)
        except ValueError:
            errors["publication_year"] = "Please enter a valid publication year."
            errors["total_copies"] = "Please enter a valid total copies."
            errors["available_copies"] = "Please enter a valid available copies."
            
        if errors:
            for error in errors.values():
                messages.error(request, error)
                
            return render(request, "books/add_book.html", {
                "errors": errors,
                "categories": CATEGORY_CHOICES,
            })
            

        if publication_year > current_year:
            errors["publication_year"] = "Publication year cannot be in the future."
            

        if total_copies < 0 or available_copies < 0:
            errors["total_copies"] = "Copies cannot be negative."
            

        if available_copies > total_copies:
            errors["available_copies"] = "Available copies cannot be greater than total copies."
            
        if errors:
            for error in errors.values():
                messages.error(request, error)
                
            return render(request, "books/add_book.html", {
                "errors": errors,
                "categories": CATEGORY_CHOICES,
            })

        Book.objects.create(
            title=title,
            author=author,
            category=category,
            isbn=isbn,
            publisher=publisher,
            publication_year=publication_year,
            total_copies=total_copies,
            available_copies=available_copies,
            shelf_location=shelf_location,
            description=description,
            book_cover=book_cover,
        )
        
        message= f'A new book, "{title}", has been added to the library collection.'
        
        
        notification_settings = NotificationSettings.objects.first()
        
        if notification_settings.new_book_alert:
            Notification.objects.create(
                title="New Book Added",
                message=message,
                notification_type="new_book",
            )

        messages.success(request, "Book added successfully.")
        return redirect("books_list")

    return render(request, "books/add_book.html", {
        "categories": CATEGORY_CHOICES,
    })
    
    