from flask import request,jsonify
from werkzeug.security import generate_password_hash
from db_connection import get_db_connection
from auth_middleware import token_required


def register_user_routes(app):

     #--------CREATE USER API (POST)-------------
    @app.route("/users", methods=["POST"])
    def create_user():
        try:
            
            data=request.get_json()
            if not data:
                return jsonify({"error":"No data provided"}),400
            name = data.get("name")
            email = data.get("email")
            password = data.get("password")
            age = int(data.get("age") if data.get("age") else None)

            
            if not name or not email or not password:
                return jsonify({"error":"Name email and password required"}),400
            
            hashed_password=generate_password_hash(password)
            
            conn=get_db_connection()
            cursor=conn.cursor()

            cursor.execute("select id from users where email = %s",(email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({"error":"Email already exists"}),409

            query="insert into users(name,email,password,age) values(%s,%s,%s,%s)"
            cursor.execute(query,(name,email,hashed_password,age))
            conn.commit()

            user_id=cursor.lastrowid
            cursor.close()
            conn.close()

            return jsonify({
            "message":"User Created successfully",
            "id": user_id,
            "name":name,
            "email":email,
            "age":age
            }),201
        
        except Exception as e:
            return jsonify({"error":str(e)}),500



    #---------READ ALL USERS API (GET)---------
    @app.route("/users", methods=["GET"])
    @token_required
    def get_users(current_user_id, current_user_role):
        try:
            conn=get_db_connection()
            cursor=conn.cursor(dictionary=True)

            cursor.execute("select id, name, email, age, role, status from users where status='active'")
            users=cursor.fetchall()

            cursor.close()
            conn.close()
            
            return jsonify({
                "count":len(users),
                "users":users
                }), 200
        
        except Exception as e:
            return jsonify({"error":str(e)}),500
        
    #--------- GET inactive USERS (admin only)-----------
    @app.route("/users/inactive", methods=["GET"])
    @token_required
    def inactive_users(current_user_id, current_user_role):
        try:

            if current_user_role != "admin":
                return jsonify({"error":"Only admin access required"})
            
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("select id, name, email, role, status from users where status='inactive'")
            user = cursor.fetchall()

            cursor.close()
            conn.close()

            return jsonify({"users":inactive_users}),200
        
        except Exception as e:
            return jsonify({"error":str(e)}),500


    #----------READ SINGLE USER BY ID API (GET)-------------
    @app.route("/users/<int:user_id>", methods=["GET"])
    @token_required
    def get_user(current_user_id, current_user_role, user_id):
        try:

            conn=get_db_connection()    
            cursor=conn.cursor(dictionary=True)

            cursor.execute("select id, name, email, age, role, status from users where id=%s",(user_id,))
            user=cursor.fetchone()

            cursor.close()
            conn.close()

            if user:
                return jsonify(user),200
            else:    
                return jsonify({
                    "message":"User not found"}), 404
            
        except Exception as e:
            return jsonify({"error":str(e)}),500

        

    #--------------UPDATE USER API (PUT)---------------
    @app.route("/users/<int:user_id>", methods=["PUT"])
    @token_required
    def update_user(current_user_id, current_user_role, user_id):
        try:


            if current_user_role != 'admin' and current_user_id !=user_id:
                return jsonify({"error":"you can update only your account"}),403

            data=request.get_json()
            if not data:
                return jsonify({"error":"No data provided"}),400

            name = data.get("name")
            email = data.get("email")
            password = data.get("password")
            age = int(data.get("age") if data.get("age") else None)
            
            
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("select id from users where id=%s",(user_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({"error":"User not found"}),404
            
            if password:
                password = generate_password_hash(password)
            else:
                cursor.execute("select password from users where id=%s",(user_id,))
                password = cursor.fetchone()[0]

            query = " update users set name=%s, email=%s, password=%s, age=%s where id=%s"
            cursor.execute(query,(name,email,password,age,user_id))
            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({
                "message":"User update successfully",
                "id":user_id,
                "name":name,
                "email":email,
                "age":age     
                }),200
        
        except Exception as e:
            return jsonify({"error":str(e)}),500


    # ------------- PARTIAL UPDATE USER API (PATCH)------------------
    @app.route("/users/<int:user_id>", methods=["PATCH"])
    @token_required
    def partial_update(current_user_id, current_user_role, user_id):
        try:

            if current_user_role != 'admin' and current_user_id !=user_id:
                return jsonify({"error":"you can update only your account"}),403
            
            data = request.get_json()
            if not data:
                return jsonify({"error":"No data provided"}),400
            
            age = int(data.get("age") if data.get("age") else None)
            
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("select id from users where id=%s",(user_id,))

            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({"message":"User not found"}),404
            
            query = "update users set age=%s where id=%s"
            cursor.execute(query,( age, user_id))
            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({
                "message": "Partial user update successfully",
                "id":user_id,
                "age":age
                }),200
        
        except Exception as e:
            return jsonify({"error":str(e)}),500


    #--------------DELETE USER API (DELETE)---------------------
    @app.route("/users/<int:user_id>", methods=["DELETE"])
    @token_required
    def delete_user(current_user_id, current_user_role, user_id):
        try:

            if current_user_id == user_id:
                return jsonify({"error":"Admin cannot delete yourself"}),403

            if current_user_role != 'admin' and current_user_id != user_id:
                return jsonify({"error":"Only admin access required"}),403

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("select id from users where id=%s",(user_id,))
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({"error":"User not found"}),404
            
            cursor.execute("update users set status='inactive' where id=%s",(user_id,))
            conn.commit()

            cursor.close()
            conn.close()

            if current_user_id == user_id:
                return jsonify({"message":"Your Account deactivated. please login again"}),200

            return jsonify({
                "message":"User Account Deactivated Successfully"}),200
        
        except Exception as e:
            return jsonify({"error":str(e)}),500
    
