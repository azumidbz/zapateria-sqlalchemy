# Sistema de Inventario de Zapatos — SQLAlchemy ORM

## 1. Información del proyecto

| Información | Descripción |
|---|---|
| Estudiante | Gabriel Davila |
| Asignatura | Desarrollo de aplicaciones con acceso a datos |
| Docente | Eduardo Pimienta |
| Fecha | 17 de noviembre de 2026 |
| Lenguaje de programación | Python |
| ORM utilizado | SQLAlchemy |
| Base de datos | SQLite |

## 2. Descripción del proyecto

**¿En qué consiste el programa?**

Es una aplicación de consola para administrar el inventario de una pequeña tienda de zapatos. Guarda de cada zapato su identificador, modelo, talla y precio. Antes, el programa no conservaba nada; ahora la información se almacena de forma permanente en una base de datos SQLite (`zapateria.db`) usando el ORM SQLAlchemy, de modo que los zapatos siguen existiendo aunque se cierre el programa.

**¿Qué funcionalidades tiene?**

- Registrar zapatos.
- Consultar el inventario.
- Buscar zapatos por ID.
- Actualizar precios.
- Eliminar zapatos.

## 3. Estructura del proyecto

```text
Parcial 3/
├── main.py
├── datos.py
├── requirements.txt
├── README.md
├── .gitignore
└── evidencias/
```

**Explicación de los archivos:**

| Archivo | ¿Cuál es su responsabilidad? |
|---|---|
| `main.py` | Contiene el menú de consola y la interacción con el usuario: pide los datos, valida que sean correctos y llama a las funciones de `datos.py`. No se modificó. |
| `datos.py` | Capa de persistencia. Define el engine, la clase `Base`, el modelo `Zapato` y las funciones CRUD con SQLAlchemy. |
| `requirements.txt` | Lista la dependencia necesaria: `SQLAlchemy>=2.0,<3.0`. |
| `zapateria.db` | Archivo de base de datos SQLite. Se genera automáticamente la primera vez que se ejecuta `main.py` (al llamar a `inicializar_bd()`), en la carpeta desde donde se ejecuta el programa. No se sube al repositorio. |

## 4. Instalación y ejecución

**Paso 1. Requisitos**

Tener instalado Python 3.8 o superior (se probó con Python 3.13) y `pip`. No hace falta instalar SQLite, porque viene incluido con Python.

**Paso 2. Instalación de dependencias**

Desde la carpeta del proyecto (si la ruta tiene espacios, escribirla entre comillas al usar `cd`):

```bash
python -m pip install -r requirements.txt
```

**Paso 3. Ejecución**

```bash
python main.py
```

**Paso 4. Resultado esperado**

Aparece el menú "TIENDA DE ZAPATOS" con las opciones del 1 al 6. Se crea el archivo `zapateria.db` y se puede registrar, listar, buscar, actualizar y eliminar zapatos.

---

# 5. Documentación técnica — Preguntas obligatorias

### Pregunta 1. Modelo y tabla

¿Qué clase de Python representa la tabla de la base de datos? Explica cómo SQLAlchemy identifica el nombre de la tabla y sus columnas.

**Respuesta:**

La tabla la representa la clase `Zapato`, que hereda de `Base`, una clase que a su vez hereda de `DeclarativeBase`. SQLAlchemy toma el nombre de la tabla del atributo `__tablename__`, que en este caso es `"zapatos"`. Las columnas salen de los atributos de la clase anotados con `Mapped[...]`: cada uno se convierte en una columna, y el tipo de Python indica el tipo SQL (`int` → INTEGER, `float` → DOUBLE, `str` → VARCHAR). El atributo `id` se marca con `primary_key=True`, por lo que es la clave primaria y se genera automáticamente.

**Fragmento de código relacionado:**

```python
class Base(DeclarativeBase):
    pass


class Zapato(Base):
    __tablename__ = "zapatos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    modelo: Mapped[str] = mapped_column(String)
    talla: Mapped[int]
    precio: Mapped[float]
```

Cada objeto `Zapato` que creo en Python corresponde a una fila de la tabla `zapatos`, y sus atributos (`modelo`, `talla`, `precio`) corresponden a las columnas.

### Pregunta 2. Creación de la base de datos

¿Qué ocurre cuando ejecutas el programa por primera vez? Explica cómo se crea la base de datos `zapateria.db` y la tabla `zapatos`.

**Respuesta:**

Al ejecutar `python main.py`, la primera instrucción de `main()` es `datos.inicializar_bd()`. Esa función llama a `Base.metadata.create_all(engine)`, que revisa todos los modelos que heredan de `Base` y crea sus tablas si todavía no existen. Para hacerlo, SQLAlchemy abre una conexión a través del engine, configurado con `sqlite:///zapateria.db`; como el archivo no existe, SQLite lo crea en ese momento y dentro de él se crea la tabla `zapatos` con sus cuatro columnas. En las siguientes ejecuciones el archivo y la tabla ya existen, así que `create_all` no hace nada y no borra los datos.

**Fragmento de código relacionado:**

