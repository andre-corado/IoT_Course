import mysql.connector

try:
    # Conectar al servidor MySQL sin especificar base de datos
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin"
    )
    cursor = conn.cursor()

    # Eliminar la base de datos 'test' si existe
    cursor.execute("DROP DATABASE IF EXISTS sensores_sistema")
    conn.commit()
    print("Base de datos 'sensores_sistema' eliminada con éxito.")

except mysql.connector.Error as err:
    print("Error:", err)

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
