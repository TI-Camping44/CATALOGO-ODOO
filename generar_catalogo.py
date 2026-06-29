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

            # AHORA SOLO GUARDAMOS EN TODO PARA EL CONTEO, SIN DUPLICAR HTML MÁS ADELANTE
            categorias_datos[hoja].append(p)
            categorias_datos["Todo"].append(p)

        print("Armando interfaz web híbrida ULTRA RÁPIDA...")
        logo_html = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""
        
        # INICIO HTML Y CSS OPTIMIZADO (content-visibility para que no explote la memoria)
        html = """<!DOCTYPE html><html lang='es'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Catálogo Mayorista - Camping 44</title><link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'><style>body{background-color:#f4f6f9;font-family:'Segoe UI',sans-serif;padding-bottom:30px;}.stock-rojo{background-color:#FEE2E2!important;color:#991B1B;}.stock-amarillo{background-color:#FEF3C7!important;color:#92400E;}.stock-verde{background-color:#D1FAE5!important;color:#065F46;}/* Sidebar y Scrollbars */.nav-scroll-container{overflow-x:auto;white-space:nowrap;display:flex;flex-wrap:nowrap;padding:10px 5px;gap:8px;-webkit-overflow-scrolling:touch;scrollbar-width:none;}.nav-scroll-container::-webkit-scrollbar{display:none;}.desktop-sidebar{position:sticky;top:0;height:100vh;overflow-y:auto;background:#fff;border-right:1px solid #e5e7eb;padding:20px 15px;box-shadow:2px 0 10px rgba(0,0,0,0.03);scrollbar-width:thin;}/* Botones Filtro */.btn-filtro{color:#081226;font-size:0.95rem;padding:9px 16px;font-weight:600;border-radius:30px;border:1px solid #dee2e6;text-align:left;width:100%;cursor:pointer;background:#fff;transition:0.2s;}.nav-scroll-container .btn-filtro{width:auto;text-align:center;}.btn-filtro.active{background-color:#081226;color:white;border-color:#081226;}/* Tarjeta Ultra Optimizada */.tarjeta-contenedor{content-visibility:auto;contain-intrinsic-size:350px;}.producto-img{width:100%;height:220px;object-fit:contain;background:white;padding:10px;}.card-producto{border-radius:14px;overflow:hidden;transition:transform 0.15s,box-shadow 0.15s;background:#fff;border:1px solid #e5e7eb;height:100%;}.card-producto:hover{transform:translateY(-3px);box-shadow:0 10px 20px rgba(0,0,0,0.08)!important;}.price-box{background:#f9fafb;border-radius:8px;padding:6px 4px;font-size:0.82rem;text-align:center;border:1px solid #e5e7eb;height:100%;display:flex;flex-direction:column;justify-content:center;}.btn-back-to-top{position:fixed;bottom:25px;right:25px;width:50px;height:50px;border-radius:50%;background-color:#081226;color:white;border:none;box-shadow:0 4px 10px rgba(0,0,0,0.3);display:none;justify-content:center;align-items:center;z-index:1000;font-size:1.5rem;cursor:pointer;}@media print{body{background:#fff;padding:0;}.desktop-sidebar,#buscadorWeb,.btn-back-to-top,.row-controles,.nav-scroll-container,.row-encabezado-web{display:none!important;}.row{display:block!important;}#print-section{display:block!important;}.print-table{width:100%!important;border-collapse:collapse!important;margin-top:20px;}.print-table th{background-color:#081226!important;color:white!important;padding:10px;border:1px solid #ddd;font-size:11px;text-transform:uppercase;}.print-table td{padding:8px;border:1px solid #ddd;font-size:11px;vertical-align:middle;}.print-img-pdf{width:70px!important;height:70px!important;object-fit:contain;} }</style></head><body><button onclick='window.scrollTo({top:0,behavior:"smooth"})' id='backToTop' class='btn-back-to-top' title='Volver arriba'>↑</button><div class='container-fluid'><div class='row'><div class='col-lg-3 d-none d-lg-block desktop-sidebar'><div class='text-center mb-4'><img src='##LOGO_HTML##' alt='Camping 44 Logo' style='height:65px;max-width:100%;object-fit:contain;'><h5 class='fw-bold mt-3 text-dark' style='letter-spacing:-0.5px;'>Camping 44 - Catálogo</h5></div><ul class='nav flex-column gap-2'>"""
        
        html = html.replace('##LOGO_HTML##', logo_html)
        
        first_tab = True
        for hoja in orden_hojas:
            pandas_clone = categorias_datos[hoja]
            if not pandas_clone and hoja != "Todo": continue
            active_class = "active" if first_tab else ""
            html += f"<li class='nav-item'><button class='btn-filtro {active_class}' data-filtro='{hoja}'>📦 {hoja} ({len(pandas_clone)})</button></li>"
            first_tab = False

        html += """</ul></div><div class='col-12 col-lg-9 py-3'><div class='row align-items-center mb-3 d-lg-none row-encabezado-web'><div class='col-4 text-start'><img src='##LOGO_HTML##' alt='Camping 44 Logo' style='height: 50px; max-width:160px; object-fit:contain;'></div><div class='col-8 text-end'><h3 class='fw-bold mb-0 text-dark' style='letter-spacing:-0.5px;'>Catálogo Digital</h3></div></div><div class='row row-controles g-2 justify-content-center mb-3'><div class='col-12 col-md-6'><input type='text' id='buscadorWeb' class='form-control form-control-lg border-2 shadow-sm rounded-pill px-4' placeholder='🔍 Escribe para buscar en TODO el catálogo...' style='font-size:1.1rem;'></div><div class='col-7 col-md-3'><select id='selectTarifaPDF' class='form-select form-select-lg border-2 shadow-sm rounded-pill' style='font-size:1rem;'><option value=''>-- Seleccionar Tarifa PDF --</option>"""
        
        html = html.replace('##LOGO_HTML##', logo_html)
        
        for pl in pricelists:
            html += f"<option value='{pl['name_clean']}'>Exportar {pl['name_clean']}</option>"
            
        html += "</select></div><div class='col-5 col-md-2'><button onclick='generarPDFCotizacion()' class='btn btn-lg btn-danger shadow-sm rounded-pill w-100 fw-bold' style='font-size:1rem;'>📄 PDF</button></div></div><div class='position-sticky top-0 bg-light z-3 shadow-sm rounded-4 mb-3 nav-scroll-container d-lg-none'><ul class='nav flex-nowrap'>"
        
        first_tab = True
        for hoja in orden_hojas:
            pandas_clone = categorias_datos[hoja]
            if not pandas_clone and hoja != "Todo": continue
            active_class = "active" if first_tab else ""
            html += f"<li class='nav-item'><button class='btn-filtro {active_class}' data-filtro='{hoja}'>{hoja}</button></li>"
            first_tab = False

        html += "</ul></div>"

        # GENERACIÓN DE GRILLA ÚNICA (SÚPER RÁPIDA, NO MÁS TABS DUPLICADAS)
        html += "<div class='row row-productos g-3' id='grilla-productos' style='padding:5px;'>"
        
        # Iteramos SOLO la lista TODO. Cada tarjeta tiene el data-hoja asignado.
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

        # MOTOR JAVASCRIPT RE-ESCRITO PARA PERFORMANCE (DEBOUNCING Y DOM CACHE)
        footer_html = """</div></div></div></div><div id='print-placeholder'></div>
        <script>
            // CACHE EN MEMORIA PARA QUE LA TABLET NO EXPLOTE BUSCANDO
            const arrayTarjetas = Array.from(document.querySelectorAll('.tarjeta-contenedor')).map(t => ({
                el: t,
                texto: t.innerText.toUpperCase(),
                hoja: t.getAttribute('data-hoja')
            }));

            const botonesFiltro = document.querySelectorAll('.btn-filtro');

            // SISTEMA DE BOTONES (FILTROS INSTANTÁNEOS SIN RECARGAR)
            botonesFiltro.forEach(btn => {
                btn.addEventListener('click', () => {
                    let filtro = btn.getAttribute('data-filtro');
                    
                    botonesFiltro.forEach(b => b.classList.remove('active'));
                    document.querySelectorAll(`.btn-filtro[data-filtro="${filtro}"]`).forEach(b => b.classList.add('active'));

                    let buscador = document.getElementById('buscadorWeb');
                    if(buscador.value !== '') buscador.value = ''; // Limpiar buscador al cambiar de pestaña

                    arrayTarjetas.forEach(t => {
                        t.el.style.display = (filtro === 'Todo' || t.hoja === filtro) ? '' : 'none';
                    });
                    window.scrollTo({top: 0});
                });
            });

            // BUSCADOR INTELIGENTE CON "ACELERADOR" (DEBOUNCE 300ms)
            let debounceTimer;
            document.getElementById('buscadorWeb').addEventListener('input', function() {
                clearTimeout(debounceTimer);
                let query = this.value.toUpperCase().trim();
                
                debounceTimer = setTimeout(() => {
                    if (query !== '') {
                        // Forzar a pestaña TODO
                        botonesFiltro.forEach(b => b.classList.remove('active'));
                        document.querySelectorAll(`.btn-filtro[data-filtro="Todo"]`).forEach(b => b.classList.add('active'));
                        
                        arrayTarjetas.forEach(t => {
                            t.el.style.display = t.texto.includes(query) ? '' : 'none';
                        });
                    } else {
                        // Si borra el texto, vuelve a la pestaña TODO y muestra todo
                        document.querySelector('.btn-filtro[data-filtro="Todo"]').click();
                    }
                }, 300); // <-- ESTA ES LA CLAVE PARA QUE NO SE CUELGUE LA TABLET
            });

            // BOTÓN VOLVER ARRIBA
            window.onscroll = function() {
                let btn = document.getElementById('backToTop');
                if (document.body.scrollTop > 400 || document.documentElement.scrollTop > 400) {
                    btn.style.display = 'flex';
                } else {
                    btn.style.display = 'none';
                }
            };

            // PDF BLINDADO (NO SE ROMPE SI FALTA FOTO)
            function generarPDFCotizacion() {
                try {
                    let tarifa = document.getElementById('selectTarifaPDF').value;
                    if (!tarifa) {
                        alert('Por favor, selecciona una Lista de Precios antes de generar el PDF.');
                        return;
                    }
                    
                    let activeBtn = document.querySelector('.btn-filtro.active');
                    let nombreCategoria = activeBtn ? activeBtn.innerText.split('(')[0].trim() : 'General';
                    
                    let htmlPdf = '<div id="print-section">';
                    htmlPdf += '<div style="display:flex; justify-content:space-between; align-items:center; border-bottom:3px solid #081226; padding-bottom:10px; margin-bottom:15px;">';
                    htmlPdf += '<div style="display: flex; align-items: center; gap: 15px;">';
                    htmlPdf += '<img src="##LOGO_HTML##" alt="Camping 44" style="height: 55px; max-width:180px; object-fit:contain;">';
                    htmlPdf += '<div style="margin-left: 15px;"><h2 style="margin:0; color:#081226; font-family:sans-serif;">CAMPING 44</h2><small style="color:#666;">Catálogo Digital de Productos</small></div>';
                    htmlPdf += '</div>';
                    htmlPdf += '<div style="text-align:right;"><span style="background:#081226; color:white; padding:5px 15px; border-radius:20px; font-weight:bold; font-size:12px;">TARIFA: ' + tarifa + '</span><br><small style="color:#666;">Filtro: ' + nombreCategoria + '</small></div>';
                    htmlPdf += '</div>';
                    
                    htmlPdf += '<table class="print-table"><thead><tr><th style="width:80px; text-align:center;">Imagen</th><th style="width:100px;">Código</th><th>Descripción / Producto</th><th style="width:70px; text-align:center;">Stock</th><th style="width:130px; text-align:right;">Precio ('+tarifa+')</th></tr></thead><tbody>';
                    
                    let totalContados = 0;
                    
                    // Solo exporta los que están visibles en pantalla ahora mismo
                    let visibles = arrayTarjetas.filter(t => t.el.style.display !== 'none');
                    
                    visibles.forEach(tObj => {
                        let t = tObj.el;
                        let precioFinal = '-';
                        let celdasPrecio = t.querySelectorAll('.price-cell');
                        celdasPrecio.forEach(c => {
                            if (c.getAttribute('data-tarifa-name') === tarifa) {
                                precioFinal = c.getAttribute('data-tarifa-val');
                            }
                        });
                        
                        if (precioFinal === '-' || !precioFinal) return; 
                        
                        let imgEl = t.querySelector('.producto-img');
                        let imgHtml = '<span style="color:#aaa; font-size:10px;">Sin foto</span>';
                        if (imgEl && imgEl.tagName === 'IMG') {
                            imgHtml = '<img src="' + imgEl.src + '" class="print-img-pdf">';
                        }
                        
                        let codEl = t.querySelector('[data-campo="codigo"]');
                        let cod = codEl ? codEl.innerText : '-';
                        
                        let stockEl = t.querySelector('[data-campo="stock"]');
                        let stock = stockEl ? stockEl.innerText.replace('Stock: ', '') : '0';
                        
                        let nombreEl = t.querySelector('[data-campo="nombre"]');
                        let nombre = nombreEl ? nombreEl.innerText : 'Producto';
                        
                        let marcaEl = t.querySelector('[data-campo="marca"]');
                        let marca = marcaEl ? marcaEl.innerText : 'Sin Marca';
                        
                        htmlPdf += '<tr>';
                        htmlPdf += '<td style="text-align:center;">' + imgHtml + '</td>';
                        htmlPdf += '<td><strong style="font-family:monospace; font-size:12px;">' + cod + '</strong></td>';
                        htmlPdf += '<td><span style="font-weight:bold; font-size:12px; color:#333;">' + nombre + '</span><br><small style="color:#777; font-weight:600;">Marca: ' + marca + '</small></td>';
                        htmlPdf += '<td style="text-align:center; font-weight:bold;">' + stock + '</td>';
                        htmlPdf += '<td style="text-align:right; font-weight:bold; font-size:13px; color:#166534;">' + precioFinal + '</td>';
                        htmlPdf += '</tr>';
                        totalContados++;
                    });
                    
                    htmlPdf += '</tbody></table>';
                    htmlPdf += '<div style="margin-top:15px; text-align:right; font-size:11px; color:#777; font-weight:500;">Total de productos cotizados: ' + totalContados + ' | Generado automáticamente desde Odoo.</div>';
                    htmlPdf += '</div>';
                    
                    let placeholder = document.getElementById('print-placeholder');
                    placeholder.innerHTML = htmlPdf;
                    window.print();
                    placeholder.innerHTML = '';
                    
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
        print(f"¡Catálogo Ultra-Rápido optimizado con éxito! Peso: {peso_final:.2f} MB")

    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    main()
