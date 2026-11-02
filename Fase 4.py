
import json
import os
import datetime
import string
import streamlit as st

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
            obra_con_codigo = {"codigo": generar_codigo_obra(lista_obras)}
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

def validar_codigo_obra(texto):
    if len(texto) < 6:
        return False

    if texto[:3] != "OBR":
        return False

    return solo_digitos(texto[3:])

def generar_codigo_obra(lista_obras):
    mayor = 0
    for obra in lista_obras:
        codigo = obra.get("codigo", "")
        if validar_codigo_obra(codigo) and int(codigo[3:]) > mayor:
            mayor = int(codigo[3:])

    return "OBR" + str(mayor + 1).zfill(3)

#Datos de Modulo de Materiales==============================================================================================================
categorias_materiales = [
    "Cemento y concreto", "Acero y hierro", "Madera", "Bloques y ladrillos",
    "Plomería", "Electricidad", "Pintura y acabados", "Otros"
]

campos_material = ["codigo", "nombre", "categoria", "cantidad", "costo", "fecha_entrega", "lugar_entrega"]

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

campos_herramientas = ["nombre", "codigo", "marca", "ubicacion", "estado", "descripcion", "comentarios"]

etiquetas_herramientas = {
        "nombre": "Nombre",
        "codigo": "Código",
        "marca": "Marca",
        "ubicacion": "Ubicación",
        "estado": "Estado",
        "descripcion": "Descripción",
        "comentarios": "Comentarios"
    }

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

def validar_codigo(texto):
    if len(texto) != 6:
        return False

    for caracter in texto[:3]:
        if caracter not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            return False

    for caracter in texto[3:]:
        if caracter not in "0123456789":
            return False

    return True

def validar_marca(texto):
    return validar_nombre(texto)

def validar_ubicacion(texto):
    return validar_nombre(texto)

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
            return "", "la zona debe ser un número entero del 1 al " + str(zona_maxima) + "."
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
 
    dato = dato.strip()
 
    if campo == "codigo":
        if not validar_codigo(dato):
            return "", "el código debe tener 3 letras MAYÚSCULAS de A a Z seguidas de 3 dígitos de 0 a 9, sin espacios. Ejemplo: MAT001."
        for material in lista_materiales:
            if material["codigo"] == dato:
                return "", "el código ya está registrado en otro material."
        return dato, ""
 
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
        return "", "el lugar no puede estar vacío y solo admite letras, números, espacios o los caracteres especiales permitidos."
    if campo == "lugar_nuevo" and dato.lower() == material_ref["lugar_entrega"].lower():
        return "", "el lugar de destino debe ser distinto al lugar actual."
    return dato, ""

def validar_dato_herramienta(campo,dato, lista_herramientas, codigo_actual):
    if campo == "estado":
        return dato, ""
 
    dato = dato.strip()
 
    if campo == "nombre" or campo == "marca" or campo == "ubicacion":
        if campo == "nombre":
            dato_valido = validar_nombre(dato)
        elif campo == "marca":
            dato_valido = validar_marca(dato)
        else:
            dato_valido = validar_ubicacion(dato)
 
        if not dato_valido:
            return "", "no puede estar vacío; debe empezar con una letra mayúscula y contener solo letras, números, espacios o los caracteres especiales permitidos."
        return dato, ""
 
    if campo == "codigo":
        if not validar_codigo(dato):
            return "", "el código debe tener 3 letras MAYÚSCULAS de A a Z seguidas de 3 dígitos de 0 a 9, sin espacios. Ejemplo: TAL001."
        for herramienta in lista_herramientas:
            if herramienta["codigo"] == dato and dato != codigo_actual:
                return "", "el código ya está registrado en otra herramienta."
        return dato, ""
 
    return dato, ""

#Streamlit ======================================================================================================================================================================================
def seguro(texto):
    resultado = ""
    for caracter in str(texto):
        if caracter in string.punctuation:
            resultado = resultado + "\\" + caracter
        else:
            resultado = resultado + caracter
    return resultado

