from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import folium
import datetime
from urllib.parse import quote_plus # Importante si tu clave tiene símbolos

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_muy_segura'

# --- CONFIGURACIÓN DE BASE DE DATOS ---

clave_raw = 'xxjoe246xx'  # PON AQUÍ TU CLAVE REAL
clave_encoded = quote_plus(clave_raw)

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'mysql+pymysql://AlvaroR:{clave}@{servidor}/{database}?charset=utf8'.format(
        clave = clave_encoded,
        servidor = 'AlvaroR.mysql.pythonanywhere-services.com',
        database = 'AlvaroR$pedidoEntrega'
    )

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS DE LA BASE DE DATOS ---

class Usuarios(db.Model):
    __tablename__ = 'usuarios'
    nombre = db.Column(db.String(40), nullable=False)
    usuario = db.Column(db.String(20), primary_key=True)
    clave = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(80), nullable=False)

class Productos(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    articulo = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(100), nullable=False)
    precio_venta = db.Column(db.DECIMAL(9,2), nullable=False)
    stock_minimo = db.Column(db.Integer, nullable=False)
    existencia = db.Column(db.Integer, nullable=False)

class Clientes(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    razon_social = db.Column(db.String(60), nullable=False)
    nit_ci = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(80), nullable=True)
    pedidos = db.relationship('Pedidos', backref='cliente', lazy=True)

