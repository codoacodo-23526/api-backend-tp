from flask import Flask, request, jsonify

from flask_cors import CORS

import mysql.connector

app = Flask(__name__)
CORS(app) #ESTO HABILITA CORS PARA TODAS LAS RUTAS

class Catalogo:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host = host,
            user = user,
            password = password
        )
        self.cursor = self.conn.cursor()
        
        self.cursor.execute(f"USE `{database}`")
        
            
    def agregar_producto(self, nombre, precio, stock):
        sql = "INSERT INTO `db-tpf`.`productos` (`nombre`, `precio`, `stock`) VALUES ('" + nombre + "', " + precio + ", " + stock + ");"
    
        self.cursor.execute(sql)
        self.conn.commit()
        return True
            
    def eliminar_producto():
        return None
        
    def modificar_producto():
        return None
        
    def modificar_producto():
        return None
        
    def traer_producto():
        return None
  

# PROGRAMA PRINCIPAL

catalogo = Catalogo(host='localhost', user='root', password='', database='db-tpf')

@app.route("/productos", methods=["POST"])
def agregar_producto():
    
    nombre = request.form['nombre']
    precio = request.form['precio']
    stock = request.form['stock']
    
    si_se_agrego = catalogo.agregar_producto(nombre, precio, stock)
    if si_se_agrego:
        return jsonify({"mensaje": "producto agregado"}), 200
    else:
       return jsonify({"mensaje": "Error"}), 400

    

if __name__ == '__main__':
    app.run(port=4000, debug=True)