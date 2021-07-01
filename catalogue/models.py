from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date

# Create your models here.
class Book(models.Model):
    """ Models representing book model(but not a specific book"""
    title = models.CharField(max_length=200)


    #Foriegn key used cos a book can only have one author, but authors can have multiple books
    #Authors as a string rather than an object because it hasn't been declared yet in the file
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13, unique=True, help_text='13 Character <a href="https//www.isbn-international.org/content/what-isbn">ISBN number</a>')

    #ManytoManyField is used because genre can contain many books. Books can have many genres.
    #Genre class has already been defined above.
    genre = models.ManyToManyField('Genre', help_text="Select a genre for this book")


    class Meta:
        ordering = ['title']
    
    
    def __str__(self):
        """String for representing a model object"""
        return self.title

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        """create a string for the Genre"""
        return ', '.join(genre.name for genre in self.genre.all()[:3] )

    display_genre.short_description = "Genre"


class MyModelName(models.Model):
    """ a typical class defining a model, derived from a model class"""

    #Field
    my_field_name = models.CharField(max_length=20, help_text="Enter Field Documentation")

    #Metadata
    class Meta:
        ordering = ['-my_field_name']

    #Methods
    def get_absolute_url(self):
        return reverse('model-detail-view', args=[str(self.id)])

    def __self__(self):
        """ String for representing the MyModelName object(in ADmin site)"""
        return self.my_field_name



class Genre(models.Model):
    """ Models representing books genre"""
    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g Romance Fictiion)")

    def __str__(self):
        """ String for representing the Model object."""
        return self.name




class Language(models.Model):
    """ Model representing a language (e.g English, French, German)"""
    name = models.CharField(max_length=200, help_text="Enter the book's natural language(e.g English, French, German, Korean etc.)")

    def __str__(self):
        """ String for representing a model object"""
        return self.name

class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)


    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False



    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On Loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank = True,
        default = 'm',
        help_text = 'Book availability',
        )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)
        

    def __str__(self):
        """String for representing the model object"""
        return f'{self.id} ({self.book.title})'

    


class Author(models.Model):
    """Model representing an author"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)
    
    class Meta:
        ordering = ['last_name']

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model Object."""
        return f'{self.last_name}, {self.first_name}'
