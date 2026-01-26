from functools import wraps
from flask import request, jsonify
import jwt
from config import SECRET_KEY
from db_connection import get_db_connection

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error":"Authorization header missing"}), 401

        if not auth_header.startswith("Bearer "):
            return jsonify({"error":"Invalid token header"}), 401

        token = auth_header.split(" ")[1]
        if not token:
            return jsonify({"error":"Token is missing"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data["user_id"]
            current_user_role = data["role"]

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, status FROM users WHERE id=%s", (current_user_id,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if not user or user["status"] != "active":
                return jsonify({"error":"Account inactive"}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({"error":"Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error":"Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return f(current_user_id, current_user_role, *args, **kwargs)

    return decorated
