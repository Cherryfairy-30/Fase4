
import json
import os
import datetime
import string
import html
import unicodedata
import streamlit as st

# Paleta de colores ===========================================================
COLOR_AZUL = "#367199"
COLOR_NARANJA = "#d0812e"
COLOR_OSCURO = "#113f58"
COLOR_CLARO = "#f6f7f7"
COLOR_GRIS = "#648485"

#Modificar=====================================================================
dominios_permitidos = ["gmail", "outlook", "hotmail", "nivela"]
terminaciones_permitidas = ["com", "org", "net", "gt"]
caracteres_especiales = [
    ".", ",", ":", ";", "?", "!", "@", "#", "_", "-", "$", "%", "&", "*",
    "=", "(", ")", "[", "]", "{", "}"
]

#Validacion de usario y contraseña ===============================================================================================================================
def validar_usuario(usuario):
    if usuario.count("@") != 1:
        return False

    partes_usuario = usuario.split("@")
    nombre = partes_usuario[0]
    dominio_y_terminacion = partes_usuario[1]

    if nombre == "":
        return False

    for caracter in nombre:
        if caracter.isupper():
            return False
        if caracter.isspace():
            return False

    partes_dominio = dominio_y_terminacion.split(".")
    if len(partes_dominio) != 2:
        return False

    dominio = partes_dominio[0]
    terminacion = partes_dominio[1]

    if dominio not in dominios_permitidos:
        return False

    if terminacion not in terminaciones_permitidas:
        return False

    return True

def validar_contrasena(contrasena):
    if len(contrasena) < 8:
        return False

    tiene_mayuscula = False
    tiene_minuscula = False
    tiene_numero = False
    tiene_especial = False

    for caracter in contrasena:
        if caracter.isupper():
            tiene_mayuscula = True
        if caracter.islower():
            tiene_minuscula = True
        if caracter.isdigit():
            tiene_numero = True
        if caracter in caracteres_especiales:
            tiene_especial = True

    if tiene_mayuscula and tiene_minuscula and tiene_numero and tiene_especial:
        return True

    return False

#Datos de Modulo de obras================================================================================================================================
caracteres_especiales_obras = [
    ".", ",", ":", ";", "?", "!", "@", "#", "_", "-", "$", "%", "&", "*",
    "=", "(", ")", "[", "]", "{", "}", "/"
]
zona_maxima = 25
anio_minimo = 2000
anio_maximo = 2100

campos_obra = [
    "titulo", "descripcion", "cliente_nombre", "cliente_apellido", "zona",
    "direccion", "colonia", "informacion", "fecha_inicio", "fecha_fin",
    "presupuesto", "gerente_nombre", "gerente_apellido"
]

etiquetas_obras = {
    "titulo": "Título de obra",
    "descripcion": "Descripción",
    "cliente_nombre": "Nombre del cliente",
    "cliente_apellido": "Apellido del cliente",
    "zona": "Zona",
    "direccion": "Dirección",
    "colonia": "Colonia",
    "informacion": "Información adicional",
    "fecha_inicio": "Fecha de inicio estimada",
    "fecha_fin": "Fecha de finalización estimada",
    "presupuesto": "Presupuesto inicial en quetzales",
    "gerente_nombre": "Nombre del gerente de obra",
    "gerente_apellido": "Apellido del gerente de obra"
}

opciones_edicion_obra = [
    ["titulo"],
    ["descripcion"],
    ["cliente_nombre", "cliente_apellido"],
    ["zona"],
    ["direccion"],
    ["colonia"],
    ["informacion"],
    ["fecha_inicio"],
    ["fecha_fin"],
    ["presupuesto"],
    ["gerente_nombre", "gerente_apellido"]
]

nombres_opciones_edicion_obra = [
    "Título de obra",
    "Descripción",
    "Cliente",
    "Zona",
    "Dirección",
    "Colonia",
    "Información adicional",
    "Fecha de inicio estimada",
    "Fecha de finalización estimada",
    "Presupuesto inicial",
    "Gerente de obra"
]

#Generador de códigos (estándar: PREFIJO-AÑO-NÚMERO) ============================================================================
# Obras:        OBR-Z10-2026-001   (zona - año de inicio - n.º de obra de esa zona en ese año)
# Materiales:   MAT-CEM-2026-001   (categoría - año de entrega - n.º de ese año)
# Herramientas: HER-MAR-2026-001   (3 letras del nombre - año de registro - n.º)
def generar_codigo(lista, prefijo, anio):
    inicio = prefijo + "-" + str(anio) + "-"
    mayor = 0
    for elemento in lista:
        codigo = elemento.get("codigo", "")
        resto = codigo[len(inicio):]
        if codigo.startswith(inicio) and solo_digitos(resto) and int(resto) > mayor:
            mayor = int(resto)

    return inicio + str(mayor + 1).zfill(3)

def letras_prefijo(texto):
    letras = ""
    for caracter in unicodedata.normalize("NFD", texto):
        if caracter.isalpha() and caracter.upper() in string.ascii_uppercase:
            letras = letras + caracter.upper()
    return (letras + "XXX")[:3]

def generar_codigo_obra(lista_obras, obra):
    prefijo = "OBR-Z" + str(int(obra["zona"])).zfill(2)
    anio = fecha_a_tupla(obra["fecha_inicio"])[0]
    return generar_codigo(lista_obras, prefijo, anio)

def generar_titulo_obra(codigo, zona):
    # Ejemplo: "Obra Zona 10 - 2026 - 001" (único porque sale del código)
    partes = codigo.split("-")
    return "Obra Zona " + str(int(zona)) + " - " + partes[2] + " - " + partes[3]

#Almacenamiento ============================================================================================
def cargar_obras():
    if not os.path.exists("obras.json"):
        return []

    if os.path.getsize("obras.json") == 0:
        return []

    archivo = open("obras.json", "r", encoding="utf-8")
    contenido = archivo.read()
    archivo.close()

    if contenido.strip() == "":
        return []

    lista_obras = json.loads(contenido)

    hubo_cambios = False
    for posicion in range(len(lista_obras)):
        if "codigo" not in lista_obras[posicion]:
            obra_con_codigo = {"codigo": generar_codigo_obra(lista_obras, lista_obras[posicion])}
            obra_con_codigo.update(lista_obras[posicion])
            lista_obras[posicion] = obra_con_codigo
            hubo_cambios = True

    if hubo_cambios:
        guardar_obras(lista_obras)

    return lista_obras

def guardar_obras(lista_obras):
    archivo = open("obras.json", "w", encoding="utf-8")
    json.dump(lista_obras, archivo, indent=4, ensure_ascii=False)
    archivo.close()

#Validaciones Generales===================================================================================================================
def solo_digitos(texto):
    if texto == "":
        return False

    for caracter in texto:
        if caracter not in "0123456789":
            return False

    return True

def texto_permitido(texto):
    for caracter in texto:
        if not caracter.isalpha() and not caracter.isdigit() and caracter != " " and caracter not in caracteres_especiales_obras:
            return False

    return True

