from flask import jsonify
from db_connection import get_db_connection
from auth_middleware import token_required

def register_restore_routes(app):

    @app.route("/users/<int:user_id>/restore", methods=["PUT"])
    @token_required
    def restore_user(current_user_id, current_user_role, user_id):

        if current_user_role != "admin" and current_user_id != user_id:
            return jsonify({"error":"Only admin access required"}),403
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("select status from users where id=%s",(user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error":"User not found"}),404
         
        if user["status"] == "active":
            return jsonify({"error":"User already active"}),400
        
        cursor.execute("update users set status='active' where id=%s",(user_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message":"User restore successfully"}),200
        


        
