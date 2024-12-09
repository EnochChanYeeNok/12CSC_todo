# Flask-based Todo List Application

## Authentication Flow
- Users start at the auth page where they can login or signup.
- Passwords are securely hashed using SHA256.
- After successful login, a cookie is set with the user's ID.

## Main Features
### Home Page
- View todo items.
- View closed/completed items.
- Add new items.
- Logout.

### Task Management
- Users can create new tasks via a simple form.
- Tasks can be viewed in two tables:
  - Open/active items.
  - Closed/completed items.
- Each task has an edit button for modifications.

## Security
- Protected routes using a `login_required` decorator.
- Database interactions using SQLite.
- Secure password storage.

## Project Structure
The app follows a clean separation between routes (`todo.py`) and templates (HTML files), with consistent styling through CSS files. The interface is straightforward and user-friendly, making it easy to manage daily tasks.