def validar_titulo_obra(texto):
    if texto == "":
        return False

    if not texto[0].isalpha() or not texto[0].isupper():
        return False

    return texto_permitido(texto)

def validar_nombre_persona(texto):
    if texto == "":
        return False

    if not texto[0].isalpha() or not texto[0].isupper():
        return False

    for caracter in texto:
        if not caracter.isalpha() and caracter != " " and caracter != "-":
            return False

    return True

def validar_zona(texto):
    if not solo_digitos(texto):
        return False

    numero = int(texto)
    return numero >= 1 and numero <= zona_maxima

def validar_direccion(texto):
    if texto == "":
        return False

    return texto_permitido(texto)

def validar_colonia(texto):
    return validar_direccion(texto)

def validar_monto(texto):
    partes = texto.split(".")
    if len(partes) > 2:
        return False

    if not solo_digitos(partes[0]):
        return False

    if len(partes) == 2:
        if not solo_digitos(partes[1]) or len(partes[1]) > 2:
            return False

    return float(texto) > 0

def dias_del_mes(mes):
    if mes == 2:
        return 29

    if mes == 4 or mes == 6 or mes == 9 or mes == 11:
        return 30

    return 31

def fecha_a_tupla(fecha):
    partes = fecha.split("/")
    return (int(partes[2]), int(partes[1]), int(partes[0]))

def formatear_monto(presupuesto):
    return "Q " + format(float(presupuesto), ",.2f")

def titulo_repetido(lista_obras, titulo, titulo_actual):
    for obra in lista_obras:
        if obra["titulo"].lower() == titulo.lower() and titulo.lower() != titulo_actual.lower():
            return True

    return False

#Datos de Modulo de Materiales==============================================================================================================
categorias_materiales = [
    "Cemento y concreto", "Acero y hierro", "Madera", "Bloques y ladrillos",
    "Plomería", "Electricidad", "Pintura y acabados", "Otros"
]

prefijos_categorias = {
    "Cemento y concreto": "CEM",
    "Acero y hierro": "ACE",
    "Madera": "MAD",
    "Bloques y ladrillos": "BLO",
    "Plomería": "PLO",
    "Electricidad": "ELE",
    "Pintura y acabados": "PIN",
    "Otros": "OTR"
}

# El código ya no se escribe: se genera solo al registrar.
campos_material = ["nombre", "categoria", "cantidad", "costo", "fecha_entrega", "lugar_entrega"]

etiquetas_materiales = {
    "codigo": "Código",
    "nombre": "Nombre",
    "categoria": "Categoría",
    "cantidad": "Cantidad",
    "costo": "Costo por unidad en quetzales",
    "fecha_entrega": "Fecha de entrega",
    "lugar_entrega": "Lugar de entrega",
    "cantidad_transferir": "Cantidad a transferir",
    "lugar_nuevo": "Lugar de destino"
}

def generar_codigo_material(lista_materiales, categoria, fecha_entrega):
    prefijo = "MAT-" + prefijos_categorias.get(categoria, "OTR")
    return generar_codigo(lista_materiales, prefijo, fecha_a_tupla(fecha_entrega)[0])

def cargar_materiales():
    if not os.path.exists("materiales.json"):
        return []

    if os.path.getsize("materiales.json") == 0:
        return []

    archivo = open("materiales.json", "r", encoding="utf-8")
    contenido = archivo.read()
    archivo.close()

    if contenido.strip() == "":
        return []

    lista_materiales = json.loads(contenido)
    return lista_materiales

def guardar_materiales(lista_materiales):
    archivo = open("materiales.json", "w", encoding="utf-8")
    json.dump(lista_materiales, archivo, indent=4, ensure_ascii=False)
    archivo.close()

#Datos de Modulo de Herramientas========================================================================
caracteres_especiales_herramientas = [
    ".", ",", ":", ";", "?", "!", "@", "#", "_", "-", "$", "%", "&", "*",
    "=", "(", ")", "[", "]", "{", "}"
]

estados_herramientas = ["Bueno", "Regular", "Malo", "En mantenimiento"]

# El código ya no se escribe: se genera solo al registrar.
campos_herramientas = ["nombre", "marca", "ubicacion", "estado", "descripcion", "comentarios"]

etiquetas_herramientas = {
    "nombre": "Nombre",
    "codigo": "Código",
    "marca": "Marca",
    "ubicacion": "Ubicación",
    "estado": "Estado",
    "descripcion": "Descripción",
    "comentarios": "Comentarios"
}

def generar_codigo_herramienta(lista_herramientas, nombre):
    prefijo = "HER-" + letras_prefijo(nombre)
    return generar_codigo(lista_herramientas, prefijo, datetime.date.today().year)

def cargar_herramientas():
    if not os.path.exists("herramientas.json"):
        return []

    if os.path.getsize("herramientas.json") == 0:
        return []

    archivo = open("herramientas.json", "r", encoding="utf-8")
    contenido = archivo.read()
    archivo.close()

    if contenido.strip() == "":
        return []

    lista_herramientas = json.loads(contenido)
    return lista_herramientas

def guardar_herramientas(lista_herramientas):
    archivo = open("herramientas.json", "w", encoding="utf-8")
    json.dump(lista_herramientas, archivo, indent=4, ensure_ascii=False)
    archivo.close()

def validar_nombre(texto):
    if texto == "":
        return False

    if not texto[0].isalpha() or not texto[0].isupper():
        return False

    for caracter in texto:
        if not caracter.isalpha() and not caracter.isdigit() and caracter != " " and caracter not in caracteres_especiales_herramientas:
            return False

    return True

def validar_marca(texto):
    return validar_nombre(texto)

def validar_ubicacion(texto):
    # La ubicación se elige de una lista (bodega u obras registradas).
    return validar_direccion(texto)

#Lugares disponibles (lista desplegable) ===========================================================================
def opciones_lugares():
    lugares = ["Bodega central"]
    for obra in cargar_obras():
        if obra["titulo"] not in lugares:
            lugares.append(obra["titulo"])
    return lugares

