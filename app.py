from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from datetime import date

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'library_user'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'library_db'

mysql = MySQL(app)

# -----------------------
# Books CRUD Operations (Example)
# -----------------------
@app.route('/books', methods=['GET'])
def get_books():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM books")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)
@app.route('/books', methods=['POST'])
def add_book():
    title = request.json.get('title')
    author = request.json.get('author')
    published_date = request.json.get('published_date')

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO books (title, author, published_date) VALUES (%s, %s, %s)", (title, author, published_date))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Book added successfully"})

@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    # Logic to fetch the book with the given id from the database
    # Ensure the correct query and handling is in place to retrieve the book data
    # Example:
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM books WHERE id = %s", (id,))
    book = cur.fetchone()
    cur.close()
    if book:
        return jsonify(book)
    else:
        return jsonify({"error": "Book not found"}), 404

@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    # Logic to update the book with the given id in the database
    # Ensure the correct query and handling is in place to update the book data
    # Example:
    title = request.json['title']
    author = request.json['author']
    published_date = request.json['published_date']  # Ensure this field exists in your JSON data

    cur = mysql.connection.cursor()
    cur.execute("UPDATE books SET title = %s, author = %s, published_date = %s WHERE id = %s", (title, author, published_date, id))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Book updated successfully"})

@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    # Delete transactions related to the book
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM transactions WHERE book_id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    # Delete the book itself
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM books WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Book deleted successfully"})


# -----------------------
# Borrowers CRUD Operations
# -----------------------
@app.route('/borrowers', methods=['GET'])
def get_borrowers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM borrowers")
    data = cur.fetchall()
    cur.close()
    return jsonify(data)

@app.route('/borrowers/<int:id>', methods=['GET'])
def get_borrower(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM borrowers WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()
    return jsonify(data)

@app.route('/borrowers', methods=['POST'])
def add_borrower():
    name = request.json['name']
    contact = request.json['contact']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO borrowers (name, contact) VALUES (%s, %s)", (name, contact))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Borrower added successfully"})

@app.route('/borrowers/<int:id>', methods=['PUT'])
def update_borrower(id):
    name = request.json['name']
    contact = request.json['contact']

    cur = mysql.connection.cursor()
    cur.execute("UPDATE borrowers SET name = %s, contact = %s WHERE id = %s", (name, contact, id))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Borrower updated successfully"})

@app.route('/borrowers/<int:id>', methods=['DELETE'])
def delete_borrower(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM borrowers WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Borrower deleted successfully"})

# -----------------------
# Transactions CRUD Operations
# -----------------------
# Format date function
def format_date(date):
    if date:
        return date.strftime('%Y-%m-%d')
    else:
        return None

# CRUD Operations

# Get all transactions
@app.route('/transactions', methods=['GET'])
def get_transactions():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM transactions")
    data = cur.fetchall()
    cur.close()

    transactions = []
    for transaction in data:
        transactions.append({
            'id': transaction[0],
            'book_id': transaction[1],
            'borrower_name': transaction[2],
            'borrow_date': format_date(transaction[3]),
            'transaction_date': format_date(transaction[4])
        })

    return jsonify(transactions)



# Get a single transaction by ID
@app.route('/transactions/<int:id>', methods=['GET'])
def get_transaction(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM transactions WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()

    if data:
        transaction = {
            'id': data[0],
            'book_id': data[1],
            'borrower_name': data[2],
            'borrow_date': data[3].strftime('%Y-%m-%d'),  # Format date as YYYY-MM-DD
            'transaction_date': data[4].strftime('%Y-%m-%d') if data[4] else None  # Format or handle null date
        }
        return jsonify(transaction)
    else:
        return jsonify({'message': 'Transaction not found'}), 404

@app.route('/transactions', methods=['POST'])
def add_transaction():
    if request.method == 'POST':
        data = request.get_json()
        book_id = data['book_id']
        borrower_name = data['borrower_name']
        borrow_date = data.get('borrow_date', date.today().isoformat())  # Default to current date if not provided

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO transactions (book_id, borrower_name, borrow_date, transaction_date) VALUES (%s, %s, %s, CURDATE())", (book_id, borrower_name, borrow_date))
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Transaction added successfully"}), 201


# Update a transaction
@app.route('/transactions/<int:id>', methods=['PUT'])
def update_transaction(id):
    data = request.get_json()
    book_id = data.get('book_id')
    borrower_name = data.get('borrower_name')
    borrow_date = data.get('borrow_date')
    transaction_date = data.get('transaction_date')

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE transactions
        SET book_id = %s, borrower_name = %s, borrow_date = %s, transaction_date = %s
        WHERE id = %s
    """, (book_id, borrower_name, borrow_date, transaction_date, id))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Transaction updated successfully'})

# Delete a transaction
@app.route('/transactions/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM transactions WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Transaction deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)