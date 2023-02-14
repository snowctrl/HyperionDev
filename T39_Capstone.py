import pandas as pd
import sqlite3

CSV = 'initial books'
SQL = 'ebookstore.sqlite'



def display_Books():
    '''Display 'Books' table with Dataframe formatting'''
    try:
        db = sqlite3.connect(SQL)                                   # Create/connect to dBase
        r_df = pd.read_sql("SELECT * FROM Books ORDER BY Id", db)   # read into Dataframe
        print(r_df.to_string(index=False))                          # ... so it displays as table
        del r_df

    except Exception as e:
        print(f'Error reading Books table from SQL!!')
        db.rollback()
        raise e
    finally:
        db.close()
   



def create_table():
    '''Creates 'Books' table if it is yet to exist'''

    try:
        db = sqlite3.connect(SQL)                                                       # connect to SQL
        cursor = db.cursor()                                                            # get SQL cursor
        cursor.execute('''SELECT name FROM sqlite_schema WHERE type='table' ''')        # get all tables
        if cursor.fetchall() == []:                                                     # if there are none, create 'Books' table
            cursor.execute('CREATE TABLE Books (Id char(4) PRIMARY KEY, Title VarChar, Author VarChar, Qty Int)')
            print('New eBookstore created')                                             # ... and let User know
            db.commit()                                                                 # commit changes

    except Exception as e:
        db.rollback()                                                                   # rollback changes if errors
        raise e                                                                         # ... and then display error once db is safe
    finally:
        db.close()                                                                      # always close the db



def add_books_from_csv(csv):
    '''Adds books from supplied .csv, if they have yet to be entered'''

    # Import books from .csv file to be added   
    new_books = pd.read_csv(f'{csv}.csv')                   # read the books from CSV into dataframe

    for book in range(new_books.shape[0]):                  # iterate through new book records

        id = str(new_books.iloc[book].Id)
        if not check_id(id, output=False):                  # if Id already present in table, skip this record
            continue

        title = new_books.iloc[book].Title
        author = new_books.iloc[book].Author
        if not check_book(title, author, output=False):     # if title/author combo already present in table, skip this record
            continue

        qty = int(new_books.iloc[book].Qty)                 

        book_to_insert = (id, title, author, qty)
        insert_book(book_to_insert)                         # insert new (checked) record into table

    del new_books                                           # lose the dataframe



def insert_book(insert_me):
    '''Inserts supplied book into Books table'''

    try:
        db = sqlite3.connect(SQL)         
        cursor = db.cursor()                                # Inserts supplied book into Books table
        cursor.execute(f'INSERT INTO Books (Id, Title, Author, Qty) VALUES (?,?,?,?)', (insert_me))
        print(f'Inserted book {insert_me}')                 # ... and display details of inserted book
        db.commit()

    except Exception as e:
        print(f'Error inserting book: {insert_me}')
        db.rollback()
        raise e
    finally:
        db.close()



def check_id(Id_to_check, output=True):
    '''Returns True if supplied ID is new, or False if known: if False, displays Book unless output=False'''

    try:
        db = sqlite3.connect(SQL) 
        cursor = db.cursor()
        cursor.execute('SELECT * FROM Books WHERE Id=(?)', (Id_to_check,))  # checks for presence of supplied Id in Books table
        fetched = cursor.fetchall()                                         # ... and gets the result
        if fetched == []:                                                   # If result is empty, Id has not already been used
            good = True
        else:            
            if output: print(f'That Id number is in use: {fetched}')        # ... otherwise warn user
            good = False

    except Exception as e:
        print(f'Error checking ID: {Id_to_check}')
        db.rollback()
        raise e
    finally:
        db.close()

    return good                                                             # return whether or not the supplied Id is 'good' to go



def check_book(title, author, output=True):
    '''Returns True if supplied author/title combo are new, or False if known: if False, displays Book unless output=False'''

    try:
        db = sqlite3.connect(SQL) 
        cursor = db.cursor()                                                # Checks for presence of supplied book ie author/title combo
        cursor.execute('SELECT * FROM Books WHERE (Title, Author) = (?,?)', (title, author,))   
        fetched = cursor.fetchall()                                         # ... and gets the result
        if fetched == []:                                                   # If result is empty, this book is not already listed in Books
            good = True
        else:
            if output: print(f'That book is already listed: {fetched.to_string(index=False)}')  # otherwise warn user
            good = False

    except Exception as e:
        print(f'Error checking Book: {title}, by {author}')
        db.rollback()
        raise e
    finally:
        db.close()

    return good                                                             # return whether or not the supplied book is 'good' to go



def get_valid_Id():
    """get from user valid Id"""
    while True:
        id = input('ID\t: ')
        if len(id) == 4 and id.isnumeric():                                 # checks for correct string length and that only digits are entered
            break
        print('ID values are 4 digits, for example \'0123\'') 
    return id


def get_valid_Title():
    '''get from user valid Title'''
    return input('Title\t: ').strip().replace("\'", "\'\'")                 # removes excess spaces and substitues apostrophes for double apostrophes for SQL


def get_valid_Author():
    '''get from user valid Author'''
    return input('Author\t: ').strip().replace("\'", "\'\'")                # removes excess spaces and substitues apostrophes for double apostrophes for SQL


def get_valid_Qty():
    """get from user valid Qty"""
    while True:
        try:
            qty = int(input('Quantity: '))                                  # gets integer
            if qty >= 0:                                                    # and ensures it is not negative
                break
        except:
            print('For book quantity please enter a positive numeric integer in digits')
    return qty



