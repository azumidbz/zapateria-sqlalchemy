
from sqlalchemy import create_engine, select, String
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    Session
)


# =====================================
# ORM 1 - CONFIGURACION DE LA CONEXION
# =====================================

# El archivo zapateria.db se crea en la carpeta de ejecucion
# la primera vez que se abre una conexion.
engine = create_engine("sqlite:///zapateria.db")


# =====================================
# ORM 2 - CLASE BASE
# =====================================

class Base(DeclarativeBase):
    pass


# =====================================
# ORM 3 - MODELO ZAPATO
# =====================================

class Zapato(Base):
    __tablename__ = "zapatos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    modelo: Mapped[str] = mapped_column(String)
    talla: Mapped[int]
    precio: Mapped[float]

    def __repr__(self):
        return (f"Zapato(id={self.id}, modelo={self.modelo!r}, "
                f"talla={self.talla}, precio={self.precio})")


# =====================================
# ORM 4 - CREAR LA TABLA
# =====================================

def inicializar_bd():
    # Crea la tabla zapatos solo si no existe (no borra datos).
    Base.metadata.create_all(engine)


# =====================================
# ORM 5 - REGISTRAR ZAPATO
# =====================================

def crear_zapato(modelo, talla, precio):
    zapato = Zapato(modelo=modelo, talla=talla, precio=precio)
    with Session(engine) as session:
        session.add(zapato)
        session.commit()
    return True


# =====================================
# ORM 6 - LISTAR ZAPATOS
# =====================================

def listar_zapatos():
    with Session(engine) as session:
        return list(session.scalars(select(Zapato).order_by(Zapato.id)))


# =====================================
# ORM 7 - BUSCAR POR ID
# =====================================

def buscar_zapato(id_zapato):
    with Session(engine) as session:
        return session.get(Zapato, id_zapato)  # objeto o None


# =====================================
# ORM 8 - ACTUALIZAR PRECIO
# =====================================

def actualizar_precio(id_zapato, nuevo_precio):
    with Session(engine) as session:
        zapato = session.get(Zapato, id_zapato)
        if zapato is None:
            return False
        zapato.precio = nuevo_precio
        session.commit()
        return True


# =====================================
# ORM 9 - ELIMINAR ZAPATO
# =====================================

def eliminar_zapato(id_zapato):
    with Session(engine) as session:
        zapato = session.get(Zapato, id_zapato)
        if zapato is None:
            return False
        session.delete(zapato)
        session.commit()
        return True