```python
engine = create_engine("sqlite:///zapateria.db")

def inicializar_bd():
    Base.metadata.create_all(engine)
```

### Pregunta 3. Registro de zapatos

Cuando seleccionas la opción de registrar un zapato, ¿qué recorrido siguen los datos desde el menú hasta quedar almacenados en SQLite? Identifica las funciones utilizadas.

**Respuesta:**

1. En `main()` el usuario elige la opción `1` y escribe modelo, talla y precio con `input()`. `main.py` convierte la talla a `int` y el precio a `float`, y valida que el modelo no esté vacío y que talla y precio sean positivos.
2. Si los datos son válidos, `main.py` llama a `datos.crear_zapato(modelo, talla, precio)`.
3. Dentro de `crear_zapato` se crea un objeto `Zapato` con esos valores.
4. Se abre una sesión con `Session(engine)`, se agrega el objeto con `session.add()` y se confirma con `session.commit()`. En el `commit` SQLAlchemy genera el `INSERT` y lo ejecuta en SQLite, que asigna el `id`.
5. La función devuelve `True` y `main.py` muestra "Zapato registrado correctamente.", como se ve en las capturas `registro.png` y `registro_2.png`.

**Fragmento de código relacionado:**

```python
def crear_zapato(modelo, talla, precio):
    zapato = Zapato(modelo=modelo, talla=talla, precio=precio)
    with Session(engine) as session:
        session.add(zapato)
        session.commit()
    return True
```

### Pregunta 4. Sesiones y transacciones

¿Para qué se utiliza una sesión de SQLAlchemy? ¿Qué ocurriría si agregas o modificas un objeto, pero no confirmas la transacción con `commit()`?

**Respuesta:**

La sesión es el intermediario entre los objetos de Python y la base de datos. Mantiene un registro de los objetos que se agregan, modifican o eliminan, y agrupa esos cambios en una transacción que se envía a la base de datos cuando se llama a `commit()`. En mi programa cada función abre su sesión con `with Session(engine) as session:`, de modo que la sesión se cierra automáticamente al terminar.

Si agrego o modifico un objeto y no hago `commit()`, los cambios quedan solo pendientes dentro de la transacción. Al cerrarse la sesión, la transacción se revierte (rollback) y la base de datos queda como estaba: el zapato no se registraría, el precio no cambiaría o el registro no se eliminaría, aunque el programa no muestre ningún error.

### Pregunta 5. Búsqueda por ID

¿Cómo funciona la búsqueda de zapatos por ID? Explica qué devuelve tu función cuando encuentra el registro y qué devuelve cuando no existe.

**Respuesta:**

`buscar_zapato(id_zapato)` abre una sesión y usa `session.get(Zapato, id_zapato)`, que consulta la tabla por su clave primaria. Si existe una fila con ese ID, devuelve un objeto `Zapato` con sus datos; si no existe, devuelve `None`. `main.py` revisa ese resultado: con `None` muestra "Zapato no encontrado.", y si hay objeto lo muestra con `mostrar_zapato`. En la captura `busqueda.png` se buscó el ID 1 y apareció Jordan, talla 43, precio $100000.00.

**Fragmento de código relacionado:**

```python
def buscar_zapato(id_zapato):
    with Session(engine) as session:
        return session.get(Zapato, id_zapato)
```

### Pregunta 6. Actualización de precios

¿Cómo se actualiza el precio de un zapato mediante el ORM? Explica cómo se obtiene el objeto, cómo se modifica su atributo y cómo se guarda el cambio.

**Respuesta:**

Primero se obtiene el objeto con `session.get(Zapato, id_zapato)`. Si es `None`, la función devuelve `False` porque no existe. Si existe, se modifica simplemente el atributo del objeto: `zapato.precio = nuevo_precio`. No se escribe ninguna sentencia SQL: la sesión detecta que el objeto cambió. Finalmente, `session.commit()` guarda el cambio, y en ese momento SQLAlchemy genera y ejecuta el `UPDATE`. En la prueba, el zapato con ID 1 pasó de 100000 a 140000 (`actualizacion.png`), y el nuevo precio se ve en `persistencia.png`.

**Fragmento de código relacionado:**

```python
def actualizar_precio(id_zapato, nuevo_precio):
    with Session(engine) as session:
        zapato = session.get(Zapato, id_zapato)
        if zapato is None:
            return False
        zapato.precio = nuevo_precio
        session.commit()
        return True
```

### Pregunta 7. Eliminación de registros

¿Qué ocurre cuando eliminas un zapato? Explica cómo compruebas que el registro ya no existe en la base de datos.

**Respuesta:**

`eliminar_zapato` obtiene el objeto con `session.get()`; si no existe devuelve `False`. Si existe, lo marca para borrado con `session.delete(zapato)` y `session.commit()` ejecuta el `DELETE` sobre la tabla, y devuelve `True`. Eliminé el zapato con ID 2 (Nike) y el programa mostró "Zapato eliminado." (`eliminacion.png`). Para comprobarlo, volví a listar los zapatos: solo aparece el ID 1. Otra forma de comprobarlo es buscar el ID 2, que ahora devuelve `None` y muestra "Zapato no encontrado.".