#Validacion de cada dato===========================================================================================================================================
def validar_dato_obra(campo, dato, lista_obras, titulo_actual, obra_ref):
    if campo == "fecha_inicio" or campo == "fecha_fin":
        fecha = dato.strftime("%d/%m/%Y")

        if campo == "fecha_inicio":
            fecha_maxima = obra_ref.get("fecha_fin", "")
            if fecha_maxima != "" and fecha_a_tupla(fecha) > fecha_a_tupla(fecha_maxima):
                return "", "la fecha de inicio no puede ser posterior a la de finalización (" + fecha_maxima + ")."
        else:
            fecha_minima = obra_ref.get("fecha_inicio", "")
            if fecha_minima != "" and fecha_a_tupla(fecha) < fecha_a_tupla(fecha_minima):
                return "", "la fecha de finalización no puede ser anterior a la de inicio (" + fecha_minima + ")."

        return fecha, ""

    if dato is None:
        dato = ""
    dato = dato.strip()

    if campo == "titulo":
        if not validar_titulo_obra(dato):
            return "", "el título no puede estar vacío; debe empezar con una letra mayúscula y contener solo letras, números, espacios o los caracteres especiales permitidos."
        if titulo_repetido(lista_obras, dato, titulo_actual):
            return "", "ya existe una obra con ese título."
        return dato, ""

    if campo == "cliente_nombre" or campo == "cliente_apellido" or campo == "gerente_nombre" or campo == "gerente_apellido":
        if not validar_nombre_persona(dato):
            return "", "no puede estar vacío; debe empezar con una letra mayúscula y contener solo letras, espacios o guiones."
        return dato, ""

    if campo == "zona":
        if not validar_zona(dato):
            return "", "elija una zona de la lista (del 1 al " + str(zona_maxima) + ")."
        return str(int(dato)), ""

    if campo == "direccion" or campo == "colonia":
        if not validar_direccion(dato):
            return "", "no puede estar vacío y solo admite letras, números, espacios o los caracteres especiales permitidos."
        return dato, ""

    if campo == "presupuesto":
        if not validar_monto(dato):
            return "", "escriba un número mayor que cero, sin comas ni símbolos, con hasta 2 decimales. Ejemplo: 150000.50"
        return format(float(dato), ".2f"), ""

    if campo == "descripcion":
        if dato == "":
            return "", "la descripción no puede estar vacía."
        return dato, ""

    return dato, ""

def validar_dato_material(campo, dato, lista_materiales, material_ref):
    if campo == "fecha_entrega":
        return dato.strftime("%d/%m/%Y"), ""

    if campo == "categoria":
        return dato, ""

    if dato is None:
        dato = ""
    dato = dato.strip()

    if campo == "nombre":
        if not validar_nombre(dato):
            return "", "el nombre no puede estar vacío; debe empezar con una letra mayúscula y contener solo letras, números, espacios o los caracteres especiales permitidos."
        return dato, ""

    if campo == "cantidad":
        if not solo_digitos(dato) or int(dato) < 1:
            return "", "la cantidad debe ser un número entero mayor que cero."
        return str(int(dato)), ""

    if campo == "cantidad_transferir":
        if not solo_digitos(dato) or int(dato) < 1 or int(dato) > int(material_ref["cantidad"]):
            return "", "escriba un número entero del 1 al " + material_ref["cantidad"] + "."
        return str(int(dato)), ""

    if campo == "costo":
        if not validar_monto(dato):
            return "", "escriba un número mayor que cero, sin comas ni símbolos, con hasta 2 decimales. Ejemplo: 25.50"
        return format(float(dato), ".2f"), ""

    if not validar_direccion(dato):
        return "", "elija un lugar de la lista."
    if campo == "lugar_nuevo" and dato.lower() == material_ref["lugar_entrega"].lower():
        return "", "el lugar de destino debe ser distinto al lugar actual."
    return dato, ""

def validar_dato_herramienta(campo, dato):
    if campo == "estado":
        return dato, ""

    if dato is None:
        dato = ""
    dato = dato.strip()

    if campo == "nombre" or campo == "marca" or campo == "ubicacion":
        if campo == "nombre":
            dato_valido = validar_nombre(dato)
        elif campo == "marca":
            dato_valido = validar_marca(dato)
        else:
            dato_valido = validar_ubicacion(dato)

        if not dato_valido:
            if campo == "ubicacion":
                return "", "elija una ubicación de la lista."
            return "", "no puede estar vacío; debe empezar con una letra mayúscula y contener solo letras, números, espacios o los caracteres especiales permitidos."
        return dato, ""

    return dato, ""

#Estilos ======================================================================================================================================================================================
ESTILOS = """
<style>
:root { --azul:#367199; --naranja:#d0812e; --oscuro:#113f58; --claro:#f6f7f7; --gris:#648485; }
.stApp { background: var(--claro); }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 880px; padding-top: 1.2rem; padding-bottom: 3rem; }

/* Banner superior */
.banner { background: linear-gradient(120deg, var(--oscuro) 0%, var(--azul) 100%); border-bottom: 5px solid var(--naranja);
  border-radius: 16px; padding: 1.4rem 1.6rem; margin-bottom: 1.4rem; display: flex; justify-content: space-between;
  align-items: center; gap: 1rem; flex-wrap: wrap; box-shadow: 0 6px 18px rgba(17,63,88,.25); }
.banner-titulo { color: #fff; font-size: 1.6rem; font-weight: 800; letter-spacing: .3px; }
.banner-sub { color: var(--claro); opacity: .85; font-size: .95rem; margin-top: .15rem; }
.usuario { background: rgba(246,247,247,.15); color: #fff; border: 1px solid rgba(246,247,247,.45);
  border-radius: 999px; padding: .35rem .9rem; font-size: .85rem; }

/* Títulos */
[data-testid="stHeading"] h2, [data-testid="stHeading"] h1 { color: var(--oscuro) !important; font-weight: 800;
  border-bottom: 4px solid var(--naranja); padding-bottom: .35rem; display: inline-block; }
.stApp, .stMarkdown, .stMarkdown p, .stMarkdown li { color: #1d3a47; }
.stMarkdown strong { color: var(--oscuro); }
.stMarkdown code { color: var(--oscuro); background: rgba(100,132,133,.15); border-radius: 6px; }
label p { color: var(--oscuro) !important; font-weight: 600; }

/* Botones */
.stButton > button, .stFormSubmitButton > button { width: 100%; background: var(--azul); color: #fff; border: none;
  border-radius: 10px; padding: .65rem 1rem; font-weight: 700; box-shadow: 0 2px 6px rgba(17,63,88,.2);
  transition: all .15s ease; }
.stButton > button *, .stFormSubmitButton > button * { color: inherit !important; }
.stButton > button:hover { background: var(--oscuro); color: #fff; transform: translateY(-2px); box-shadow: 0 6px 14px rgba(17,63,88,.3); }
.stFormSubmitButton > button { background: var(--naranja); }
.stFormSubmitButton > button:hover { background: var(--naranja); color: #fff; filter: brightness(.9); transform: translateY(-2px); }
.stButton > button:focus:not(:active) { color: #fff; border: none; box-shadow: 0 0 0 3px rgba(208,129,46,.5); }

/* Navegación */
.st-key-nav_atras button, .st-key-nav_menu button, .st-key-login_volver button, .st-key-fin_volver button {
  background: #fff; color: var(--azul); border: 2px solid var(--azul); box-shadow: none; }
.st-key-nav_atras button:hover, .st-key-nav_menu button:hover, .st-key-login_volver button:hover, .st-key-fin_volver button:hover {
  background: var(--azul); color: #fff; }
.st-key-nav_fin button, .st-key-inicio_fin button { background: var(--naranja); }
.st-key-nav_fin button:hover, .st-key-inicio_fin button:hover { background: var(--naranja); filter: brightness(.9); }

/* Menú principal */
[class*="st-key-menu_"] button { padding: 1.6rem 1rem; font-size: 1.25rem; border-left: 8px solid var(--naranja); border-radius: 14px; }

/* Listas de elementos (obras, materiales, herramientas) */
[class*="st-key-lista_"] button { background: #fff; color: var(--oscuro); border: 1px solid var(--gris);
  border-left: 6px solid var(--azul); justify-content: flex-start; text-align: left; box-shadow: none; font-weight: 600; }
[class*="st-key-lista_"] button:hover { background: var(--azul); color: #fff; border-left-color: var(--naranja); }

/* Formularios y campos */
[data-testid="stForm"] { background: #fff; border: 1px solid #dde4e4; border-top: 6px solid var(--azul);
  border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 14px rgba(17,63,88,.08); }
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"] > div, div[data-baseweb="textarea"] {
  border-radius: 10px !important; border-color: var(--gris) !important; background: #fff !important; }
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within { border-color: var(--naranja) !important;
  box-shadow: 0 0 0 2px rgba(208,129,46,.3); }
ul[data-baseweb="menu"] li:hover { background: rgba(54,113,153,.12); }

/* Desplegables, alertas y divisores */
[data-testid="stExpander"] { background: #fff; border: 1px solid var(--gris); border-radius: 14px; }
[data-testid="stExpander"] summary { color: var(--oscuro); font-weight: 700; }
[data-testid="stAlert"] { border-radius: 12px; }
hr { border-color: var(--gris) !important; opacity: .4; }

/* Detalles (tarjetas) */
.tarjeta { background: #fff; border-left: 8px solid var(--azul); border-radius: 14px; padding: 1.2rem 1.4rem;
  box-shadow: 0 4px 14px rgba(17,63,88,.08); margin-bottom: 1rem; }
.fila { display: flex; justify-content: space-between; gap: 1rem; padding: .5rem 0; border-bottom: 1px solid #e6ecec; }
.fila:last-child { border-bottom: none; }
.fila-etiqueta { color: var(--gris); font-weight: 600; }
.fila-valor { color: var(--oscuro); font-weight: 700; text-align: right; }
.codigo { display: inline-block; background: var(--naranja); color: #fff; border-radius: 8px; padding: .15rem .6rem; font-weight: 800; }
</style>
"""

