# Fase4
Gestión de Obras, Materiales y Herramientas

Aplicación web hecha con Streamlit para registrar y consultar obras de construcción, los materiales  y las herramientas disponibles. Es la versión web del programa  de la Fase 4 (Grupo 03).

Qué puede hacer:
Módulo = 	Funciones
Obras	= Registrar obra, buscar obra por código, actualizar datos de una obra
Materiales = Registrar material, transferir material (total o parcial) a otro lugar, buscar y ver materiales
Herramientas =	Registrar herramienta, actualizar datos, ver herramientas


Requisitos:
Python 3.9 o superior
Streamlit 1.27 o superior
pip install streamlit

Cómo ejecutarla:
Guarde Fase4_Grupo03_Software_streamlit.py en una carpeta.
Abra una terminal en esa carpeta.

Ejecute:
streamlit run Fase4_Grupo03_Software_streamlit.py

Inicio de sesión:

El nombre de usuario debe cumplir este formato:

Orden exacto: nombre, símbolo @, dominio y terminación.
El nombre va todo en minúscula y sin espacios.
Dominios permitidos: gmail, outlook, hotmail, nivela.
Terminaciones permitidas: .com, .org, .net, .gt.
Ejemplo válido: juan@gmail.com

La contraseña debe tener (en cualquier orden):

Mínimo 8 caracteres.
Al menos una mayúscula, una minúscula y un número.
Al menos un carácter especial de esta lista: . , : ; ? ! @ # _ - $ % & * = ( ) [ ] { }

Después de 3 intentos fallidos la aplicación se bloquea. Recargue la página para volver a intentarlo.
No hay una base de usuarios: cualquier usuario y contraseña que cumplan el formato entran al sistema.
Uso de los módulos

En cada pantalla hay botones para Regresar uno, Regresar al menú principal y Finalizar sesión.

Obras:
Registrar obra: se llena un formulario con título, descripción, cliente (nombre y apellido), zona, dirección, colonia, información adicional (opcional), fecha de inicio, fecha de finalización, presupuesto y gerente de obra (nombre y apellido). El código (OBR001, OBR002, ...) se genera solo. Guárdelo: se necesita para buscar la obra.
Buscar obra: se escribe el código (también se acepta en minúscula) y se muestran todos los datos.
Actualizar obra: se elige la obra, se elige el dato a modificar y se guarda el cambio. Se pueden hacer varios cambios seguidos.

Reglas principales:
El título empieza con mayúscula y no puede repetirse.
Nombres y apellidos empiezan con mayúscula y solo llevan letras, espacios o guiones.
La zona es un número entero del 1 al 25.
Las fechas se eligen en un calendario (años 2000 a 2100). La finalización no puede ser anterior al inicio.
El presupuesto es mayor que cero, sin comas y con hasta 2 decimales (ejemplo: 150000.50).

Materiales:
Registrar material: código (3 letras mayúsculas y 3 dígitos, por ejemplo MAT001, sin repetirse), nombre, categoría, cantidad, costo por unidad, fecha de entrega y lugar de entrega.
Transferencia de material: se elige el material, la cantidad y el lugar de destino. Si se transfiere todo, el material cambia de lugar. Si se transfiere una parte, queda el resto en el lugar actual y se crea un material nuevo (con un código nuevo) en el destino.
Buscar materiales: lista de materiales y detalle de cada uno.
Categorías disponibles: Cemento y concreto, Acero y hierro, Madera, Bloques y ladrillos, Plomería, Electricidad, Pintura y acabados, Otros.

Herramientas:
Registrar herramientas: nombre, código (por ejemplo TAL001, sin repetirse), marca, ubicación, estado, descripción (opcional) y comentarios (opcional).
Actualizar herramientas: se elige la herramienta y el dato a modificar.
Ver herramientas: lista y detalle.
Estados disponibles: Bueno, Regular, Malo, En mantenimiento.

Archivos de datos = Archivo	Contenido:
obras.json = 	Lista de obras
materiales.json = 	Lista de materiales
herramientas.json	= Lista de herramientas

Se crean automáticamente al registrar el primer elemento. Son texto legible y se pueden respaldar copiando los archivos. Las obras guardadas antes de que existieran los códigos reciben uno al cargarse.

Cómo está organizado el código:
El archivo se divide en secciones:

Constantes y validaciones: dominios, terminaciones, caracteres especiales y las funciones validar_*.
Almacenamiento: cargar_* y guardar_* para cada archivo JSON.
Validación de cada dato: validar_dato_obra, validar_dato_material y validar_dato_herramienta. Cada una devuelve (dato, error); si no hay error, el texto de error queda vacío.
Ayudas de Streamlit y navegación: st.session_state guarda la pantalla actual y una pila de pantallas anteriores, que es lo que usa "Regresar uno".
Pantallas: una función pantalla_* por cada pantalla.
main(): inicia el estado y dibuja la pantalla actual.

Para agregar un dominio, una terminación, una categoría o un estado, basta con añadirlo a la lista correspondiente al inicio del archivo.

Diferencias con la versión de consola
Los datos se llenan en formularios en vez de pedirse uno por uno con input(); si hay errores se muestran todos juntos.
Ya no existe "0 para cancelar": se usa el botón Regresar uno.
Las fechas se eligen en un calendario.
La contraseña se oculta al escribirla.
Problemas frecuentes
NameError al iniciar sesión: revise que la función esté definida como def validar_contrasena(contrasena): y que no haya líneas movidas fuera de ella.
streamlit no se reconoce como comando: instálelo con pip install streamlit o ejecute python -m streamlit run Fase4_Grupo03_Software_streamlit.py.
No aparecen mis datos: ejecute la aplicación desde la carpeta donde están los archivos .json.
