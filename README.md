⁸# Flask User Management API

A secure and modular **Flask REST API** for managing users, authentication, and roles.  
Implements **JWT login**, **role-based access control (Admin/User)**, **soft delete & restore**, and **forgot/reset password workflow**.



## Features

- User Registration & Login  
- JWT Authentication  
- Role-Based Access Control (Admin / User)  
- User CRUD Operations  
- Soft Delete & Restore Users  
- Forgot & Reset Password  
- Password Hashing using Werkzeug  
- Modular Project Structure  
- Environment-based Configuration (`.env`)



##  User Roles

- **Admin**: Full access to manage users, assign roles, soft delete & restore  
- **User**: Can view and update own profile, limited access



##  Tech Stack

Python | Flask | MySQL | JWT | Werkzeug | VS Code | Postman | Git 


## API Endpoints

### Authentication
- POST `/register`  → Register new user
- POST `/login`     → Login and generate JWT token

### Users
- GET `/users`              → Get all users (Admin only)
- GET `/users/<id>`         → Get user by id
- PUT `/users/<id>`         → Update user
- DELETE `/users/<id>`      → Soft delete user

### Restore
- PUT `/restore/<id>`       → Restore deleted user (Admin only)

### Password
- POST `/forgot-password`   → Forgot password request
- POST `/reset-password`    → Reset password

  

##  Project Structure

```txt
FLASK_USER_MANAGEMENT/
├── routes/
│   ├── auth.py
│   ├── users.py
│   ├── forgot_password.py
│   └── restore.py
├── app.py
├── auth_middleware.py
├── config.py
├── db_connection.py
├── requirements.txt
├── .env
└── .gitignore
