from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import psycopg2
from flask_cors import CORS
import os

#hola
app = Flask(__name__)
CORS(app)

# Conexión a PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT") 
    )

# Ruta para registrar estudiante
@app.route('/registrar_estudiante', methods=['POST'])
def registrar_estudiante():
    data = request.get_json()
    nombre = data.get('nombre')
    apP = data.get('apP')
    apM = data.get('apM')
    ci = data.get('ci')

    if not (nombre and apP and apM and ci):
        return jsonify({'mensaje': 'Datos incompletos'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO estudiantes (nombre, apellido_paterno, apellido_materno, ci)
            VALUES (%s, %s, %s, %s)
        """, (nombre, apP, apM, ci))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'mensaje': 'Estudiante registrado correctamente'}), 200

    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'mensaje': 'El CI ya existe, registro duplicado'}), 409

    except Exception as e:
        return jsonify({'mensaje': f'Error: {str(e)}'}), 500

#registrar maestro
@app.route('/registrar_maestro', methods=['POST'])
def registrar_maestro():
    data = request.get_json()
    nombre = data.get('nombre')
    apP = data.get('apP')
    apM = data.get('apM')
    ci = data.get('ci')
    asignatura = data.get('asignatura') 

    if not (nombre and apP and apM and ci):
        return jsonify({'mensaje': 'Datos incompletos'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO maestros (nombre, apellido_paterno, apellido_materno, ci)
            VALUES (%s, %s, %s, %s)
            RETURNING id_maestro

        """, (nombre, apP, apM, ci))
        id_maestro = cur.fetchone()[0]

        # Insertar asignatura vinculada al maestro
        if asignatura:
            cur.execute("""
                INSERT INTO asignaturas (nombre, id_maestro)
                VALUES (%s, %s)
             """, (asignatura, id_maestro))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'mensaje': 'Maestro registrado correctamente'}), 200

    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'mensaje': 'El CI ya existe, registro duplicado'}), 409

    except Exception as e:
        return jsonify({'mensaje': f'Error: {str(e)}'}), 500

#ver estudiantes

@app.route('/ver_estudiantes', methods=['GET'])
def ver_estudiantes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nombre, apellido_paterno, apellido_materno, ci FROM estudiantes ORDER BY apellido_paterno")
    rows = cur.fetchall()
    estudiantes = []
    for row in rows:
        estudiantes.append({
            'nombre': row[0],
            'apP': row[1],
            'apM': row[2],
            'ci': row[3]
        })
    cur.close()
    conn.close()
    return jsonify({'estudiantes': estudiantes})



@app.route('/ver_maestros_asignaturas')
def ver_maestros_asignaturas():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT m.nombre, m.apellido_paterno, m.apellido_materno, m.ci, a.nombre
        FROM maestros m
        JOIN asignaturas a ON m.id_maestro = a.id_maestro
        ORDER BY m.apellido_paterno, m.apellido_materno
    """)
    
    datos = cur.fetchall()
    cur.close()
    conn.close()

    # Transformamos a lista de diccionarios
    maestros = []
    for fila in datos:
        maestros.append({
            "nombre": fila[0],
            "apP": fila[1],
            "apM": fila[2],
            "ci": fila[3],
            "asignatura": fila[4]
        })

    return jsonify(maestros=maestros)



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data.get('username')
    contrasena = data.get('password')

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT usuario, rol, estado 
        FROM usuarios 
        WHERE usuario = %s AND contrasena = %s
    """, (usuario, contrasena))

    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        if user[2]:  # estado = TRUE
            return jsonify({"success": True, "rol": user[1]})
        else:
            return jsonify({"success": False, "error": "Usuario inactivo"})
    else:
        return jsonify({"success": False, "error": "Credenciales incorrectas"})




@app.route('/eliminar_estudiante/<ci>', methods=['DELETE'])
def eliminar_estudiante(ci):
    try:
        
        cur = conn.cursor()

        # Borra al estudiante por CI (debes tener FK de personas a estudiantes)
        cur.execute("DELETE FROM estudiantes WHERE ci = %s", (ci,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'mensaje': 'Estudiante eliminado correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/editar_estudiante/<ci_original>', methods=['PUT'])
def editar_estudiante(ci_original):
    try:
        data = request.get_json()
        nuevo_nombre = data['nombre']
        nuevo_apP = data['apP']
        nuevo_apM = data['apM']
        nuevo_ci = data['ci']

        
        cur = conn.cursor()

        # Actualiza los datos en la tabla personas
        cur.execute("""
            UPDATE estudiantes
            SET nombre = %s, apellido_paterno = %s, apellido_materno = %s, ci = %s
            WHERE ci = %s
        """, (nuevo_nombre, nuevo_apP, nuevo_apM, nuevo_ci, ci_original))
        
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'mensaje': 'Estudiante actualizado correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/guardar_nota', methods=['POST'])
def guardar_nota():
    data = request.get_json()
    id_estudiante = data.get('id_estudiante')
    nombre_asignatura = data.get('id_asignatura')  
    nota = data.get('nota')
    trimestre = data.get('trimestre')

    if not (id_estudiante and nombre_asignatura and nota and trimestre):
        return jsonify({'mensaje': 'Datos incompletos'}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Buscar el ID de la asignatura a partir del nombre
        cur.execute("SELECT id_asignatura FROM asignaturas WHERE nombre = %s", (nombre_asignatura,))
        resultado = cur.fetchone()
        if not resultado:
            cur.close()
            conn.close()
            return jsonify({'mensaje': 'Asignatura no encontrada'}), 404
        id_asignatura = resultado[0]

        # Insertar la nota
        cur.execute("""
            INSERT INTO calificaciones (id_estudiante, id_asignatura, nota, trimestre)
            VALUES (%s, %s, %s, %s)
        """, (id_estudiante, id_asignatura, nota, trimestre))

        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'mensaje': 'Nota guardada correctamente'}), 200

    except Exception as e:
        return jsonify({'mensaje': f'Error: {str(e)}'}), 500
    
@app.route('/ver_notas', methods=['GET'])
def ver_notas():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            e.nombre,
            e.apellido_paterno AS apP,
            e.apellido_materno AS apM,
            e.ci,
            a.nombre AS materia,
            c.nota
        FROM estudiantes e
        JOIN calificaciones c ON e.id_estudiante = c.id_estudiante
        JOIN asignaturas a ON c.id_asignatura = a.id_asignatura
        WHERE a.id_asignatura = 7; 
    """)
    rows = cur.fetchall()
    estudiantes = []
    for row in rows:
        estudiantes.append({
            "nombre": row[0],
            "apP": row[1],
            "apM": row[2],
            "ci": row[3],
            "materia": row[4],
            "nota": row[5]
        })
    cur.close()
    conn.close()
    return jsonify({"estudiantes": estudiantes})



    
if __name__ == '__main__':
    app.run(debug=True)
