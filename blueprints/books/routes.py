from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from models import Books, User_Read_Books, Reviews
from extensions import db
from ..auth.forms import ReviewForm
import requests, os

books = Blueprint('books', __name__)

google_api_key = os.environ.get('GOOGLE_BOOKS_API_KEY')

@books.route('/search', methods=['GET', 'POST'])
@login_required  
def search():
    if request.method == 'POST':
        query = request.form.get('query')  # Get the search query from the form
        if query:
            # Send request to Google Books API with the search query
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {
                'q': query,
                'maxResults': 10,  # Limit the number of results
                'key': google_api_key
            }
            response = requests.get(url, params=params)

            # Check if the request was successful
            if response.status_code == 200:
                book_data = response.json()
                books = book_data.get('items', [])  # Extract the list of books from the API response
                if books:
                    return render_template('results.html', books=books, query=query) # Pass books to the results page

            # If no results or error, pass an empty list
            return render_template('results.html', books=[])
        
    return render_template('search.html')  # Display the search form if no POST request.   

@books.route('/books.my_books')
@login_required
def my_books():
    # Get the read status from the query parameter, if provided
    read_status = request.args.get('read_status', 'all')

    # Retrieve all books saved by the logged-in user
    query = User_Read_Books.query.filter_by(user_id=current_user.id)

    # Apply additional filtering by read status, if provided
    if read_status and read_status != 'all':
        query = query.filter_by(read_status=read_status)

    user_books = query.all()
    
    # Create a list to store book details
    books = []
    for user_book in user_books:
        book = Books.query.get(user_book.book_id)  # Fetch book details from Books table
        books.append({
            'book_id': book.book_id,
            'title': book.title,
            'author': book.author,
            'description': book.description,
            'cover_page': book.cover_page,
            'read_status': user_book.read_status  # Include the user's read status
        })
    
    return render_template('user_books.html', books=books)

@books.route('/view/<int:book_id>', methods=['GET'])
@login_required
def view_book(book_id):
    # Retrieve the book by its book_id
    book = Books.query.get_or_404(book_id)

    # Get reviews for the book
    reviews = Reviews.query.filter_by(book_id=book_id).all()

    # Calculate average rating
    if reviews:
        average_rating = sum(review.rating for review in reviews) / len(reviews)
    else:
        average_rating = None  # Handle case where there are no reviews yet

    # Check if the current user has already reviewed the book
    user_review = Reviews.query.filter_by(user_id=current_user.id, book_id=book_id).first()

    return render_template('view_book.html', book=book, reviews=reviews, average_rating=average_rating, user_review=user_review)

@books.route('/add_book', methods=['POST'])
@login_required
def add_book():
    # Get book data from the form
    api_id = request.form.get('api_id')
    title = request.form.get('title')
    author = request.form.get('author')
    description = request.form.get('description')
    cover_page = request.form.get('cover_page')

    # Check for missing required fields
    if not api_id or not title or not author:
        flash("Missing required book information.", "error")
        return redirect(url_for('books.search'))

    #Get the selected read_status from the form
    read_status = request.form.get('read_status')

    # Validate read_status
    if not read_status or read_status not in ['to-read', 'reading', 'completed']:
        flash("Invalid or missing read status.", "error")
        return redirect(url_for('books.search'))

    # Check if the book already exists in the Books table
    existing_book = Books.query.filter_by(api_id=api_id).first()
    if not existing_book:
        try:
            new_book = Books(api_id=api_id, title=title, author=author, description=description, cover_page=cover_page)
            db.session.add(new_book)
            db.session.commit()
            book_id = new_book.book_id  # Assign book_id from the new book
        except Exception as e:
            db.session.rollback()  # Rollback in case of database errors
            flash(f"Error adding book: {str(e)}", "error")
            return redirect(url_for('books.search'))
    else:
        # If the book already exists, get the book_id from the existing book
        book_id = existing_book.book_id

    # Check if the user already has this book in their list
    existing_user_book = User_Read_Books.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if existing_user_book:
        flash("This book is already in your list.", "info")
        return redirect(url_for('books.my_books'))
    
    # If not, add the book to the User_Read_Books table
    try:
        user_book = User_Read_Books(user_id=current_user.id, book_id=book_id, read_status=read_status)
        db.session.add(user_book)
        db.session.commit()
        flash("Book added to your list successfully.", "success")
    except Exception as e:
        db.session.rollback()  # Rollback in case of database errors
        flash(f"Error adding book to your list: {str(e)}", "error")
    
    return redirect(url_for('books.my_books'))  # Redirect to the user's book list after adding
                            
