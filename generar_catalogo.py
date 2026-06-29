import xmlrpc.client
import os

# =====================================
# CONFIGURACIÓN Y CREDENCIALES
# =====================================
URL = os.environ.get("ODOO_URL")
DB = os.environ.get("ODOO_DB")
USER = os.environ.get("ODOO_USER")
API_KEY = os.environ.get("ODOO_API_KEY")

def main():
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USER, API_KEY, {})
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

        print("Conectado a Odoo. Extrayendo Listas de Precios...")

        # =====================================
        # 1. LISTAS DE PRECIOS
        # =====================================
        pl_data = models.execute_kw(DB, uid, API_KEY, 'product.pricelist', 'search_read',
            [[['company_id', '=', 1]]], {'fields': ['id', 'name'], 'limit': 500})
        
        listas_excluir = ["DIA CONTI", "ALSK-ALQUILER DE OFICINA", "PROMO", "MAYS USD", "CRE USD", "DIST1 USD", "DIST2 USD", "SAL USD"]
        pricelists = []
        usados = set()

        for pl in pl_data:
            nombre = (pl.get('name') or "").upper().strip()
            if nombre in listas_excluir:
                continue
            if nombre == "DIST1": nombre = "DIST 1"
            if nombre == "DIST2": nombre = "DIST 2"
            
            if nombre not in usados:
                usados.add(nombre)
                pl['name_clean'] = nombre
                pricelists.append(pl)

        orden_precios = ["CONGS", "DIST 1", "DIST 2", "CREGS", "MAYGS", "SALGS"]
        pricelists.sort(key=lambda x: orden_precios.index(x['name_clean']) if x['name_clean'] in orden_precios else 999)

        # =====================================
        # 2. ITEMS PRECIOS (Fixed Price)
        # =====================================
        print("Extrayendo items de listas de precios...")
        pl_items = models.execute_kw(DB, uid, API_KEY, 'product.pricelist.item', 'search_read',
            [[]], {'fields': ['pricelist_id', 'product_tmpl_id', 'fixed_price'], 'limit': 50000})

        mapa_precios = {}
        for item in pl_items:
            tmpl_id = item['product_tmpl_id'][0] if item.get('product_tmpl_id') else None
            pl_id = item['pricelist_id'][0] if item.get('pricelist_id') else None
            if tmpl_id and pl_id:
                if tmpl_id not in mapa_precios:
                    mapa_precios[tmpl_id] = {}
                mapa_precios[tmpl_id][pl_id] = item.get('fixed_price', 0.0)

        # =====================================
        # 3. PRODUCTOS
        # =====================================
        print("Extrayendo productos...")
        filtros = [['sale_ok', '=', True], ['active', '=', True], ['company_id', '=', 1]]
        campos = ['id', 'name', 'default_code', 'qty_available', 'categ_id', 'product_brand_id', 'product_tmpl_id', 'image_128']
        
        products = models.execute_kw(DB, uid, API_KEY, 'product.product', 'search_read', [filtros], {'fields': campos, 'limit': 50000})

        # =====================================
        # 4. LÓGICA DE NEGOCIO Y STOCK
        # =====================================
        stock_salon = {
            "501048": 20000, "501113": 15000, "501121": 20000, "501333": 5000,
            "501366": 20000, "501379": 20000, "501493": 13000, "501505": 20000,
            "501527": 10000, "501567": 2000,  "501577": 20000, "501581": 20000,
            "501591": 20000, "501593": 15000, "501604": 4000
        }

        # ID de MAYGS para validación de armas
        maygs_id = next((pl['id'] for pl in pricelists if pl['name_clean'] == 'MAYGS'), None)

        categorias_datos = {}
        orden_hojas = [
            "Municiones", "Armas", "Cargadores", "ASG", "TSS", "CROSMAN", "UMAREX",
            "DOBERMAN RIFLES", "DOBERMAN MOCHILAS", "DOBERMAN BOTAS", "DOBERMAN LINTERNAS", "DOBERMAN BALINES",
            "VECTOR OPTICS", "KONUS", "BWC", "TRUGLO", "MIGUEL NIETO", "NTK", "COLEMAN", "IMALENT",
            "APOLO", "AITOR", "ROCKY BOOTS", "KCI", "NITECORE", "CATERPILLAR", "POLYMER", "SNAKE",
            "FOBUS", "BERETTA MOD", "B.E ARMOR", "OTRO"
        ]
        for hoja in orden_hojas:
            categorias_datos[hoja] = []

        for p in products:
            ref = (p.get('default_code') or "").upper().strip()
            if ref.startswith("AVE") or ref.startswith("NSE"):
                continue

            categoria_str = p['categ_id'][1].upper() if p.get('categ_id') else ""
            if "VITALICA" in categoria_str:
                continue

            stock = float(p.get('qty_available') or 0.0)
            if ref in stock_salon:
                stock = max(0, stock - stock_salon[ref])
            
            if stock <= 0:
                continue

            tmpl_id = p['product_tmpl_id'][0] if p.get('product_tmpl_id') else 0
            
            # Lógica de Armas
            es_arma = "ARMA" in categoria_str and "ACCESORIO" not in categoria_str
            if es_arma:
                precio_maygs = mapa_precios.get(tmpl_id, {}).get(maygs_id, 0.0)
                if not maygs_id or float(precio_maygs) <= 0:
                    continue

            desc = (p.get('name') or "").upper()
            marca_str = p['product_brand_id'][1].upper() if p.get('product_brand_id') else "SIN MARCA"

            # =====================================
            # 5. CLASIFICACIÓN DE "HOJAS"
            # =====================================
            hoja = "OTRO"
            if "MUNICION" in categoria_str: hoja = "Municiones"
            elif es_arma: hoja = "Armas"
            elif "ASG" in categoria_str or "ASG" in marca_str or "ASG" in desc: hoja = "ASG"
            elif "TSS" in marca_str: hoja = "TSS"
            elif "CROSMAN" in marca_str: hoja = "CROSMAN"
            elif "UMAREX" in marca_str: hoja = "UMAREX"
            elif "VECTOR" in marca_str: hoja = "VECTOR OPTICS"
            elif "KONUS" in marca_str: hoja = "KONUS"
            elif "BWC" in marca_str: hoja = "BWC"
            elif "TRUGLO" in marca_str: hoja = "TRUGLO"
            elif "MIGUEL" in marca_str: hoja = "MIGUEL NIETO"
            elif "NTK" in marca_str: hoja = "NTK"
            elif "COLEMAN" in marca_str: hoja = "COLEMAN"
            elif "IMALENT" in marca_str: hoja = "IMALENT"
            elif "APOLO" in marca_str: hoja = "APOLO"
            elif "AITOR" in marca_str: hoja = "AITOR"
            elif "ROCKY" in marca_str: hoja = "ROCKY BOOTS"
            elif "KCI" in marca_str: hoja = "KCI"
            elif "NITECORE" in marca_str: hoja = "NITECORE"
            elif "CATERPILLAR" in marca_str: hoja = "CATERPILLAR"
            elif "POLYMER" in marca_str: hoja = "POLYMER"
            elif "SNAKE" in marca_str: hoja = "SNAKE"
            elif "FOBUS" in marca_str: hoja = "FOBUS"
            elif "BERETTA" in marca_str: hoja = "BERETTA MOD"
            elif "B.E" in marca_str: hoja = "B.E ARMOR"

            if "DOBERMAN" in marca_str:
                if "RIFLE" in desc: hoja = "DOBERMAN RIFLES"
                if "MOCHILA" in desc: hoja = "DOBERMAN MOCHILAS"
                if "BOTA" in desc: hoja = "DOBERMAN BOTAS"
                if "LINTERNA" in desc: hoja = "DOBERMAN LINTERNAS"
                if "BALIN" in desc: hoja = "DOBERMAN BALINES"

            es_cargador = "CARGADOR" in desc and not any(x in desc for x in ["PORTA", "BASE", "PISO", "ACOPLE"])
            if es_cargador:
                hoja = "Cargadores"

            p['stock_calculado'] = stock
            p['hoja_asignada'] = hoja
            p['categoria_limpia'] = p['categ_id'][1] if p.get('categ_id') else ""
            p['marca_limpia'] = p['product_brand_id'][1] if p.get('product_brand_id') else "Sin Marca"
            
            # Extraer los precios de cada lista
            p_precios = []
            for pl in pricelists:
                p_val = mapa_precios.get(tmpl_id, {}).get(pl['id'], 0.0)
                p_precios.append(p_val)
            p['lista_precios_vals'] = p_precios

            categorias_datos[hoja].append(p)

        # =====================================
        # 6. CONSTRUIR HTML (Navegación tipo "Pestañas" de Google Sheets)
        # =====================================
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Catálogo Mayorista - Camping 44</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            <style>
                body {{ background-color: #f8f9fa; }}
                .stock-rojo {{ background-color: #FECACA !important; }}
                .stock-amarillo {{ background-color: #FEF3C7 !important; }}
                .stock-verde {{ background-color: #BBF7D0 !important; }}
                .table thead th {{ background-color: #081226; color: white; }}
                .nav-pills .nav-link.active {{ background-color: #081226; }}
            </style>
        </head>
        <body>
            <div class="container-fluid py-4">
                <h2 class="fw-bold mb-4 text-center">Catálogo de Precios - Camping 44</h2>
                
                <ul class="nav nav-pills mb-4 justify-content-center flex-wrap" id="pills-tab" role="tablist">
        """
        
        # Crear los botones de las pestañas (Omitir las vacías)
        first_tab = True
        for hoja in orden_hojas:
            if not categorias_datos[hoja]: continue
            active_class = "active" if first_tab else ""
            html += f"""
                    <li class="nav-item" role="presentation">
                        <button class="nav-link {active_class} m-1" id="pills-{hoja.replace(' ', '')}-tab" data-bs-toggle="pill" data-bs-target="#pills-{hoja.replace(' ', '')}" type="button" role="tab">{hoja} ({len(categorias_datos[hoja])})</button>
                    </li>
            """
            first_tab = False

        html += """
                </ul>
                <div class="tab-content shadow bg-white p-3 rounded" id="pills-tabContent">
        """

        # Crear las tablas por cada pestaña
        first_content = True
        for hoja in orden_hojas:
            productos_hoja = categorias_datos[hoja]
            if not productos_hoja: continue
            
            active_class = "show active" if first_content else ""
            
            html += f"""
                    <div class="tab-pane fade {active_class}" id="pills-{hoja.replace(' ', '')}" role="tabpanel">
                        <div class="table-responsive">
                            <table class="table table-hover align-middle mb-0">
                                <thead>
                                    <tr>
                                        <th class="text-center">IMG</th>
                                        <th>CÓDIGO</th>
                                        <th>DESCRIPCIÓN</th>
                                        <th class="text-center">STOCK</th>
            """
            for pl in pricelists:
                html += f'<th class="text-end">{pl["name_clean"]}</th>'
            
            html += """
                                        <th>CATEGORÍA</th>
                                        <th>MARCA</th>
                                    </tr>
                                </thead>
                                <tbody>
            """

            for p in productos_hoja:
                img_data = p.get('image_128')
                img_tag = f'<img src="data:image/png;base64,{img_data.decode("utf-8") if isinstance(img_data, bytes) else img_data}" width="40">' if img_data else '-'
                
                stock_val = p['stock_calculado']
                stock_class = "stock-rojo" if stock_val <= 5 else ("stock-amarillo" if stock_val <= 20 else "stock-verde")

                html += f"""
                                    <tr>
                                        <td class="text-center">{img_tag}</td>
                                        <td class="fw-bold">{p.get('default_code', '-')}</td>
                                        <td>{p.get('name', '')}</td>
                                        <td class="text-center fw-bold {stock_class}">{int(stock_val)}</td>
                """
                for precio in p['lista_precios_vals']:
                    html += f'<td class="text-end text-success fw-bold">${float(precio):,.2f}</td>'
                
                html += f"""
                                        <td><small>{p['categoria_limpia']}</small></td>
                                        <td><small>{p['marca_limpia']}</small></td>
                                    </tr>
                """

            html += """
                                </tbody>
                            </table>
                        </div>
                    </div>
            """
            first_content = False

        html += """
                </div>
            </div>
        </body>
        </html>
        """

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("HTML generado exitosamente.")

    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    main()
