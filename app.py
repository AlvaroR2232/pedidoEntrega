from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

import json
import folium

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_muy_segura' # Cambia esto en producción

# Simulación de una base de datos de usuarios
users = {
    'manager1': {'password': 'manager1pass', 'role': 'admin'},
    'manager2': {'password': 'manager2pass', 'role': 'admin'},
    'driver1': {'password': 'driver1pass', 'role': 'driver'},
    'driver2': {'password': 'driver2pass', 'role': 'driver'},
    'seller1': {'password': 'seller1pass', 'role': 'seller'},
    'seller2': {'password': 'seller2pass', 'role': 'seller'},
    'seller3': {'password': 'seller3pass', 'role': 'seller'}
}

# Base de datos simulada de clientes
CLIENTES_DB = {
    "CLI001": {
        "codigo": "CLI001",
        "cliente": "Juan Pérez",
        "fecha": "2024-06-01",
        "direccion": "Av. Los Sauces # 345",
        "telefono": "7777 7777",
        "ciudad": "Cochabamba",
        "articulos": [
            {"id": 1, "nombre": "Laptop Dell", "cantidad": 2, "precio": 1200.00},
            {"id": 2, "nombre": "Mouse Inalámbrico", "cantidad": 5, "precio": 25.00},
            {"id": 3, "nombre": "Teclado Mecánico", "cantidad": 3, "precio": 80.00},
            {"id": 4, "nombre": "Monitor 24\"", "cantidad": 2, "precio": 200.00},
            {"id": 5, "nombre": "Webcam HD", "cantidad": 1, "precio": 150.00}
        ]
    },
    "CLI002": {
        "codigo": "CLI002",
        "cliente": "María García",
        "fecha": "2024-06-02",
        "direccion": "Av. Los Sauces # 345",
        "telefono": "7777 7777",
        "ciudad": "Cochabamba",
        "articulos": [
            {"id": 1, "nombre": "Smartphone Samsung", "cantidad": 1, "precio": 800.00},
            {"id": 2, "nombre": "Funda Protectora", "cantidad": 2, "precio": 15.00},
            {"id": 3, "nombre": "Cargador Rápido", "cantidad": 1, "precio": 35.00},
            {"id": 4, "nombre": "Auriculares Bluetooth", "cantidad": 1, "precio": 120.00},
            {"id": 5, "nombre": "Protector de Pantalla", "cantidad": 3, "precio": 10.00}
        ]
    },
    "CLI003": {
        "codigo": "CLI003",
        "cliente": "Carlos López",
        "fecha": "2024-06-03",
        "direccion": "Av. Los Sauces # 345",
        "telefono": "7777 7777",
        "ciudad": "Cochabamba",
        "articulos": [
            {"id": 1, "nombre": "Tablet iPad", "cantidad": 1, "precio": 600.00},
            {"id": 2, "nombre": "Apple Pencil", "cantidad": 1, "precio": 130.00},
            {"id": 3, "nombre": "Funda Smart Cover", "cantidad": 1, "precio": 45.00},
            {"id": 4, "nombre": "Adaptador USB-C", "cantidad": 2, "precio": 25.00},
            {"id": 5, "nombre": "Cable Lightning", "cantidad": 1, "precio": 20.00}
        ]
    }
}