def linea(etiqueta,valor):
    st.write("**" + etiqueta + ":**" + seguro(valor))
    
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
        columnas[0].button("Regresar uno", key="nav_atras", on_click=regresar_uno)
    if mostrar_menu:
        columnas[1].button("Regresar al menú principal", key="nav_menu", on_click=regresar_al_menu)
    columnas[2].button("Finalizar sesión", key="nav_fin", on_click=finalizar_sesion)
    
#Pantallas: Inicio y sesion=============================================================================================================================================================================
def pantalla_inicio():
    st.header("Inicio")
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
    st.button("Obras", key="menu_obras", on_click=ir_a, args=("obras",))
    st.button("Materiales", key="menu_materiales", on_click=ir_a, args=("materiales",))
    st.button("Herramientas", key="menu_herramientas", on_click=ir_a, args=("herramientas",))
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
    lineas.append("- **Título de obra:** debe empezar con una letra mayúscula, no puede repetirse y admite letras, números, espacios y estos caracteres especiales: `" + " ".join(caracteres_especiales_obras) + "`")
    lineas.append("- **Cliente y Gerente de obra:** nombre y apellido deben empezar con una letra mayúscula y contener solo letras, espacios o guiones.")
    lineas.append("- **Zona:** número entero del 1 al " + str(zona_maxima) + ".")
    lineas.append("- **Fechas:** se eligen en el calendario. La finalización no puede ser anterior al inicio.")
    lineas.append("- **Presupuesto inicial:** en quetzales, mayor que cero, sin comas. Ejemplo: `150000.50`")
    lineas.append("- **Información adicional:** es opcional.")
    with st.expander("Requisitos de los datos", expanded=True):
        st.write("\n".join(lineas))
  
def crear_entrada_obra(campo, clave, valor_inicial):
    etiqueta = etiquetas_obras[campo]
 
    if campo == "fecha_inicio" or campo == "fecha_fin":
        return crear_entrada_fecha(etiqueta, clave, valor_inicial)
 
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
        enviado = st.form_submit_button("Registrar obra")
 
    if enviado:
        obra_nueva = {"codigo": generar_codigo_obra(lista_obras)}
        errores = []
 
        for campo in campos_obra:
            dato, error = validar_dato_obra(campo, entradas[campo], lista_obras, "", obra_nueva)
            if error != "":
                errores.append(etiquetas_obras[campo] + ": " + error)
            else:
                obra_nueva[campo] = dato
 
        if len(errores) > 0:
            mostrar_errores(errores)
        else:
            lista_obras.append(obra_nueva)
            guardar_obras(lista_obras)
            avisar("exito", "Obra registrada correctamente. Código de la obra: " + obra_nueva["codigo"] + ". Guarde este código: lo necesitará para buscar la obra.")
            regresar_uno()
            st.rerun()
 
    barra_navegacion(mostrar_menu=False)
 
def mostrar_detalle_obra(obra):
    linea("Código de obra", obra["codigo"])
    linea("Título de obra", obra["titulo"])
    linea("Descripción", obra["descripcion"])
    linea("Cliente", obra["cliente_nombre"] + " " + obra["cliente_apellido"])
    linea("Zona", obra["zona"])
    linea("Dirección", obra["direccion"])
    linea("Colonia", obra["colonia"])
 
    if obra["informacion"] == "":
        linea("Información adicional", "Sin información adicional")
    else:
        linea("Información adicional", obra["informacion"])
 
    linea("Fecha de inicio estimada", obra["fecha_inicio"])
    linea("Fecha de finalización estimada", obra["fecha_fin"])
    linea("Presupuesto inicial", formatear_monto(obra["presupuesto"]))
    linea("Gerente de obra", obra["gerente_nombre"] + " " + obra["gerente_apellido"])
  
