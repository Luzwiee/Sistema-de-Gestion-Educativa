CREATE TABLE personas(
	id_persona SERIAL PRIMARY KEY,
	Nombre VARCHAR(50) NOT NULL,
	Apellido_paterno VARCHAR(50) NOT NULL,
	Apellido_materno VARCHAR(50) NOT NULL,	
	ci VARCHAR(8) NOT NULL
);

CREATE TABLE administrativos(
	id_administrativo SERIAL PRIMARY KEY,
	id_persona INT NOT NULL,
	FOREIGN KEY (id_persona) REFERENCES personas (id_persona)
);

CREATE TABLE tutores(
	id_tutor SERIAL PRIMARY KEY,
	num_celular VARCHAR(8) NOT NULL,
	id_persona INT NOT NULL,
	FOREIGN KEY (id_persona) REFERENCES personas (id_persona)
);

CREATE TABLE estudiantes(
	id_estudiante SERIAL PRIMARY KEY,
	id_persona INT NOT NULL,
	FOREIGN KEY (id_persona) REFERENCES personas (id_persona)
);

CREATE TABLE maestros(
	id_maestro SERIAL PRIMARY KEY,
	id_persona INT NOT NULL,
	FOREIGN KEY (id_persona) REFERENCES personas (id_persona)
);

CREATE TABLE usuarios(
	id_usuario SERIAL PRIMARY KEY,
	Usuario VARCHAR(30) NOT NULL,
	Estado BOOLEAN NOT NULL,
	Rol VARCHAR(20) NOT NULL,
	Contrasena VARCHAR(20) NOT NULL,
	Correo VARCHAR(100) UNIQUE NOT NULL,
	id_persona INT NOT NULL,
	FOREIGN KEY (id_persona) REFERENCES personas (id_persona)
);

CREATE TABLE turorias(
	id_tutoria SERIAL PRIMARY KEY,
	id_tutor INT NOT NULL,
	id_estudiante INT NOT NULL,
	FOREIGN KEY (id_tutor) REFERENCES tutores (id_tutor),
	FOREIGN KEY (id_estudiante) REFERENCES estudiantes (id_estudiante)
	
);

CREATE TABLE campos(
	id_campo SERIAL PRIMARY KEY,
	Nombre_campo VARCHAR(30) NOT NULL
);

CREATE TABLE niveles(
	id_nivel SERIAL PRIMARY KEY,
	Nombre_nivel VARCHAR(30) NOT NULL,
	Paralelo VARCHAR(1) NOT NULL,
	Grado VARCHAR(20) NOT NULL
);

CREATE TABLE asignaturas(
	id_asignatura SERIAL PRIMARY KEY,
	Nombre VARCHAR(30) NOT NULL,
	Sigla VARCHAR(10) NOT NULL,
	id_maestro INT NOT NULL,
	id_campo INT NOT NULL,
	id_nivel INT NOT NULL,
	FOREIGN KEY (id_maestro) REFERENCES maestros(id_maestro),
	FOREIGN KEY (id_campo) REFERENCES campos (id_campo),
	FOREIGN KEY (id_nivel) REFERENCES niveles (id_nivel)
	
);

CREATE TABLE calificaciones(
	id_calificacion SERIAL PRIMARY KEY,
	Nota DECIMAL(5,2) NOT NULL,
	Fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	Trimestre VARCHAR(20) NOT NULL,
	id_estudiante INT NOT NULL,
	id_asignatura INT NOT NULL,
	FOREIGN KEY (id_asignatura) REFERENCES asignaturas(id_asignatura),
	FOREIGN KEY (id_estudiante) REFERENCES estudiantes (id_estudiante)
	
);
CREATE TABLE inscripcion(
	id_inscripcion SERIAL PRIMARY KEY,
	id_estudiante INT NOT NULL,
	id_nivel INT NOT NULL,
	Fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (id_estudiante) REFERENCES estudiantes (id_estudiante),
	FOREIGN KEY (id_nivel) REFERENCES niveles (id_nivel)

);