@books.route('/update_read_status/<int:book_id>', methods=['POST'])
@login_required
def update_read_status(book_id):
    new_status = request.form.get('read_status')

    # Validate read_status
    if new_status not in ['to-read', 'reading', 'completed']:
        flash("Invalid read status selected.", "error")
        return redirect(url_for('books.my_books'))
    
    user_book = User_Read_Books.query.filter_by(user_id=current_user.id, book_id=book_id).first()

    if not user_book:
        flash("Book not found in your list.", "error")
        return redirect(url_for('books.my_books'))
    
    user_book.read_status = new_status
    db.session.commit()
    flash("Read status updated successfully.", "success")
    return redirect(url_for('books.my_books'))  # Redirect back to the user's book list

@books.route('/remove_book/<int:book_id>', methods=['POST'])
@login_required
def remove_book(book_id):
    user_book = User_Read_Books.query.filter_by(user_id=current_user.id, book_id=book_id).first()

    if not user_book:
        flash("Book not found in your list.", "error")
        return redirect(url_for('books.my_books'))

    try:
        db.session.delete(user_book)
        db.session.commit()
        flash("Book removed from your list.", "success")
    except Exception as e:
        db.session.rollback()  # Rollback in case of database errors
        flash(f"Error removing book: {str(e)}", "error")

    return redirect(url_for('books.my_books')) # Redirect back to the user's book list

@books.route('/<int:book_id>/review', methods=['GET', 'POST'])
@login_required
def review_book(book_id):
    book = Books.query.get_or_404(book_id)
    form = ReviewForm()

    if form.validate_on_submit():
        # Check if the user already reviewed this book
        existing_review = Reviews.query.filter_by(user_id=current_user.id, book_id=book_id).first()

        if existing_review:
            flash('You have already reviewed this book.', 'warning')
            return redirect(url_for('books.my_books', book_id=book_id))

        # Add new review
        review = Reviews(
            user_id=current_user.id,
            book_id=book_id,
            rating=form.rating.data,
            review_text=form.review_text.data
        )
        db.session.add(review)
        db.session.commit()

        flash('Your review has been submitted!', 'success')
        return redirect(url_for('books.my_books', book_id=book_id))

    return render_template('review_book.html', form=form, book=book)

@books.route('/review/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Reviews.query.get_or_404(review_id)

    # Ensure the current user is the owner of the review
    if review.user_id != current_user.id:
        flash('You cannot delete this review.', 'danger')
        return redirect(url_for('books.view_book', book_id=review.book_id))

    db.session.delete(review)
    db.session.commit()
    flash('Your review has been deleted.', 'success')

    return redirect(url_for('books.view_book', book_id=review.book_id))

@books.route('/recommendations')
@login_required
def recommendations():
    user_books = User_Read_Books.query.filter_by(user_id=current_user.id).all()
    
    if len(user_books) > 0:
        similar_books = collaborative_recommendations(current_user.id)
        
        if not similar_books:
            # Fallback to API recommendations
            api_books = api_based_recommendations(user_books)
            return render_template('recommendations.html', books=api_books)
        
        return render_template('recommendations.html', books=similar_books)
    else:
        flash("No books in your reading history for recommendations.", "info")
        return redirect(url_for('books.my_books'))
    
def collaborative_recommendations(user_id):
    # Identify books the user has read
    user_books = User_Read_Books.query.filter_by(user_id=user_id).all()
    user_book_ids = [book.book_id for book in user_books]

    # Find other users who have read similar books
    similar_users = User_Read_Books.query.filter(User_Read_Books.book_id.in_(user_book_ids), User_Read_Books.user_id != user_id).all()

    # Create a set to store recommended books
    recommended_books = set()

    # Add books read by similar users, but not yet read by the current user
    for entry in similar_users:
        if entry.book_id not in user_book_ids:
            recommended_books.add(entry.book_id)
    
    # Fetch book details from the Books table
    books = Books.query.filter(Books.book_id.in_(recommended_books)).all()
    return books

def api_based_recommendations(user_books):
    recommendations = []
    
    for user_book in user_books:
        book = Books.query.get(user_book.book_id)
        if book:
            # Use book title and author to search for similar books in Google Books API
            url = "https://www.googleapis.com/books/v1/volumes"
            params = {
                'q': f'intitle:{book.title} inauthor:{book.author}',
                'maxResults': 5,  # Adjust as needed
                'key': google_api_key
            }
            response = requests.get(url, params=params)

            if response.status_code == 200:
                book_data = response.json().get('items', [])
                for item in book_data:
                    recommendations.append({
                        'id': item['id'],
                        'title': item['volumeInfo'].get('title'),
                        'author': ', '.join(item['volumeInfo'].get('authors', [])),
                        'description': item['volumeInfo'].get('description', 'No description available'),
                        'cover_page': item['volumeInfo'].get('imageLinks', {}).get('thumbnail')
                    })
            if len(recommendations) >= 10:  # Stop if enough recommendations are collected
                break

    return recommendations