def pantalla_obras_buscar():
    st.header("Buscar obra")
    lista_obras = cargar_obras()
 
    if len(lista_obras) == 0:
        st.info("No hay obras registradas")
    else:
        with st.form("form_obra_buscar"):
            codigo = st.text_input("Código de obra (ejemplo: OBR001)")
            enviado = st.form_submit_button("Buscar")
 
        if enviado:
            codigo = codigo.strip().upper()
 
            if not validar_codigo_obra(codigo):
                st.error("El código debe empezar con OBR seguido de números, sin espacios. Ejemplo: OBR001.")
            elif buscar_por_codigo(lista_obras, codigo) is None:
                st.error("No se encontró ninguna obra con el código " + codigo)
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
            avisar("exito", "Dato actualizado correctamente")
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
    lineas.append("- **Código:** 3 letras MAYÚSCULAS de A a Z y 3 dígitos de 0 a 9, sin repetirse. Ejemplo: `MAT001`.")
    lineas.append("- **Nombre:** debe empezar con una letra mayúscula y no quedar vacío. Admite letras, números, espacios y estos caracteres especiales: `" + " ".join(caracteres_especiales_herramientas) + "`")
    lineas.append("- **Cantidad:** número entero mayor que cero.")
    lineas.append("- **Costo:** por unidad, en quetzales, mayor que cero y sin comas. Ejemplo: `25.50`")
    with st.expander("Requisitos de los datos", expanded=True):
        st.write("\n".join(lineas))
 
    lista_materiales = cargar_materiales()
 
    with st.form("form_material_registrar"):
        entradas = {}
        entradas["codigo"] = st.text_input(etiquetas_materiales["codigo"] + " (ejemplo: MAT001)", key="reg_mat_codigo")
        entradas["nombre"] = st.text_input(etiquetas_materiales["nombre"], key="reg_mat_nombre")
        entradas["categoria"] = st.selectbox(etiquetas_materiales["categoria"], categorias_materiales, key="reg_mat_categoria")
        entradas["cantidad"] = st.text_input(etiquetas_materiales["cantidad"], key="reg_mat_cantidad")
        entradas["costo"] = st.text_input(etiquetas_materiales["costo"], key="reg_mat_costo")
        entradas["fecha_entrega"] = crear_entrada_fecha(etiquetas_materiales["fecha_entrega"], "reg_mat_fecha", "")
        entradas["lugar_entrega"] = st.text_input(etiquetas_materiales["lugar_entrega"], key="reg_mat_lugar")
        enviado = st.form_submit_button("Registrar material")
 
    if enviado:
        material_nuevo = {}
        errores = []
 
        for campo in campos_material:
            dato, error = validar_dato_material(campo, entradas[campo], lista_materiales, {})
            if error != "":
                errores.append(etiquetas_materiales[campo] + ": " + error)
            else:
                material_nuevo[campo] = dato
 
        if len(errores) > 0:
            mostrar_errores(errores)
        else:
            lista_materiales.append(material_nuevo)
            guardar_materiales(lista_materiales)
            avisar("exito", "Material registrado correctamente")
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
        linea("Código", material["codigo"])
        linea("Nombre", material["nombre"])
        linea("Categoría", material["categoria"])
        linea("Cantidad", material["cantidad"])
        linea("Costo por unidad", formatear_monto(material["costo"]))
        linea("Fecha de entrega", material["fecha_entrega"])
        linea("Lugar de entrega", material["lugar_entrega"])
 
    barra_navegacion()
  