class Pedidos(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    vendedor_usuario = db.Column(db.String(20), db.ForeignKey('usuarios.usuario'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.datetime.now)
    total = db.Column(db.DECIMAL(10, 2), default=0.00)
    detalles = db.relationship('DetallePedidos', backref='pedido', lazy=True)

class DetallePedidos(db.Model):
    __tablename__ = 'detalle_pedidos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.DECIMAL(9, 2), nullable=False)
    producto = db.relationship('Productos', backref='detalles_en_pedidos')

# --- DECORADORES Y RUTAS GENERALES ---

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

        registro_usuario = Usuarios.query.filter_by(usuario=username).first()

        if registro_usuario and registro_usuario.clave == password:
            session['username'] = str(registro_usuario.usuario)
            session['role'] = str(registro_usuario.role)
            flash(f'Bienvenido, {registro_usuario.nombre}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# --- RUTAS DE VENDEDOR (PREVENTA) ---

@app.route('/preventa')
def preventa():
    if 'username' not in session or session['role'] not in ['seller', 'admin']:
        return redirect(url_for('login'))

    productos = Productos.query.all()
    return render_template("preventa.html", productos=productos)

@app.route('/buscar_cliente', methods=['GET', 'POST'])
@login_required
def buscar_cliente():
    cliente_encontrado = None
    error = None
    productos = Productos.query.all()

    if request.method == 'POST':
        criterio = request.form.get('codigo_cliente', '').strip()
        if not criterio:
            error = "Por favor, ingrese Razón Social o NIT."
        else:
            cliente_encontrado = Clientes.query.filter(
                (Clientes.nit_ci == criterio) |
                (Clientes.razon_social.like(f'%{criterio}%'))
            ).first()

            if not cliente_encontrado:
                error = f"No se encontró el cliente '{criterio}'."

    return render_template('preventa.html',
                           cliente=cliente_encontrado,
                           error=error,
                           productos=productos)

@app.route('/grabar_pedido', methods=['POST'])
@login_required
def grabar_pedido():
    try:
        cliente_id = request.form.get('cliente_id')
        if not cliente_id:
            flash("Error: No se seleccionó un cliente.", "error")
            return redirect(url_for('preventa'))

        nuevo_pedido = Pedidos(
            cliente_id=cliente_id,
            vendedor_usuario=session['username'],
            total=0
        )
        db.session.add(nuevo_pedido)
        db.session.flush()

        total_pedido = 0
        productos = Productos.query.all()
        items_agregados = 0

        for prod in productos:
            cantidad_str = request.form.get(f'cantidad_{prod.id}')
            if cantidad_str:
                cantidad = int(cantidad_str)
                if cantidad > 0:
                    subtotal = float(prod.precio_venta) * cantidad
                    total_pedido += subtotal

                    detalle = DetallePedidos(
                        pedido_id=nuevo_pedido.id,
                        producto_id=prod.id,
                        cantidad=cantidad,
                        precio_unitario=prod.precio_venta
                    )
                    db.session.add(detalle)
                    items_agregados += 1

        if items_agregados == 0:
            db.session.rollback()
            flash("No se seleccionaron productos para el pedido.", "error")
            return redirect(url_for('preventa'))

        nuevo_pedido.total = total_pedido
        db.session.commit()

        flash(f"Pedido #{nuevo_pedido.id} guardado con éxito. Total: {total_pedido}", "success")
        return redirect(url_for('preventa'))

    except Exception as e:
        db.session.rollback()
        flash(f"Error al grabar pedido: {str(e)}", "error")
        return redirect(url_for('preventa'))

# --- RUTAS DE DRIVER (PEDIDOS Y MAPA) ---

@app.route('/pedido')
def pedido():
    if 'username' not in session or session['role'] not in ['driver', 'admin']:
        return redirect(url_for('login'))
    return render_template("pedido.html")

@app.route('/buscar_pedido', methods=['GET', 'POST'])
@login_required
def buscar_pedido():
    pedido_encontrado = None
    error = None

    if request.method == 'POST':
        numero_pedido = request.form.get('numero_pedido', '').strip()

        if numero_pedido.isdigit():
            pedido_encontrado = Pedidos.query.get(int(numero_pedido))
            if not pedido_encontrado:
                error = f"El pedido #{numero_pedido} no existe."
        else:
            error = "Ingrese un número de pedido válido."

    return render_template('pedido.html',
                           pedido=pedido_encontrado,
                           error=error)

@app.route('/actualizar_pedido', methods=['POST'])
@login_required
def actualizar_pedido():
    id_pedido = request.form.get('numero_pedido')

    try:
        pedido_actual = Pedidos.query.get(id_pedido)
        if not pedido_actual:
            flash("Pedido no encontrado", "error")
            return redirect(url_for('pedido'))

        nuevo_total = 0

        for detalle in pedido_actual.detalles:
            nueva_cant_str = request.form.get(f'cantidad_{detalle.id}')

            if nueva_cant_str:
                nueva_cantidad = int(nueva_cant_str)
                if nueva_cantidad >= 0:
                    detalle.cantidad = nueva_cantidad
                    nuevo_total += (float(detalle.precio_unitario) * nueva_cantidad)

        pedido_actual.total = nuevo_total
        db.session.commit()

        flash("Pedido actualizado correctamente.", "success")
        return render_template('pedido.html', pedido=pedido_actual, success="Actualizado")

    except Exception as e:
        db.session.rollback()
        return render_template('pedido.html', error=f"Error crítico: {str(e)}")

@app.route('/ver_mapa')
@login_required
def ver_mapa():
    m = folium.Map(location=[-17.3935, -66.1570], zoom_start=15)

    tiendas = [
        {'nombre': 'Doña Filomena', 'lat': -17.3935, 'lon': -66.1570, 'dir': 'Calle La Tablada'},
        {'nombre': 'Abarrotes Carmen', 'lat': -17.3850, 'lon': -66.1700, 'dir': 'Av. Blanco Galindo'},
        {'nombre': 'Minimarket Andes', 'lat': -17.3980, 'lon': -66.1420, 'dir': 'Av. América'}
    ]

    for tienda in tiendas:
        popup_content = f"<b>{tienda['nombre']}</b><br>{tienda['dir']}"
        folium.Marker(
            location=[tienda['lat'], tienda['lon']],
            popup=popup_content,
            icon=folium.Icon(color='blue', icon='shopping-cart', prefix='fa')
        ).add_to(m)

    m.get_root().width = "100%"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()

    return render_template('mapa.html', mapa=iframe)

# --- GESTIÓN DE USUARIOS (ADMIN) ---

@app.route('/usuarios')
@login_required
def usuarios_index():
    if session['role'] != 'admin':
        flash("Acceso denegado", "error")
        return redirect(url_for('dashboard'))
    usuarios = Usuarios.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/agregar_usuario', methods=['GET', 'POST'])
@login_required
def agregar_usuario():
    if session['role'] != 'admin': return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            nuevo_usuario = Usuarios(
                nombre=request.form['nombre'],
                usuario=request.form['usuario'],
                clave=request.form['clave'],
                role=request.form['role'],
                correo=request.form['correo']
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            return redirect(url_for('usuarios_index'))
        except Exception as e:
            flash("Error al crear usuario (posible duplicado)", "error")

    return render_template('agregar_usuarios.html')

# --- ESTA ES LA FUNCIÓN NUEVA QUE SOLUCIONA EL ERROR ---
@app.route('/editar_usuario/<id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    if session['role'] != 'admin':
        return redirect(url_for('dashboard'))

    # Busca el usuario por su ID (campo 'usuario' en la BD)
    usuario_editar = Usuarios.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # Actualizamos los datos
            usuario_editar.nombre = request.form['nombre']
            usuario_editar.clave = request.form['clave']
            usuario_editar.role = request.form['role']
            usuario_editar.correo = request.form['correo']

            db.session.commit()
            flash('Usuario actualizado correctamente', 'success')
            return redirect(url_for('usuarios_index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'error')

    return render_template('editar_usuarios.html', usuario=usuario_editar)

@app.route('/eliminar_usuario/<id>')
@login_required
def eliminar_usuario(id):
    if session['role'] != 'admin': return redirect(url_for('dashboard'))

    usuario = Usuarios.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
    return redirect(url_for('usuarios_index'))

if __name__ == '__main__':
    app.run(debug=True)