def aplicar_estilos():
    st.markdown(ESTILOS, unsafe_allow_html=True)

def encabezado():
    usuario = ""
    if st.session_state.usuario != "":
        usuario = '<span class="usuario">👤 ' + html.escape(st.session_state.usuario) + '</span>'
    st.markdown(
        '<div class="banner"><div><div class="banner-titulo">🏗️ Obras, Materiales y Herramientas</div>'
        '<div class="banner-sub">Sistema de gestión de construcción</div></div>' + usuario + '</div>',
        unsafe_allow_html=True
    )

#Streamlit ======================================================================================================================================================================================
def seguro(texto):
    resultado = ""
    for caracter in str(texto):
        if caracter in string.punctuation:
            resultado = resultado + "\\" + caracter
        else:
            resultado = resultado + caracter
    return resultado

def linea(etiqueta, valor):
    st.write("**" + etiqueta + ":** " + seguro(valor))

def tarjeta_detalle(filas):
    # filas: lista de [etiqueta, valor]; se muestran como tarjeta con colores
    cuerpo = ""
    for etiqueta, valor in filas:
        cuerpo = cuerpo + '<div class="fila"><span class="fila-etiqueta">' + html.escape(etiqueta) + '</span><span class="fila-valor">' + html.escape(str(valor)) + '</span></div>'
    st.markdown('<div class="tarjeta">' + cuerpo + '</div>', unsafe_allow_html=True)

def mostrar_codigo(codigo):
    st.markdown('Código asignado: <span class="codigo">' + html.escape(codigo) + '</span>', unsafe_allow_html=True)

def mostrar_errores(errores):
    for error in errores:
        st.error(error)

def buscar_por_codigo(lista, codigo):
    for elemento in lista:
        if elemento["codigo"] == codigo:
            return elemento
    return None

def mostrar_lista(lista, textos, pantalla_destino):
    for posicion in range(len(lista)):
        codigo = lista[posicion]["codigo"]
        st.button(
            seguro(textos[posicion]),
            key="lista_" + pantalla_destino + "_" + codigo,
            on_click=ir_a,
            args=(pantalla_destino, codigo)
        )

def fecha_minima_permitida():
    return datetime.date(anio_minimo, 1, 1)

def fecha_maxima_permitida():
    return datetime.date(anio_maximo, 12, 31)

def crear_entrada_fecha(etiqueta, clave, texto_inicial):
    if texto_inicial == "":
        fecha_inicial = datetime.date.today()
    else:
        fecha_inicial = datetime.datetime.strptime(texto_inicial, "%d/%m/%Y").date()

    return st.date_input(
        etiqueta,
        value=fecha_inicial,
        min_value=fecha_minima_permitida(),
        max_value=fecha_maxima_permitida(),
        format="DD/MM/YYYY",
        key=clave
    )

def crear_lista_desplegable(etiqueta, opciones, clave, valor_inicial, obligar_eleccion=True):
    # Menú desplegable. Si ya hay un valor (edición), queda seleccionado;
    # si no, y obligar_eleccion es True, empieza vacío para que la persona elija.
    opciones = list(opciones)
    if valor_inicial != "" and valor_inicial not in opciones:
        opciones.append(valor_inicial)

    if valor_inicial != "":
        posicion = opciones.index(valor_inicial)
    elif obligar_eleccion:
        posicion = None
    else:
        posicion = 0

    return st.selectbox(etiqueta, opciones, index=posicion, key=clave, placeholder="Elija una opción")

#Navegacion========================================================================================================================================================
def iniciar_estado():
    if "pantalla" not in st.session_state:
        st.session_state.pantalla = "inicio"
        st.session_state.pila = []
        st.session_state.usuario = ""
        st.session_state.intentos_fallidos = 0
        st.session_state.bloqueado = False
        st.session_state.seleccion = ""
        st.session_state.aviso = None

def ir_a(pantalla, seleccion=""):
    st.session_state.pila.append(st.session_state.pantalla)
    st.session_state.pantalla = pantalla
    st.session_state.seleccion = seleccion

def regresar_uno():
    if len(st.session_state.pila) > 0:
        st.session_state.pantalla = st.session_state.pila.pop()
    else:
        st.session_state.pantalla = "menu"
    st.session_state.seleccion = ""

def regresar_al_menu():
    st.session_state.pila = []
    st.session_state.pantalla = "menu"
    st.session_state.seleccion = ""

def finalizar_sesion():
    st.session_state.pila = []
    st.session_state.pantalla = "fin"
    st.session_state.usuario = ""
    st.session_state.seleccion = ""

def volver_al_inicio():
    st.session_state.pila = []
    st.session_state.pantalla = "inicio"
    st.session_state.intentos_fallidos = 0
    st.session_state.seleccion = ""

def avisar(tipo, texto):
    st.session_state.aviso = [tipo, texto]

def mostrar_aviso():
    aviso = st.session_state.aviso
    if aviso is not None:
        if aviso[0] == "exito":
            st.success(aviso[1])
        elif aviso[0] == "error":
            st.error(aviso[1])
        else:
            st.info(aviso[1])
        st.session_state.aviso = None

