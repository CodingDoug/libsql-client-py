=========
Reference
=========

--------------
Asyncio client
--------------

.. function:: create_client(url, *, auth_token=None)

   :param url: Database URL
   :type url: str
   :param auth_token: Optional authentication token (JWT)
   :type auth_token: Optional[str]
   :rtype: :class:`Client`

   Creates an asynchronous client for connecting to a database. This library supports multiple approaches for
   connecting to the database, which are distinguished by the scheme (protocol) in the URL:

   * ``file:`` connects to a local SQLite database (using the builtin ``sqlite3`` package)

      * ``file:/absolute/path`` or ``file:///absolute/path`` is an absolute path on local filesystem
      * ``file:relative/path`` is a relative path on local filesystem
      * (``file://path`` is not a valid URL)

   * ``ws:`` or ``wss:`` connect to sqld using WebSockets (the Hrana protocol).
   * ``http:`` or ``https:`` connect to sqld using HTTP. The :meth:`Client.transaction()` API is not
     available in this case.
   * ``libsql:`` is equivalent to ``wss:``.

   Usage example::

      # Connect to a local SQLite database in a file
      client = libsql_client.create_client("file:local.db")

      # Connect to sqld using WebSockets
      client = libsql_client.create_client("ws://localhost:8080")

      # Connect to sqld using HTTPS and authenticate with a token
      client = libsql_client.create_client("https://my-db.example.com", auth_token=TOKEN)

   You should always call :meth:`Client.close()` on the returned :class:`Client` to release resources
   associated with the database connection. You can also use an `async with` statement with the client::

      async with libsql_client.create_client("file:local.db") as client:
         ...

.. class:: Client

   An opened database is represented by a ``Client`` object, which is created by :func:`create_client()`. This
   is an abstract class, the concrete instance depends on the URL that you pass to ``create_client()``.

   You should always close the client by calling :meth:`close()` or by using an ``async with`` statement.

   .. method:: execute(stmt, args=None)
      :async:

      :param stmt: SQL statement to execute
      :type stmt: :data:`InStatement`
      :param args: Optional SQL arguments to the statement
      :type args: :data:`InArgs`
      :return: The result set produced by the statement
      :rtype: :class:`ResultSet`

      Executes a single statement and returns the result. If you need to execute multiple statements, consider
      using :meth:`batch()` or :meth:`transaction()`.

   .. method:: batch(stmts)
      :async:

      :param stmts: List of SQL statements to execute
      :type stmts: List[:data:`InStatement`]
      :return: List of results from the statements
      :rtype: List[:class:`ResultSet`]

      Executes a batch of statements in a transaction and returns the results. If any of the statements fails,
      the transaction is rolled back and this method throws an exception.

   .. method:: transaction()

      :rtype: :class:`Transaction`

      Starts an interactive transaction and returns a :class:`Transaction` object, which you can use to
      execute statements in the transaction.

   .. method:: close()
      :async:

      :rtype: None

      Closes the client and releases resources.

   .. property:: closed

      :type: bool

      Indicates whether the client has been closed.

.. class:: Transaction

   A ``Transaction`` object refers to an interactive transaction. You can open a transaction using
   :meth:`Client.transaction()`.

   You should always close the transaction by calling :meth:`commit()`, :meth:`rollback()` or :meth:`close()`,
   or by using a ``with`` statement. If you don't :meth:`commit()` the transaction, the changes will be rolled
   back automatically.

   .. method:: execute(stmt, args=None)
      :async:

      :param stmt: SQL statement to execute
      :type stmt: :data:`InStatement`
      :param args: Optional SQL arguments to the statement
      :type args: :data:`InArgs`
      :return: The result set produced by the statement
      :rtype: :class:`ResultSet`

      Executes a statement in the transaction and returns the result.

   .. method:: commit()
      :async:

      :rtype: None

      Commits the transaction to the database and closes the transaction.

   .. method:: rollback()
      :async:

      :rtype: None

      Rolls back the transaction and closes it.

   .. method:: close()

      :rtype: None

      Closes the transaction. If the transaction has not been committed with :meth:`commit()`, it will be
      rolled back.

   .. property:: closed

      :type: bool

      Indicates whether the transaction has been closed.

------------------
Synchronous client
------------------

For very simple use cases, we also provide a synchronous version of the client. It is a thin wrapper around
the ``asyncio``-based :class:`Client`, but it runs the event loop in a background thread and provides blocking
APIs. The sync client is thread-safe, it can be accessed from multiple threads concurrently.

.. function:: create_client_sync(url, *, auth_token=None)

   :param url: Database URL
   :type url: str
   :param auth_token: Optional authentication token (JWT)
   :type auth_token: Optional[str]
   :rtype: :class:`ClientSync`

   Creates a synchronous client for connecting to a database. This is the same as :func:`create_client()`, but
   it returns an instance of :class:`ClientSync`.

.. class:: ClientSync

   A synchronous version of :class:`Client`. It provides the same methods, but they will block the current
   thread until they complete.

   You should always close the client by calling :meth:`close()` or by using a ``with`` statement.

   .. method:: execute(stmt, args=None)

      :param stmt: SQL statement to execute
      :type stmt: :data:`InStatement`
      :param args: Optional SQL arguments to the statement
      :type args: :data:`InArgs`
      :return: The result set produced by the statement
      :rtype: :class:`ResultSet`

      Executes a single statement and returns the result. If you need to execute multiple statements, consider
      using :meth:`batch()` or :meth:`transaction()`.

   .. method:: batch(stmts)

      :param stmts: List of SQL statements to execute
      :type stmts: List[:data:`InStatement`]
      :return: List of results from the statements
      :rtype: List[:class:`ResultSet`]

      Executes a batch of statements in a transaction and returns the results. If any of the statements fails,
      the transaction is rolled back and this method throws an exception.

   .. method:: transaction()

      :rtype: :class:`TransactionSync`

      Starts an interactive transaction and returns a :class:`TransactionSync` object, which you can use to
      synchronously execute statements in the transaction.

   .. method:: close()

      :rtype: None

      Closes the client and releases resources.

   .. property:: closed

      :type: bool

      Indicates whether the client has been closed.

.. class:: TransactionSync

   A ``TransactionSync`` is analogous to :class:`Transaction`, but it provides a synchronous API. You can open
   a transaction using :meth:`ClientSync.transaction()`.

   You should always close the transaction by calling :meth:`commit()`, :meth:`rollback()` or :meth:`close()`,
   or by using a ``with`` statement. If you don't :meth:`commit()` the transaction, the changes will be rolled
   back automatically.

   .. method:: execute(stmt, args=None)

      :param stmt: SQL statement to execute
      :type stmt: :data:`InStatement`
      :param args: Optional SQL arguments to the statement
      :type args: :data:`InArgs`
      :return: The result set produced by the statement
      :rtype: :class:`ResultSet`

      Executes a statement in the transaction and returns the result.

   .. method:: commit()

      :rtype: None

      Commits the transaction to the database and closes the transaction.

   .. method:: rollback()

      :rtype: None

      Rolls back the transaction and closes it.

   .. method:: close()

      :rtype: None

      Closes the transaction. If the transaction has not been committed with :meth:`commit()`, it will be
      rolled back.

   .. property:: closed

      :type: bool

      Indicates whether the transaction has been closed.

----------
Statements
----------

.. data:: InStatement

   You can pass the following as a statement to the :class:`Client` and :class:`Transaction`:

   * ``str``: a SQL statement without arguments::

      "SELECT * FROM book"

   * ``Tuple[str, InArgs]``: a pair of the SQL statement and :data:`arguments <InArgs>` 
     (passed by position or by name)::

      ("SELECT * FROM book WHERE published < ? AND author = ?", [1940, "Agatha Christie"])
      ("SELECT * FROM book WHERE published < $year", {"year": 1850})

   * :class:`Statement` object::

      libsql_client.Statement("SELECT ? + ?", [2, 3])

.. data:: InArgs

   SQL statements can contain `parameters <https://www.sqlite.org/lang_expr.html#parameters>`_, which act as
   placeholders for values. The values are passed as arguments, either by position or by name:

   * Use a list or a tuple to pass arguments by position::

      (1, "two", 3.0)
      ["some", "arguments"]

   * Use a dict to pass arguments by name::

      {"foo": 10, "bar": "baz"}

.. class:: Statement(sql, args=None)

   :param sql: Text of the SQL statement
   :type sql: str
   :param args: Arguments to the statement
   :type args: :data:`InArgs`

   This class can be used to pass a statement to :class:`Client` or :class:`Transaction`, instead of using a
   tuple.

-------
Results
-------

.. class:: ResultSet

   ``ResultSet`` stores the result of executing a SQL statement. This object behaves like a sequence of
   :class:`Row`-s, it supports indexing and iteration.

   .. property:: rows

      :type: List[Row]

      List of :class:`Row`-s produced by the statement.

   .. property:: columns

      :type: Tuple[str, ...]

      Tuple of column names. For columns without an explicit ``AS`` clause, the column name is unspecified.

   .. property:: rows_affected

      :type: int

      Number of rows that were changed by the statement. This is only meaningful for INSERT, UPDATE and DELETE
      statements.

   .. property:: last_insert_rowid

      :type: Optional[int]

      ROWID of the last successful insert into a rowid table.

   .. describe:: rs[i]

      Returns the :class:`Row` at index ``i``

   .. describe:: rs[i:j]

      Returns a list of :class:`Row`-s from index ``i`` to ``j``.

   .. describe:: len(rs)

      Returns the number of rows in the result set.

   .. describe:: for row in rs

      Iterates over :class:`Row`-s in the result set.

.. class:: Row

   ``Row`` represents one row returned by a SQL statement.

   .. describe:: row[key]

      Returns the value of one column by ``key``. The key can be either an integer (to return a column by
      position, indexed from 0) or a string (to return a column by name).

   .. describe:: row[i:j]

      Returns a tuple of column values with indexes in range ``i:j``.

   .. describe:: len(row)

      Returns the number of columns in this row.

   .. method:: astuple()

      :rtype: Tuple[:data:`Value`, ...]

      Returns the values in the row as a tuple.

   .. method:: asdict()

      :rtype: Dict[str, :data:`Value`]

      Returns the values in the row in a dict where keys are column names.
   
------
Values
------

.. data:: Value

   SQLite values are mapped to Python as follows:

   - ``TEXT`` is converted to a Python ``str``
   - ``INTEGER`` is converted to a Python ``int``
   - ``FLOAT`` is converted to a Python ``float``
   - ``BLOB`` is converted to a Python ``bytes``
   - ``NULL`` is converted to ``None``

   Conversion from Python to SQLite is analogous, but the library also supports the following Python data types:

   - ``datetime.datetime`` is converted to an integer that represents the Unix timestamp in milliseconds
   - ``True`` and ``False`` are converted to integers ``1`` and ``0``, respectively

   Non-finite float values (infinity and NaN) are not supported, you will get a `ValueError` if you try to pass
   them to the database as arguments. Also, the SQLite ``INTEGER`` type is a signed 64-bit integer, so if you
   pass a Python ``int`` that is out of range (smaller than ``-2**63`` or greater than ``2**63-1``), you will get
   an ``OverflowError``.

----------
Exceptions
----------

.. exception:: LibsqlError

   All operations in this library can throw a ``LibsqlError``, which is derived from ``RuntimeError``.

   .. property:: code

      :type: str

      Machine-readable error code that identifies the kind of error.
