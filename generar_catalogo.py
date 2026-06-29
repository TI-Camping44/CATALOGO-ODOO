import xmlrpc.client
import os

# 1. Traer credenciales ocultas desde GitHub Secrets
URL = os.environ.get("ODOO_URL")
DB = os.environ.get("ODOO_DB")
USER = os.environ.get("ODOO_USER")
API_KEY = os.environ.get("ODOO_API_KEY")

# ID de la Lista de Precios por defecto (la tarifa que usa tu Odoo)
# Nota: Si luego quieres otra tarifa específica, cambiaremos este número
TARIFA_ID = 1 

try:
    # 2. Conectar a la API de Odoo 17
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
    uid = common.authenticate(DB, USER, API_KEY, {})
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

    print("Conexión a Odoo exitosa. Buscando productos...")

    # 3. Buscar productos activos que se puedan vender
    filtros = [['sale_ok', '=', True]]
    productos_ids = models.execute_kw(DB, uid, API_KEY, 'product.product', 'search', [filtros], {'limit': 150}) # Limitado a 150 para la primera prueba

    # 4. Leer los datos pasando el contexto de la tarifa para calcular el precio dinámico
    campos = ['default_code', 'name', 'price', 'image_128']
    contexto = {'context': {'pricelist': TARIFA_ID}}
    productos = models.execute_kw(DB, uid, API_KEY, 'product.product', 'read', [productos_ids, campos], contexto)

    # 5. Construir el diseño HTML limpio con Bootstrap 5
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Catálogo de Precios - Camping 44</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container py-5">
            <div class="text-center mb-5">
                <h1 class="fw-bold text-dark">Listado de Precios</h1>
                <p class="text-muted">Actualizado automáticamente desde Odoo</p>
            </div>
            <div class="card shadow-sm border-0 rounded-3 overflow-hidden">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-dark text-uppercase fs-7">
                            <tr>
                                <th class="text-center" style="width: 100px;">Imagen</th>
                                <th style="width: 150px;">Código</th>
                                <th>Descripción del Producto</th>
                                <th class="text-end" style="width: 150px;">Precio</th>
                            </tr>
                        </thead>
                        <tbody>
    """

    for p in productos:
        # Procesar imagen de Odoo (viene en base64)
        img_data = p.get('image_128')
        if img_data:
            # Si viene como string binario o limpio, lo manejamos directo
            if isinstance(img_data, bytes):
                img_data = img_data.decode('utf-8')
            img_tag = f'<img src="data:image/png;base64,{img_data}" class="img-thumbnail" style="width: 64px; height: 64px; object-fit: cover;">'
        else:
            img_tag = '<span class="text-muted small">Sin foto</span>'
            
        codigo = p.get('default_code') or '-'
        nombre = p.get('name', 'Producto sin nombre')
        precio = p.get('price', 0.0)
        
        html += f"""
                            <tr>
                                <td class="text-center">{img_tag}</td>
                                <td><span class="badge bg-secondary font-monospace fs-6">{codigo}</span></td>
                                <td class="fw-semibold text-secondary">{nombre}</td>
                                <td class="text-end fw-bold text-success fs-5">${precio:,.2f}</td>
                            </tr>
        """

    html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Guardar el archivo index.html en la raíz del repositorio
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("¡Catálogo index.html generado con éxito!")

except Exception as e:
    print(f"Ocurrió un error durante la ejecución: {e}")