# Base de datos simulada de pedidos
PEDIDOS_DB = {
    "PED001": {
        "numero": "PED001",
        "cliente": "Juan Pérez",
        "fecha": "2024-06-01",
        "direccion": "Av. Los Sauces # 345",
        "telefono": "7777 7777",
        "ciudad": "Cochabamba",
        "estado": "Pendiente",
        "articulos": [
            {"id": 1, "nombre": "Laptop Dell", "cantidad": 2, "precio": 1200.00},
            {"id": 2, "nombre": "Mouse Inalámbrico", "cantidad": 5, "precio": 25.00},
            {"id": 3, "nombre": "Teclado Mecánico", "cantidad": 3, "precio": 80.00},
            {"id": 4, "nombre": "Monitor 24\"", "cantidad": 2, "precio": 200.00},
            {"id": 5, "nombre": "Webcam HD", "cantidad": 1, "precio": 150.00}
        ]
    },
    "PED002": {
        "numero": "PED002",
        "cliente": "María García",
        "fecha": "2024-06-02",
        "direccion": "Av. Los Sauces # 345",
        "telefono": "7777 7777",
        "ciudad": "Cochabamba",
        "estado": "Pendiente",
        "articulos": [
            {"id": 1, "nombre": "Smartphone Samsung", "cantidad": 1, "precio": 800.00},
            {"id": 2, "nombre": "Funda Protectora", "cantidad": 2, "precio": 15.00},
            {"id": 3, "nombre": "Cargador Rápido", "cantidad": 1, "precio": 35.00},
            {"id": 4, "nombre": "Auriculares Bluetooth", "cantidad": 1, "precio": 120.00},
            {"id": 5, "nombre": "Protector de Pantalla", "cantidad": 3, "precio": 10.00}
        ]
    },
    "PED003": {
        "numero": "PED003",
        "cliente": "Carlos López",
        "fecha": "2024-06-03",
        "direccion": "Av. Los Sauces # 345",
        "telefono": "7777 7777",
        "ciudad": "Cochabamba",
        "estado": "Pendiente",
        "articulos": [
            {"id": 1, "nombre": "Tablet iPad", "cantidad": 1, "precio": 600.00},
            {"id": 2, "nombre": "Apple Pencil", "cantidad": 1, "precio": 130.00},
            {"id": 3, "nombre": "Funda Smart Cover", "cantidad": 1, "precio": 45.00},
            {"id": 4, "nombre": "Adaptador USB-C", "cantidad": 2, "precio": 25.00},
            {"id": 5, "nombre": "Cable Lightning", "cantidad": 1, "precio": 20.00}
        ]
    }
}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            flash('Bienvenido, {}'.format(username), 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/ver_mapa')
def ver_mapa():
    if 'username' not in session or session['username'] == None:
        return redirect(url_for('login'))

    # Crear el mapa centrado en Cochabamba
    m = folium.Map(location=[-17.3935, -66.1570], zoom_start=15)

    # Lista de tiendas con sus datos
    tiendas = [
        {
            'nombre': 'Doña Filomena',
            'contacto': 'Filomena Delgado',
            'direccion': 'Calle La Tablada #4533',
            'telefono': '77788909',
            'pedido': '1001',
            'foto': 'tienda_barrio.jpg',
            'ubicacion': [-17.3935, -66.1570]
        },
        {
            'nombre': 'Abarrotes El Carmen',
            'contacto': 'Carmen Rojas',
            'direccion': 'Av. Blanco Galindo Km 2',
            'telefono': '77543210',
            'pedido': '1002',
            'foto': 'tienda_carmen.jpg',
            'ubicacion': [-17.3850, -66.1700]
        },
        {
            'nombre': 'Minimarket Los Andes',
            'contacto': 'Juan Mamani',
            'direccion': 'Av. América Este #345',
            'telefono': '70707070',
            'pedido': '1003',
            'foto': 'tienda_andes.jpg',
            'ubicacion': [-17.3980, -66.1420]
        },
        {
            'nombre': 'Tienda Don Pedro',
            'contacto': 'Pedro Flores',
            'direccion': 'Calle Sucre #1234',
            'telefono': '71234567',
            'pedido': '1004',
            'foto': 'tienda_pedro.jpg',
            'ubicacion': [-17.4050, -66.1610]
        },
        {
            'nombre': 'Mercadito Central',
            'contacto': 'María Gutiérrez',
            'direccion': 'Av. Ayacucho #887',
            'telefono': '78901234',
            'pedido': '1004',
            'foto': 'tienda_central.jpg',
            'ubicacion': [-17.3925, -66.1480]
        },
        {
            'nombre': 'Almacén El Sol',
            'contacto': 'Roberto Mendoza',
            'direccion': 'Av. Heroínas #765',
            'telefono': '76767676',
            'pedido': '1005',
            'foto': 'tienda_sol.jpg',
            'ubicacion': [-17.3880, -66.1550]
        },
        {
            'nombre': 'Tienda Doña Rosa',
            'contacto': 'Rosa Méndez',
            'direccion': 'Calle Hamiraya #432',
            'telefono': '79876543',
            'pedido': '1006',
            'foto': 'tienda_rosa.jpg',
            'ubicacion': [-17.4010, -66.1520]
        }
    ]

    # Agregar marcadores para cada tienda
    for tienda in tiendas:
        foto_url = url_for('static', filename=f"fotos/{tienda['foto']}")
        popup_content = f"""
        <table border="1" class="table table-success table-striped">
            <tr><td colspan="2"><img src="{foto_url}" width="250" height="200"></td></tr>
            <tr><td><b>Tienda:</b></td><td>{tienda['nombre']}</td></tr>
            <tr><td><b>Contacto:</b></td><td>{tienda['contacto']}</td></tr>
            <tr><td><b>Dirección:</b></td><td>{tienda['direccion']}</td></tr>
            <tr><td><b>Teléfono:</b></td><td>{tienda['telefono']}</td></tr>
            <tr><td><b>Pedido:</b></td><td>{tienda['pedido']}</td></tr>
            </table>
        """

        folium.Marker(
            location=tienda['ubicacion'],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"Tienda: {tienda['nombre']}",
            icon=folium.Icon(color='blue', icon='shopping-cart', prefix='fa')
        ).add_to(m)

    # Guardar el mapa en un archivo HTML
    #path = 'home/GabrielCes/mysite/static/mapa_cbb.html'
    #m.save(path)
    mapa_html = m._repr_html_()

    # Renderizar la plantilla HTML
    return render_template('mapa.html', mapa=mapa_html)


@app.route('/pedido')
def pedido():
    if 'username' not in session or session['username'] == None:
        return redirect(url_for('login'))
    return render_template('pedido.html')


@app.route('/buscar_pedido', methods=['GET', 'POST'])
def buscar_pedido():
    pedido = None
    error = None
    success = None
    total = 0

    if request.method == 'POST':
        numero_pedido = request.form.get('numero_pedido', '').strip().upper()

        if not numero_pedido:
            error = "Por favor, ingrese un número de pedido."
        elif numero_pedido in PEDIDOS_DB:
            pedido = PEDIDOS_DB[numero_pedido]
            # Calcular total
            total = sum([art['cantidad'] * art['precio'] for art in pedido['articulos']])
        else:
            error = f"El pedido '{numero_pedido}' no existe en el sistema."

    return render_template('pedido.html',
                           pedido=pedido,
                           error=error,
                           success=success,
                           total=total,
                           pedidos_ejemplo=True)


@app.route('/actualizar_pedido', methods=['POST'])
def actualizar_pedido():
    numero_pedido = request.form.get('numero_pedido')

    if numero_pedido not in PEDIDOS_DB:
        return render_template('pedido.html',
                           error=f"Pedido no encontrado.")

    # Actualizar articulos
    pedido = PEDIDOS_DB[numero_pedido]

    try:
        for articulo in pedido['articulos']:
            articulo_id = str(articulo['id'])
            articulo['nombre'] = request.form.get(f'nombre_{articulo_id}', '').strip()
            articulo['cantidad'] = int(request.form.get(f'cantidad_{articulo_id}', 0))
            articulo['precio'] = float(request.form.get(f'precio_{articulo_id}', 0))

            # Validaciones básicas
            if not articulo['nombre']:
                raise ValueError("El nombre del artículo no puede estar vacío.")
            if articulo['cantidad'] <= 0:
                raise ValueError("La cantidad debe ser mayor a cero.")
            if articulo['precio'] < 0:
                raise ValueError("El precio no puede ser negativo.")

        # Calcular nuevo total
        total = sum([art['cantidad'] * art['precio'] for art in pedido['articulos']])

        return render_template('pedido.html',
                               pedido=pedido,
                               success="Pedido actualizado correctamente.",
                               total=total)

    except (ValueError, TypeError) as e:
        return render_template('pedido.html',
                               pedido=pedido,
                               error=f"Error al actualizar: {str(e)}",
                               total=sum([art['cantidad'] * art['precio'] for art in
                               pedido['articulos']]))


@app.route('/preventa')
def preventa():
    if 'username' not in session or session['username'] == None:
        return redirect(url_for('login'))
    return render_template('preventa.html')


@app.route('/buscar_cliente', methods=['GET', 'POST'])
def buscar_cliente():
    codigo = None
    error = None
    success = None
    total = 0

    if request.method == 'POST':
        codigo_cliente = request.form.get('codigo_cliente', '').strip().upper()

        if not codigo_cliente:
            error = "Por favor, ingrese un código de cliente."
        elif codigo_cliente in CLIENTES_DB:
            codigo = CLIENTES_DB[codigo_cliente]
            # Calcular total
            total = sum([art['cantidad'] * art['precio'] for art in codigo['articulos']])
            ###total = sum([art['cantidad'] * art['precio'] for art in pedido['articulos']])
        else:
            error = f"El cliente '{codigo_cliente}' no existe en el sistema."

    return render_template('preventa.html',
                           codigo=codigo,
                           error=error,
                           success=success,
                           total=total,
                           clientes_ejemplo=True)


@app.route('/grabar_pedido', methods=['POST'])
def grabar_pedido():
    ##numero_pedido = request.form.get('numero_pedido')
    return "Grabando Pedido ..."