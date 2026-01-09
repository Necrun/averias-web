# app/models.py - VERSIÓN COMPLETA CON GRÁFICOS
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "avisos.db")

def get_connection():
    """Obtiene una conexión a la base de datos"""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Inicializa la base de datos con la estructura completa"""
    conn = get_connection()
    c = conn.cursor()
    
    # Crear tabla de avisos
    c.execute("""
    CREATE TABLE IF NOT EXISTS avisos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        zona TEXT,
        titulo TEXT,
        texto TEXT,
        tipo INTEGER DEFAULT 0,
        ubicacion_tecnica TEXT,
        descripcion TEXT,
        usuario_subida TEXT,
        fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Crear tabla de usuarios
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT NOT NULL DEFAULT 'lector',
        nombre TEXT,
        email TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
    
    # Crear usuario admin por defecto
    init_users()
    print("✅ Base de datos inicializada con estructura completa")

def insertar_aviso(fecha, zona, titulo, texto, tipo=0, ubicacion="", descripcion=""):
    """Inserta un nuevo aviso en la base de datos"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO avisos (fecha, zona, titulo, texto, tipo, ubicacion_tecnica, descripcion)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (fecha, zona, titulo, texto, tipo, ubicacion, descripcion))
    conn.commit()
    conn.close()

def obtener_avisos():
    """Obtiene todos los avisos ordenados por fecha descendente"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT id, fecha, zona, titulo, texto, tipo, ubicacion_tecnica, descripcion 
    FROM avisos 
    ORDER BY fecha DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def obtener_aviso(id):
    """Obtiene un aviso específico por su ID"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT id, fecha, zona, titulo, texto, tipo, ubicacion_tecnica, descripcion 
    FROM avisos 
    WHERE id=?
    """, (id,))
    row = c.fetchone()
    conn.close()
    return row

def obtener_avisos_por_zona():
    """Obtiene todos los avisos agrupados por zona"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""
        SELECT id, fecha, zona, titulo, tipo, ubicacion_tecnica 
        FROM avisos 
        ORDER BY fecha DESC
    """)
    
    rows = c.fetchall()
    conn.close()
    
    avisos_por_zona = {}
    
    for row in rows:
        zona = row[2]
        if zona not in avisos_por_zona:
            avisos_por_zona[zona] = []
        
        avisos_por_zona[zona].append({
            'id': row[0],
            'fecha': row[1],
            'titulo': row[3],
            'tipo': row[4],
            'ubicacion': row[5]
        })
    
    return dict(sorted(avisos_por_zona.items()))

def obtener_historico_anual(year=None, zona=None, tipo=None):
    """Obtiene histórico de avisos agrupado por zona y mes"""
    conn = get_connection()
    c = conn.cursor()
    
    query = """
        SELECT id, fecha, zona, titulo, tipo, ubicacion_tecnica 
        FROM avisos 
        WHERE 1=1
    """
    params = []
    
    if year:
        query += " AND fecha LIKE ?"
        params.append(f"{year}-%")
    
    if zona:
        query += " AND zona = ?"
        params.append(zona)
    
    if tipo:
        query += " AND tipo = ?"
        params.append(int(tipo))
    
    query += " ORDER BY fecha DESC"
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    historico = {}
    
    for row in rows:
        aviso = {
            'id': row[0],
            'fecha': row[1],
            'zona': row[2],
            'titulo': row[3],
            'tipo': row[4],
            'ubicacion': row[5]
        }
        
        zona_nombre = row[2]
        fecha = row[1]
        
        # Extraer mes
        if fecha and '-' in fecha:
            try:
                fecha_obj = datetime.strptime(fecha[:10], "%Y-%m-%d")
                mes_nombre = fecha_obj.strftime("%B %Y").capitalize()
                meses_es = {
                    'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
                    'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
                    'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
                    'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
                }
                for eng, esp in meses_es.items():
                    mes_nombre = mes_nombre.replace(eng, esp)
            except:
                mes_nombre = "Sin fecha"
        else:
            mes_nombre = "Sin fecha"
        
        if zona_nombre not in historico:
            historico[zona_nombre] = {}
        
        if mes_nombre not in historico[zona_nombre]:
            historico[zona_nombre][mes_nombre] = []
        
        historico[zona_nombre][mes_nombre].append(aviso)
    
    return historico

