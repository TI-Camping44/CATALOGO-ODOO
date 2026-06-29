import xmlrpc.client
import os

# =====================================
# CONFIGURACIÓN DIRECTA (CAMPING 44)
# =====================================
URL = "https://camping44.odoo.com"
DB = "gcaceres93-camping-main-15845610"
USER = "facundocolman@camping44.com.py"
API_KEY = "55f70e57a3caa3113e3ffa559b5ba020931dc501"

def main():
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USER, API_KEY, {})
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

        print("Conectado a Odoo exitosamente. Extrayendo datos de la empresa...")

        comp_data = models.execute_kw(DB, uid, API_KEY, 'res.company', 'search_read', [[['id', '=', 1]]], {'fields': ['logo_web']})
        logo_base64 = ""
        if comp_data and comp_data[0].get('logo_web'):
            logo_base64 = comp_data[0]['logo_web']
            if isinstance(logo_base64, bytes):
                logo_base64 = logo_base64.decode('utf-8')

        pl_data = models.execute_kw(DB, uid, API_KEY, 'product.pricelist', 'search_read',
            [[['company_id', '=', 1]]], {'fields': ['id', 'name'], 'limit': 500})
        
        listas_excluir = ["DIA CONTI", "ALSK-ALQUILER DE OFICINA", "PROMO", "MAYS USD", "CRE USD", "DIST1 USD", "DIST2 USD", "SAL USD"]
        pricelists = []
        usados = set()

        for pl in pl_data:
            nombre = (pl.get('name') or "").upper().strip()
            if nombre in listas_excluir: continue
            if nombre == "DIST1": nombre = "DIST 1"
            if nombre == "DIST2": nombre = "DIST 2"
            
            if nombre not in usados:
                usados.add(nombre)
                pl['name_clean'] = nombre
                pricelists.append(pl)

        orden_precios = ["CONGS", "DIST 1", "DIST 2", "CREGS", "MAYGS", "SALGS"]
        pricelists.sort(key=lambda x: orden_precios.index(x['name_clean']) if x['name_clean'] in orden_precios else 999)

        print("Extrayendo items de listas de precios...")
        pl_items = models.execute_kw(DB, uid, API_KEY, 'product.pricelist.item', 'search_read',
            [[]], {'fields': ['pricelist_id', 'product_tmpl_id', 'fixed_price'], 'limit': 50000})

        mapa_precios = {}
        for item in pl_items:
            tmpl_id = item['product_tmpl_id'][0] if item.get('product_tmpl_id') else None
            pl_id = item['pricelist_id'][0] if item.get('pricelist_id') else None
            if tmpl_id and pl_id:
                if tmpl_id not in mapa_precios: mapa_precios[tmpl_id] = {}
                mapa_precios[tmpl_id][pl_id] = item.get('fixed_price', 0.0)

        print("Extrayendo productos de Odoo...")
        filtros = [['sale_ok', '=', True], ['active', '=', True], ['company_id', '=', 1]]
        campos = ['id', 'name', 'default_code', 'qty_available', 'categ_id', 'product_brand_id', 'product_tmpl_id', 'image_256']
        products = models.execute_kw(DB, uid, API_KEY, 'product.product', 'search_read', [filtros], {'fields': campos, 'limit': 50000})

        stock_salon = {
            "501048": 20000, "501113": 15000, "501121": 20000, "501333": 5000,
            "501366": 20000, "501379": 20000, "501493": 13000, "501505": 20000,
            "501527": 10000, "501567": 2000,  "501577": 20000, "501581": 20000,
            "501591": 20000, "501593": 15000, "501604": 4000
        }

        maygs_id = next((pl['id'] for pl in pricelists if pl['name_clean'] == 'MAYGS'), None)
        categorias_datos = {}
        
        orden_hojas = [
            "Todo", "Municiones", "Armas", "Cargadores", "ASG", "TSS", "CROSMAN", "UMAREX",
            "DOBERMAN RIFLES", "DOBERMAN MOCHILAS", "DOBERMAN BOTAS", "DOBERMAN LINTERNAS", "DOBERMAN BALINES",
            "VECTOR OPTICS", "KONUS", "BWC", "TRUGLO", "MIGUEL NIETO", "NTK", "COLEMAN", "IMALENT",
            "APOLO", "AITOR", "ROCKY BOOTS", "KCI", "NITECORE", "CATERPILLAR", "POLYMER", "SNAKE",
            "FOBUS", "BERETTA MOD", "B.E ARMOR", "OTRO"
        ]
        for hoja in orden_hojas: categorias_datos[hoja] = []

        print("Procesando catálogo visual...")
        for p in products:
            ref = (p.get('default_code') or "").upper().strip()
            if ref.startswith("AVE") or ref.startswith("NSE"): continue

            categoria_str = p['categ_id'][1].upper() if p.get('categ_id') else ""
            if "VITALICA" in categoria_str: continue

            stock = float(p.get('qty_available') or 0.0)
            if ref in stock_salon: stock = max(0, stock - stock_salon[ref])
            if stock <= 0: continue

            tmpl_id = p['product_tmpl_id'][0] if p.get('product_tmpl_id') else 0
            
            es_arma = "ARMA" in categoria_str and "ACCESORIO" not in categoria_str
            if es_arma:
                precio_maygs = mapa_precios.get(tmpl_id, {}).get(maygs_id, 0.0)
                if not maygs_id or float(precio_maygs or 0) <= 0: continue

            desc = (p.get('name') or "").upper()
            marca_str = p['product_brand_id'][1].upper() if p.get('product_brand_id') else "SIN MARCA"

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
                if "MOCHIL" in desc: hoja = "DOBERMAN MOCHILAS"
                if "BOTA" in desc: hoja = "DOBERMAN BOTAS"
                if "LINTERNA" in desc: hoja = "DOBERMAN LINTERNAS"
                if "BALIN" in desc: hoja = "DOBERMAN BALINES"

            es_cargador = "CARGADOR" in desc and not any(x in desc for x in ["PORTA", "BASE", "PISO", "ACOPLE"])
            if es_cargador: hoja = "Cargadores"

            p['stock_calculado'] = stock
            p['hoja_asignada'] = hoja
            p['categoria_limpia'] = p['categ_id'][1] if p.get('categ_id') else ""
            p['marca_limpia'] = p['product_brand_id'][1] if p.get('product_brand_id') else "Sin Marca"
            
            p_precios = []
            for pl in pricelists:
                p_val = mapa_precios.get(tmpl_id, {}).get(pl['id'], 0.0)
                p_precios.append(p_val)
            p['lista_precios_vals'] = p_precios

            categorias_datos[hoja].append(p)
            categorias_datos["Todo"].append(p)

        print("Armando interfaz web híbrida ULTRA RÁPIDA con Filtro de Vista de Tarifas...")
        logo_html = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""
        
        html = """<!DOCTYPE html><html lang='es'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Catálogo Mayorista - Camping 44</title><link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'><script src='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'></script><style>body{background-color:#f4f6f9;font-family:'Segoe UI',sans-serif;padding-bottom:30px;}.stock-rojo{background-color:#FEE2E2!important;color:#991B1B;}.stock-amarillo{background-color:#FEF3C7!important;color:#92400E;}.stock-verde{background-color:#D1FAE5!important;color:#065F46;}/* Sidebar PC */.nav-scroll-container{overflow-x:auto;white-space:nowrap;display:flex;flex-wrap:nowrap;padding:8px 5px;gap:8px;-webkit-overflow-scrolling:touch;scrollbar-width:none;}.nav-scroll-container::-webkit-scrollbar{display:none;}.desktop-sidebar{position:sticky;top:0;height:100vh;overflow-y:auto;background:#fff;border-right:1px solid #e5e7eb;padding:20px 15px;box-shadow:2px 0 10px rgba(0,0,0,0.03);scrollbar-width:thin;}/* Botones Filtro Categoria */.btn-filtro{color:#081226;font-size:0.9rem;padding:7px 10px;font-weight:600;border-radius:30px;border:1px solid #dee2e6;text-align:left;width:100%;cursor:pointer;background:#fff;transition:0.2s;margin-bottom:4px;}.nav-scroll-container .btn-filtro{width:auto;text-align:center;margin-bottom:0;}.btn-filtro.active{background-color:#081226;color:white;border-color:#081226;}/* Botones Filtro Tarifa */.btn-tarifa{color:#166534;font-size:0.9rem;padding:7px 10px;font-weight:600;border-radius:30px;border:1px solid #bbf7d0;text-align:left;width:100%;cursor:pointer;background:#f0fdf4;transition:0.2s;margin-bottom:4px;}.nav-scroll-container .btn-tarifa{width:auto;text-align:center;margin-bottom:0;}.btn-tarifa.active{background-color:#166534;color:white;border-color:#166534;}/* Tarjeta Optimizada */.tarjeta-contenedor{content-visibility:auto;contain-intrinsic-size:350px;}.producto-img{width:100%;height:200px;object-fit:contain;background:white;padding:10px;}.card-producto{border-radius:12px;overflow:hidden;transition:transform 0.15s,box-shadow 0.15s;background:#fff;border:1px solid #e5e7eb;height:100%;}.card-producto:hover{transform:translateY(-3px);box-shadow:0 10px 20px rgba(0,0,0,0.08)!important;}.price-box{background:#f9fafb;border-radius:8px;padding:6px 4px;font-size:0.82rem;text-align:center;border:1px solid #e5e7eb;height:100%;display:flex;flex-direction:column;justify-content:center;}.btn-back-to-top{position:fixed;bottom:25px;right:25px;width:50px;height:50px;border-radius:50%;background-color:#081226;color:white;border:none;box-shadow:0 4px 10px rgba(0,0,0,0.3);display:none;justify-content:center;align-items:center;z-index:1000;font-size:1.5rem;cursor:pointer;}/* CSS IMPRESIÓN */@media print{body{background:#fff;padding:0;}#web-app{display:none!important;}#print-placeholder{display:block!important;width:100%;}.print-table{width:100%!important;border-collapse:collapse!important;margin-top:20px;}.print-table th{background-color:#081226!important;color:white!important;padding:8px;border:1px solid #ddd;font-size:11px;text-transform:uppercase;text-align:center;}.print-table td{padding:6px;border:1px solid #ddd;font-size:11px;vertical-align:middle;}.print-img-pdf{width:60px!important;height:60px!important;object-fit:contain;} }</style></head><body><div id="web-app"><button onclick='window.scrollTo({top:0,behavior:"smooth"})' id='backToTop' class='btn-back-to-top' title='Volver arriba'>↑</button><div class='container-fluid'><div class='row'><div class='col-lg-2 d-none d-lg-block desktop-sidebar'><div class='text-center mb-4'><img src='##LOGO_HTML##' alt='Camping 44 Logo' style='height:45px;max-width:100%;object-fit:contain;'><h6 class='fw-bold mt-2 text-dark' style='letter-spacing:-0.5px;'>Catálogo Mayorista</h6></div><h6 class='fw-bold mb-2 text-dark px-1' style='font-size:0.8rem;'>1. FILTRAR CATEGORÍA</h6><ul class='nav flex-column gap-1 mb-3'>"""
        
        html = html.replace('##LOGO_HTML##', logo_html)
        
        first_tab = True
        for hoja in orden_hojas:
            pandas_clone = categorias_datos[hoja]
            if not pandas_clone and hoja != "Todo": continue
            active_class = "active" if first_tab else ""
            html += f"<li class='nav-item'><button class='btn-filtro {active_class}' data-filtro='{hoja}'>📦 {hoja} ({len(pandas_clone)})</button></li>"
            first_tab = False

        # BOTONES LATERALES DE TARIFA
        html += """</ul><hr style="border-color:#dee2e6;"><h6 class='fw-bold mb-2 text-success px-1' style='font-size:0.8rem;'>2. FILTRAR TARIFA VISIBLE</h6><ul class='nav flex-column gap-1'><li class='nav-item'><button class='btn-tarifa active' data-tarifa='Todas'>👁️ Mostrar Todas</button></li>"""
        for pl in pricelists:
            html += f"<li class='nav-item'><button class='btn-tarifa' data-tarifa='{pl['name_clean']}'>💲 Solo {pl['name_clean']}</button></li>"

        html += """</ul></div><div class='col-12 col-lg-10 py-3'><div class='row align-items-center mb-3 d-lg-none row-encabezado-web'><div class='col-4 text-start'><img src='##LOGO_HTML##' alt='Camping 44 Logo' style='height: 45px; max-width:140px; object-fit:contain;'></div><div class='col-8 text-end'><h4 class='fw-bold mb-0 text-dark' style='letter-spacing:-0.5px;'>Catálogo Digital</h4></div></div><div class='row row-controles g-2 justify-content-center mb-3'><div class='col-12 col-md-6'><input type='text' id='buscadorWeb' class='form-control form-control-lg border-2 shadow-sm rounded-pill px-4' placeholder='🔍 Escribe para buscar en TODO el catálogo...' style='font-size:1rem;'></div>"""
        
        html = html.replace('##LOGO_HTML##', logo_html)
        
        # MULTI-SELECTOR DE TARIFAS PARA PDF
        html += """<div class='col-7 col-md-4'><div class='dropdown'><button class='btn btn-lg btn-outline-secondary dropdown-toggle w-100 bg-white shadow-sm rounded-pill text-start d-flex justify-content-between align-items-center' type='button' data-bs-toggle='dropdown' aria-expanded='false' data-bs-auto-close='outside' style='font-size:1rem; border:2px solid #dee2e6;'><span id='lblMultiTarifa' class='text-truncate'>Seleccionar Tarifas (PDF)</span></button><ul class='dropdown-menu w-100 shadow p-2' style='max-height: 250px; overflow-y: auto;'>"""
        
        for pl in pricelists:
            html += f"<li><div class='form-check ms-2 mb-2'><input class='form-check-input check-tarifa-pdf' type='checkbox' value='{pl['name_clean']}' id='chk_{pl['name_clean']}'><label class='form-check-label fw-bold' for='chk_{pl['name_clean']}'>Tarifa {pl['name_clean']}</label></div></li>"
            
        html += "</ul></div></div><div class='col-5 col-md-2'><button id='btnGenerarPDF' onclick='generarPDFCotizacion()' class='btn btn-lg btn-danger shadow-sm rounded-pill w-100 fw-bold' style='font-size:1rem;'>📄 PDF</button></div></div><div class='position-sticky top-0 bg-light z-3 shadow-sm rounded-4 mb-3 p-2 d-lg-none' style='overflow:hidden;'><div class='nav-scroll-container mb-1 pb-2 border-bottom' style='padding:0 5px;'><ul class='nav flex-nowrap align-items-center'><span class='fw-bold text-dark me-2' style='font-size:0.8rem;'>CATEGORÍA:</span>"
        
        first_tab = True
        for hoja in orden_hojas:
            pandas_clone = categorias_datos[hoja]
            if not pandas_clone and hoja != "Todo": continue
            active_class = "active" if first_tab else ""
            html += f"<li class='nav-item'><button class='btn-filtro {active_class}' data-filtro='{hoja}'>{hoja}</button></li>"
            first_tab = False

        html += "</ul></div><div class='nav-scroll-container mt-1' style='padding:0 5px;'><ul class='nav flex-nowrap align-items-center'><span class='fw-bold text-success me-2' style='font-size:0.8rem;'>VER TARIFA:</span><li class='nav-item'><button class='btn-tarifa active' data-tarifa='Todas'>Mostrar Todas</button></li>"
        
        for pl in pricelists:
            html += f"<li class='nav-item'><button class='btn-tarifa' data-tarifa='{pl['name_clean']}'>Solo {pl['name_clean']}</button></li>"

        html += "</ul></div></div>"

        html += "<div class='row row-productos g-3' id='grilla-productos' style='padding:5px;'>"
        
        for p in categorias_datos["Todo"]:
            hoja = p['hoja_asignada']
            img_data = p.get('image_256')
            if img_data:
                if hasattr(img_data, 'data'): img_data = img_data.data
                img_base64 = img_data.decode("utf-8") if isinstance(img_data, bytes) else img_data
                img_tag = f"<img src='data:image/png;base64,{img_base64}' class='producto-img' loading='lazy' alt='P'>"
            else:
                img_tag = "<div class='producto-img d-flex align-items-center justify-content-center text-muted border-bottom'><small>Sin foto</small></div>"
            
            stock_val = p['stock_calculado']
            stock_class = "stock-rojo" if stock_val <= 5 else ("stock-amarillo" if stock_val <= 20 else "stock-verde")

            html += f"<div class='col-12 col-sm-6 col-md-4 col-lg-4 col-xl-3 tarjeta-contenedor' data-hoja='{hoja}'><div class='card card-producto shadow-sm d-flex flex-column justify-content-between'><div class='position-relative'>{img_tag}<span class='position-absolute top-0 start-0 m-2 badge bg-dark font-monospace fs-6' data-campo='codigo'>{p.get('default_code', '-')}</span><span class='position-absolute top-0 end-0 m-2 badge {stock_class} fw-bold fs-6' data-campo='stock'>Stock: {int(stock_val)}</span></div><div class='card-body d-flex flex-column justify-content-between p-3 bg-white'><div class='mb-2'><h6 class='fw-bold text-dark text-uppercase mb-1' data-campo='nombre' style='font-size:0.9rem;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;height:38px;'>{p.get('name', '')}</h6><div class='d-flex justify-content-between align-items-center'><small class='text-muted fw-bold' data-campo='marca'>{p['marca_limpia']}</small></div></div><div class='row g-1 border-top pt-2 fila-precios-tarjeta'>"
            
            has_any_price = False
            for idx, precio in enumerate(p['lista_precios_vals']):
                pl_name = pricelists[idx]["name_clean"]
                precio_val = float(precio or 0.0)
                
                if precio_val <= 0: continue 
                has_any_price = True
                
                if "USD" in pl_name:
                    precio_html = f"US$ {precio_val:,.2f}"
                else:
                    precio_html = f"{int(round(precio_val)):,}".replace(",", ".") + " Gs."
                    
                html += f"<div class='col-4 price-cell' data-tarifa-name='{pl_name}' data-tarifa-val='{precio_html}'><div class='price-box'><span class='text-muted d-block fw-bold' style='font-size:0.62rem;'>{pl_name}</span><strong class='text-success fw-bold' style='font-size:0.75rem;'>{precio_html}</strong></div></div>"
            
            if not has_any_price:
                html += "<div class='col-12'><div class='price-box text-muted small fw-semibold py-2'>Consulte precio</div></div>"
                
            html += "</div></div></div></div>"

        # JS CON MOTOR DUAL (FILTRO VISTA + FILTRO PDF MULTIPLE + REGLAS DE NEGOCIO)
        footer_html = """</div></div></div></div></div><div id='print-placeholder'></div>
        <script>
            const arrayTarjetas = Array.from(document.querySelectorAll('.tarjeta-contenedor')).map(t => ({
                el: t,
                texto: t.textContent.toUpperCase(),
                hoja: t.getAttribute('data-hoja')
            }));

            let stateCat = 'Todo';
            let stateSearch = '';
            let stateTarifa = 'Todas';

            function renderizarFiltros() {
                arrayTarjetas.forEach(t => {
                    let matchCat = (stateCat === 'Todo' || t.hoja === stateCat);
                    let matchSearch = (stateSearch === '' || t.texto.includes(stateSearch));
                    let matchTarifa = true;

                    if (stateTarifa !== 'Todas') {
                        // Verifica si la tarjeta tiene la clase correspondiente a la tarifa seleccionada
                        let priceNode = t.el.querySelector(`.price-cell[data-tarifa-name="${stateTarifa}"]`);
                        matchTarifa = (priceNode !== null);
                    }

                    t.el.style.display = (matchCat && matchSearch && matchTarifa) ? '' : 'none';
                });
            }

            // EVENTOS DE CATEGORÍA
            document.querySelectorAll('.btn-filtro').forEach(btn => {
                btn.addEventListener('click', () => {
                    let val = btn.getAttribute('data-filtro');
                    document.querySelectorAll('.btn-filtro').forEach(b => b.classList.remove('active'));
                    document.querySelectorAll(`.btn-filtro[data-filtro="${val}"]`).forEach(b => b.classList.add('active'));
                    
                    stateCat = val;
                    let buscador = document.getElementById('buscadorWeb');
                    if(buscador.value !== '') {
                        buscador.value = ''; 
                        stateSearch = '';
                    }
                    renderizarFiltros();
                    window.scrollTo({top: 0});
                });
            });

            // EVENTOS DE TARIFA VISIBLE
            document.querySelectorAll('.btn-tarifa').forEach(btn => {
                btn.addEventListener('click', () => {
                    let val = btn.getAttribute('data-tarifa');
                    document.querySelectorAll('.btn-tarifa').forEach(b => b.classList.remove('active'));
                    document.querySelectorAll(`.btn-tarifa[data-tarifa="${val}"]`).forEach(b => b.classList.add('active'));
                    
                    stateTarifa = val;
                    renderizarFiltros();
                });
            });

            // BUSCADOR INTELIGENTE
            let debounceTimer;
            document.getElementById('buscadorWeb').addEventListener('input', function() {
                clearTimeout(debounceTimer);
                let query = this.value.toUpperCase().trim();
                
                debounceTimer = setTimeout(() => {
                    stateSearch = query;
                    if (query !== '') {
                        stateCat = 'Todo';
                        document.querySelectorAll('.btn-filtro').forEach(b => b.classList.remove('active'));
                        document.querySelectorAll(`.btn-filtro[data-filtro="Todo"]`).forEach(b => b.classList.add('active'));
                    } else {
                        document.querySelector('.btn-filtro[data-filtro="Todo"]').click();
                    }
                    renderizarFiltros();
                }, 300);
            });

            window.onscroll = function() {
                let btn = document.getElementById('backToTop');
                if (document.body.scrollTop > 400 || document.documentElement.scrollTop > 400) {
                    btn.style.display = 'flex';
                } else {
                    btn.style.display = 'none';
                }
            };

            const reglasComerciales = {
                "CROSMAN": "<b>DIST 1:</b> 3 Unidades o Monto Gs. 10.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 6 Unidades o Monto Gs. 16.000.000",
                "UMAREX": "<b>DIST 1:</b> 3 Unidades o Monto Gs. 16.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 6 Unidades o Monto Gs. 25.000.000",
                "FOBUS": "<b>DIST 1:</b> 15 Unidades o Monto Gs. 4.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 30 Unidades o Monto Gs. 8.000.000",
                "KONUS": "<b>DIST 1:</b> 3 Unidades o Monto Gs. 10.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 6 Unidades o Monto Gs. 16.000.000",
                "COLEMAN": "<b>DIST 1:</b> 3 Unidades o Monto Gs. 4.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 6 Unidades o Monto Gs. 8.000.000",
                "NTK": "<b>DIST 1:</b> 3 Unidades o Monto Gs. 6.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 6 Unidades o Monto Gs. 12.000.000",
                "DOBERMAN MOCHILAS": "<b>DIST 1:</b> 12 Unidades o Monto Gs. 24.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 24 Unidades o Monto Gs. 48.000.000",
                "DOBERMAN LINTERNAS": "<b>DIST 1:</b> 25 Unidades o Monto Gs. 10.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 50 Unidades o Monto Gs. 25.000.000",
                "DOBERMAN BALINES": "<b>DIST 1:</b> 3 Cajones o Monto Gs. 10.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 6 Cajones o Monto Gs. 20.000.000",
                "NITECORE": "<b>DIST 1:</b> 6 Unidades o Monto Gs. 6.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 12 Unidades o Monto Gs. 12.000.000",
                "VECTOR OPTICS": "<b>DIST 1:</b> 3 Unidades o Monto Gs. 10.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 6 Unidades o Monto Gs. 18.000.000",
                "ASG": "<b>DIST 1:</b> 3 Unidades o Monto Gs. 12.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 6 Unidades o Monto Gs. 20.000.000",
                "CATERPILLAR": "<b>DIST 1:</b> 12 Unid (o 2 en Display) o Gs. 4.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 24 Unid (o 3 en Display) o Gs. 8.000.000",
                "KCI": "<b>DIST 1:</b> 30 Unidades o Monto Gs. 20.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 50 Unidades o Monto Gs. 40.000.000",
                "TSS": "<b>DIST 1:</b> 20 Unidades o Monto Gs. 16.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> 50 Unidades o Monto Gs. 35.000.000",
                "APOLO": "<b>DIST 1:</b> Monto Mínimo Gs. 10.000.000 &nbsp;&nbsp;|&nbsp;&nbsp; <b>DIST 2:</b> Monto Mínimo Gs. 20.000.000"
            };

            function generarPDFCotizacion() {
                try {
                    let checkboxes = document.querySelectorAll('.check-tarifa-pdf:checked');
                    let tarifasSeleccionadas = Array.from(checkboxes).map(cb => cb.value);
                    
                    if (tarifasSeleccionadas.length === 0) {
                        alert('Por favor, selecciona al menos 1 Lista de Precios en el menú (Seleccionar Tarifas PDF) antes de generar el documento.');
                        return;
                    }
                    
                    let visibles = arrayTarjetas.filter(t => t.el.style.display !== 'none');
                    
                    if (visibles.length > 400) {
                        let continuar = confirm('⚠️ ATENCIÓN: Estás a punto de exportar ' + visibles.length + ' PRODUCTOS.\\n\\nEl documento tardará en generarse debido a la cantidad de imágenes y tarifas seleccionadas.\\n\\n¿Deseás continuar?');
                        if (!continuar) return;
                    }

                    let btnPdf = document.getElementById('btnGenerarPDF');
                    let originalText = btnPdf.innerHTML;
                    btnPdf.innerHTML = '⏳ Generando...';
                    btnPdf.disabled = true;
                    
                    let activeBtn = document.querySelector('.btn-filtro.active');
                    let nombreCategoria = activeBtn ? activeBtn.getAttribute('data-filtro') : 'General';
                    
                    let htmlPdf = '<div id="print-section">';
                    
                    htmlPdf += '<div style="display:flex; justify-content:space-between; align-items:center; border-bottom:3px solid #081226; padding-bottom:10px; margin-bottom:10px;">';
                    htmlPdf += '<div style="display: flex; align-items: center; gap: 15px;">';
                    htmlPdf += '<img src="##LOGO_HTML##" alt="Camping 44" style="height: 55px; max-width:180px; object-fit:contain;">';
                    htmlPdf += '<div style="margin-left: 15px;"><h2 style="margin:0; color:#081226; font-family:sans-serif;">CAMPING 44</h2><small style="color:#666;">Cotización Múltiple de Productos</small></div>';
                    htmlPdf += '</div>';
                    htmlPdf += '<div style="text-align:right;"><span style="background:#081226; color:white; padding:5px 15px; border-radius:20px; font-weight:bold; font-size:12px;">FILTRO: ' + nombreCategoria + '</span><br><small style="color:#666;">' + tarifasSeleccionadas.join(" | ") + '</small></div>';
                    htmlPdf += '</div>';
                    
                    if (reglasComerciales[nombreCategoria]) {
                        htmlPdf += '<div style="background-color: #f8f9fa; border-left: 4px solid #166534; padding: 10px; margin-bottom: 15px; font-size: 11.5px; border-radius: 4px;">';
                        htmlPdf += '<strong style="color:#081226;">CONDICIONES COMERCIALES (' + nombreCategoria + '):</strong><br>';
                        htmlPdf += reglasComerciales[nombreCategoria];
                        htmlPdf += '</div>';
                    }
                    
                    htmlPdf += '<table class="print-table"><thead><tr><th style="width:70px; text-align:center;">Imagen</th><th style="width:90px;">Código</th><th>Descripción / Producto</th><th style="width:60px; text-align:center;">Stock</th>';
                    
                    tarifasSeleccionadas.forEach(t => {
                        htmlPdf += '<th style="width:100px; text-align:right;">Precio ' + t + '</th>';
                    });
                    htmlPdf += '</tr></thead><tbody>';
                    
                    let totalContados = 0;
                    
                    visibles.forEach(tObj => {
                        let t = tObj.el;
                        let preciosFila = [];
                        let tieneAlgunPrecio = false;
                        
                        tarifasSeleccionadas.forEach(tarifaReq => {
                            let pFinal = '-';
                            let celdasPrecio = t.querySelectorAll('.price-cell');
                            celdasPrecio.forEach(c => {
                                if (c.getAttribute('data-tarifa-name') === tarifaReq) {
                                    pFinal = c.getAttribute('data-tarifa-val');
                                }
                            });
                            if (pFinal !== '-' && pFinal) tieneAlgunPrecio = true;
                            preciosFila.push(pFinal);
                        });
                        
                        if (!tieneAlgunPrecio) return; 
                        
                        let imgEl = t.querySelector('.producto-img');
                        let imgHtml = '<span style="color:#aaa; font-size:10px;">Sin foto</span>';
                        if (imgEl && imgEl.tagName === 'IMG') {
                            imgHtml = '<img src="' + imgEl.src + '" class="print-img-pdf">';
                        }
                        
                        let codEl = t.querySelector('[data-campo="codigo"]');
                        let cod = codEl ? codEl.textContent.trim() : '-';
                        
                        let stockEl = t.querySelector('[data-campo="stock"]');
                        let stock = stockEl ? stockEl.textContent.replace('Stock:', '').trim() : '0';
                        
                        let nombreEl = t.querySelector('[data-campo="nombre"]');
                        let nombre = nombreEl ? nombreEl.textContent.trim() : 'Producto';
                        
                        let marcaEl = t.querySelector('[data-campo="marca"]');
                        let marca = marcaEl ? marcaEl.textContent.trim() : 'Sin Marca';
                        
                        htmlPdf += '<tr>';
                        htmlPdf += '<td style="text-align:center;">' + imgHtml + '</td>';
                        htmlPdf += '<td><strong style="font-family:monospace; font-size:11px;">' + cod + '</strong></td>';
                        htmlPdf += '<td><span style="font-weight:bold; font-size:11px; color:#333;">' + nombre + '</span><br><small style="color:#777; font-weight:600; font-size:10px;">Marca: ' + marca + '</small></td>';
                        htmlPdf += '<td style="text-align:center; font-weight:bold; font-size:11px;">' + stock + '</td>';
                        
                        preciosFila.forEach(precioTexto => {
                            htmlPdf += '<td style="text-align:right; font-weight:bold; font-size:12px; color:#166534;">' + precioTexto + '</td>';
                        });
                        
                        htmlPdf += '</tr>';
                        totalContados++;
                    });
                    
                    htmlPdf += '</tbody></table>';
                    htmlPdf += '<div style="margin-top:15px; text-align:right; font-size:11px; color:#777; font-weight:500;">Total de productos cotizados: ' + totalContados + ' | Generado de forma automática.</div>';
                    htmlPdf += '</div>';
                    
                    let placeholder = document.getElementById('print-placeholder');
                    placeholder.innerHTML = htmlPdf;
                    
                    setTimeout(() => {
                        window.print();
                        placeholder.innerHTML = '';
                        btnPdf.innerHTML = originalText;
                        btnPdf.disabled = false;
                    }, 500);
                    
                } catch (err) {
                    alert('Ocurrió un inconveniente al armar el PDF. Por favor intenta de nuevo.');
                    console.error(err);
                }
            }
        </script></body></html>"""

        html += footer_html.replace('##LOGO_HTML##', logo_html)

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        peso_final = os.path.getsize("index.html") / (1024 * 1024)
        print(f"¡Catálogo Multi-Tarifa optimizado con éxito! Peso: {peso_final:.2f} MB")

    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    main()