def enter_book():
    '''Allow user to add a new book to the eBookstore'''
    print('\nPlease enter details of book to be added to the eBookstore:')

    while True:
        id = get_valid_Id()                                                 # gets a valid new ID from user
        if check_id(id): break                                              # ... and checks it is not already in the dBase

    while True:
        title = get_valid_Title()                                           # gets a valid book title from user
        author = get_valid_Author()                                         # gets a valid book author from user
        if check_book(title, author): break                                 # ... and checks they do not form a known book
    
    qty = get_valid_Qty()
    book_to_insert = (id, title, author, qty)
    insert_book(book_to_insert)                                             # inserts new valid book record into dBase



def update_book():
    '''Allow user to update a book in the eBookstore'''
    book = search_books('Update by')                                        # gets book to be updated from user

    if len(book) == 0: return                                               # returns to main menu if user search returns no books

    if len(book) > 1:                                                       # warns user and returns to main menu if search returns multiple books
        print('Search returned mutliple results.\nPlease choose a single book to update.')
        return
 
    field, value = get_search(action='Choose field to update, from')        # gets field to update from user

    if field == 'Id':                                                       # if Id is to be updated
        if not check_id(value): return                                      # return to Main Menu if chosen Id is not in dBase 
    elif field == 'Title':                                                  # etc
        if not check_book(field, book.Author.to_string(index=False)): return
    elif field == 'Author':
        if not check_book(book.Title.to_string(index=False), field): return

    query = f'UPDATE Books SET {field} = ? WHERE Id = ?'                    # create query (secure since 'field' is not user entered) to Update chosen book
    values = (value, book.Id.to_string(index=False))                        # create values for query

    try:
        db = sqlite3.connect(SQL)
        cursor = db.cursor()
        cursor.execute(query, values)                                       # perform update on dBase

        print(f'\n\nBook:\n{book.to_string(index=False)}\nupdated to')
        q = db.execute('SELECT * FROM Books WHERE id = ?', (value,))
        r_df = pd.DataFrame.from_records(q.fetchall(), columns=['Id', 'Title', 'Author', 'Qty']) 
        db.commit()
        print(f'{r_df.to_string(index=False)}\n')                           # and tell user changes (which requires a further query since UPDATE returns nothing)
        del r_df

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
   


def delete_book():
    '''Allow user to delete a book from the eBookstore'''

    book_to_delete = search_books('Delete by')                              # get book to be deleted from user

    if len(book_to_delete) == 0: return                                     # returns to main menu if user search returns no books

    if len(book_to_delete) > 1:                                             # warns user and returns to main menu if search returns multiple books
        print('Search returned mutliple results.\nPlease choose a single book to delete.')
        return
    while True:                                                             # get final confirmation from user before book is deleted
        ui = input('Delete book?  Please confirm (Y/N): ')
        if ui.upper() == 'N': return
        elif ui.upper() == 'Y': break

    try:
        db = sqlite3.connect(SQL)
        cursor = db.cursor()                                                # delete book, and tell user the details of the deleted book
        cursor.execute('DELETE FROM Books WHERE Id = ?', (book_to_delete.iloc[0,0],))       
        print(f"\nBook:\t{book_to_delete.to_string(index=False, header=False)}\tdeleted\n")
        db.commit()
        del book_to_delete

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()



def get_search(action='Search'):
    """Returns Field and Term pair from user"""

    fields = {'I':'Id', 'T':'Title', 'A':'Author', 'Q':'Qty'}               # dict of user inputs for the fields in the Books table

    while True:
        ui = input(f'{action} ID, Title, Author, Quantity? (I/T/A/Q): ')    # get user choice of fields
        try:
            field = fields[ui.upper()]
            break
        except:
            print('Please choose by entering I, T, A, Q')

    exec_str = "term = get_valid_" + field + '()'                           # call user choice of search function
    exec(exec_str, globals())                       

    return field, term                                                      # return user chosen field and term/value for that table field 



def search_books(action='Search'):
    '''Allows user to search the eBookstore'''
    field, term = get_search(action)                                        # get field and value from user

    db = sqlite3.connect(SQL)

    query = f'SELECT * FROM Books WHERE {field} = ?'                        # assemble query to get data from users choice of field (field is program generated, so this is secure)
    q = db.execute(query, (term,))                                          # execute query with user search term

    cols = [column[0] for column in q.description]                          # get column values from Books table (we could just use ['Id', 'Title', 'Author', 'Qty'] :)
    r_df = pd.DataFrame.from_records(data = q.fetchall(), columns=cols)     # read result into dataframe so it displays well easily etc

    if len(r_df) != 0:                                                      # display search result if anything returned
        print(f'\n{r_df.to_string(index=False)}\n')          
    else:                                                                   # ... else warn user nothing was found
        print('Search returned no results.\n')

    return r_df                                                             # return results as dataframe
    


### MAIN LOOP ###
create_table()                                          # Create the SQL table 'books' if it does not already exist
add_books_from_csv(CSV)                                 # Add initial selection of books from .csv, if they're not already present 

while True:

    print('\n1. Enter book\n\n2. Update book\n\n3. Delete book\n\n4. Search books\n\n0. Exit')
    ui = input()

    if ui == '0': break

    if ui == '1':
        print('\nChosen: ADD book to eBookstore')     
        enter_book()

    elif ui == '2':
        print('\nChosen: UPDATE book')
        update_book()

    elif ui == '3':
        print('\nChosen: DELETE book from eBookstore')
        delete_book()

    elif ui == '4':
        print('\nChosen: SEARCH eBookstore')
        search_books()

    elif ui == 'd': display_Books()                     # debug :)
