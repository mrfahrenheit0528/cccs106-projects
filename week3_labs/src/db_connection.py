import mysql.connector

def connect_db():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="fletapp"
    )
    if connection.is_connected():
        return connection
    return None