def barra_navegacion(mostrar_atras=True, mostrar_menu=True):
    st.divider()
    columnas = st.columns(3)
    if mostrar_atras:
        columnas[0].button("⬅ Regresar uno", key="nav_atras", on_click=regresar_uno)
    if mostrar_menu:
        columnas[1].button("🏠 Menú principal", key="nav_menu", on_click=regresar_al_menu)
    columnas[2].button("Finalizar sesión", key="nav_fin", on_click=finalizar_sesion)

#Pantallas: Inicio y sesion=============================================================================================================================================================================
def pantalla_inicio():
    st.header("Inicio")
    st.write("Bienvenido. Inicie sesión para administrar obras, materiales y herramientas.")
    st.button("Iniciar sesión", key="inicio_login", on_click=ir_a, args=("login",))
    st.button("Finalizar sesión", key="inicio_fin", on_click=finalizar_sesion)

def mostrar_requisitos():
    terminaciones = ""
    for terminacion in terminaciones_permitidas:
        if terminaciones != "":
            terminaciones = terminaciones + ", "
        terminaciones = terminaciones + "." + terminacion

    lineas = []
    lineas.append("**Requisitos para el nombre de usuario:**")
    lineas.append("- Debe tener este orden exacto: nombre, símbolo @, dominio y terminación.")
    lineas.append("- El nombre debe estar todo en minúscula y sin espacios.")
    lineas.append("- Dominios permitidos: " + ", ".join(dominios_permitidos) + ".")
    lineas.append("- Terminaciones permitidas: " + terminaciones)
    lineas.append("- Ejemplo válido: `juan@gmail.com`")
    lineas.append("")
    lineas.append("**Requisitos para la contraseña (sin importar el orden):**")
    lineas.append("- Mínimo 8 caracteres.")
    lineas.append("- Al menos una letra mayúscula.")
    lineas.append("- Al menos una letra minúscula.")
    lineas.append("- Al menos un número.")
    lineas.append("- Al menos un carácter especial de esta lista: `" + " ".join(caracteres_especiales) + "`")
    with st.expander("Requisitos de usuario y contraseña", expanded=True):
        st.write("\n".join(lineas))

def pantalla_login():
    st.header("Iniciar sesión")
    mostrar_requisitos()

    with st.form("form_login"):
        usuario = st.text_input("Nombre de usuario")
        contrasena = st.text_input("Contraseña", type="password")
        enviado = st.form_submit_button("Entrar")

    if enviado:
        usuario_valido = validar_usuario(usuario)
        contrasena_valida = validar_contrasena(contrasena)

        if usuario_valido and contrasena_valida:
            st.session_state.usuario = usuario
            regresar_al_menu()
            avisar("exito", "Bienvenido " + seguro(usuario))
            st.rerun()
        else:
            st.session_state.intentos_fallidos = st.session_state.intentos_fallidos + 1

            if st.session_state.intentos_fallidos == 3:
                st.session_state.bloqueado = True
                finalizar_sesion()
                st.rerun()
            else:
                st.error("Error, inténtelo de nuevo")

    st.button("Volver al inicio", key="login_volver", on_click=regresar_uno)

def pantalla_fin():
    if st.session_state.bloqueado:
        st.error("Límite de intentos alcanzado. Recargue la página para volver a intentarlo.")
    else:
        st.info("Sesión finalizada.")
        st.button("Volver al inicio", key="fin_volver", on_click=volver_al_inicio)

def pantalla_menu():
    st.header("Seleccione una opción")
    st.button("🏗️  Obras", key="menu_obras", on_click=ir_a, args=("obras",))
    st.button("🧱  Materiales", key="menu_materiales", on_click=ir_a, args=("materiales",))
    st.button("🔧  Herramientas", key="menu_herramientas", on_click=ir_a, args=("herramientas",))
    barra_navegacion(mostrar_atras=False, mostrar_menu=False)

#Pantalla obras =============================================================================================================
def pantalla_obras():
    st.header("Módulo de Obras")
    st.button("Registrar obra", key="obras_registrar", on_click=ir_a, args=("obras_registrar",))
    st.button("Buscar obra", key="obras_buscar", on_click=ir_a, args=("obras_buscar",))
    st.button("Actualizar obra", key="obras_actualizar", on_click=ir_a, args=("obras_actualizar",))
    barra_navegacion(mostrar_menu=False)

def mostrar_reglas_obra():
    lineas = []
    lineas.append("- **Código de obra:** se genera automáticamente con el formato `OBR-Z10-2026-001` (zona, año de inicio y número de obra).")
    lineas.append("- **Título de obra:** debe empezar con una letra mayúscula, no puede repetirse y admite letras, números, espacios y estos caracteres especiales: `" + " ".join(caracteres_especiales_obras) + "`. También puede generarse automáticamente.")
    lineas.append("- **Cliente y Gerente de obra:** nombre y apellido deben empezar con una letra mayúscula y contener solo letras, espacios o guiones.")
    lineas.append("- **Zona:** se elige de la lista (1 al " + str(zona_maxima) + ").")
    lineas.append("- **Fechas:** se eligen en el calendario. La finalización no puede ser anterior al inicio.")
    lineas.append("- **Presupuesto inicial:** en quetzales, mayor que cero, sin comas. Ejemplo: `150000.50`")
    lineas.append("- **Información adicional:** es opcional.")
    with st.expander("Requisitos de los datos", expanded=True):
        st.write("\n".join(lineas))

def crear_entrada_obra(campo, clave, valor_inicial):
    etiqueta = etiquetas_obras[campo]

    if campo == "fecha_inicio" or campo == "fecha_fin":
        return crear_entrada_fecha(etiqueta, clave, valor_inicial)

    if campo == "zona":
        zonas = []
        for numero in range(1, zona_maxima + 1):
            zonas.append(str(numero))
        posicion = None
        if valor_inicial in zonas:
            posicion = zonas.index(valor_inicial)
        return st.selectbox(etiqueta, zonas, index=posicion, format_func=lambda z: "Zona " + z, key=clave, placeholder="Elija una zona")

    if campo == "informacion":
        etiqueta = etiqueta + " (opcional)"

    return st.text_input(etiqueta, value=valor_inicial, key=clave)

