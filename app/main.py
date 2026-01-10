# app/main.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename

from app import models

# --------------------------------------------------
# CONFIGURACIÓN APP
# --------------------------------------------------
app = Flask(__name__)

# 🔑 SECRET KEY (OBLIGATORIO EN PRODUCCIÓN)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

UPLOAD_BASE = os.environ.get("UPLOAD_DIR", "/tmp/pdfs")
app.config["UPLOAD_FOLDER"] = UPLOAD_BASE

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

_db_initialized = False

@app.before_request
def init_db_once():
    global _db_initialized
    if not _db_initialized:
        models.init_db()
        _db_initialized = True


# --------------------------------------------------
# FILTROS JINJA
# --------------------------------------------------
@app.template_filter("format_fecha")
def format_fecha(fecha):
    if not fecha:
        return ""
    return fecha.split(" ")[0]

# --------------------------------------------------
# DECORADORES DE SEGURIDAD
# --------------------------------------------------
def requiere_login(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión", "info")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def requiere_rol(*roles):
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                flash("Debes iniciar sesión", "info")
                return redirect(url_for("login"))

            user = models.obtener_usuario_por_id(session["user_id"])
            if not user or user["rol"] not in roles:
                flash("No tienes permisos para acceder", "error")
                return redirect(url_for("index"))

            return f(*args, **kwargs)
        return decorated
    return decorator

# --------------------------------------------------
# AUTENTICACIÓN
# --------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = models.verificar_usuario(username, password)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["rol"] = user["rol"]
            session["nombre"] = user["nombre"]

            flash(f"Bienvenido {user['nombre']}", "success")
            return redirect(url_for("index"))
        else:
            flash("Usuario o contraseña incorrectos", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for("login"))


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        nombre = request.form.get("nombre", "")
        email = request.form.get("email", "")

        if len(username) < 3:
            flash("Usuario demasiado corto", "error")
        elif len(password) < 6:
            flash("Contraseña demasiado corta", "error")
        elif models.crear_usuario(username, password, "lector", nombre, email):
            flash("Usuario creado correctamente", "success")
            return redirect(url_for("login"))
        else:
            flash("El usuario ya existe", "error")

    return render_template("registro.html")

# --------------------------------------------------
# RUTAS PRINCIPALES
# --------------------------------------------------
@app.route("/")
@requiere_login
def index():
    avisos = models.obtener_avisos_del_ultimo_pdf()
    user = models.obtener_usuario_por_id(session["user_id"])
    return render_template("index.html", avisos=avisos, user=user)


@app.route("/aviso/<int:id>")
@requiere_login
def aviso(id):
    aviso = models.obtener_aviso(id)
    user = models.obtener_usuario_por_id(session["user_id"])
    return render_template("aviso.html", aviso=aviso, user=user)


@app.route("/zonas")
@requiere_login
def zonas():
    zonas = models.obtener_avisos_por_zona()
    totales = {z: len(v) for z, v in zonas.items()}
    user = models.obtener_usuario_por_id(session["user_id"])
    return render_template("zonas.html", zonas=zonas, totales=totales, user=user)


@app.route("/historico")
@requiere_login
def historico():
    year = request.args.get("year", "2025")
    zona = request.args.get("zona", "")
    tipo = request.args.get("tipo", "")

    data = models.obtener_historico_anual(year, zona, tipo)
    stats = models.obtener_estadisticas_historico(year)
    user = models.obtener_usuario_por_id(session["user_id"])

    return render_template(
        "historico.html",
        avisos_por_zona=data,
        estadisticas=stats,
        filtros={"year": year, "zona": zona, "tipo": tipo},
        user=user
    )

# --------------------------------------------------
# BUSCAR
# --------------------------------------------------
@app.route("/buscar")
@requiere_login
def buscar():
    q = request.args.get("q", "")
    zona = request.args.get("zona", "")
    tipo = request.args.get("tipo", "")
    fecha_desde = request.args.get("fecha_desde", "")
    fecha_hasta = request.args.get("fecha_hasta", "")
    pagina = int(request.args.get("pagina", 1))

    por_pagina = 20
    offset = (pagina - 1) * por_pagina

    resultados = None
    total = 0
    total_paginas = 0

    if request.args:
        data = models.buscar_avisos(
            q=q,
            zona=zona,
            tipo=tipo,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limit=por_pagina,
            offset=offset
        )
        resultados = data["resultados"]
        total = data["total"]
        total_paginas = (total + por_pagina - 1) // por_pagina

    user = models.obtener_usuario_por_id(session["user_id"])

    return render_template(
        "buscar.html",
        resultados=resultados,
        total_resultados=total,
        total_paginas=total_paginas,
        pagina=pagina,
        user=user
    )

# --------------------------------------------------
# GRÁFICOS
# --------------------------------------------------
@app.route("/graficos")
@requiere_login
def graficos():
    year = request.args.get("year", "")
    zona = request.args.get("zona", "")

    estadisticas = models.obtener_estadisticas_graficos(
        year=year if year else None,
        zona=zona if zona else None
    )

    problemas = models.obtener_top_problemas(limit=6)
    heatmap = models.obtener_heatmap_zona_mes(
        year=year if year else None,
        zona=zona if zona else None
    )

    user = models.obtener_usuario_por_id(session["user_id"])

    return render_template(
        "graficos.html",
        estadisticas=estadisticas,
        problemas=problemas,
        heatmap=heatmap,
        user=user
    )

# --------------------------------------------------
# SUBIR PDFs
# --------------------------------------------------
@app.route("/subir", methods=["GET", "POST"])
@requiere_rol("admin", "editor")
def subir_pdf():
    user = models.obtener_usuario_por_id(session["user_id"])

    if request.method == "POST":
        files = request.files.getlist("pdfs[]")

        if not files or files[0].filename == "":
            flash("No se seleccionó ningún PDF", "error")
            return redirect(request.url)

        total_pdfs = 0
        total_avisos = 0

        for file in files:
            if not file.filename.lower().endswith(".pdf"):
                continue

            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            file.save(filepath)
            resultados = models.procesar_pdf_y_guardar(filepath, session["user_id"])
            total_pdfs += 1
            total_avisos += len(resultados)

        flash(f"✅ {total_pdfs} PDF(s) procesados. {total_avisos} avisos añadidos.", "success")
        return redirect(url_for("index"))

    return render_template("subir.html", user=user)

# --------------------------------------------------
# PERFIL
# --------------------------------------------------
@app.route("/perfil")
@requiere_login
def perfil():
    user = models.obtener_usuario_por_id(session["user_id"])
    return render_template("perfil.html", user=user)

# --------------------------------------------------
# ARRANQUE
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

