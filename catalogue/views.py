from django.shortcuts import render
from catalogue.models import Book, Author, BookInstance, Genre
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils import timezone

# Create your views here.
#@permission_required('catalogue.can_mark_returned')
#@permission_required('catalogue.can_edit')
def index(request):
    """View function for home page"""

    # Generate counts of the main objects
    num_of_books = Book.objects.all().count()
    num_of_instances = BookInstance.objects.all().count()

    #Available books(status = 'a)
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_instances_on_loan = BookInstance.objects.filter(status__exact='o').count()
    num_of_genre = Genre.objects.count()

    #The 'all()' is implied by default
    num_of_authors = Author.objects.count()
    #Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1


    context = {
        'num_of_books' : num_of_books,
        'num_of_instances': num_of_instances,
        'num_instances_available': num_instances_available,
        'num_instances_on_loan':  num_instances_on_loan,
        'num_of_authors': num_of_authors,
        'num_of_genre': num_of_genre,
        'num_visits': num_visits,

    }
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    #template_name = 'catalogue/book_list.html'
    #permission_denied_message = "You are not allowed here"

    context_object_name = 'book_list'
    paginate_by = 2
    
    #def get_queryset(self):
     #   return Book.objects.filter(title__icontains='war')[ :5] #get 5 books containing the title war

    def get_context_data(self,**Kwargs):
        #call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**Kwargs)
        #Create any data and add it to the context
        context['book_list'] = Book.objects.all()
        return context
    #template_name = 'books/my_arbitrary_template_name_list.html' #specify your own template name/location

    
class BookDetailView(generic.DetailView):
    model = Book

    def book_detail_view(request, primary_key):
        book = get_object_or_404(Book, pk=primary_key)
        return render(request, 'catalogue/book_detail.html', context={'book': book})

#class AuthorListView(LoginRequiredMixin, generic.ListView):
class AuthorListView(generic.ListView):
    model = Author
    #template_name = 'catalogue/author_list.html'
    #context_object_name = 'author_list'
    paginate_by = 2

    def get_context_data(self,**Kwargs):
        context = super(AuthorListView, self).get_context_data(**Kwargs)
        context['author_list'] = Author.objects.all()
        return context


class AuthorDetailView(generic.DetailView):
    model = Author

    def author_detail_view(request, primary_key):
        author = get_object_or_404(Author, pk=primary_key)
        return render(request, 'catalogue/author_detail.html', context={'author': author})



class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalogue/bookinstance_list_borrowed_user.html'
    paginate_by = 1

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """generic class-based view listing all books on loan. only visible to users with can_mark_returned permission """
    model = BookInstance
    permission_required = 'catalogue.can_mark_returned'
    template_name = 'catalogue/bookinstance_list_borrowed_all.html'
    paginate_by = 1
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')




from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required, permission_required

# from .forms import RenewBookForm
from catalogue.forms import RenewBookForm


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalogue/book_renew_librarian.html', context)



from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalogue.models import Author

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    permission_required = 'catalogue.can_mark_returned'
    template_name = 'catalogue/author_form.html'

class AuthorUpdate(UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ["title", 'author', 'summary', 'isbn', 'genre']
    permission_required = 'catalogue.can_mark_returned'
    template_name = 'catalogue/book_form.html'

class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'

class BookDelete(DeleteView):
    model = Book
    success_url =  reverse_lazy('books')