def pantalla_obras_registrar():
    st.header("Registrar obra")
    mostrar_reglas_obra()
    lista_obras = cargar_obras()

    with st.form("form_obra_registrar"):
        entradas = {}
        for campo in campos_obra:
            entradas[campo] = crear_entrada_obra(campo, "registrar_obra_" + campo, "")
            if campo == "titulo":
                titulo_auto = st.checkbox("Generar el título automáticamente (si dejo el campo vacío)", value=True, key="registrar_obra_titulo_auto")
        enviado = st.form_submit_button("Registrar obra")

    if enviado:
        obra_nueva = {}
        errores = []
        generar_titulo = titulo_auto and entradas["titulo"].strip() == ""

        for campo in campos_obra:
            if campo == "titulo" and generar_titulo:
                continue
            dato, error = validar_dato_obra(campo, entradas[campo], lista_obras, "", obra_nueva)
            if error != "":
                errores.append(etiquetas_obras[campo] + ": " + error)
            else:
                obra_nueva[campo] = dato

        if len(errores) > 0:
            mostrar_errores(errores)
        else:
            codigo = generar_codigo_obra(lista_obras, obra_nueva)
            if generar_titulo:
                obra_nueva["titulo"] = generar_titulo_obra(codigo, obra_nueva["zona"])

            obra_final = {"codigo": codigo}
            for campo in campos_obra:
                obra_final[campo] = obra_nueva[campo]

            lista_obras.append(obra_final)
            guardar_obras(lista_obras)
            avisar("exito", "Obra registrada correctamente. Código de la obra: " + codigo + ". Guarde este código: lo necesitará para buscar la obra.")
            regresar_uno()
            st.rerun()

    barra_navegacion(mostrar_menu=False)

def mostrar_detalle_obra(obra):
    if obra["informacion"] == "":
        informacion = "Sin información adicional"
    else:
        informacion = obra["informacion"]

    mostrar_codigo(obra["codigo"])
    tarjeta_detalle([
        ["Título de obra", obra["titulo"]],
        ["Descripción", obra["descripcion"]],
        ["Cliente", obra["cliente_nombre"] + " " + obra["cliente_apellido"]],
        ["Zona", obra["zona"]],
        ["Dirección", obra["direccion"]],
        ["Colonia", obra["colonia"]],
        ["Información adicional", informacion],
        ["Fecha de inicio estimada", obra["fecha_inicio"]],
        ["Fecha de finalización estimada", obra["fecha_fin"]],
        ["Presupuesto inicial", formatear_monto(obra["presupuesto"])],
        ["Gerente de obra", obra["gerente_nombre"] + " " + obra["gerente_apellido"]]
    ])

def pantalla_obras_buscar():
    st.header("Buscar obra")
    lista_obras = cargar_obras()

    if len(lista_obras) == 0:
        st.info("No hay obras registradas")
    else:
        codigos = []
        nombres = {}
        for obra in lista_obras:
            codigos.append(obra["codigo"])
            nombres[obra["codigo"]] = obra["codigo"] + " - " + obra["titulo"]

        with st.form("form_obra_buscar"):
            codigo = st.selectbox(
                "Código de obra (escriba para filtrar)",
                codigos,
                index=None,
                format_func=lambda c: nombres[c],
                placeholder="Elija o escriba un código"
            )
            enviado = st.form_submit_button("Buscar")

        if enviado:
            if codigo is None:
                st.error("Elija una obra de la lista.")
            else:
                ir_a("obras_detalle", codigo)
                st.rerun()

    barra_navegacion()

def pantalla_obras_detalle():
    st.header("Detalle de la obra")
    obra = buscar_por_codigo(cargar_obras(), st.session_state.seleccion)

    if obra is None:
        st.error("No se encontró la obra.")
    else:
        mostrar_detalle_obra(obra)

    barra_navegacion()

def pantalla_obras_actualizar():
    st.header("Actualizar obra")
    lista_obras = cargar_obras()

    if len(lista_obras) == 0:
        st.info("No hay obras registradas")
    else:
        st.write("Elija la obra que desea modificar:")
        textos = []
        for obra in lista_obras:
            textos.append(obra["codigo"] + " - " + obra["titulo"] + " (" + obra["cliente_nombre"] + " " + obra["cliente_apellido"] + ")")
        mostrar_lista(lista_obras, textos, "obras_editar")

    barra_navegacion()

def valor_actual_obra(obra, campos):
    if campos[0] == "presupuesto":
        return formatear_monto(obra["presupuesto"])

    if campos[0] == "informacion" and obra["informacion"] == "":
        return "Sin información adicional"

    texto = obra[campos[0]]
    if len(campos) == 2:
        texto = texto + " " + obra[campos[1]]

    return texto

def pantalla_obras_editar():
    st.header("Actualizar obra")
    lista_obras = cargar_obras()
    obra = buscar_por_codigo(lista_obras, st.session_state.seleccion)

    if obra is None:
        st.error("No se encontró la obra.")
        barra_navegacion()
        return

    codigo = obra["codigo"]
    linea("Obra", codigo + " - " + obra["titulo"])

    nombre_elegido = st.selectbox(
        "Indique el dato que desea modificar",
        nombres_opciones_edicion_obra,
        key="opcion_obra_" + codigo
    )
    campos = opciones_edicion_obra[nombres_opciones_edicion_obra.index(nombre_elegido)]

    linea("Dato actual", valor_actual_obra(obra, campos))

    with st.form("form_obra_editar_" + codigo + "_" + campos[0]):
        entradas = {}
        for campo in campos:
            entradas[campo] = crear_entrada_obra(campo, "editar_obra_" + codigo + "_" + campo, obra[campo])
        enviado = st.form_submit_button("Guardar cambio")

    if enviado:
        datos_nuevos = {}
        errores = []

        for campo in campos:
            dato, error = validar_dato_obra(campo, entradas[campo], lista_obras, obra["titulo"], obra)
            if error != "":
                errores.append(etiquetas_obras[campo] + ": " + error)
            else:
                datos_nuevos[campo] = dato

        if len(errores) > 0:
            mostrar_errores(errores)
        else:
            for campo in datos_nuevos:
                obra[campo] = datos_nuevos[campo]

            guardar_obras(lista_obras)
            avisar("exito", "Dato actualizado correctamente. El código de la obra no cambia.")
            st.rerun()

    barra_navegacion()

#Pantalla Materiales =====================================================================================================================================================
def pantalla_materiales():
    st.header("Módulo de Materiales")
    st.button("Registrar material", key="mat_registrar", on_click=ir_a, args=("mat_registrar",))
    st.button("Transferencia de material", key="mat_transferir", on_click=ir_a, args=("mat_transferir",))
    st.button("Buscar materiales", key="mat_buscar", on_click=ir_a, args=("mat_buscar",))
    barra_navegacion(mostrar_menu=False)