def obtener_estadisticas_historico(year=None):
    """Obtiene estadísticas del histórico"""
    conn = get_connection()
    c = conn.cursor()
    
    # Total avisos
    if year:
        c.execute("SELECT COUNT(*) FROM avisos WHERE fecha LIKE ?", (f"{year}-%",))
    else:
        c.execute("SELECT COUNT(*) FROM avisos")
    total_avisos = c.fetchone()[0]
    
    # Total zonas únicas
    if year:
        c.execute("SELECT COUNT(DISTINCT zona) FROM avisos WHERE fecha LIKE ?", (f"{year}-%",))
    else:
        c.execute("SELECT COUNT(DISTINCT zona) FROM avisos")
    total_zonas = c.fetchone()[0]
    
    # Zona con más averías
    if year:
        c.execute("""
            SELECT zona, COUNT(*) as count 
            FROM avisos 
            WHERE fecha LIKE ? 
            GROUP BY zona 
            ORDER BY count DESC 
            LIMIT 1
        """, (f"{year}-%",))
    else:
        c.execute("""
            SELECT zona, COUNT(*) as count 
            FROM avisos 
            GROUP BY zona 
            ORDER BY count DESC 
            LIMIT 1
        """)
    zona_mas_result = c.fetchone()
    zona_mas_activa = zona_mas_result[0] if zona_mas_result else "Ninguna"
    
    # Promedio por mes
    if year:
        c.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT strftime('%m', fecha)) as meses
            FROM avisos 
            WHERE fecha LIKE ?
        """, (f"{year}-%",))
    else:
        c.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT strftime('%Y-%m', fecha)) as meses
            FROM avisos
        """)
    avg_result = c.fetchone()
    if avg_result and avg_result[1] > 0:
        promedio_mes = avg_result[0] / avg_result[1]
    else:
        promedio_mes = 0
    
    conn.close()
    
    return {
        'total_avisos': total_avisos,
        'total_zonas': total_zonas,
        'zona_mas_activa': zona_mas_activa,
        'promedio_mes': promedio_mes
    }