**Fragmento de código relacionado:**

```python
def eliminar_zapato(id_zapato):
    with Session(engine) as session:
        zapato = session.get(Zapato, id_zapato)
        if zapato is None:
            return False
        session.delete(zapato)
        session.commit()
        return True
```

### Pregunta 8. Persistencia de datos

¿Qué sucede con los zapatos registrados cuando cierras y vuelves a ejecutar el programa? Explica por qué permanecen almacenados.

**Respuesta:**

Los zapatos siguen ahí. Los datos no se guardan en variables del programa (que desaparecen al cerrarlo), sino en el archivo `zapateria.db`, que está en el disco. Al volver a ejecutar, `inicializar_bd()` llama a `create_all`, que no borra ni recrea una tabla que ya existe, y `listar_zapatos()` lee las filas guardadas. Lo comprobé cerrando el programa con la opción 6, ejecutando de nuevo `python main.py` y listando: apareció el zapato con ID 1 (Jordan, talla 43) con el precio ya actualizado a $140000.00, y el ID 2 no aparece porque fue eliminado (`persistencia.png`).

---

## 6. Pruebas de funcionamiento y evidencias

### Prueba 1. Registrar zapatos

- **Acción realizada:** registrar dos zapatos.
- **Datos utilizados:** Jordan, talla 43, precio 100000; y Nike, talla 45, precio 120000.
- **Resultado obtenido:** en ambos casos el programa mostró "Zapato registrado correctamente.".

**Evidencia:**

![Registro de zapatos](evidencias/registro.png)

![Registro del segundo zapato](evidencias/registro_2.png)

### Prueba 2. Listar inventario

- **Acción realizada:** consultar todos los zapatos.
- **Resultado obtenido:** el programa listó los dos zapatos con ID 1 (Jordan) e ID 2 (Nike), con su talla y precio.

**Evidencia:**

![Listado de zapatos](evidencias/listado.png)

### Prueba 3. Buscar por ID

- **ID utilizado:** 1.
- **Resultado obtenido:** el programa mostró únicamente el zapato Jordan, talla 43, precio $100000.00.

**Evidencia:**

![Búsqueda de zapatos](evidencias/busqueda.png)

### Prueba 4. Actualizar precio

- **Zapato seleccionado:** ID 1 (Jordan).
- **Precio anterior:** 100000.
- **Precio nuevo:** 140000.
- **Resultado obtenido:** el programa mostró "Precio actualizado.". El nuevo precio se ve en la captura de la Prueba 6.

**Evidencia:**

![Actualización de precio](evidencias/actualizacion.png)

### Prueba 5. Eliminar zapato

- **ID eliminado:** 2 (Nike).
- **Resultado obtenido:** el programa mostró "Zapato eliminado.". La verificación se ve en la captura de la Prueba 6, donde solo queda el ID 1.

**Evidencia:**

![Eliminación de zapato](evidencias/eliminacion.png)

### Prueba 6. Comprobar persistencia

- **Acción realizada:** cerrar y ejecutar nuevamente el programa.
- **Resultado obtenido:** al volver a ejecutar `python main.py` y listar, apareció solo el zapato con ID 1 (Jordan, talla 43, precio $140000.00), con el precio ya actualizado. El ID 2 no aparece porque fue eliminado.

**Evidencia:**

![Persistencia de datos](evidencias/persistencia.png)

### Pruebas con registros inexistentes

Se probaron las operaciones de buscar, actualizar y eliminar con un ID que no existe (por ejemplo, el 99).

| Operación | ¿Qué sucedió? |
|---|---|
| Buscar ID inexistente | `session.get()` devuelve `None` y el programa muestra "Zapato no encontrado.". No hay error ni se modifica la base. |
| Actualizar ID inexistente | `actualizar_precio` no encuentra el objeto y devuelve `False`, sin hacer `commit`; el programa muestra "Zapato no encontrado.". |
| Eliminar ID inexistente | `eliminar_zapato` no encuentra el objeto y devuelve `False`, sin hacer `commit`; el programa muestra "Zapato no encontrado.". |

## 7. Conclusiones

1. **¿Qué aprendí al implementar el CRUD con SQLAlchemy?** Aprendí que cada operación sigue la misma idea: abrir una sesión, obtener o crear un objeto, modificarlo y confirmar con `commit()`. También entendí la importancia del `commit()`, porque sin él los cambios no quedan guardados.
2. **¿Qué diferencia identifiqué entre objetos Python y SQL directo?** Con el ORM trabajo con objetos y atributos (`zapato.precio = 140000`) en lugar de escribir sentencias `INSERT`, `UPDATE` o `DELETE`. El código queda más corto y legible, y SQLAlchemy se encarga de generar el SQL.
3. **¿Cuál fue la principal dificultad y cómo la solucioné?** Al ejecutar el programa, PowerShell no encontraba `main.py` ni `requirements.txt` porque la terminal no estaba ubicada en la carpeta del proyecto, y además la ruta tenía espacios. Lo resolví entrando a la carpeta con `cd` y escribiendo la ruta entre comillas.
