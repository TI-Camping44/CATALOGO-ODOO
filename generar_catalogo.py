import xmlrpc.client
import os
import json
import sys
import traceback

# =====================================
# CONFIGURACIÓN DIRECTA (CAMPING 44)
# =====================================
URL = "https://camping44.odoo.com"
DB = "gcaceres93-camping-main-15845610"
USER = "facundocolman@camping44.com.py"
API_KEY = "55f70e57a3caa3113e3ffa559b5ba020931dc501"

# DICCIONARIO MAESTRO CON PRECIOS EXACTOS DE LIQUIDACIÓN (SOLO SALGS)
PRECIOS_LIQUIDACION_EXACTOS = {
    "110306": "20.000", "110307": "20.000", "110509": "250.000", "110562": "220.000", "110563": "380.000", "110567": "275.000", "110568": "215.000", "110569": "215.000", "110582": "215.000", "110583": "190.000", "110584": "215.000", "110585": "385.000", "110586": "385.000", "110587": "385.000", "110588": "385.000", "110589": "725.000", "110734": "250.000", "110738": "250.000", "110739": "380.000", "110751": "150.000", "110753": "170.000", "110756": "390.000", "110759": "265.000", "110760": "350.000", "111564": "220.000", "111566": "220.000", "112000": "25.000", "115702": "750.000", "115703": "850.000", "115704": "900.000", "140470": "55.000", "140704": "230.000", "140705": "230.000", "140706": "230.000", "140707": "230.000", "151500": "650.000", "151501": "650.000", "151502": "570.000", "151516": "140.000", "151523": "650.000", "151531": "990.000", "151537": "890.000", "151538": "890.000", "151539": "890.000", "151543": "550.000", "151544": "550.000", "151565": "400.000", "151570": "400.000", "151590": "997.000", "151595": "1.350.000", "151661": "750.000", "160082": "55.000", "170229": "675.000", "170356": "17.000", "190001": "70.000", "200137": "280.000", "200138": "100.000", "200139": "100.000", "200320": "65.000", "200378": "85.000", "250060": "57.000", "250061": "57.000", "250062": "57.000", "250690": "130.000", "250691": "95.000", "250692": "80.000", "250693": "65.000", "250694": "80.000", "260252": "25.000", "260275": "4.000.000", "260357": "990.000", "260360": "850.000", "260361": "990.000", "260362": "420.000", "260366": "1.350.000", "260368": "1.850.000", "260372": "400.000", "260375": "70.000", "260601": "250.000", "260715": "65.000", "260850": "170.000", "261300": "75.000", "261405": "1.750.000", "261406": "700.000", "262000": "500.000", "270050": "300.000", "270056": "420.000", "270057": "140.000", "270101": "4.000.000", "270103": "2.500.000", "270150": "1.100.000", "270151": "1.200.000", "270151U": "700.000", "270152": "2.000.000", "270157": "320.000", "270198": "1.300.000", "270200": "210.000", "270202": "495.000", "270203": "265.000", "270204": "350.000", "270204U": "180.000", "270250": "175.000", "270251": "190.000", "270500": "120.000", "270501": "120.000", "270550": "210.000", "270560": "250.000", "270565": "250.000", "270570": "250.000", "270575": "250.000", "270601": "285.000", "270602": "850.000", "270650": "600.000", "270660": "75.000", "270680": "235.000", "270689": "55.000", "270801": "295.000", "270808": "320.000", "270809": "380.000", "270812": "320.000", "270813": "310.000", "270816": "280.000", "270821": "320.000", "270822": "320.000", "270823": "320.000", "270830": "320.000", "270900": "140.000", "272022": "1.600.000", "272063": "140.000", "300090": "1.800.000", "300091": "1.800.000", "300092": "1.200.000", "300093": "1.350.000", "300094": "7.875.000", "300096": "7.875.000", "320016": "142.500", "320054": "200.000", "320061": "300.000", "320065": "350.000", "320079": "520.000", "320095": "350.000", "320130": "235.000", "320155": "1.600.000", "320156": "1.750.000", "320202": "650.000", "320207": "1.450.000", "320259": "1.000.000", "320400": "950.000", "320514": "180.000", "320515": "230.000", "320516": "375.000", "320517": "100.000", "320600": "420.000", "321055": "95.000", "321057": "30.000", "321058": "30.000", "321060": "105.000", "321061": "350.000", "321062": "350.000", "321070": "50.000", "321075": "50.000", "323110": "1.490.000", "323510": "140.000", "324000": "3.750.000", "324020": "3.750.000", "350200": "320.000", "350201": "200.000", "350202": "285.000", "350203": "255.000", "400212": "6.500", "400214": "25.000", "400216": "5.000", "400217": "30.000", "400221": "12.000", "400231": "73.000", "400247": "48.000", "400253": "42.500", "400290": "35.000", "400291": "35.000", "400386": "55.000", "440154": "1.565.000", "440158": "1.565.000", "440161": "1.565.000", "440162": "1.565.000", "510260": "540.000", "510261": "480.000", "510262": "365.000", "510749": "300.000", "550259": "5.000", "550400": "990.000", "610914": "285.000", "610927": "230.000", "610932": "165.000", "610935": "11.000", "610936": "12.000", "610937": "14.000", "610939": "23.000", "610941": "29.000", "610945": "70.000", "610946": "75.000", "610947": "85.000", "610948": "95.000", "610950": "33.000", "610966": "125.000", "610967": "160.000", "610968": "160.000", "610979": "25.000", "610980": "27.000", "611254": "22.000", "620122": "45.000", "620123": "45.000", "620182": "500", "620184": "500", "620189": "500", "620193": "1.750", "620202": "3.000", "620580": "4.500", "620581": "5.500", "620582": "6.500", "620583": "8.000", "620584": "8.000", "620585": "7.000", "620586": "6.500", "620587": "6.000", "620588": "6.000", "620589": "7.000", "620590": "7.700", "620591": "10.000", "620600": "7.000", "620601": "6.000", "620602": "5.000", "620603": "5.000", "620604": "5.000", "620605": "7.000", "620606": "5.000", "620607": "8.000", "620608": "5.000", "620609": "5.500", "620610": "3.500", "620611": "7.800", "620612": "4.500", "620613": "6.000", "620615": "6.800", "620616": "7.000", "620617": "7.000", "620618": "7.000", "620619": "7.000", "620620": "7.000", "620621": "3.000", "620622": "2.500", "620623": "2.500", "620624": "2.500", "620625": "2.500", "620626": "2.500", "620627": "2.500", "620628": "2.500", "620629": "2.500", "620630": "2.500", "620631": "2.500", "620632": "2.500", "620633": "3.000", "620634": "3.500", "620644": "3.000", "620646": "3.500", "620648": "5.000", "620649": "6.500", "620650": "7.500", "620651": "9.500", "620653": "8.000", "620655": "8.000", "620656": "7.000", "620657": "6.500", "620658": "6.000", "620659": "5.000", "620660": "5.000", "620661": "5.000", "620662": "5.000", "620663": "5.000", "620664": "6.500", "620665": "6.500", "620666": "6.500", "620667": "6.500", "620668": "5.500", "620670": "6.500", "620672": "2.000", "620673": "2.000", "620674": "2.750", "620676": "3.250", "620677": "3.250", "620679": "4.000", "620680": "5.000", "620681": "2.000", "620682": "2.000", "620683": "2.000", "620684": "2.000", "620685": "2.500", "620686": "3.000", "620687": "3.000", "620688": "3.500", "620689": "4.500", "620690": "5.500", "620691": "5.500", "620692": "5.500", "620693": "5.500", "620694": "5.500", "620695": "5.000", "620696": "5.500", "620697": "6.000", "620698": "6.000", "620699": "5.500", "621010": "3.000", "621011": "3.500", "621013": "3.500", "621022": "3.000", "621040": "3.000", "621041": "3.500", "621042": "3.000", "621043": "3.500", "621044": "3.000", "621046": "3.000", "621050": "3.000", "621054": "3.000", "621058": "3.000", "621062": "3.000", "621070": "3.000", "621071": "3.500", "621072": "3.000", "621073": "4.000", "621076": "3.000", "621080": "3.500", "621084": "3.000", "621100": "7.000", "621101": "7.000", "621102": "7.000", "621103": "7.000", "621104": "7.000", "621105": "7.000", "621106": "7.000", "621107": "7.000", "621108": "7.000", "621109": "7.000", "621110": "7.000", "621111": "7.000", "621112": "7.000", "621114": "7.000", "621115": "7.000", "621116": "7.000", "621117": "7.000", "621118": "7.000", "621119": "7.000", "621120": "7.000", "621121": "4.000", "621122": "3.000", "621123": "3.000", "621124": "3.500", "621125": "2.500", "621126": "2.500", "621127": "2.500", "621128": "2.500", "621129": "2.500", "621130": "2.500", "621131": "2.500", "621132": "2.500", "621150": "8.500", "621151": "8.500", "621152": "7.500", "621153": "7.500", "621154": "7.500", "621155": "7.500", "621156": "8.000", "621200": "12.000", "621201": "9.000", "621202": "10.000", "621203": "9.000", "621204": "10.000", "621205": "12.000", "621206": "9.000", "621207": "14.000", "621208": "7.500", "621209": "19.000", "621210": "7.000", "621214": "5.500", "621218": "5.000", "621222": "5.000", "630030": "5.000", "630031": "8.500", "630032": "14.000", "630033": "6.000", "630034": "6.000", "630035": "6.000", "630036": "7.000", "630037": "5.500", "630038": "7.000", "630039": "7.000", "630040": "8.000", "670113": "50.000", "680085": "80.000", "680466": "210.000", "680477": "210.000", "680532": "345.000", "680534": "230.000", "680537": "550.000", "680539": "285.000", "680552": "110.000", "680564": "275.000", "680571": "420.000", "680572": "850.000", "680592": "1.700.000", "680597": "650.000", "680598": "570.000", "680599": "350.000", "680675": "70.000", "680848": "260.000", "680850": "155.000", "681090": "850.000", "681100": "600.000", "681101": "420.000", "681102": "550.000", "681103": "250.000", "681104": "790.000", "681105": "700.000", "681106": "580.000", "681107": "1.800.000", "681108": "1.250.000", "681109": "320.000", "681110": "500.000", "681111": "850.000", "681112": "320.000", "681113": "520.000", "681115": "550.000", "681116": "420.000", "681120": "250.000", "681122": "710.000", "710418": "390.000", "711300": "735.000", "711305": "735.000", "711307": "735.000", "712115": "195.000", "712116": "210.000", "712117": "210.000", "712118": "210.000", "712120": "25.000", "730459": "75.000", "749000": "130.000", "751000": "40.000", "751002": "48.000", "751003": "40.000", "751004": "70.000", "751005": "40.000", "751007": "40.000", "751008": "47.000", "751009": "57.000", "751010": "80.000", "760060": "95.000", "770522": "225.000", "800170": "85.000", "800173": "65.000", "830240": "17.000", "830241": "17.000", "830242": "17.000", "830243": "17.000", "830246": "17.000", "830247": "17.000", "830249": "28.500", "830250": "26.500", "830251": "30.000", "830252": "30.000", "830253": "4.500", "830254": "5.500", "830255": "5.500", "830256": "6.000", "830257": "6.000", "830258": "6.500", "830259": "6.500", "830260": "7.250", "830261": "8.000", "830262": "10.500", "830263": "14.000", "830264": "17.500", "830265": "20.000", "830266": "10.500", "830267": "12.500", "830268": "12.500", "830269": "13.500", "830270": "16.000", "830273": "18.500", "830276": "39.000", "830277": "51.000", "830278": "59.000", "830280": "14.000", "830281": "14.000", "830282": "14.000", "830283": "14.000", "830284": "14.000", "830285": "14.000", "830286": "16.500", "830287": "16.500", "830288": "16.500", "830290": "14.000", "830291": "14.000", "830293": "14.000", "830294": "14.000", "830295": "14.000", "830296": "14.000", "830313": "30.000", "830314": "30.000", "830318": "55.000", "830319": "55.000", "830322": "26.000", "830323": "26.000", "830324": "26.000", "830325": "28.000", "830327": "26.000", "830328": "26.000", "830329": "26.000", "830334": "47.000", "830335": "47.000", "830337": "47.000", "830340": "47.000", "830342": "47.000", "830345": "25.000", "830346": "25.000", "830350": "28.000", "830351": "28.000", "830352": "28.000", "830353": "28.000", "830354": "55.000", "830355": "59.000", "830356": "64.000", "830357": "72.000", "830358": "79.500", "900376": "710.000", "900379": "65.000", "900382": "95.000", "900383": "95.000", "900397": "1.590.000", "900398": "1.400.000", "900621": "100.000", "900806": "75.000", "900810": "18.000", "901001": "70.000", "901005": "70.000", "901010": "70.000", "901150": "120.000", "901152": "135.000", "901265": "115.000", "901273": "95.000", "901408": "150.000", "901410": "120.000", "901411": "80.000", "901412": "17.000", "901500": "190.000", "901600": "55.000", "901601": "500.000", "901610": "60.000", "901611": "550.000", "901620": "65.000", "901621": "600.000", "904000": "100.000", "904100": "8.000", "920120": "15.000", "920140": "8.600", "920141": "8.600", "920142": "8.600", "920143": "8.600", "920146": "50.000", "920147": "50.000", "920150": "550.000", "920184": "45.000", "920392": "95.000", "920394": "150.000", "920398": "190.000", "920414": "300.000", "920415": "300.000", "920420": "300.000", "921063": "100.000", "921140": "90.000", "940178": "90.000", "940179": "90.000", "990060": "65.000", "DES149010": "1.350.000", "DES150080": "185.000", "DES151202": "250.000", "DES151562": "220.000", "DES151563": "420.000", "DES151564": "520.000", "DES151611": "450.000", "DES151612": "550.000", "DES190001": "70.000", "DES191100": "325.000", "DES191110": "265.000", "DES320154": "820.000", "DES320202": "650.000", "DES320207": "1.400.000", "DES320259": "1.425.000", "DES320270": "1.990.000", "DES320275": "1.750.000", "DES320522": "2.200.000", "DES320850": "1.750.000", "DES321201": "600.000", "DES321202": "790.000", "DES321203": "140.000", "DES323500": "140.000", "DES325000": "400.000", "DES400258": "35.000", "DES440220": "70.000", "DES510130": "155.000", "DES611034": "335.000", "DES650225": "125.000", "DES680467": "175.000", "DES680470": "110.000", "DES680507": "140.000", "DES680509": "1.400.000", "DES680512": "245.000", "DES680513": "1.600.000", "DES680514": "1.900.000", "DES680516": "1.200.000", "DES680517": "1.100.000", "DES680518": "1.100.000", "DES680525": "150.000", "DES680529": "80.000", "DES680531": "65.000", "DES680532": "65.000", "DES680537": "65.000", "DES680539": "285.000", "DES680540": "125.000", "DES680549": "250.000", "DES680552": "65.000", "DES680554": "570.000", "DES680557": "210.000", "DES680561": "520.000", "DES681101": "415.000", "DES710031": "390.000", "DES710240": "120.000", "DES710422": "375.000", "DES750100": "95.000", "DES750185": "850.000", "DES750186": "1.125.000", "DES750190": "25.000", "DES750300": "185.000", "DES750301": "210.000", "DES750302": "250.000", "DES750305": "360.000", "DES750310": "320.000", "DES750315": "380.000", "DES750325": "275.000", "DES750330": "375.000", "DES750335": "420.000", "DES750340": "520.000", "DES750420": "220.000", "DES750422": "3.550.000", "DES750427": "227.500", "DES750428": "227.500", "DES750429": "227.500", "DES770700": "75.000", "DES880051": "1.400.000", "DES880052": "1.400.000", "DES880053": "1.400.000", "DES880054": "1.400.000", "DES880055": "1.400.000", "DES880070": "1.275.000", "DES880071": "1.275.000", "DES880072": "1.275.000", "DES880073": "1.275.000", "DES880074": "1.275.000", "DES880075": "1.275.000", "DES880091": "1.100.000", "DES880092": "1.100.000", "DES901152": "125.550", "DES901411": "80.000", "DES920155": "1.650.000", "DES920284": "400.000", "DES941058": "285.000", "DES941059": "195.000", "EGF320007": "-", "LIQ150970": "469.000", "LIQ150982": "2.450.000", "LIQ150983": "2.450.000", "LIQ150985": "850.000", "LIQ150995": "1.390.000", "LIQ150996": "1.350.000", "LIQ151190": "320.000", "LIQ170135": "200.000", "LIQ260048": "1.800.000", "LIQ260276": "3.300.000", "LIQ260560": "1.150.000", "LIQ320019": "350.000", "LIQ320069": "330.000", "LIQ320156": "1.800.000", "LIQ320202": "600.000", "LIQ320260": "1.650.000", "LIQ320264": "1.800.000", "LIQ320445": "330.000", "LIQ320450": "275.000", "LIQ320511": "3.300.000", "LIQ320800": "1.000.000", "LIQ320850": "1.500.000", "LIQ321000": "285.000", "LIQ322500": "1.500.000", "LIQ324100": "850.000", "LIQ610902": "99.000", "LIQ610962": "155.000", "LIQ610964": "115.000", "LIQ680465": "200.000", "LIQ680554": "530.000", "LIQ680555": "285.000", "LIQ680558": "225.000", "LIQ680595": "320.000", "LIQ680597": "1.700.000", "LIQ680598": "570.000", "LIQ680599": "350.000", "LIQ680670": "35.000", "LIQ710031": "380.000", "LIQ750301": "190.000", "LIQ750330": "340.000", "LIQ750428": "210.000", "LIQ750429": "210.000", "LIQ770301": "465.000", "LIQ800160": "40.000", "LIQ800170": "85.000", "LIQ800173": "65.000", "LIQ800175": "60.000", "LIQ800186": "60.000", "LIQ920110": "70.000", "LIQREP611063": "98.000", "LIQREP900770": "136.500", "LIQREP900772": "171.500", "LIQREP900773": "87.500", "REP900300": "21.000", "REP900301": "21.000", "REP900302": "7.000", "REP900767": "38.500", "REP900768": "38.500", "REP900769": "38.500", "REP900775": "56.000", "REP900776": "17.500", "REP900777": "70.000", "REP900778": "17.500", "REP900779": "70.000", "REP900780": "56.000", "REP900781": "84.000", "REP900782": "21.000", "REP900783": "21.000", "REP900784": "35.000", "REP900785": "35.000", "REP900786": "35.000", "REP900787": "14.000", "REP900788": "7.000", "REP900789": "7.000", "REP900791": "35.000", "REP900792": "35.000", "REP900793": "14.000", "REP900795": "14.000", "REP900798": "7.000", "REP900803": "17.500", "REP900853": "38.500", "REP900866": "42.000", "REP900867": "38.500", "REP900868": "38.500", "REP900869": "38.500", "REP901100": "3.500", "REP901120": "12.600", "REP901130": "10.500", "REP901140": "14.000"
}

