from flask import Flask, request, jsonify

from flask_cors import CORS

import mysql.connector

from werkzeug.utils import secure_filename # ESTO ES PARA QUE EL NOMBRE DE LA IMAGEN NO TENGA CARACTERES RAROS

import os
import time

app = Flask(__name__)
CORS(app) #ESTO HABILITA CORS PARA TODAS LAS RUTAS

# CLASE CATALOGO
class Catalogo:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host = host,
            user = user,
            password = password
        )
        self.cursor = self.conn.cursor()
        
        self.cursor.execute(f"USE `{database}`")
        
            
    def agregar_producto(self, nombre, precio, stock, imagen):
        #sql = "INSERT INTO `db-tpf`.`productos` (`nombre`, `precio`, `stock`) VALUES ('" + nombre + "', " + precio + ", " + stock + ");"
        sql = "INSERT INTO `db-tpf`.`productos` (`nombre`, `precio`, `stock`, `imagen_url` ) VALUES (%s, %s, %s, %s);" # ESTO ES UNA CONSULTA PARAMETRIZADA (ES MAS SEGURA) %s ES UNA VARIABLE QUE SE VA A CAMBIAR POR OTRO VALOR EVITA EL SQL INJECTION
        valores = (nombre, precio, stock, imagen)
        
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return True
            
    def eliminar_producto(self, codigo):
        #sql = "DELETE FROM `db-tpf`.`productos` WHERE (`id` = " + str(codigo) + ");"
        sql = (f"DELETE FROM `db-tpf`.`productos` WHERE (`id` = {codigo});") 
        self.cursor.execute(sql)
        self.conn.commit()
        return True
        
    def traer_producto_por_id(self, codigo):
        #sql = "SELECT * FROM `db-tpf`.`productos` WHERE (`id` = " + str(codigo) + ");"
        sql = (f"SELECT * FROM `db-tpf`.`productos` WHERE (`id` = {codigo});")
        self.cursor.execute(sql)
        producto = self.cursor.fetchone()
        return producto
        
    def modificar_producto(self, codigo, nombre, precio, stock):
        #sql = "UPDATE `db-tpf`.`productos` SET `nombre` = '" + nombre + "', `precio` = " + precio + ", `stock` = " + stock + " WHERE (`id` = " + str(codigo) + ");"
        sql = "UPDATE `db-tpf`.`productos` SET `nombre` = %s, `precio` = %s, `stock` = %s WHERE (`id` = %s);"
        valores = (nombre, precio, stock, codigo)
        
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return True
        
    def traer_productos(self): # ESTO ES UN METODO TIPO GET
        sql = "SELECT * FROM `db-tpf`.`productos`;"
        self.cursor.execute(sql) # ESTO EJECUTA LA CONSULTA
        productos = self.cursor.fetchall() # ESTO DEVUELVE UNA LISTA DE TUPLAS
        return productos
  
# FIN CLASE CATALOGO

####################################################
# PROGRAMA PRINCIPAL

# CREAMOS UN OBJETO DE LA CLASE CATALOGO QUE LE PASA LOS PARAMETROS DE CONEXION
catalogo = Catalogo(host='localhost', user='root', password='', database='db-tpf') 


RUTA_DESTINO = "./static/imagenes/"

@app.route("/productos", methods=["POST"]) #ESTO ES UN DECORADOR
def agregar_producto():
    
    nombre = request.form['nombre']
    precio = request.form['precio']
    stock = request.form['stock']
    imagen = request.files['imagen'] # ESTO ES UNA VARIABLE DE TIPO FILE STORAGE
    
    nombre_imagen = secure_filename(imagen.filename) # ESTO ES PARA QUE EL NOMBRE DE LA IMAGEN NO TENGA CARACTERES RAROS
    nombre_base, extension = os.path.splitext(nombre_imagen) # ESTO SEPARA EL NOMBRE DE LA IMAGEN DE LA EXTENSION
    imagen_url = f"{nombre_base}{extension}" # ESTO ES PARA QUE EL NOMBRE DE LA IMAGEN SEA UNICO
    
    # ESTO ES PARA GUARDAR LA IMAGEN EN UNA CARPETA    
    si_se_agrego = catalogo.agregar_producto(nombre, precio, stock, imagen_url)
    if si_se_agrego:
        imagen.save(os.path.join(RUTA_DESTINO, imagen_url))
        
        return jsonify({"mensaje": "producto agregado"}), 200 # ESTO ES UNA RESPUESTA HTTP OK
    else:
       return jsonify({"mensaje": "Error"}), 400 # ESTO ES UNA RESPUESTA HTTP ERROR

@app.route("/productos", methods=["GET"])
def traer_productos():
    productos = catalogo.traer_productos()
    
    productos_json = [] # ESTO ES UNA LISTA DE DICCIONARIOS
    
    for producto in productos:
        producto_json = { # ESTO ES UN DICCIONARIO
            "id": producto[0],
            "nombre": producto[1],
            "precio": producto[2],
            "stock": producto[3],
            "imagen_url": producto[4]
        }
        productos_json.append(producto_json)
        
    return jsonify(productos_json), 200 # ESTO ES UNA RESPUESTA HTTP OK

@app.route("/productos/<int:codigo>", methods=["DELETE"])
def eliminar_producto(codigo):
    producto_eliminado = catalogo.eliminar_producto(codigo)
    if producto_eliminado:
        return jsonify({"mensaje": "producto eliminado"}), 200
    else:
        return jsonify({"mensaje": "Error"}), 400

@app.route("/productos/<int:codigo>", methods=["GET"])
def traer_producto_por_id(codigo):
    producto = catalogo.traer_producto_por_id(codigo)
    if producto:
        producto_json = { # ESTO ES UN DICCIONARIO
            "id": producto[0],
            "nombre": producto[1],
            "precio": producto[2],
            "stock": producto[3],
            "imagen_url": producto[4]
        }
        return jsonify(producto_json), 200
    else:
        return jsonify({"mensaje": "Producto no encontrado"}), 400

@app.route("/productos/<int:codigo>", methods=["PUT"])
def modificar_producto(codigo):    
    nombre = request.form['nombre']
    precio = request.form['precio']
    stock = request.form['stock']
    
    si_se_modifico = catalogo.modificar_producto(codigo, nombre, precio, stock)
    if si_se_modifico:
        return jsonify({"mensaje": "producto modificado"}), 200
    else:
        return jsonify({"mensaje": "Error"}), 400

if __name__ == '__main__':
    app.run(port=4000, debug=True)