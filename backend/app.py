
from flask import Flask, jsonify
from database import get_db_connection
from routes.orders import orders_bp

app = Flask(__name__)
app.register_blueprint(orders_bp)

@app.route("/")
def home():
    return jsonify({
        "message": "F-commerce Growth AI Backend is Running!",
        "status": "Success"
    })


@app.route("/test-db")
def test_database():
    connection = get_db_connection()

    if connection:
        connection.close()
        return jsonify({
            "message": "MySQL Database Connected Successfully!",
            "status": "Success"
        })

    return jsonify({
        "message": "Database Connection Failed!",
        "status": "Error"
    }), 500
if __name__ == "__main__":
    app.run(debug=True)