def main():
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USER, API_KEY, {})
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')

        print("Conectado a Odoo exitosamente. Extrayendo datos de la empresa...")
        comp_data = models.execute_kw(DB, uid, API_KEY, 'res.company', 'search_read', [[['id', '=', 1]]], {'fields': ['logo_web']})
        logo_base64 = ""
        if isinstance(comp_data, list) and comp_data and comp_data[0].get('logo_web'):
            logo_base64 = comp_data[0]['logo_web']
            if isinstance(logo_base64, bytes):
                logo_base64 = logo_base64.decode('utf-8')

        pl_data = models.execute_kw(DB, uid, API_KEY, 'product.pricelist', 'search_read',
            [[['active', '=', True]]], {'fields': ['id', 'name'], 'limit': 500})
        
        if not isinstance(pl_data, list):
            pl_data = []
            
        listas_permitidas = ["CONGS", "DIST 1", "DIST 2", "CREGS", "MAYGS", "SALGS"]
        pricelists_dict = {}

        for pl in pl_data:
            raw_name = str(pl.get('name') or "").upper().strip()
            
            # IGNORA SI ES USD O VIEJA
            if "USD" in raw_name or "PROMO" in raw_name or "DIA CONTI" in raw_name: 
                continue

            nombre = None
            if "DIST" in raw_name and "1" in raw_name: nombre = "DIST 1"
            elif "DIST" in raw_name and "2" in raw_name: nombre = "DIST 2"
            elif "CONGS" in raw_name: nombre = "CONGS"
            elif "CREGS" in raw_name: nombre = "CREGS"
            elif "MAYGS" in raw_name: nombre = "MAYGS"
            elif "SALGS" in raw_name: nombre = "SALGS"
            
            if nombre:
                # SI ENCUENTRA LA MISMA LISTA DOS VECES, SIEMPRE SE QUEDA CON LA QUE TIENE "(PYG)"
                if nombre not in pricelists_dict or "PYG" in raw_name:
                    pl['name_clean'] = nombre
                    pricelists_dict[nombre] = pl
                    
        pricelists = list(pricelists_dict.values())
        pricelists.sort(key=lambda x: listas_permitidas.index(x['name_clean']))
        pl_ids_to_fetch = [pl['id'] for pl in pricelists]

        print(f"Extrayendo items SOLO para las {len(pl_ids_to_fetch)} listas oficiales...")
        # ACA ESTÁ EL TRUCO: LE PIDE A ODOO SOLO LAS LISTAS CORRECTAS PARA NO AHOGARLO
        pl_items = models.execute_kw(DB, uid, API_KEY, 'product.pricelist.item', 'search_read',
            [[['pricelist_id', 'in', pl_ids_to_fetch]]], 
            {'fields': ['pricelist_id', 'product_tmpl_id', 'product_id', 'fixed_price'], 'limit': 300000})

        if not isinstance(pl_items, list):
            pl_items = []

        mapa_precios_tmpl = {}
        mapa_precios_prod = {}
        
        for item in pl_items:
            pl_id = item['pricelist_id'][0] if item.get('pricelist_id') else None
            if not pl_id: continue
            
            precio = float(item.get('fixed_price') or 0.0)
            
            tmpl_id = item.get('product_tmpl_id')
            if tmpl_id:
                t_id = tmpl_id[0] if isinstance(tmpl_id, list) else tmpl_id
                if t_id not in mapa_precios_tmpl: mapa_precios_tmpl[t_id] = {}
                mapa_precios_tmpl[t_id][pl_id] = precio
                
            prod_id = item.get('product_id')
            if prod_id:
                p_id = prod_id[0] if isinstance(prod_id, list) else prod_id
                if p_id not in mapa_precios_prod: mapa_precios_prod[p_id] = {}
                mapa_precios_prod[p_id][pl_id] = precio

        print("Extrayendo productos base de Odoo (sin imágenes para no saturar)...")
        filtros = [['sale_ok', '=', True], ['active', '=', True], ['company_id', '=', 1]]
        campos = ['id', 'name', 'default_code', 'qty_available', 'categ_id', 'product_brand_id', 'product_tmpl_id']
        products = models.execute_kw(DB, uid, API_KEY, 'product.product', 'search_read', [filtros], {'fields': campos, 'limit': 50000})

        if not isinstance(products, list):
            products = []

        print(f"Se encontraron {len(products)} productos. Extrayendo imágenes en lotes pequeños...")
        product_ids = [p['id'] for p in products]
        imagenes_dict = {}
        chunk_size = 300 
        
        for i in range(0, len(product_ids), chunk_size):
            chunk_ids = product_ids[i:i+chunk_size]
            try:
                img_data = models.execute_kw(DB, uid, API_KEY, 'product.product', 'search_read', [[['id', 'in', chunk_ids]]], {'fields': ['id', 'image_256']})
                if isinstance(img_data, list):
                    for img in img_data:
                        if img.get('image_256'):
                            val = img['image_256']
                            imagenes_dict[img['id']] = val.decode('utf-8') if isinstance(val, bytes) else val
            except Exception as e_chunk:
                print(f"Aviso: Fallo al extraer el lote de imágenes {i}, omitiendo.")

        print("Calculando y descontando productos perdidos en ubicación NSE...")
        nse_locs = models.execute_kw(DB, uid, API_KEY, 'stock.location', 'search', [[['complete_name', 'ilike', 'NSE']]])
        if not isinstance(nse_locs, list): nse_locs = []
        
        nse_stock = {}
        if nse_locs:
            quants = models.execute_kw(DB, uid, API_KEY, 'stock.quant', 'search_read', 
                [[['location_id', 'in', nse_locs]]], 
                {'fields': ['product_id', 'quantity']})
            if not isinstance(quants, list): quants = []
                
            for q in quants:
                if q.get('product_id'):
                    pid = q['product_id'][0] if isinstance(q['product_id'], list) else q['product_id']
                    nse_stock[pid] = nse_stock.get(pid, 0.0) + float(q.get('quantity', 0.0))

        stock_salon = {
            "501048": 20000, "501113": 15000, "501121": 20000, "501333": 5000,
            "501366": 20000, "501379": 20000, "501493": 13000, "501505": 20000,
            "501527": 10000, "501567": 2000,  "501577": 20000, "501581": 20000,
            "501591": 20000, "501593": 15000, "501604": 4000
        }

        maygs_id = next((pl['id'] for pl in pricelists if pl['name_clean'] == 'MAYGS'), None)
        categorias_datos = {}
        
        orden_hojas = [
            "Todo", "🔥 LIQUIDACIÓN", "Municiones", "Armas", "Cargadores", "ASG", "TSS", "CROSMAN", "UMAREX",
            "DOBERMAN RIFLES", "DOBERMAN MOCHILAS", "DOBERMAN BOTAS", "DOBERMAN LINTERNAS", "DOBERMAN BALINES",
            "VECTOR OPTICS", "KONUS", "BWC", "TRUGLO", "MIGUEL NIETO", "NTK", "COLEMAN", "IMALENT",
            "APOLO", "AITOR", "ROCKY BOOTS", "KCI", "NITECORE", "CATERPILLAR", "POLYMER", "SNAKE",
            "FOBUS", "BERETTA MOD", "B.E ARMOR", "OTRO"
        ]
        for hoja in orden_hojas: categorias_datos[hoja] = []

        print("Procesando catálogo visual...")
        for p in products:
            ref = str(p.get('default_code') or "").upper().strip()
            if ref.startswith("AVE") or ref.startswith("NSE"): continue

            categoria_str = p['categ_id'][1].upper() if p.get('categ_id') else ""
            if "VITALICA" in categoria_str: continue

            stock = float(p.get('qty_available') or 0.0)
            if ref in stock_salon: stock = stock - stock_salon[ref]
            if p['id'] in nse_stock: stock = stock - nse_stock[p['id']]

            tmpl_id = p['product_tmpl_id'][0] if p.get('product_tmpl_id') else 0
            prod_id = p['id']
            
            es_arma = "ARMA" in categoria_str and "ACCESORIO" not in categoria_str
            if es_arma:
                precio_maygs = mapa_precios_prod.get(prod_id, {}).get(maygs_id)
                if not precio_maygs or precio_maygs <= 0:
                    precio_maygs = mapa_precios_tmpl.get(tmpl_id, {}).get(maygs_id, 0.0)
                    
                if not maygs_id or float(precio_maygs or 0) <= 0: continue

            desc = str(p.get('name') or "").upper()
            marca_str = p['product_brand_id'][1].upper() if p.get('product_brand_id') else "SIN MARCA"
            
            es_liquidacion = ref in PRECIOS_LIQUIDACION_EXACTOS or any(palabra in categoria_str or palabra in desc for palabra in ["LIQUIDACION", "LIQUIDACIÓN", "OUTLET"])

            hoja = "OTRO"
            if es_liquidacion: hoja = "🔥 LIQUIDACIÓN"
            elif "MUNICION" in categoria_str: hoja = "Municiones"
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

            es_cargador = "CARGADOR" in desc and not any(x in desc for x in ["PORTA", "BASE", "PISO", "ACOPLE"]) and not es_liquidacion
            if es_cargador: hoja = "Cargadores"

            p['stock_calculado'] = stock
            p['hoja_asignada'] = hoja
            p['categoria_limpia'] = p['categ_id'][1] if p.get('categ_id') else ""
            p['marca_limpia'] = p['product_brand_id'][1] if p.get('product_brand_id') else "Sin Marca"
            
            p_precios = []
            for pl in pricelists:
                pl_id = pl['id']
                p_val = mapa_precios_prod.get(prod_id, {}).get(pl_id)
                if not p_val or p_val <= 0:
                    p_val = mapa_precios_tmpl.get(tmpl_id, {}).get(pl_id, 0.0)
                p_precios.append(float(p_val or 0.0))
                
            p['lista_precios_vals'] = p_precios

            categorias_datos[hoja].append(p)
            categorias_datos["Todo"].append(p)

        print("Creando Base de Datos Liviana...")
        productos_js = []
        imagenes_js = {}
        
        for p in categorias_datos["Todo"]:
            base_price = 0.0
            for val in p['lista_precios_vals']:
                if float(val or 0.0) > 0:
                    base_price = float(val)
                    break
                    
            cod_limpio = str(p.get('default_code') or '-').strip()
            nombre_limpio = str(p.get('name') or '')

            prod_dict = {
                "c": cod_limpio,
                "n": nombre_limpio,
                "m": p['marca_limpia'],
                "s": int(p['stock_calculado']),
                "h": p['hoja_asignada'],
                "pr": base_price, 
                "p": {}
            }
            
            img_base64 = imagenes_dict.get(p['id'])
            if img_base64:
                imagenes_js[cod_limpio] = img_base64
                
            for idx, precio in enumerate(p['lista_precios_vals']):
                pl_name = pricelists[idx]["name_clean"]
                precio_val = float(precio or 0.0)
                if precio_val > 0:
                    if "USD" in pl_name:
                        prod_dict["p"][pl_name] = f"US$ {precio_val:,.2f}"
                    else:
                        prod_dict["p"][pl_name] = f"{int(round(precio_val)):,}".replace(",", ".") + " Gs."
                        
            productos_js.append(prod_dict)

        json_str = json.dumps(productos_js)
        json_images_str = json.dumps(imagenes_js)
        json_ofertas_str = json.dumps(PRECIOS_LIQUIDACION_EXACTOS)
        logo_html = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

        print("Generando index.html...")
        
        html = """<!DOCTYPE html><html lang='es'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Catálogo Mayorista - Camping 44</title>
        <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>
        <script src='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.31/jspdf.plugin.autotable.min.js"></script>
        <style>body{background-color:#f4f6f9;font-family:'Segoe UI',sans-serif;padding-bottom:30px;}.stock-rojo{background-color:#FEE2E2!important;color:#991B1B;}.stock-amarillo{background-color:#FEF3C7!important;color:#92400E;}.stock-verde{background-color:#D1FAE5!important;color:#065F46;}/* Sidebar PC */.nav-scroll-container{overflow-x:auto;white-space:nowrap;display:flex;flex-wrap:nowrap;padding:8px 5px;gap:8px;-webkit-overflow-scrolling:touch;scrollbar-width:none;}.nav-scroll-container::-webkit-scrollbar{display:none;}.desktop-sidebar{position:sticky;top:0;height:100vh;overflow-y:auto;background:#fff;border-right:1px solid #e5e7eb;padding:20px 15px;box-shadow:2px 0 10px rgba(0,0,0,0.03);scrollbar-width:thin;}/* Botones Filtro Categoria */.btn-filtro{color:#081226;font-size:0.9rem;padding:7px 10px;font-weight:600;border-radius:30px;border:1px solid #dee2e6;text-align:left;width:100%;cursor:pointer;background:#fff;transition:0.2s;margin-bottom:4px;}.nav-scroll-container .btn-filtro{width:auto;text-align:center;margin-bottom:0;}.btn-filtro.active{background-color:#081226;color:white;border-color:#081226;}.btn-filtro[data-filtro="🔥 LIQUIDACIÓN"] { color: #dc3545; border-color: #f8d7da; background-color: #fff5f5; }.btn-filtro[data-filtro="🔥 LIQUIDACIÓN"].active { background-color: #dc3545; color: white; border-color: #dc3545; }/* Botones Filtro Tarifa */.btn-tarifa{color:#166534;font-size:0.9rem;padding:7px 10px;font-weight:600;border-radius:30px;border:1px solid #bbf7d0;text-align:left;width:100%;cursor:pointer;background:#f0fdf4;transition:0.2s;margin-bottom:4px;}.nav-scroll-container .btn-tarifa{width:auto;text-align:center;margin-bottom:0;}.btn-tarifa.active{background-color:#166534;color:white;border-color:#166534;}/* Panel PDF Foolproof */.pdf-panel{background:#fff;border:2px solid #fecaca;border-radius:12px;padding:12px 18px;display:flex;flex-wrap:wrap;gap:15px;align-items:center;justify-content:space-between;}.pdf-panel-title{font-size:0.85rem;font-weight:800;color:#dc3545;margin:0;}.check-group{display:flex;flex-wrap:wrap;gap:12px;align-items:center;}/* Tarjeta Optimizada */.tarjeta-contenedor{contain: content;}.producto-img{width:100%;height:200px;object-fit:contain;background:white;padding:10px;}.card-producto{border-radius:12px;overflow:hidden;transition:transform 0.15s,box-shadow 0.15s;background:#fff;border:1px solid #e5e7eb;height:100%;}.card-producto:hover{transform:translateY(-3px);box-shadow:0 10px 20px rgba(0,0,0,0.08)!important;}.price-box{background:#f9fafb;border-radius:8px;padding:6px 4px;font-size:0.82rem;text-align:center;border:1px solid #e5e7eb;height:100%;display:flex;flex-direction:column;justify-content:center;}.btn-back-to-top{position:fixed;bottom:25px;right:25px;width:50px;height:50px;border-radius:50%;background-color:#081226;color:white;border:none;box-shadow:0 4px 10px rgba(0,0,0,0.3);display:none;justify-content:center;align-items:center;z-index:1000;font-size:1.5rem;cursor:pointer;}
        </style></head><body><div id="web-app"><button onclick='window.scrollTo({top:0,behavior:"smooth"})' id='backToTop' class='btn-back-to-top' title='Volver arriba'>↑</button><div class='container-fluid'><div class='row'>
        
        <div class='col-lg-2 d-none d-lg-block desktop-sidebar' id="sidebarDesktop">
            <div class='text-center mb-4'><img src='##LOGO_HTML##' alt='Camping 44 Logo' style='height:45px;max-width:100%;object-fit:contain;'><h6 class='fw-bold mt-2 text-dark' style='letter-spacing:-0.5px;'>Catálogo Mayorista</h6></div>
            <div id="seccionFiltrosMaster">
                <h6 class='fw-bold mb-2 text-success px-1' style='font-size:0.8rem;'>1. VER PRECIOS EN PANTALLA</h6>
                <ul class='nav flex-column gap-1 mb-3'>
                    <li class='nav-item'><button class='btn-tarifa active' data-tarifa='Todas'>👁️ Mostrar Todas</button></li>"""
        
        html = html.replace('##LOGO_HTML##', logo_html)

        for pl in pricelists:
            html += f"<li class='nav-item'><button class='btn-tarifa' data-tarifa='{pl['name_clean']}'>💲 {pl['name_clean']}</button></li>"

        html += """</ul><hr style="border-color:#dee2e6;">
                <h6 class='fw-bold mb-2 text-dark px-1' style='font-size:0.8rem;'>2. FILTRAR POR CATEGORÍA</h6>
                <ul class='nav flex-column gap-1' id="listaCategoriasM">"""
        
        first_tab = True
        for hoja in orden_hojas:
            pandas_clone = categorias_datos[hoja]
            if not pandas_clone and hoja != "Todo": continue
            active_class = "active" if first_tab else ""
            html += f"<li class='nav-item'><button class='btn-filtro {active_class}' data-filtro='{hoja}'>📦 {hoja} ({len(pandas_clone)})</button></li>"
            first_tab = False

        html += """</ul></div></div>
        
        <div class='col-12 col-lg-10 py-3'>
            <div class='row align-items-center mb-3 d-lg-none row-encabezado-web'>
                <div class='col-4 text-start'><img src='##LOGO_HTML##' alt='Camping 44 Logo' style='height: 45px; max-width:140px; object-fit:contain;'></div>
                <div class='col-8 text-end'><h4 class='fw-bold mb-0 text-dark' style='letter-spacing:-0.5px;'>Catálogo Mayorista</h4></div>
            </div>"""
        
        html = html.replace('##LOGO_HTML##', logo_html)
        
        html += """<div class='row g-2 mb-3'>
                <div class='col-12 col-md-8'><input type='text' id='buscadorWeb' class='form-control form-control-lg border-2 shadow-sm rounded-pill px-4' placeholder='🔍 Escribe para buscar...' style='font-size:1.05rem;'></div>
                <div class='col-12 col-md-4'><select id='ordenarPor' class='form-select form-select-lg border-2 shadow-sm rounded-pill' style='font-size:1rem;'><option value='default'>⇅ Ordenar por...</option><option value='az'>🔤 A - Z (Alfabético)</option><option value='za'>🔤 Z - A (Alfabético)</option><option value='stock_desc'>📦 Mayor Stock</option><option value='stock_asc'>📦 Menor Stock</option><option value='precio_asc'>💲 Menor Precio</option><option value='precio_desc'>💲 Mayor Precio</option></select></div>
            </div>"""

        html += """<div class='pdf-panel shadow-sm mb-3'>
                <div class='check-group'>
                    <span class='pdf-panel-title'>📄 DESCARGAR PDF:</span>"""
        for pl in pricelists:
            html += f"<div class='form-check form-check-inline m-0'><input class='form-check-input check-tarifa-pdf' type='checkbox' value='{pl['name_clean']}' id='chk_{pl['name_clean']}'><label class='form-check-label small fw-bold text-dark' for='chk_{pl['name_clean']}'>{pl['name_clean']}</label></div>"
            
        html += "<div class='form-check form-check-inline m-0 border-start ps-3 ms-1'><input class='form-check-input' type='checkbox' id='chkMostrarStock' checked><label class='form-check-label small text-muted fw-bold' for='chkMostrarStock'>📦 Stock</label></div>"
        html += "<div class='form-check form-check-inline m-0 border-start ps-2'><input class='form-check-input' type='checkbox' id='chkOcultarAgotados' checked><label class='form-check-label small text-muted fw-bold' for='chkOcultarAgotados'>🚫 Ocultar Agotados</label></div>"
        html += """</div>
                <div class='d-flex align-items-center mt-2 mt-md-0'>
                    <span id='lblSeleccionados' class='small fw-bold text-primary me-3'></span>
                    <button id='btnGenerarPDF' onclick='descargarPDFNativo()' class='btn btn-danger btn-sm fw-bold px-4 py-2 rounded-pill shadow-sm' style='font-size:0.9rem;'>DESCARGAR</button>
                </div>
            </div>"""
        
        html += """<div class='position-sticky top-0 bg-light z-3 shadow-sm rounded-4 mb-3 p-2 d-lg-none' style='overflow:hidden;'>
                <div class='nav-scroll-container mb-1 pb-2 border-bottom' style='padding:0 5px;'>
                    <ul class='nav flex-nowrap align-items-center' id="contenedorTarifasMovil">
                        <span class='fw-bold text-success me-2' style='font-size:0.8rem;'>PRECIOS:</span>
                        <li class='nav-item'><button class='btn-tarifa active' data-tarifa='Todas'>Todas</button></li>"""
        for pl in pricelists:
            html += f"<li class='nav-item'><button class='btn-tarifa' data-tarifa='{pl['name_clean']}'>{pl['name_clean']}</button></li>"
            
        html += """</ul>
                </div>
                <div class='nav-scroll-container mt-1' style='padding:0 5px;'>
                    <ul class='nav flex-nowrap align-items-center' id="contenedorCategoriasMovil">
                        <span class='fw-bold text-dark me-2' style='font-size:0.8rem;'>MARCA:</span>"""
        
        first_tab = True
        for hoja in orden_hojas:
            pandas_clone = categorias_datos[hoja]
            if not pandas_clone and hoja != "Todo": continue
            active_class = "active" if first_tab else ""
            html += f"<li class='nav-item'><button class='btn-filtro {active_class}' data-filtro='{hoja}'>{hoja}</button></li>"
            first_tab = False

        html += """</ul></div></div>
            <div class='row row-productos g-3' id='grilla-productos' style='padding:5px;'></div>
        </div>"""

        footer_html = """</div></div></div><div id='print-placeholder'></div>
        <script>
            const PRODUCTOS = ##JSON_DATA##;
            const IMAGENES = ##JSON_IMAGES##;
            const OFERTAS_EXACTAS = ##JSON_OFERTAS##;
            
            let stateCat = 'Todo';
            let stateSearch = '';
            let stateTarifa = 'Todas';
            let stateSort = 'default';
            let productosFiltrados = [];
            let paginaActual = 0;
            const ITEMS_POR_PAGINA = 30; 
            let selectedSKUs = new Set();

            function toggleProdPDF(sku, isChecked) {
                if (isChecked) selectedSKUs.add(sku);
                else selectedSKUs.delete(sku);
                
                let lbl = document.getElementById('lblSeleccionados');
                if(selectedSKUs.size > 0) {
                    lbl.innerHTML = `🛒 ${selectedSKUs.size} para PDF <a href="javascript:void(0)" onclick="limpiarSeleccion()" class="text-danger ms-1">Limpiar</a>`;
                } else {
                    lbl.innerHTML = '';
                }
            }

            function limpiarSeleccion() {
                selectedSKUs.clear();
                document.getElementById('lblSeleccionados').innerHTML = '';
                document.getElementById('grilla-productos').innerHTML = '';
                paginaActual = 0;
                renderizarPagina();
            }

            function aplicarFiltros() {
                let q = stateSearch.toUpperCase().trim();
                let ocultarAgotados = document.getElementById('chkOcultarAgotados').checked;
                
                productosFiltrados = PRODUCTOS.filter(p => {
                    if (ocultarAgotados && p.s <= 0) return false;
                    let matchCat = (stateCat === 'Todo' || p.h === stateCat);
                    let matchSearch = (q === '' || p.n.toUpperCase().includes(q) || p.c.toUpperCase().includes(q));
                    let matchTarifa = true;
                    if (stateTarifa !== 'Todas') {
                        matchTarifa = (p.p[stateTarifa] !== undefined);
                    }
                    return matchCat && matchSearch && matchTarifa;
                });
                
                if (stateSort === 'az') productosFiltrados.sort((a, b) => a.n.localeCompare(b.n));
                else if (stateSort === 'za') productosFiltrados.sort((a, b) => b.n.localeCompare(a.n));
                else if (stateSort === 'stock_desc') productosFiltrados.sort((a, b) => b.s - a.s);
                else if (stateSort === 'stock_asc') productosFiltrados.sort((a, b) => a.s - b.s);
                else if (stateSort === 'precio_asc') productosFiltrados.sort((a, b) => a.pr - b.pr);
                else if (stateSort === 'precio_desc') productosFiltrados.sort((a, b) => b.pr - a.pr);
                
                paginaActual = 0;
                document.getElementById('grilla-productos').innerHTML = '';
                renderizarPagina();
            }

            document.getElementById('ordenarPor').addEventListener('change', function() {
                stateSort = this.value;
                aplicarFiltros();
                window.scrollTo({top: 0});
            });
            
            document.getElementById('chkOcultarAgotados').addEventListener('change', aplicarFiltros);

            function renderizarPagina() {
                let start = paginaActual * ITEMS_POR_PAGINA;
                let end = start + ITEMS_POR_PAGINA;
                let items = productosFiltrados.slice(start, end);
                
                if (items.length === 0 && paginaActual === 0) {
                    document.getElementById('grilla-productos').innerHTML = '<div class="col-12 text-center py-5"><h5 class="text-muted">No se encontraron productos</h5></div>';
                    return;
                }

                let html = '';
                items.forEach(p => {
                    let b64 = IMAGENES[p.c];
                    let imgTag = b64 ? `<img src="data:image/png;base64,${b64}" class="producto-img" loading="lazy">` : `<div class="producto-img d-flex align-items-center justify-content-center text-muted border-bottom"><small>Sin foto</small></div>`;
                    let stockClass = p.s <= 0 ? 'bg-danger text-white' : (p.s <= 5 ? 'stock-rojo' : (p.s <= 20 ? 'stock-amarillo' : 'stock-verde'));
                    let stockText = p.s <= 0 ? 'AGOTADO' : `Stock: ${p.s}`;
                    let badgeLiq = p.h === '🔥 LIQUIDACIÓN' ? `<span class='position-absolute top-0 end-0 m-2 badge bg-danger text-white fw-bold shadow' style='font-size:0.8rem; padding:5px 9px; border-radius:8px; z-index:11; letter-spacing:0.5px;'>💥 OFERTA</span>` : '';
                    
                    let preciosHtml = '';
                    for (const [tarifa, precio] of Object.entries(p.p)) {
                        if (stateTarifa !== 'Todas' && tarifa !== stateTarifa) continue;
                        
                        if (p.h === '🔥 LIQUIDACIÓN' && OFERTAS_EXACTAS[p.c]) {
                            let precioOferta = OFERTAS_EXACTAS[p.c] + ' Gs.';
                            preciosHtml += `<div class='col-12 p-1'><div class='price-box border-danger' style='background-color:#FFF5F5;'><span class='text-muted d-block fw-bold' style='font-size:0.6rem; line-height:1;'>${tarifa}</span><span class='text-muted text-decoration-line-through d-block small' style='font-size:0.65rem;'>Mayorista: ${precio}</span><strong class='text-danger fw-black' style='font-size:0.85rem;'>🔥 Oferta: ${precioOferta}</strong></div></div>`;
                        } else {
                            preciosHtml += `<div class='col-6 price-cell p-1'><div class='price-box'><span class='text-muted d-block fw-bold' style='font-size:0.62rem;'>${tarifa}</span><strong class='text-success fw-bold' style='font-size:0.75rem;'>${precio}</strong></div></div>`;
                        }
                    }
                    if (preciosHtml === '') {
                        preciosHtml = `<div class='col-12'><div class='price-box text-muted small fw-semibold py-2'>Consulte precio</div></div>`;
                    }
                    
                    let checkChecked = selectedSKUs.has(p.c) ? 'checked' : '';

                    html += `<div class='col-12 col-sm-6 col-md-4 col-lg-4 col-xl-3 tarjeta-contenedor'>
                        <div class='card card-producto shadow-sm d-flex flex-column justify-content-between'>
                            <div class='position-relative'>
                                ${badgeLiq}
                                ${imgTag}
                                <span class='position-absolute top-0 start-0 m-2 badge bg-dark font-monospace fs-6'>${p.c}</span>
                                <span class='position-absolute bottom-0 end-0 m-2 badge ${stockClass} fw-bold fs-6'>${stockText}</span>
                            </div>
                            <div class='card-body d-flex flex-column justify-content-between p-3 bg-white'>
                                <div class='mb-2'>
                                    <h6 class='fw-bold text-dark text-uppercase mb-1' style='font-size:0.9rem;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;height:38px;'>${p.n}</h6>
                                    <div class='d-flex justify-content-between align-items-center'>
                                        <small class='text-muted fw-bold'>${p.m}</small>
                                    </div>
                                </div>
                                <div class="form-check mt-1 mb-2">
                                    <input class="form-check-input" type="checkbox" value="${p.c}" id="chk_${p.c}" ${checkChecked} onchange="toggleProdPDF('${p.c}', this.checked)" style="border-color:#0d6efd; cursor:pointer;">
                                    <label class="form-check-label fw-bold text-primary" for="chk_${p.c}" style="font-size:0.75rem; cursor:pointer; user-select:none;">Añadir al PDF</label>
                                </div>
                                <div class='row g-0 pt-1 border-top'>
                                    ${preciosHtml}
                                </div>
                            </div>
                        </div>
                    </div>`;
                });
                
                document.getElementById('grilla-productos').insertAdjacentHTML('beforeend', html);
                paginaActual++;
            }

            window.addEventListener('scroll', () => {
                if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 800) {
                    if (paginaActual * ITEMS_POR_PAGINA < productosFiltrados.length) {
                        renderizarPagina();
                    }
                }
                let btn = document.getElementById('backToTop');
                if (document.body.scrollTop > 400 || document.documentElement.scrollTop > 400) {
                    btn.style.display = 'flex';
                } else {
                    btn.style.display = 'none';
                }
            });

            document.addEventListener("DOMContentLoaded", () => {
                aplicarFiltros();
            });

            document.querySelectorAll('.btn-filtro').forEach(btn => {
                btn.addEventListener('click', () => {
                    let val = btn.getAttribute('data-filtro');
                    document.querySelectorAll('.btn-filtro').forEach(b => b.classList.remove('active'));
                    document.querySelectorAll(`.btn-filtro[data-filtro="${val}"]`).forEach(b => b.classList.add('active'));
                    stateCat = val;
                    let buscador = document.getElementById('buscadorWeb');
                    if(buscador.value !== '') { buscador.value = ''; stateSearch = ''; }
                    aplicarFiltros();
                    window.scrollTo({top: 0});
                });
            });

            document.querySelectorAll('.btn-tarifa').forEach(btn => {
                btn.addEventListener('click', () => {
                    let val = btn.getAttribute('data-tarifa');
                    document.querySelectorAll('.btn-tarifa').forEach(b => b.classList.remove('active'));
                    document.querySelectorAll(`.btn-tarifa[data-tarifa="${val}"]`).forEach(b => b.classList.add('active'));
                    stateTarifa = val;
                    aplicarFiltros();
                });
            });

            let debounceTimer;
            document.getElementById('buscadorWeb').addEventListener('input', function() {
                clearTimeout(debounceTimer);
                let query = this.value;
                debounceTimer = setTimeout(() => {
                    stateSearch = query;
                    aplicarFiltros();
                }, 300);
            });

            const reglasComerciales = {
                "CROSMAN": "DIST 1: 3 Unidades o Monto Gs. 10.000.000  |  DIST 2: 6 Unidades o Monto Gs. 16.000.000",
                "UMAREX": "DIST 1: 3 Unidades o Monto Gs. 16.000.000  |  DIST 2: 6 Unidades o Monto Gs. 25.000.000",
                "FOBUS": "DIST 1: 15 Unidades o Monto Gs. 4.000.000  |  DIST 2: 30 Unidades o Monto Gs. 8.000.000",
                "KONUS": "DIST 1: 3 Unidades o Monto Gs. 10.000.000  |  DIST 2: 6 Unidades o Monto Gs. 16.000.000",
                "COLEMAN": "DIST 1: 3 Unidades o Monto Gs. 4.000.000  |  DIST 2: 6 Unidades o Monto Gs. 8.000.000",
                "NTK": "DIST 1: 3 Unidades o Monto Gs. 6.000.000  |  DIST 2: 6 Unidades o Monto Gs. 12.000.000",
                "DOBERMAN MOCHILAS": "DIST 1: 12 Unidades o Monto Gs. 24.000.000  |  DIST 2: 24 Unidades o Monto Gs. 48.000.000",
                "DOBERMAN LINTERNAS": "DIST 1: 25 Unidades o Monto Gs. 10.000.000  |  DIST 2: 50 Unidades o Monto Gs. 25.000.000",
                "DOBERMAN BALINES": "DIST 1: 3 Cajones o Monto Gs. 10.000.000  |  DIST 2: 6 Cajones o Monto Gs. 20.000.000",
                "NITECORE": "DIST 1: 6 Unidades o Monto Gs. 6.000.000  |  DIST 2: 12 Unidades o Monto Gs. 12.000.000",
                "VECTOR OPTICS": "DIST 1: 3 Unidades o Monto Gs. 10.000.000  |  DIST 2: 6 Unidades o Monto Gs. 18.000.000",
                "ASG": "DIST 1: 3 Unidades o Monto Gs. 12.000.000  |  DIST 2: 6 Unidades o Monto Gs. 20.000.000",
                "CATERPILLAR": "DIST 1: 12 Unid (o 2 Display) o Gs. 4.000.000  |  DIST 2: 24 Unid (o 3 Display) o Gs. 8.000.000",
                "KCI": "DIST 1: 30 Unidades o Monto Gs. 20.000.000  |  DIST 2: 50 Unidades o Monto Gs. 40.000.000",
                "TSS": "DIST 1: 20 Unidades o Monto Gs. 16.000.000  |  DIST 2: 50 Unidades o Monto Gs. 35.000.000",
                "APOLO": "DIST 1: Monto Mínimo Gs. 10.000.000  |  DIST 2: Monto Mínimo Gs. 20.000.000"
            };

            function descargarPDFNativo() {
                let checkboxes = document.querySelectorAll('.check-tarifa-pdf:checked');
                let tarifasSeleccionadas = Array.from(checkboxes).map(cb => cb.value);
                
                if (tarifasSeleccionadas.length === 0) {
                    alert('Por favor, tildá al menos 1 Tarifa en el panel de Opciones PDF.');
                    return;
                }
                
                if (productosFiltrados.length > 500 && selectedSKUs.size === 0) {
                    let continuar = confirm('⚠️ ATENCIÓN: Vas a descargar ' + productosFiltrados.length + ' productos.\\n\\nComo el sistema tiene que armar una tabla muy grande y pegarle las fotos adentro, puede demorar varios segundos.\\n\\n¿Deseás continuar?');
                    if (!continuar) return;
                }

                let btnPdf = document.getElementById('btnGenerarPDF');
                let originalText = btnPdf.innerHTML;
                btnPdf.innerHTML = '⏳ Procesando...';
                btnPdf.disabled = true;

                setTimeout(() => {
                    try {
                        const { jsPDF } = window.jspdf;
                        const doc = new jsPDF();
                        let mostrarStock = document.getElementById('chkMostrarStock').checked;
                        let logoBase64 = '##LOGO_HTML##';
                        
                        let textX = 14;
                        if (logoBase64.length > 100) {
                            try {
                                let imgProps = doc.getImageProperties(logoBase64);
                                let imgRatio = imgProps.height / imgProps.width;
                                let targetWidth = 45; 
                                let targetHeight = targetWidth * imgRatio;
                                
                                if (targetHeight > 18) {
                                    targetHeight = 18;
                                    targetWidth = targetHeight / imgRatio;
                                }
                                
                                doc.addImage(logoBase64, 'PNG', 14, 10, targetWidth, targetHeight);
                                textX = 14 + targetWidth + 5; 
                            } catch(e) {
                                doc.addImage(logoBase64, 'PNG', 14, 10, 40, 15);
                                textX = 60;
                            }
                        }
                        
                        doc.setFontSize(16);
                        doc.setTextColor(8, 18, 38);
                        doc.text("CAMPING 44", textX, 16);
                        doc.setFontSize(10);
                        doc.setTextColor(100, 100, 100);
                        doc.text("Cotización Mayorista", textX, 22);
                        
                        doc.setFontSize(9);
                        doc.setTextColor(8, 18, 38);
                        doc.text("Filtro: " + stateCat, 195, 16, {align: 'right'});
                        doc.setTextColor(100, 100, 100);
                        doc.text(tarifasSeleccionadas.join(" | "), 195, 22, {align: 'right'});

                        let startY = 35;

                        if (reglasComerciales[stateCat] && selectedSKUs.size === 0) {
                            doc.setFillColor(240, 253, 244);
                            doc.rect(14, 30, 181, 12, 'F');
                            doc.setDrawColor(22, 101, 52);
                            doc.setLineWidth(1);
                            doc.line(14, 30, 14, 42);
                            
                            doc.setFontSize(8);
                            doc.setTextColor(8, 18, 38);
                            doc.text("CONDICIONES (" + stateCat + "): " + reglasComerciales[stateCat], 18, 37);
                            startY = 50;
                        }

                        let columnas = ["Img", "Código", "Descripción"];
                        if (mostrarStock) columnas.push("Stock");
                        tarifasSeleccionadas.forEach(t => columnas.push(t));

                        let filas = [];
                        let skusPdf = [];

                        let productosParaPDF = [];
                        if (selectedSKUs.size > 0) {
                            productosParaPDF = PRODUCTOS.filter(p => selectedSKUs.has(p.c));
                        } else {
                            productosParaPDF = productosFiltrados;
                        }

                        productosParaPDF.forEach(p => {
                            let preciosFila = [];
                            let tienePrecio = false;
                            
                            tarifasSeleccionadas.forEach(t => {
                                if (p.p[t]) {
                                    if (p.h === '🔥 LIQUIDACIÓN' && OFERTAS_EXACTAS[p.c]) {
                                        let po = OFERTAS_EXACTAS[p.c] + ' Gs.';
                                        preciosFila.push(po + " (OFERTA)"); 
                                    } else {
                                        preciosFila.push(p.p[t]); 
                                    }
                                    tienePrecio = true;
                                } else {
                                    preciosFila.push('-');
                                }
                            });
                            
                            if (!tienePrecio) return; 

                            let row = [];
                            row.push(""); 
                            row.push(p.c);
                            let nombreFinal = p.h === '🔥 LIQUIDACIÓN' ? "[LIQ] " + p.n : p.n;
                            row.push(nombreFinal + "\\nMarca: " + p.m);
                            
                            if (mostrarStock) row.push(p.s <= 0 ? 'AGOTADO' : p.s.toString());
                            preciosFila.forEach(precio => row.push(precio));
                            
                            filas.push(row);
                            skusPdf.push(p.c);
                        });

                        doc.autoTable({
                            head: [columnas],
                            body: filas,
                            startY: startY,
                            rowPageBreak: 'avoid',
                            styles: { fontSize: 8, valign: 'middle' },
                            headStyles: { fillColor: [8, 18, 38], textColor: 255, halign: 'center' },
                            columnStyles: {
                                0: { cellWidth: 20, halign: 'center' },
                                1: { cellWidth: 25 },
                                2: { cellWidth: 'auto' }
                            },
                            bodyStyles: { minCellHeight: 20 },
                            didDrawCell: function(data) {
                                if (data.column.index === 0 && data.cell.section === 'body') {
                                    let sku = skusPdf[data.row.index];
                                    let imgStr = IMAGENES[sku];
                                    if (imgStr) {
                                        try { doc.addImage("data:image/png;base64," + imgStr, 'PNG', data.cell.x + 2, data.cell.y + 2, 16, 16); } catch(e){}
                                    } else {
                                        doc.setFontSize(6);
                                        doc.setTextColor(150);
                                        doc.text("Sin foto", data.cell.x + 3, data.cell.y + 11);
                                    }
                                }
                            }
                        });

                        doc.save("Cotizacion_Camping44_" + stateCat.replace(/[^a-zA-Z0-9]/g, "") + ".pdf");

                        btnPdf.innerHTML = originalText;
                        btnPdf.disabled = false;
                        
                    } catch (err) {
                        console.error(err);
                        alert("Hubo un error construyendo el PDF. Por favor intentá de nuevo.");
                        btnPdf.innerHTML = originalText;
                        btnPdf.disabled = false;
                    }
                }, 100);
            }
        </script></body></html>"""

        html += footer_html.replace('##LOGO_HTML##', logo_html)
        html = html.replace('##JSON_DATA##', json_str)
        html = html.replace('##JSON_IMAGES##', json_images_str)
        html = html.replace('##JSON_OFERTAS##', json_ofertas_str)

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        peso_final = os.path.getsize("index.html") / (1024 * 1024)
        print(f"¡Catálogo VIRTUAL con Ordenamiento optimizado con éxito! Peso: {peso_final:.2f} MB")

    except Exception as e:
        print(f"Error general: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
