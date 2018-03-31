from __future__ import unicode_literals
from django.shortcuts import render, HttpResponse, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from time import gmtime, strftime
from django.db.models import Count
from django.utils.crypto import get_random_string
from .models import Users, Authors, Books, Reviews
import bcrypt, re

def index(request):
    for key in request.session.keys():
            request.session.pop(key)
    return render(request, "beltreviewer/index.html")

def register(request):
    if request.method =='POST':
        request.session["firstname"] = request.POST["firstname"]
    hash1 = bcrypt.hashpw(request.POST["password"].encode(), bcrypt.gensalt())
    print "hash1", hash1
    errors = Users.objects.basic_validator(request.POST)
    if len(errors):
        for tag, error in errors.iteritems():
            messages.error(request, error, extra_tags=tag)
        return redirect("/")
    else:
        user = Users.objects.create(first_name = request.POST["firstname"], last_name = request.POST["lastname"], email = request.POST["email"], birthdate = request.POST["birthdate"], password = hash1)
        user.save()
        reguser = Users.objects.filter(email__contains=request.POST["email"])
        for fname in reguser:
            request.session["user_id"] = fname.id
            # print "user_id ", request.session["user_id"]
        return redirect("/books")

def login(request):
    loginerrors = Users.loginobjects.login_validator(request.POST)
    user = Users.objects.filter(email__contains=request.POST["loginemail"])
    for fname in user:
        request.session["user_id"] = fname.id
        # print "user id ", request.session["user_id"]
        request.session["firstname"] = fname.first_name
    if len(loginerrors):
        for tag, loginerror in loginerrors.iteritems():
            messages.error(request, loginerror, extra_tags=tag)
        return redirect("/")
    else:
        return redirect("/books")
def books(request):
# Below is for not allowing user to view pages if not logged in.
    if "user_id" not in request.session:
        return redirect("/")
    context = {
        "reviews": Reviews.objects.all().order_by("-created_at")[:3],
        "reviewedbooks": Reviews.objects.values('book__title', 'book__id').annotate(Count("book"))
    }
    return render(request, "beltreviewer/books.html", context)

def booksadd(request):
    if "user_id" not in request.session:
        return redirect("/")
    context = {
        "authors": Authors.objects.all()
    }
    return render(request, "beltreviewer/addbook.html", context)

def addbook(request):
    if request.method == "POST":
    ########## below for creating new book and review if author already in database
        if len(request.POST["newauthor"]) == 0:
            listauthorid = request.POST["author"]
            newbook = Books.objects.create(title=request.POST["booktitle"], author=Authors.objects.get(id=listauthorid))
            newbook.save()
            getbook = Books.objects.filter(title__contains=request.POST["booktitle"])
            for book in getbook:
                bookid = book.id
            newreview = Reviews.objects.create(rating = request.POST["rating"], desc = request.POST["review"], user = Users.objects.get(id = int(request.session["user_id"])), book = Books.objects.get(id = bookid))
            newreview.save()
        else: #below for if creating new author+book+review
            newauthor = Authors.objects.create(name = request.POST["newauthor"])
            newauthor.save()
            getauthor = Authors.objects.filter(name__contains=request.POST["newauthor"])
            for author in getauthor:
                authorid = author.id
            newbook = Books.objects.create(title=request.POST["booktitle"], author=Authors.objects.get(id=authorid))
            newbook.save()
            # work on below for getting by book id
            getbook = Books.objects.filter(title__contains=request.POST["booktitle"])
            for book in getbook:
                bookid = book.id
            newreview = Reviews.objects.create(rating = request.POST["rating"], desc = request.POST["review"], user = Users.objects.get(id = int(request.session["user_id"])), book = Books.objects.get(id = bookid))
            newreview.save()
        return redirect("show_book", bid=bookid)

def addreview(request):
    if request.method == "POST":
        newreview = Reviews.objects.create(rating = request.POST["rating"], desc = request.POST["review"], user = Users.objects.get(id = request.session["user_id"]), book = Books.objects.get(id = request.POST["bookid"]))
        newreview.save()
        return redirect("show_book", bid=request.POST["bookid"])

def showbook(request, bid):
    context = {
        "books": Books.objects.get(id = bid),
        "reviews": Reviews.objects.filter(book=bid)
    }
    return render(request, "beltreviewer/showbook.html", context)
def showuser(request, uid):
    context = {
        "users": Users.objects.get(id = uid),
        "reviews": Reviews.objects.filter(user=Users.objects.get(id=uid)).count(),
        "books": Books.objects.values('title').annotate(tcount=Count("title")),
        "booksreviewed": Reviews.objects.all().filter(user=Users.objects.get(id=uid)).values('book__title', 'book__id').annotate(Count("book"))
    }
    return render(request, "beltreviewer/showuser.html", context)

def delete(request):
    if request.method == "POST":
        update = Reviews.objects.get(id = request.POST["reviewid"])
        update.delete()
        return redirect("show_book", bid=request.POST["bookid"])