def obtener_estadisticas_graficos(year=None, zona=None):
    """Obtiene datos para gráficos estadísticos"""
    conn = get_connection()
    c = conn.cursor()
    
    where_clause = "WHERE 1=1"
    params = []
    
    if year:
        where_clause += " AND fecha LIKE ?"
        params.append(f"{year}-%")
    
    if zona:
        where_clause += " AND zona = ?"
        params.append(zona)
    
    # 1. AVERÍAS POR ZONA
    c.execute(f"""
        SELECT zona, COUNT(*) as total 
        FROM avisos 
        {where_clause}
        GROUP BY zona 
        ORDER BY total DESC
        LIMIT 10
    """, params)
    
    zonas_data = c.fetchall()
    zonas_labels = [row[0] for row in zonas_data]
    zonas_totales = [row[1] for row in zonas_data]
    
    # 2. EVOLUCIÓN MENSUAL
    c.execute(f"""
        SELECT 
            strftime('%Y-%m', fecha) as mes,
            COUNT(*) as total
        FROM avisos 
        {where_clause}
        GROUP BY strftime('%Y-%m', fecha)
        ORDER BY mes
        LIMIT 12
    """, params)
    
    meses_data = c.fetchall()
    meses_labels = [row[0] for row in meses_data]
    meses_totales = [row[1] for row in meses_data]
    
    # 3. DISTRIBUCIÓN POR TIPO
    c.execute(f"""
        SELECT 
            CASE 
                WHEN tipo = 20 THEN 'Preventivo'
                WHEN tipo = 30 THEN 'Avería'
                WHEN tipo = 60 THEN 'General'
                ELSE 'Otro'
            END as tipo_nombre,
            COUNT(*) as total
        FROM avisos 
        {where_clause}
        GROUP BY tipo
        ORDER BY total DESC
    """, params)
    
    tipos_data = c.fetchall()
    tipos_labels = [row[0] for row in tipos_data]
    tipos_totales = [row[1] for row in tipos_data]
    
    # 4. ESTADÍSTICAS CLAVE (KPIs)
    c.execute(f"""
        SELECT 
            COUNT(*) as total_avisos,
            COUNT(DISTINCT zona) as zonas_activas,
            COUNT(DISTINCT strftime('%Y-%m', fecha)) as meses_activos,
            ROUND(AVG(
                CASE 
                    WHEN tipo = 30 THEN 1 
                    ELSE 0 
                END
            ) * 100, 1) as porcentaje_averias
        FROM avisos 
        {where_clause}
    """, params)
    
    kpis = c.fetchone()
    
    conn.close()
    
    return {
        'zonas': {
            'labels': zonas_labels,
            'data': zonas_totales
        },
        'meses': {
            'labels': meses_labels,
            'data': meses_totales
        },
        'tipos': {
            'labels': tipos_labels,
            'data': tipos_totales
        },
        'kpis': {
            'total_avisos': kpis[0] if kpis else 0,
            'zonas_activas': kpis[1] if kpis else 0,
            'meses_activos': kpis[2] if kpis else 0,
            'porcentaje_averias': kpis[3] if kpis else 0
        }
    }

def obtener_top_problemas(limit=10):
    """Obtiene los problemas más comunes"""
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("""
        SELECT titulo, COUNT(*) as frecuencia
        FROM avisos
        WHERE tipo = 30  -- Solo averías
        GROUP BY titulo
        HAVING COUNT(*) > 1
        ORDER BY frecuencia DESC
        LIMIT ?
    """, (limit,))
    
    problemas = c.fetchall()
    
    conn.close()
    
    problemas_procesados = []
    for titulo, frecuencia in problemas:
        palabras = titulo.lower().split()
        palabras_clave = [p for p in palabras if len(p) > 4 and p not in ['avería', 'preventivo', 'general', 'aviso', 'plan', 'cnf']]
        
        problemas_procesados.append({
            'titulo': titulo[:50] + '...' if len(titulo) > 50 else titulo,
            'frecuencia': frecuencia,
            'palabras_clave': palabras_clave[:3]
        })
    
    return problemas_procesados

def buscar_avisos(q='', zona='', tipo='', fecha_desde='', fecha_hasta='', limit=20, offset=0):
    """Busca avisos con múltiples filtros"""
    conn = get_connection()
    c = conn.cursor()
    
    query = """
        SELECT id, fecha, zona, titulo, texto, tipo, ubicacion_tecnica 
        FROM avisos 
        WHERE 1=1
    """
    params = []
    
    if q:
        query += " AND (titulo LIKE ? OR texto LIKE ? OR descripcion LIKE ?)"
        term = f"%{q}%"
        params.extend([term, term, term])
    
    if zona:
        query += " AND zona = ?"
        params.append(zona)
    
    if tipo:
        query += " AND tipo = ?"
        params.append(int(tipo))
    
    if fecha_desde:
        query += " AND fecha >= ?"
        params.append(fecha_desde)
    
    if fecha_hasta:
        query += " AND fecha <= ?"
        params.append(f"{fecha_hasta} 23:59:59")
    
    query += " ORDER BY fecha DESC"
    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    c.execute(query, params)
    rows = c.fetchall()
    
    count_query = query.replace("LIMIT ? OFFSET ?", "")
    count_params = params[:-2]
    
    c.execute(f"SELECT COUNT(*) FROM ({count_query})", count_params)
    total = c.fetchone()[0]
    
    conn.close()
    
    resultados = []
    for row in rows:
        texto_completo = row[4]
        texto_resumen = texto_completo[:200] + "..." if len(texto_completo) > 200 else texto_completo
        
        resultados.append({
            'id': row[0],
            'fecha': row[1],
            'zona': row[2],
            'titulo': row[3],
            'texto_completo': texto_completo,
            'texto_resumen': texto_resumen,
            'tipo': row[5],
            'ubicacion': row[6]
        })
    
    return {
        'resultados': resultados,
        'total': total
    }