def pantalla_mat_registrar():
    st.header("Registrar material")

    lineas = []
    lineas.append("- **Código:** se genera automáticamente con el formato `MAT-CEM-2026-001` (categoría, año de entrega y número).")
    lineas.append("- **Nombre:** debe empezar con una letra mayúscula y no quedar vacío. Admite letras, números, espacios y estos caracteres especiales: `" + " ".join(caracteres_especiales_herramientas) + "`")
    lineas.append("- **Categoría y Lugar de entrega:** se eligen de la lista (el lugar puede ser la bodega o una obra registrada).")
    lineas.append("- **Cantidad:** número entero mayor que cero.")
    lineas.append("- **Costo:** por unidad, en quetzales, mayor que cero y sin comas. Ejemplo: `25.50`")
    with st.expander("Requisitos de los datos", expanded=True):
        st.write("\n".join(lineas))

    lista_materiales = cargar_materiales()

    with st.form("form_material_registrar"):
        entradas = {}
        entradas["nombre"] = st.text_input(etiquetas_materiales["nombre"], key="reg_mat_nombre")
        entradas["categoria"] = st.selectbox(etiquetas_materiales["categoria"], categorias_materiales, key="reg_mat_categoria")
        entradas["cantidad"] = st.text_input(etiquetas_materiales["cantidad"], key="reg_mat_cantidad")
        entradas["costo"] = st.text_input(etiquetas_materiales["costo"], key="reg_mat_costo")
        entradas["fecha_entrega"] = crear_entrada_fecha(etiquetas_materiales["fecha_entrega"], "reg_mat_fecha", "")
        entradas["lugar_entrega"] = crear_lista_desplegable(etiquetas_materiales["lugar_entrega"], opciones_lugares(), "reg_mat_lugar", "")
        enviado = st.form_submit_button("Registrar material")

    if enviado:
        datos = {}
        errores = []

        for campo in campos_material:
            dato, error = validar_dato_material(campo, entradas[campo], lista_materiales, {})
            if error != "":
                errores.append(etiquetas_materiales[campo] + ": " + error)
            else:
                datos[campo] = dato

        if len(errores) > 0:
            mostrar_errores(errores)
        else:
            codigo = generar_codigo_material(lista_materiales, datos["categoria"], datos["fecha_entrega"])
            material_nuevo = {"codigo": codigo}
            for campo in campos_material:
                material_nuevo[campo] = datos[campo]

            lista_materiales.append(material_nuevo)
            guardar_materiales(lista_materiales)
            avisar("exito", "Material registrado correctamente. Código asignado: " + codigo)
            regresar_uno()
            st.rerun()

    barra_navegacion(mostrar_menu=False)

def pantalla_mat_lista(titulo, pantalla_destino):
    st.header(titulo)
    lista_materiales = cargar_materiales()

    if len(lista_materiales) == 0:
        st.info("No hay materiales registrados")
    else:
        textos = []
        for material in lista_materiales:
            textos.append(material["nombre"] + " (" + material["codigo"] + ")")
        mostrar_lista(lista_materiales, textos, pantalla_destino)

    barra_navegacion()

def pantalla_mat_transferir():
    pantalla_mat_lista("Transferencia de material", "mat_transferir_form")

def pantalla_mat_buscar():
    pantalla_mat_lista("Buscar materiales", "mat_detalle")

def pantalla_mat_detalle():
    st.header("Detalle del material")
    material = buscar_por_codigo(cargar_materiales(), st.session_state.seleccion)

    if material is None:
        st.error("No se encontró el material.")
    else:
        mostrar_codigo(material["codigo"])
        tarjeta_detalle([
            ["Nombre", material["nombre"]],
            ["Categoría", material["categoria"]],
            ["Cantidad", material["cantidad"]],
            ["Costo por unidad", formatear_monto(material["costo"])],
            ["Fecha de entrega", material["fecha_entrega"]],
            ["Lugar de entrega", material["lugar_entrega"]]
        ])

    barra_navegacion()

def pantalla_mat_transferir_form():
    st.header("Transferencia de material")
    lista_materiales = cargar_materiales()
    material = buscar_por_codigo(lista_materiales, st.session_state.seleccion)

    if material is None:
        st.error("No se encontró el material.")
        barra_navegacion()
        return

    tarjeta_detalle([
        ["Material", material["nombre"] + " (" + material["codigo"] + ")"],
        ["Cantidad disponible", material["cantidad"]],
        ["Lugar actual", material["lugar_entrega"]]
    ])

    clave = material["codigo"]
    cantidad = st.text_input(etiquetas_materiales["cantidad_transferir"], key="transf_cantidad_" + clave)

    destinos = []
    for lugar in opciones_lugares():
        if lugar.lower() != material["lugar_entrega"].lower():
            destinos.append(lugar)
    lugar_nuevo = st.selectbox(etiquetas_materiales["lugar_nuevo"], destinos, index=None, key="transf_lugar_" + clave, placeholder="Elija el destino")

    cantidad_limpia = cantidad.strip()
    if solo_digitos(cantidad_limpia) and int(cantidad_limpia) >= 1 and int(cantidad_limpia) < int(material["cantidad"]):
        st.info("Se transfiere solo una parte: el material transferido se registrará con un código nuevo, generado automáticamente.")

    if st.button("Transferir", key="transf_boton_" + clave):
        errores = []
        datos = {}

        dato, error = validar_dato_material("cantidad_transferir", cantidad, lista_materiales, material)
        if error != "":
            errores.append(etiquetas_materiales["cantidad_transferir"] + ": " + error)
        else:
            datos["cantidad_transferir"] = dato

        dato, error = validar_dato_material("lugar_nuevo", lugar_nuevo, lista_materiales, material)
        if error != "":
            errores.append(etiquetas_materiales["lugar_nuevo"] + ": " + error)
        else:
            datos["lugar_nuevo"] = dato

        if len(errores) > 0:
            mostrar_errores(errores)
        else:
            mensaje = "Transferencia realizada correctamente"
            if datos["cantidad_transferir"] == material["cantidad"]:
                material["lugar_entrega"] = datos["lugar_nuevo"]
            else:
                codigo_nuevo = generar_codigo_material(lista_materiales, material["categoria"], material["fecha_entrega"])
                material_nuevo = {
                    "codigo": codigo_nuevo,
                    "nombre": material["nombre"],
                    "categoria": material["categoria"],
                    "cantidad": datos["cantidad_transferir"],
                    "costo": material["costo"],
                    "fecha_entrega": material["fecha_entrega"],
                    "lugar_entrega": datos["lugar_nuevo"]
                }
                material["cantidad"] = str(int(material["cantidad"]) - int(datos["cantidad_transferir"]))
                lista_materiales.append(material_nuevo)
                mensaje = mensaje + ". Código del material transferido: " + codigo_nuevo

            guardar_materiales(lista_materiales)
            avisar("exito", mensaje)
            regresar_uno()
            st.rerun()

    barra_navegacion()

#Pantalla Herramientas===================================================================================================================================================================
def pantalla_herramientas():
    st.header("Módulo de Herramientas")
    st.button("Registrar herramientas", key="herr_registrar", on_click=ir_a, args=("herr_registrar",))
    st.button("Actualizar herramientas", key="herr_actualizar", on_click=ir_a, args=("herr_actualizar",))
    st.button("Ver herramientas", key="herr_ver", on_click=ir_a, args=("herr_ver",))
    barra_navegacion(mostrar_menu=False)

def crear_entrada_herramienta(campo, clave, valor_inicial):
    # Crea el campo adecuado para cada dato y devuelve lo que eligió o escribió el usuario.
    etiqueta = etiquetas_herramientas[campo]

    if campo == "estado":
        return crear_lista_desplegable(etiqueta, estados_herramientas, clave, valor_inicial, obligar_eleccion=False)

    if campo == "ubicacion":
        return crear_lista_desplegable(etiqueta, opciones_lugares(), clave, valor_inicial)

    if campo == "descripcion" or campo == "comentarios":
        etiqueta = etiqueta + " (opcional)"

    return st.text_input(etiqueta, value=valor_inicial, key=clave)

