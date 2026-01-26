from flask import Flask
from routes.auth import register_auth_routes
from routes.users import register_user_routes
from routes.restore import register_restore_routes
from routes.forgot_password import register_password_routes

app=Flask(__name__)

register_auth_routes(app)
register_user_routes(app)
register_restore_routes(app)
register_password_routes(app)

if __name__=="__main__":
    app.run(debug=True, port=5000)

