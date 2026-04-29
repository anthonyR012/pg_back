# PonteGlam

Brief project description.

<br>

## Requirements

- Python >= 3.11.2
- PostgreSQL >= 16.1

<br>

## Installation

1. Clone the repository:

    ```bash
    git clone url_repository
    ```

2. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv env
    ```

3. Activate the virtual environment:

    - Windows:

        ```bash
        .\env\Scripts\activate
        ```

    - macOS/Linux:

        ```bash
        source env/bin/activate
        ```

4. Navigate to the project directory:

    ```bash
    cd PonteGlamBackend
    ```

5. Install the dependencies:

    ```bash
    pip install update pip
    pip install -r requirements.txt
    ```

6. Generate and apply migrations
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

7. Run the project:
    ```bash
    python manage.py runserver
    ```

### If it becomes necessary to update the database

1. Delete the current database and recreate it
    ```bash
    sudo su postgres
    psql
    DROP DATABASE dbpg;
    CREATE DATABASE dbpg;
    ```

2. Delete the migration files
    ```bash
    find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
    find . -path "*/migrations/*.pyc" -delete
    ```

3. Generate and apply migrations
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

4. Update the database
    ```bash
    Insertar aqui el comando ...
    ```

<br>

## Usage

Explain how to use the project, for example, how to run the server, how to access the application, etc.

<br>

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
