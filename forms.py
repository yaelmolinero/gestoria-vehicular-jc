from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField

class RegistraServicio(FlaskForm):
    # Información del servicio
    nombre = StringField("Nombre del servicio:", [DataRequired()])
    estado = SelectField("Estado:", [DataRequired()],
                         choices=["Seleccionar...", "edomex", "cdmx", "morelos", "guerrero", "chiapas"])
    icon = StringField("Código del icono:", [DataRequired()])
    descripcion = StringField("Descripción del servicio:", [DataRequired()])
    requisitos = CKEditorField("Escribe los requisitos:", [DataRequired()])

    # Información para las preguntas frecuentes
    pregunta1 = StringField("Pregunta 1 (Opcional)")
    respuesta1 = CKEditorField("Respuesta 1 (Opcional)")
    pregunta2 = StringField("Pregunta 2 (Opcional)")
    respuesta2 = CKEditorField("Respuesta 2 (Opcional)")
    pregunta3 = StringField("Pregunta 3 (Opcional)")
    respuesta3 = CKEditorField("Respuesta 3 (Opcional)")
    submit = SubmitField("Guardar")

class LoginAdmin(FlaskForm):
    password = PasswordField("Contraseña:", [DataRequired()])
    submit = SubmitField("Ingresar")