def pantalla_herr_registrar():
    st.header("Registrar herramientas")

    lineas = []
    lineas.append("- **Código:** se genera automáticamente con el formato `HER-MAR-2026-001` (3 letras del nombre, año de registro y número).")
    lineas.append("- **Nombre y Marca:** deben empezar con una letra mayúscula y no quedar vacíos. Admiten letras, números, espacios y estos caracteres especiales: `" + " ".join(caracteres_especiales_herramientas) + "`")
    lineas.append("- **Ubicación y Estado:** se eligen de la lista (la ubicación puede ser la bodega o una obra registrada).")
    lineas.append("- **Descripción y Comentarios:** son opcionales.")
    with st.expander("Requisitos de los datos", expanded=True):
        st.write("\n".join(lineas))

    lista_herramientas = cargar_herramientas()

    with st.form("form_herramienta_registrar"):
        entradas = {}
        for campo in campos_herramientas:
            entradas[campo] = crear_entrada_herramienta(campo, "reg_herr_" + campo, "")
        enviado = st.form_submit_button("Registrar herramienta")

    if enviado:
        datos = {}
        errores = []

        for campo in campos_herramientas:
            dato, error = validar_dato_herramienta(campo, entradas[campo])
            if error != "":
                errores.append(etiquetas_herramientas[campo] + ": " + error)
            else:
                datos[campo] = dato

        if len(errores) > 0:
            mostrar_errores(errores)
        else:
            codigo = generar_codigo_herramienta(lista_herramientas, datos["nombre"])
            herramienta_nueva = {"nombre": datos["nombre"], "codigo": codigo}
            for campo in campos_herramientas:
                if campo != "nombre":
                    herramienta_nueva[campo] = datos[campo]

            lista_herramientas.append(herramienta_nueva)
            guardar_herramientas(lista_herramientas)
            avisar("exito", "Herramienta registrada correctamente. Código asignado: " + codigo)
            regresar_uno()
            st.rerun()

    barra_navegacion(mostrar_menu=False)

def pantalla_herr_lista(titulo, pantalla_destino):
    # Lista de herramientas; se usa para actualizar y para ver.
    st.header(titulo)
    lista_herramientas = cargar_herramientas()

    if len(lista_herramientas) == 0:
        st.info("No hay herramientas registradas")
    else:
        textos = []
        for herramienta in lista_herramientas:
            textos.append(herramienta["nombre"] + " (" + herramienta["codigo"] + ")")
        mostrar_lista(lista_herramientas, textos, pantalla_destino)

    barra_navegacion()

def pantalla_herr_actualizar():
    pantalla_herr_lista("Actualizar herramientas", "herr_editar")

def pantalla_herr_ver():
    pantalla_herr_lista("Ver herramientas", "herr_detalle")

def pantalla_herr_detalle():
    st.header("Detalle de la herramienta")
    herramienta = buscar_por_codigo(cargar_herramientas(), st.session_state.seleccion)

    if herramienta is None:
        st.error("No se encontró la herramienta.")
    else:
        if herramienta["descripcion"] == "":
            descripcion = "Sin descripción"
        else:
            descripcion = herramienta["descripcion"]

        if herramienta["comentarios"] == "":
            comentarios = "Sin comentarios"
        else:
            comentarios = herramienta["comentarios"]

        mostrar_codigo(herramienta["codigo"])
        tarjeta_detalle([
            ["Nombre", herramienta["nombre"]],
            ["Marca", herramienta["marca"]],
            ["Ubicación", herramienta["ubicacion"]],
            ["Estado", herramienta["estado"]],
            ["Descripción", descripcion],
            ["Comentarios", comentarios]
        ])

    barra_navegacion()

def pantalla_herr_editar():
    st.header("Actualizar herramienta")
    lista_herramientas = cargar_herramientas()
    herramienta = buscar_por_codigo(lista_herramientas, st.session_state.seleccion)

    if herramienta is None:
        st.error("No se encontró la herramienta.")
        barra_navegacion()
        return

    codigo = herramienta["codigo"]
    linea("Herramienta", herramienta["nombre"] + " (" + codigo + ")")

    # Indique el dato que desea modificar (el código no se edita: es el identificador).
    nombres = []
    for campo_lista in campos_herramientas:
        nombres.append(etiquetas_herramientas[campo_lista])
    nombre_elegido = st.selectbox(
        "Indique el dato que desea modificar",
        nombres,
        key="opcion_herr_" + codigo
    )
    campo = campos_herramientas[nombres.index(nombre_elegido)]

    valor_actual = herramienta[campo]
    if campo == "descripcion" and valor_actual == "":
        valor_actual = "Sin descripción"
    elif campo == "comentarios" and valor_actual == "":
        valor_actual = "Sin comentarios"
    linea("Dato actual", valor_actual)

    with st.form("form_herr_editar_" + codigo + "_" + campo):
        entrada = crear_entrada_herramienta(campo, "editar_herr_" + codigo + "_" + campo, herramienta[campo])
        enviado = st.form_submit_button("Guardar cambio")

    if enviado:
        dato, error = validar_dato_herramienta(campo, entrada)

        if error != "":
            st.error(etiquetas_herramientas[campo] + ": " + error)
        else:
            herramienta[campo] = dato
            guardar_herramientas(lista_herramientas)
            avisar("exito", "Dato actualizado correctamente")
            st.rerun()

    barra_navegacion()

#Programa Principal==================================================================================================================================================================
def main():
    st.set_page_config(page_title="Obras, materiales y herramientas", page_icon="🏗️")
    aplicar_estilos()
    iniciar_estado()

    pantallas = {
        "inicio": pantalla_inicio,
        "login": pantalla_login,
        "fin": pantalla_fin,
        "menu": pantalla_menu,
        "obras": pantalla_obras,
        "obras_registrar": pantalla_obras_registrar,
        "obras_buscar": pantalla_obras_buscar,
        "obras_detalle": pantalla_obras_detalle,
        "obras_actualizar": pantalla_obras_actualizar,
        "obras_editar": pantalla_obras_editar,
        "materiales": pantalla_materiales,
        "mat_registrar": pantalla_mat_registrar,
        "mat_transferir": pantalla_mat_transferir,
        "mat_transferir_form": pantalla_mat_transferir_form,
        "mat_buscar": pantalla_mat_buscar,
        "mat_detalle": pantalla_mat_detalle,
        "herramientas": pantalla_herramientas,
        "herr_registrar": pantalla_herr_registrar,
        "herr_actualizar": pantalla_herr_actualizar,
        "herr_editar": pantalla_herr_editar,
        "herr_ver": pantalla_herr_ver,
        "herr_detalle": pantalla_herr_detalle
    }

    pantalla = st.session_state.pantalla

    if pantalla != "inicio" and pantalla != "login" and pantalla != "fin" and st.session_state.usuario == "":
        volver_al_inicio()
        pantalla = "inicio"

    encabezado()
    mostrar_aviso()
    pantallas[pantalla]()
main()


main()
