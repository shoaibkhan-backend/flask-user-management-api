from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import jwt, datetime
from db_connection import get_db_connection 
from config import SECRET_KEY



def register_auth_routes(app):
    #--------------LOGIN ROUTE API--------------------
    @app.route("/login", methods=["POST"])
    def login():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error":"No data provided"}),400
            
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return jsonify({"error":"Email and password required"}),400
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("select * from users where email=%s",(email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if not user:
                return jsonify({"error":"User not found"}),404

            if user ["status"]=="inactive":
                return jsonify({"error":"Account inactive please contact Admin"}),403
            
            if not check_password_hash(user["password"],password):
                return jsonify({"error":"Invalid password"}),401
            
            token = jwt.encode(
                {
                    "user_id": user["id"],
                    "role": user["role"],
                    "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)},
                    SECRET_KEY,
                    algorithm="HS256")
            return jsonify({
                "message": "Login successful", "token": token }),200
        except Exception as e:
            return jsonify({"error":str(e)}),500
        

    #-----------REGISTER ROUTE API------------------
    @app.route("/register", methods=["POST"])
    def register():
        try:

            data = request.get_json()

            if not data:
                return jsonify({"error":"Invalid or missing json"}),400

            name = data.get("name")
            email = data.get("email")
            password = data.get("password")

            
            if not name or not email or not password:
                return jsonify({"error":"All fields are required"}),400
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("select id from users where email=%s",(email,))
            user = cursor.fetchone()        
            if user:
                cursor.close()
                conn.close()
                return jsonify({"error":"Email already exists"}),409
            
            hashed_password = generate_password_hash(password) 

            cursor.execute("insert into users(name, email, password) values(%s, %s, %s)",(name, email, hashed_password))
            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({"message":"User register successfully"}),201
        
        except Exception as e:
            return jsonify({"error":str(e)}),500
    