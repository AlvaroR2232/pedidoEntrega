import mysql.connector
from mysql.connector import errorcode

print("Conectando...")
try:
    conn = mysql.connector.connect(
           host='AlvaroR.mysql.pythonanywhere-services.com',
           user='AlvaroR',
           password='mysqlroot'
      )
except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print('Existe un error en el nombre de usuario o en la clave')
      else:
            print(err)

cursor = conn.cursor()

cursor.execute("DROP DATABASE IF EXISTS `AlvaroR$pedidoEntrega`;")

cursor.execute("CREATE DATABASE `AlvaroR$pedidoEntrega`;")

cursor.execute("USE `AlvaroR$pedidoEntrega`;")

# creando las tablas
TABLES = {}

TABLES['productos'] = ('''
      CREATE TABLE `productos` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `articulo` varchar(50) NOT NULL,
      `descripcion` varchar(100) NOT NULL,
      `precio_venta` decimal(9,2) NOT NULL,
      `stock_minimo` int(4) NOT NULL,
      `existencia` int(4) NOT NULL,
      PRIMARY KEY (`id`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

TABLES['Usuarios'] = ('''
      CREATE TABLE `usuarios` (
      `nombre` varchar(40) NOT NULL,
      `usuario` varchar(20) NOT NULL,
      `clave` varchar(20) NOT NULL,
       `role` varchar(20) NOT NULL,
      `correo` varchar(80) NOT NULL,
      PRIMARY KEY (`usuario`)
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;''')

for tabla_nombre in TABLES:
      tabla_sql = TABLES[tabla_nombre]
      try:
            print('Creando tabla {}:'.format(tabla_nombre), end=' ')
            cursor.execute(tabla_sql)
      except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                  print('Ya existe la tabla')
            else:
                  print(err.msg)
      else:
            print('OK')


# insertando usuarios
usuario_sql = 'INSERT INTO usuarios (nombre, usuario, clave, role, correo) VALUES (%s, %s, %s, %s, %s)'

usuarios = [
      ("Jair Sampaio", "driver1", "driver1pass","driver","jair@gmail.com"),
      ("Rosa Flores", "driver2", "driver2pass","driver","rosa@gmail.com"),
      ("Yami Moto Nokamina", "driver3", "driver3pass","driver","yamimoto@gmail.com"),
      ("Mustafá ALi Babá", "seller1", "seller1pass","seller","mustafa@gmail.com"),
      ("Armando Meza", "seller2", "seller2pass","seller","ameza@gmail.com"),
      ("Teodoro Luque", "seller3", "seller3pass","seller","tluque@gmail.com"),
      ("Jacobo Zimermann", "manager1", "manager1pass","admin","jzimermann@gmail.com"),
      ("Lucrecio Pérez", "manager2", "manager2pass","admin","lperez@gmail.com")
]
cursor.executemany(usuario_sql, usuarios)


cursor.execute('select * from AlvaroR$pedidoEntrega.usuarios')
print(' -------------  Usuarios:  -------------')
for user in cursor.fetchall():
    print(user[0],user[1],user[2],user[3],user[4])



# insertando productos
productos_sql = 'INSERT INTO productos (articulo, descripcion, precio_venta, stock_minimo, existencia) VALUES (%s, %s, %s, %s, %s)'

productos = [
      ('mantequilla paquete grande', 'mantequilla paquete envase de 350 grs.', 20.00, 200, 1000),
      ('aceite de girasol', 'aceite girasol envase 1000 ml.', 15.0, 300, 1500),
      ('detergente ropa Suzzio', 'detergente ropa Suzzio 800 gr.',30.00, 24, 100),
      ('lava vajilla líquido Muggre 250 ml.', 'detergente ropa Suzzio 800 gr.',10.00, 24, 100),
      ('leche Vaka Loka', 'leche líquida Vaka Loka 800 ml.',8.00, 24, 100)
      ]
cursor.executemany(productos_sql, productos)

cursor.execute('select * from AlvaroR$pedidoEntrega.productos')
print(' -------------  Productoss:  -------------')
for producto in cursor.fetchall():
    print(producto[0],' ',producto[1],' ',producto[2] )


# commitando si no hay nada que tenga efecto
conn.commit()

cursor.close()
conn.close()