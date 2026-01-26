import uuid
from datetime import datetime, timedelta
from flask import request, jsonify
from db_connection import get_db_connection
from werkzeug.security import generate_password_hash


def register_password_routes(app):

    #------------FORGOT-PASSWORD API------------
    @app.route("/forgot-password", methods=["POST"])
    def forgot_password():

        data = request.get_json()        
        email = data.get("email")

        if not email:
            return jsonify({"error": "Email required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("select id from users where email=%s",(email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error":"User not found"})
        
        reset_token = str(uuid.uuid4())
        reset_expiry = datetime.now() + timedelta(minutes=10)

        cursor.execute(" update users set reset_token=%s, reset_token_expiry=%s where email=%s",
        (reset_token, reset_expiry, email))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Password reset token generated",
            "reset_token": reset_token}),200
    

    #--------------RESET PASSWORD API----------------
    @app.route("/reset-password", methods=["POST"])    
    def reset_password():

        data = request.get_json()
        if not data:
            return jsonify({"error":"data not provided"})
        
        token = data.get("token")
        new_password = data.get("new_password")

        if not token or not new_password:
            return jsonify({"error": "Token and new password required"}),400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check token
        cursor.execute("select id, reset_token_expiry from users where reset_token=%s", (token,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "Invalid token"}),400

        # Check expiry
        if datetime.now() > user["reset_token_expiry"]:
            return jsonify({"error": "Token expired"}),400

        # Hash new password + update
        hashed_password = generate_password_hash(new_password)
        cursor.execute(" update users set password=%s, reset_token=null, reset_token_expiry=null where id=%s", (hashed_password, user["id"]))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Password reset successful"}),200