def obtener_sugerencias_busqueda(q):
    """Genera sugerencias de búsqueda basadas en términos comunes"""
    if not q or len(q) < 2:
        return []
    
    conn = get_connection()
    c = conn.cursor()
    
    sugerencias = []
    
    c.execute("""
        SELECT DISTINCT titulo 
        FROM avisos 
        WHERE titulo LIKE ? 
        LIMIT 5
    """, (f"%{q}%",))
    
    titulos = c.fetchall()
    for titulo in titulos:
        if len(titulo[0]) > 10:
            palabras = titulo[0].split()
            for palabra in palabras:
                if len(palabra) > 4 and palabra.lower() not in sugerencias:
                    sugerencias.append(palabra.lower())
    
    c.execute("""
        SELECT DISTINCT zona 
        FROM avisos 
        WHERE zona LIKE ? 
        LIMIT 3
    """, (f"%{q}%",))
    
    zonas = c.fetchall()
    for zona in zonas:
        if zona[0] and zona[0].lower() not in sugerencias:
            sugerencias.append(zona[0].lower())
    
    conn.close()
    
    return list(set(sugerencias))[:5]

def procesar_pdf_y_guardar(ruta_pdf, usuario_id=None):
    """Procesa un PDF y guarda todos sus avisos en la base de datos"""
    from app.pdf_reader import extraer_avisos_de_pdf
    from app.zones import detectar_zona_general
    
    avisos = extraer_avisos_de_pdf(ruta_pdf)
    resultados = []
    
    print(f"\n📊 PROCESANDO PDF: {ruta_pdf}")
    print(f"📋 Se encontraron {len(avisos)} avisos")
    
    # Obtener nombre de usuario si hay ID
    usuario_nombre = None
    if usuario_id:
        usuario = obtener_usuario_por_id(usuario_id)
        if usuario:
            usuario_nombre = usuario['username']
    
    for i, aviso in enumerate(avisos):
        if i < 2:
            print(f"\n{'='*60}")
            print(f"📄 AVISO {i+1}:")
            print(f"📍 Ubicación: {aviso.get('ubicacion', 'N/D')}")
            print(f"📝 Descripción ubicación: {aviso.get('desc_ubicacion', 'N/D')}")
            print(f"📌 Título: {aviso.get('titulo', 'N/D')}")
            print(f"🏷️  Tipo: {aviso.get('tipo', 'N/D')}")
            print(f"📅 Fecha: {aviso.get('fecha', 'N/D')}")
            print(f"{'='*60}")
        
        fecha_sql = ""
        if aviso.get('fecha'):
            try:
                fecha_obj = datetime.strptime(aviso['fecha'], "%d.%m.%Y %H:%M")
                fecha_sql = fecha_obj.strftime("%Y-%m-%d %H:%M")
            except Exception as e:
                print(f"⚠️ Error convirtiendo fecha {aviso['fecha']}: {e}")
                fecha_sql = aviso['fecha']
        
        zona = detectar_zona_general(aviso.get('ubicacion', ''))
        
        texto_mostrar = f"📋 TIPO: {aviso.get('tipo', '')} - {aviso.get('tipo_desc', '')}\n"
        texto_mostrar += f"📍 UBICACIÓN: {aviso.get('ubicacion', '')}\n"
        texto_mostrar += f"🏭 DESCRIPCIÓN UBICACIÓN: {aviso.get('desc_ubicacion', '')}\n"
        texto_mostrar += f"🔢 Nº AVISO: {aviso.get('num_aviso', '')}\n"
        texto_mostrar += f"📄 Nº ORDEN: {aviso.get('num_orden', '')}\n"
        texto_mostrar += f"📊 ESTADO: {aviso.get('estado', '')}\n"
        texto_mostrar += f"👤 PERSONA: {aviso.get('persona', '')}\n"
        texto_mostrar += f"📅 FECHA COMPLETA: {aviso.get('fecha_completa', '')}\n"
        texto_mostrar += "─" * 40 + "\n\n"
        
        if aviso.get('texto_s'):
            texto_mostrar += f"🔧 **S (Situación):**\n{aviso['texto_s']}\n\n"
        if aviso.get('texto_o'):
            texto_mostrar += f"🔍 **O (Observación):**\n{aviso['texto_o']}\n\n"
        if aviso.get('texto_r'):
            texto_mostrar += f"🛠️  **R (Resolución):**\n{aviso['texto_r']}\n\n"
        if aviso.get('texto_a'):
            texto_mostrar += f"✅ **A (Acción):**\n{aviso['texto_a']}\n\n"
        
        if not any([aviso.get('texto_s'), aviso.get('texto_o'), aviso.get('texto_r'), aviso.get('texto_a')]):
            texto_mostrar += f"📝 **DESCRIPCIÓN:**\n{aviso.get('texto_completo', '')}\n"
        
        conn = get_connection()
        c = conn.cursor()
        
        c.execute("""
        INSERT INTO avisos (fecha, zona, titulo, texto, tipo, ubicacion_tecnica, descripcion, usuario_subida)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (fecha_sql, zona, aviso.get('titulo', ''), texto_mostrar, 
              aviso.get('tipo', 0), aviso.get('ubicacion', ''), aviso.get('desc_ubicacion', ''), usuario_nombre))
        
        nuevo_id = c.lastrowid
        conn.commit()
        conn.close()
        
        resultados.append({
            'id': nuevo_id,
            'titulo': aviso.get('titulo', ''),
            'zona': zona,
            'ubicacion': aviso.get('ubicacion', ''),
            'tipo': aviso.get('tipo', 0)
        })
    
    print(f"\n✅ SE INSERTARON {len(resultados)} AVISOS EN LA BASE DE DATOS")
    print(f"📁 Archivo procesado: {ruta_pdf}")
    if usuario_nombre:
        print(f"👤 Subido por: {usuario_nombre}")
    
    if resultados:
        zonas_unicas = set(r['zona'] for r in resultados)
        print(f"📍 Zonas encontradas: {', '.join(zonas_unicas)}")
    
    return resultados

def init_users():
    """Inserta el usuario admin por defecto si no existe"""
    import hashlib

    conn = get_connection()
    c = conn.cursor()

    password_hash = hashlib.sha256('admin123'.encode()).hexdigest()

    c.execute("""
        INSERT OR IGNORE INTO usuarios (username, password_hash, rol, nombre)
        VALUES (?, ?, ?, ?)
    """, ('admin', password_hash, 'admin', 'Administrador'))

    conn.commit()
    conn.close()

    print("✅ Usuario admin verificado/creado")


    # === FUNCIONES PARA USUARIOS ===
def crear_usuario(username, password, rol='lector', nombre='', email=''):
    """Crea un nuevo usuario"""
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO usuarios (username, password_hash, rol, nombre, email)
            VALUES (?, ?, ?, ?, ?)
        """, (username, password_hash, rol, nombre, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Usuario ya existe
    finally:
        conn.close()

def verificar_usuario(username, password):
    """Verifica las credenciales de un usuario"""
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, username, rol, nombre FROM usuarios 
        WHERE username = ? AND password_hash = ?
    """, (username, password_hash))
    
    usuario = c.fetchone()
    conn.close()
    
    if usuario:
        return {
            'id': usuario[0],
            'username': usuario[1],
            'rol': usuario[2],
            'nombre': usuario[3]
        }
    return None

def obtener_usuario_por_id(user_id):
    """Obtiene un usuario por su ID"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, rol, nombre FROM usuarios WHERE id = ?", (user_id,))
    
    usuario = c.fetchone()
    conn.close()
    
    if usuario:
        return {
            'id': usuario[0],
            'username': usuario[1],
            'rol': usuario[2],
            'nombre': usuario[3]
        }
    return None

def obtener_todos_usuarios():
    """Obtiene todos los usuarios (solo admin)"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, rol, nombre, email, fecha_registro FROM usuarios ORDER BY username")
    
    usuarios = []
    for row in c.fetchall():
        usuarios.append({
            'id': row[0],
            'username': row[1],
            'rol': row[2],
            'nombre': row[3],
            'email': row[4],
            'fecha_registro': row[5]
        })
    
    conn.close()
    return usuarios

def actualizar_rol_usuario(user_id, nuevo_rol):
    """Actualiza el rol de un usuario"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE usuarios SET rol = ? WHERE id = ?", (nuevo_rol, user_id))
    conn.commit()
    conn.close()
    return c.rowcount > 0