def pantalla_mat_transferir_form():
    st.header("Transferencia de material")
    lista_materiales = cargar_materiales()
    material = buscar_por_codigo(lista_materiales, st.session_state.seleccion)
 
    if material is None:
        st.error("No se encontró el material.")
        barra_navegacion()
        return
 
    linea("Material", material["nombre"] + " (" + material["codigo"] + ")")
    linea("Cantidad disponible", material["cantidad"])
    linea("Lugar actual", material["lugar_entrega"])
 
    clave = material["codigo"]
    cantidad = st.text_input(etiquetas_materiales["cantidad_transferir"], key="transf_cantidad_" + clave)
    lugar_nuevo = st.text_input(etiquetas_materiales["lugar_nuevo"], key="transf_lugar_" + clave)
 
    codigo_nuevo = ""
    cantidad_limpia = cantidad.strip()
    if solo_digitos(cantidad_limpia) and int(cantidad_limpia) >= 1 and int(cantidad_limpia) < int(material["cantidad"]):
        st.info("Se transfiere solo una parte: el material transferido se registrará con un código nuevo.")
        codigo_nuevo = st.text_input("Código del material transferido (ejemplo: MAT002)", key="transf_codigo_" + clave)
 
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
 
        if "cantidad_transferir" in datos and datos["cantidad_transferir"] != material["cantidad"]:
            dato, error = validar_dato_material("codigo", codigo_nuevo, lista_materiales, material)
            if error != "":
                errores.append(etiquetas_materiales["codigo"] + ": " + error)
            else:
                datos["codigo"] = dato
 
        if len(errores) > 0:
            mostrar_errores(errores)
        else:
            if datos["cantidad_transferir"] == material["cantidad"]:
                material["lugar_entrega"] = datos["lugar_nuevo"]
            else:
                material_nuevo = {
                    "codigo": datos["codigo"],
                    "nombre": material["nombre"],
                    "categoria": material["categoria"],
                    "cantidad": datos["cantidad_transferir"],
                    "costo": material["costo"],
                    "fecha_entrega": material["fecha_entrega"],
                    "lugar_entrega": datos["lugar_nuevo"]
                }
                material["cantidad"] = str(int(material["cantidad"]) - int(datos["cantidad_transferir"]))
                lista_materiales.append(material_nuevo)
 
            guardar_materiales(lista_materiales)
            avisar("exito", "Transferencia realizada correctamente")
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
        posicion = 0
        if valor_inicial in estados_herramientas:
            posicion = estados_herramientas.index(valor_inicial)
        return st.selectbox(etiqueta, estados_herramientas, index=posicion, key=clave)
 
    if campo == "descripcion" or campo == "comentarios":
        etiqueta = etiqueta + " (opcional)"
 
    return st.text_input(etiqueta, value=valor_inicial, key=clave)
 
 
def pantalla_herr_registrar():
    st.header("Registrar herramientas")
 
    lineas = []
    lineas.append("- **Nombre, Marca y Ubicación:** deben empezar con una letra mayúscula y no quedar vacíos. Admiten letras, números, espacios y estos caracteres especiales: `" + " ".join(caracteres_especiales_herramientas) + "`")
    lineas.append("- **Código:** 3 letras MAYÚSCULAS de A a Z y 3 dígitos de 0 a 9, sin repetirse. Ejemplo: `TAL001`.")
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
        herramienta_nueva = {}
        errores = []
 
        # Revisar los campos en orden, conservando los que ya fueron válidos.
        for campo in campos_herramientas:
            dato, error = validar_dato_herramienta(campo, entradas[campo], lista_herramientas, "")
            if error != "":
                errores.append(etiquetas_herramientas[campo] + ": " + error)
            else:
                herramienta_nueva[campo] = dato
 
        if len(errores) > 0:
            mostrar_errores(errores)
        else:
            # Agregar únicamente cuando todos los campos estén completos.
            lista_herramientas.append(herramienta_nueva)
            # Guardar inmediatamente la lista completa en el archivo JSON.
            guardar_herramientas(lista_herramientas)
            avisar("exito", "Herramienta registrada correctamente")
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
        linea("Nombre", herramienta["nombre"])
        linea("Código", herramienta["codigo"])
        linea("Marca", herramienta["marca"])
        linea("Ubicación", herramienta["ubicacion"])
        linea("Estado", herramienta["estado"])
 
        if herramienta["descripcion"] == "":
            linea("Descripción", "Sin descripción")
        else:
            linea("Descripción", herramienta["descripcion"])
 
        if herramienta["comentarios"] == "":
            linea("Comentarios", "Sin comentarios")
        else:
            linea("Comentarios", herramienta["comentarios"])
 
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
 
    # Indique el dato que desea modificar.
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
        dato, error = validar_dato_herramienta(campo, entrada, lista_herramientas, codigo)
 
        if error != "":
            st.error(etiquetas_herramientas[campo] + ": " + error)
        else:
            herramienta[campo] = dato
            guardar_herramientas(lista_herramientas)
 
            # Si cambió el código, la selección debe seguir apuntando a esta herramienta.
            if campo == "codigo":
                st.session_state.seleccion = dato
 
            avisar("exito", "Dato actualizado correctamente")
            st.rerun()
 
    barra_navegacion()

#Programa Principal==================================================================================================================================================================
def main():
    st.set_page_config(page_title="Obras, materiales y herramientas")
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
 
    if st.session_state.usuario != "":
        st.caption("Sesión iniciada: " + seguro(st.session_state.usuario))
 
    mostrar_aviso()
    pantallas[pantalla]()
 
 
main()