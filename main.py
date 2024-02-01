from flask import Flask, render_template, redirect, request, url_for, send_from_directory, flash
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from jinja2.exceptions import TemplateNotFound
from secrets import token_hex
from time import sleep
import smtplib
import os
from forms import RegistraServicio, LoginAdmin

app = Flask(__name__)
app.config["SECRET_KEY"] = token_hex(32)
ckeditor = CKEditor(app)

# -------------------- CONECTAR BASE DE DATOS -------------------- #
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///gestoria.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db = SQLAlchemy(app)

# -------------------- CONFIGURACIÓN ADMIN -------------------- #
MY_EMAIL = os.getenv("MY_EMAIL")
FROM_EMAIL = os.getenv("FROM_EMAIL")
PS = os.getenv("PS")

login_manager = LoginManager(app)
login_manager.login_view = "login_admin"


@login_manager.user_loader
def load_user(user_id):
    return Admin.get(user_id)


class Admin(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    @staticmethod
    def get(user_id):
        return Admin(user_id)


# -------------------- ESTRUCTURA DE LA BASE DE DATOS -------------------- #
class Servicio(db.Model):
    __tablename__ = "servicios"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    nombre = db.Column(db.String(250), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(250), nullable=False)
    requisitos = db.Column(db.String(4000), nullable=False)
    preguntas_relacionadas = relationship("Pregunta", back_populates="id_servicio")

    def __repr__(self):
        return f"<Servicio: {self.nombre}>"


class Pregunta(db.Model):
    __tablename__ = "preguntas"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    idServicio = db.Column(db.Integer, db.ForeignKey("servicios.id"), nullable=False)
    pregunta = db.Column(db.String(250), nullable=False)
    respuesta = db.Column(db.String(500), nullable=False)
    id_servicio = relationship("Servicio", back_populates="preguntas_relacionadas")

    def __repr__(self):
        return f"<Pregunta: {self.pregunta}>"


class Camioneta(db.Model):
    __tablename__ = "camionetas"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    marca = db.Column(db.String(250), nullable=False)
    modelo = db.Column(db.String(250), nullable=False)
    tipo = db.Column(db.String(250), nullable=False)
    color = db.Column(db.String(250), nullable=False)
    caja = db.Column(db.String(250), nullable=False)
    puertas = db.Column(db.Integer, nullable=False)
    cilindros = db.Column(db.Integer, nullable=False)
    transmision = db.Column(db.String(250), nullable=False)
    kilometraje = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    apartada = db.Column(db.Boolean, nullable=False)
    fotos_relacionadas = relationship("FotosCamioneta", back_populates="camioneta_relacionada")

    def __repr__(self):
        return f"<Camioneta: {self.id}, {self.marca}, {self.modelo}, {self.tipo}>"


class FotosCamioneta(db.Model):
    __tablename__ = "fotos_camionetas"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    nombre = db.Column(db.String(250))
    file_path = db.Column(db.String(500))
    id_camioneta = db.Column(db.Integer, db.ForeignKey("camionetas.id"), nullable=False)
    camioneta_relacionada = relationship("Camioneta", back_populates="fotos_relacionadas")

    def __repr__(self):
        return f"<Foto: {self.id} of {self.id_camioneta}>"


# with app.app_context():
#     db.create_all()
# -------------------- FUNCIONES DE APOYO -------------------- #
@app.template_filter()
def get_servicios(estado):
    return Servicio.query.filter_by(estado=estado).all()


@app.template_filter()
def get_api_key(name):
    return os.getenv(name)


# -------------------- RUTAS DE LA PAGINA -------------------- #
@app.route("/")
def home():
    return render_template("index.html", estado="")


@app.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")


# DEVUELVE LA PAGINA PARA CADA ESTADO
@app.route("/<estado>")
def current_estado(estado):
    try:
        return render_template(f"/estados/{estado}.html", estado=estado)
    except TemplateNotFound:
        return redirect(url_for("page_not_found", e=404))


# DEVUELVE EL SERVICIO DENTRO DEL ESTADO SELECCIONADO
@app.route("/<estado>/<nombre>")
def current_servicio(estado, nombre):
    try:
        servicio = Servicio.query.filter_by(estado=estado).filter_by(nombre=nombre.replace("-", " ")).first()
        preguntas_relacionadas = Pregunta.query.filter_by(idServicio=servicio.id).all()
        return render_template(f"/servicio-base.html", servicio=servicio, preguntas=preguntas_relacionadas)
    except TemplateNotFound:
        return redirect(url_for("page_not_found", e=404))


# -------------------- FUNCIONES DE ADMINISTRADOR -------------------- #
# AÑADIMOS UN NUEVO SERVICIO
@app.route("/admin/crear-servicio", methods=["GET", "POST"])
@login_required
def add_servicio():
    form = RegistraServicio()

    if form.validate_on_submit():
        nuevo_servicio = Servicio(nombre=form.nombre.data, estado=form.estado.data, icon=f"bi-{form.icon.data}",
                                  descripcion=form.descripcion.data, requisitos=form.requisitos.data)
        db.session.add(nuevo_servicio)
        db.session.commit()
        sleep(2)

        # Creamos las preguntas según el número de casillas marcadas
        check_data = request.form
        for n in range(1, 4):
            if check_data.get(f"usar{n}"):
                nueva_pregunta = Pregunta(idServicio=nuevo_servicio.id, pregunta=check_data.get(f"pregunta{n}"),
                                          respuesta=check_data.get(f"respuesta{n}"))
                db.session.add(nueva_pregunta)
        db.session.commit()

        # return redirect(url_for("current_servicio", estado=form.estado.data,
        #                         nombre="-".join(form.nombre.data.split(" "))))
        return redirect(url_for("current_estado", estado=form.estado.data))
    return render_template("formulario-servicio.html", form=form, editar_servicio=False)


# EDITA INFORMACIÓN DEL SERVICIO
@app.route("/admin/editar-servicio/<estado>/<int:s_id>", methods=["GET", "POST"])
@login_required
def editar_servicio(estado, s_id):
    servicio = Servicio.query.get(s_id)

    preguntas_relacionadas = Pregunta.query.filter_by(idServicio=s_id).all()
    preguntas, respuestas = ["", "", ""], ["", "", ""]

    if preguntas_relacionadas:
        i = 0
        for p in preguntas_relacionadas:
            preguntas[i] = p.pregunta
            respuestas[i] = p.respuesta
            i += 1

    form = RegistraServicio(nombre=servicio.nombre, estado=estado, icon=servicio.icon[3:],
                            descripcion=servicio.descripcion, requisitos=servicio.requisitos,
                            pregunta1=preguntas[0], respuesta1=respuestas[0],
                            pregunta2=preguntas[1], respuesta2=respuestas[1],
                            pregunta3=preguntas[2], respuesta3=respuestas[2])

    if form.validate_on_submit():
        # Actualizamos la información
        servicio.nombre = form.nombre.data
        servicio.estado = form.estado.data
        servicio.icon = f"bi-{form.icon.data}"
        servicio.descripcion = form.descripcion.data
        servicio.requisitos = form.requisitos.data

        check_preguntas = request.form
        for n in range(1, 4):
            # Modificamos las preguntas existentes
            if n <= len(preguntas_relacionadas) and check_preguntas.get(f"usar{n}"):
                preguntas_relacionadas[n-1].pregunta = check_preguntas.get(f"pregunta{n}")
                preguntas_relacionadas[n-1].respuesta = check_preguntas.get(f"respuesta{n}")

            # Eliminamos las preguntas no marcadas con la checkbox
            elif n <= len(preguntas_relacionadas) and not check_preguntas.get(f"usar{n}"):
                db.session.delete(preguntas_relacionadas[n-1])

            # Añadimos una nueva pregunta
            elif n > len(preguntas_relacionadas) and check_preguntas.get(f"usar{n}"):
                nueva_pregunta = Pregunta(idServicio=servicio.id, pregunta=check_preguntas.get(f"pregunta{n}"),
                                          respuesta=check_preguntas.get(f"respuesta{n}"))
                db.session.add(nueva_pregunta)

        db.session.commit()

        return redirect(url_for("current_servicio", estado=estado,
                                nombre="-".join(servicio.nombre.split(" "))))
    return render_template("formulario-servicio.html", form=form, editar_servicio=True)


# Eliminamos el servicio
@app.route("/admin/eliminar/<estado>/<int:s_id>", methods=["POST"])
@login_required
def eliminar_servicio(estado, s_id):
    servicio_eliminado = Servicio.query.get(s_id)

    preguntas_eliminadas = Pregunta.query.filter_by(idServicio=s_id)
    if preguntas_eliminadas:
        for pregunta in preguntas_eliminadas:
            db.session.delete(pregunta)

    db.session.delete(servicio_eliminado)
    db.session.commit()

    return redirect(url_for("current_estado", estado=estado))


# Ingresar administrador
@app.route("/admin", methods=["GET", "POST"])
def login_admin():
    form = LoginAdmin()

    if form.validate_on_submit():
        if form.password.data == os.getenv("ADPS"):
            user = Admin(1)
            login_user(user, remember=True)
            return redirect(url_for("home"))
        flash("Contraseña incorrecta.")

    return render_template("login.html", form=form)


# Salir administrador
@app.route("/admin/salir")
def logout_admin():
    logout_user()
    return redirect(url_for("home"))

# -------------------- FIN DE ADMINISTRADOR -------------------- #


# Robots txt
@app.route("/robots.txt")
def robots_txt():
    return send_from_directory(app.static_folder, "robots.txt")


# Sitemap
@app.route("/sitemap.xml")
def sitemap_xml():
    return send_from_directory(app.static_folder, "sitemap.xml")


# Error 404
@app.route("/error/<e>")
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# FORMULARIO DE CONTACTO
@app.route("/contact-mail", methods=["POST"])
def send_mail():
    form_info = request.form
    text = f"From: Contacto Gestoría Vehicular JC\n" \
           f"Subject: {form_info.get('asunto')}.\n" \
           f"To {MY_EMAIL}\n" \
           f"Nombre: {form_info.get('name')}.\n" \
           f"Correo: {form_info.get('email')}" \
           f"Numero de teléfono: {form_info.get('phone')}.\n" \
           f"Mensaje:\n" \
           f"{form_info.get('message')}.".encode("utf-8")

    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(FROM_EMAIL, PS)
        connection.sendmail(from_addr=FROM_EMAIL,
                            to_addrs=MY_EMAIL,
                            msg=text)

    return redirect("/" + request.args["current_page"])


if __name__ == "__main__":
    app.run()