def eliminar_usuario(user_id):
    """Elimina un usuario"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return c.rowcount > 0

def obtener_heatmap_zona_mes(year=None, zona=None):
    """
    Devuelve datos para un heatmap por zona y mes (YYYY-MM)
    """
    conn = get_connection()
    c = conn.cursor()

    where = "WHERE 1=1"
    params = []

    if year:
        where += " AND fecha LIKE ?"
        params.append(f"{year}-%")

    if zona:
        where += " AND zona = ?"
        params.append(zona)

    c.execute(f"""
        SELECT
            zona,
            strftime('%Y-%m', fecha) AS mes,
            COUNT(*) as total
        FROM avisos
        {where}
        GROUP BY zona, mes
        ORDER BY zona, mes
    """, params)

    rows = c.fetchall()
    conn.close()

    zonas = sorted({r[0] for r in rows if r[0]})
    meses = sorted({r[1] for r in rows if r[1]})

    data = {z: {m: 0 for m in meses} for z in zonas}

    for z, m, t in rows:
        if z and m:
            data[z][m] = t

    return {
        "zonas": zonas,
        "meses": meses,
        "data": data
    }
def obtener_avisos_del_ultimo_pdf():
    """
    Devuelve todos los avisos correspondientes al último PDF cargado,
    usando un rango flexible de fechas (últimas 48h).
    """
    conn = get_connection()
    c = conn.cursor()

    # 1️⃣ Obtener la fecha más reciente
    c.execute("""
        SELECT fecha
        FROM avisos
        WHERE fecha IS NOT NULL AND fecha != ''
        ORDER BY fecha DESC
        LIMIT 1
    """)
    row = c.fetchone()

    if not row:
        conn.close()
        return []

    fecha_max = row[0][:10]  # YYYY-MM-DD

    # 2️⃣ Rango amplio y seguro: día actual + día anterior
    c.execute("""
        SELECT id, fecha, zona, titulo, texto, tipo, ubicacion_tecnica, descripcion
        FROM avisos
        WHERE fecha LIKE ? OR fecha LIKE ?
        ORDER BY fecha ASC
    """, (
        f"{fecha_max}%",
        f"{str(int(fecha_max[:4]))}-{fecha_max[5:7]}-{str(int(fecha_max[8:10]) - 1).zfill(2)}%"
    ))

    avisos = c.fetchall()
    conn.close()
    return avisos

