# how would I test Barky?
# First, I wouldn't test barky, I would test the reusable modules barky relies on:
# commands.py and database.py

# we will use pytest: https://docs.pytest.org/en/stable/index.html

# should we test quit? No, its behavior is self-evident and not logic dependent
def test_quit_command():
    pass

# okay, should I test the other commands?
# # not really, they are tighly coupled with sqlite3 and its use in the database.py module

from database import DatabaseManager
from commands import *
import pytest
import os

@pytest.fixture
def test_db():
    name = "test_bookmarks.db"
    db = DatabaseManager(name)

    yield db

    db.__del__()
    os.remove(name)

@pytest.fixture
def bookmark_data():
    return {
        "title": "Google",
        "url": "https://google.com",
        "notes": "Google Website",
    }

@pytest.fixture
def bookmark_list_data():
    return [
        {
            "title": "Google",
            "url": "https://google.com",
            "notes": "Google Search Engine",
        },
        {
            "title": "Facebook",
            "url": "https://facebook.com",
            "notes": "Facebook SNS",
        },
        {
            "title": "Twitter",
            "url": "https://twitter.com",
            "notes": "Twitter SNS",
        },
    ]


def test_create_bookmarks_table_command(test_db):
    command = CreateBookmarksTableCommand()
    command.execute(_db=test_db)

    con = test_db.connection
    cursor = con.cursor()
    cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='bookmarks' ''')
    assert cursor.fetchone()[0] == 1


def test_add_bookmark_command(test_db, bookmark_data):
    CreateBookmarksTableCommand().execute(_db=test_db)

    ret = AddBookmarkCommand().execute(data=bookmark_data, _db=test_db)
    assert ret == "Bookmark added!"

    bookmarks = test_db.select("bookmarks").fetchall()
    assert len(bookmarks) == 1

    [bookmark] = bookmarks
    # 0: id, 1: title, 2: url, 3: notes, 4: date
    assert bookmark[1] == bookmark_data.get('title')
    assert bookmark[2] == bookmark_data.get('url')
    assert bookmark[3] == bookmark_data.get('notes')


def test_list_bookmarks_command(test_db, bookmark_list_data):
    CreateBookmarksTableCommand().execute(_db=test_db)
    for bookmark in bookmark_list_data:
        AddBookmarkCommand().execute(data=bookmark, _db=test_db)

    command = ListBookmarksCommand()
    bookmarks = command.execute(_db=test_db)

    assert len(bookmarks) == len(bookmark_list_data)


def test_delete_bookmark_command(test_db, bookmark_data):
    CreateBookmarksTableCommand().execute(_db=test_db)
    AddBookmarkCommand().execute(data=bookmark_data, _db=test_db)

    saved_bookmarks = ListBookmarksCommand().execute(_db=test_db)
    assert len(saved_bookmarks) == 1

    id = saved_bookmarks[0][0]
    ret = DeleteBookmarkCommand().execute(data=id, _db=test_db)
    assert ret == "Bookmark deleted!"

    assert len(ListBookmarksCommand().execute(_db=test_db)) == 0


# # Update is not implemeted in DB Manager!!
# def test_edit_bookmark_command(test_db, bookmark_data):
#     CreateBookmarksTableCommand().execute(_db=test_db)
#     AddBookmarkCommand().execute(data=bookmark_data, _db=test_db)
#     saved_bookmarks = ListBookmarksCommand().execute(_db=test_db)

#     update_data = {
#         "id": saved_bookmarks[0][0],
#         "update": {
#             "url": "https://www.google.com",
#         }
#     }
#     command = EditBookmarkCommand()
#     modified_bookmarks = command.execute(data=update_data, _db=test_db)
#     print(modified_bookmarks)


