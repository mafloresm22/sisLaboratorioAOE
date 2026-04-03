-- 1. Tablas Maestras
CREATE TABLE Rol (
    idRol SERIAL PRIMARY KEY,
    nombreRol VARCHAR(50) NOT NULL
);

CREATE TABLE EstadoConservacion (
    idEstadoCons SERIAL PRIMARY KEY,
    nombreEstado VARCHAR(50) NOT NULL -- 'Nuevo', 'Bueno', 'Regular', 'Malo'
);

CREATE TABLE Unidad (
    idUnidad SERIAL PRIMARY KEY,
    nombreUnidad VARCHAR(100) NOT NULL
);

CREATE TABLE Laboratorios (
    idLaboratorios SERIAL PRIMARY KEY,
    nombreLaboratorios VARCHAR(100) NOT NULL,
    pisoLaboratorios VARCHAR(50) NOT NULL,
    estadoLaboratorios VARCHAR(50)
);

-- 2. Usuarios e Inventario
CREATE TABLE Usuarios (
    idUsuarios SERIAL PRIMARY KEY,
    nombreUsuarios VARCHAR(100) NOT NULL,
    passwordUsuarios TEXT NOT NULL,
    rolId INTEGER REFERENCES Rol(idRol)
);

CREATE TABLE Instrumento (
    idInstrumento SERIAL PRIMARY KEY,
    nombreInstrumento VARCHAR(150) NOT NULL,
    descripcionInstrumento TEXT,
    cantidadInstrumento INTEGER DEFAULT 0,
    marcaInstrumento VARCHAR(100),
    modeloInstrumento VARCHAR(100),
    serieInstrumento VARCHAR(100),
    colorInstrumento VARCHAR(50),
    tamanoInstrumento VARCHAR(50),
    pisoInstrumento VARCHAR(50),
    idEstadoCons INTEGER REFERENCES EstadoConservacion(idEstadoCons),
    usuarioId INTEGER REFERENCES Usuarios(idUsuarios),
    laboratorioId INTEGER REFERENCES Laboratorios(idLaboratorios),
    unidadId INTEGER REFERENCES Unidad(idUnidad),
    imagenInstrumento VARCHAR(255),
    estado VARCHAR(20) DEFAULT 'disponible'
);

-- 3. Sistema de Préstamos
CREATE TABLE Prestamo (
    idPrestamo SERIAL PRIMARY KEY,
    usuarioId INTEGER REFERENCES Usuarios(idUsuarios),
    fechaSolicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estadoPrestamo VARCHAR(20) DEFAULT 'pendiente' -- 'activo', 'devuelto', 'atrasado'
);

CREATE TABLE DetallePrestamo (
    idDetalle SERIAL PRIMARY KEY,
    prestamoId INTEGER REFERENCES Prestamo(idPrestamo) ON DELETE CASCADE,
    instrumentoId INTEGER REFERENCES Instrumento(idInstrumento),
    cantidadSolicitada INTEGER NOT NULL,
    fechaDevolucion TIMESTAMP,
    estadoEntrega VARCHAR(50),
    estadoDevolucion VARCHAR(50)
);
