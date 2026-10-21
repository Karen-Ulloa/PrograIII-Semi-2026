import mysql.connector

def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_academica"
    )
    return conexion
