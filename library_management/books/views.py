from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Book, CATEGORY_CHOICES
from django.db.models import Q



def books_list(request):
    books = Book.objects.all()
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
    
        
    paginator = Paginator(books, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'books/book_list.html', {
        'page_obj': page_obj,
        'categories': CATEGORY_CHOICES,
        'search': search,
        'category': category,
        'status': status
    })


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'books/book_details.html', {'book': book})