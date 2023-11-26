from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

# Configurar conexion a la base de datos
# definir variables de la bd
USER_DB = "postgres"
PASS_DB = "admin"
URL_DB = "localhost"
NAME_DB = "escuela"

# Crear una cadena de conexion completa para la bd
FULL_URL_DB = f"postgresql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}"

# Configurar las variables para que SQLAlchemy funcione con Flask
app.config["SQLALCHEMY_DATABASE_URI"] = FULL_URL_DB
app.config[
    "SQLALCHEMY_TRACK_MODIFICATION"
] = False  # Evitar el seguimiento de modificaciones para un mejor rendimiento
app.config["SECRET_KEY"] = "llave_secreta"


# Inicializar el objeto db
db = SQLAlchemy(app)


# configurar Flask-Migrate
migrate = Migrate()
migrate.init_app(app, db)


class Profesor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250))
    apellido = db.Column(db.String(250))
    edad = db.Column(db.Integer)
    email = db.Column(db.String(250))
    materia = db.Column(db.String(250))
    grado = db.Column(db.String(250))

    # Relacion de uno a muchos
    alumnos = db.relationship("Alumno", back_populates="profesor")

    def __str__(self):
        return (
            f"Id:{self.id}, "
            f"Nombre:{self.nombre}, "
            f"Apellido:{self.apellido}, "
            f"Edad:{self.edad}, "
            f"Email:{self.email}, "
            f"Materia:{self.materia}, "
            f"Grado:{self.grado}"
        )


class Alumno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250))
    apellido = db.Column(db.String(250))
    edad = db.Column(db.Integer)

    # Relación con Profesor
    profesor_id = db.Column(db.Integer, db.ForeignKey("profesor.id"))
    profesor = db.relationship("Profesor", back_populates="alumnos")

    def __str__(self):
        return (
            f"Id:{self.id}, "
            f"Nombre:{self.nombre}, "
            f"Apellido:{self.apellido}, "
            f"Edad:{self.edad}, "
        )


class ProfesorForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    apellido = StringField("Apellido")
    edad = IntegerField("Edad")
    email = StringField("Email")
    materia = StringField("Materia")
    grado = StringField("Grado")
    enviar = SubmitField("Agregar")


class AlumnoForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    apellido = StringField("Apellido")
    edad = IntegerField("Edad")
    profesor_id = StringField("Profesor")
    enviar = SubmitField("Agregar")


@app.route("/")
def index():
    # listado de profesores
    # profesores = Profesor.query.all()
    profesores = Profesor.query.order_by("id")
    total = Profesor.query.count()
    return render_template("index.html", profesores=profesores, total=total)


@app.route("/alumnos")
def alumnos():
    # listado de profesores
    # profesores = Profesor.query.all()
    alumnos = Alumno.query.order_by("id")
    total = Alumno.query.count()
    return render_template("listado_alumnos.html", alumnos=alumnos, total=total)


@app.route("/ver/<int:id>")
def ver_detalle(id):
    # Recupera el profesor segun el id proporcionado
    # profesor = Profesor.query.get(id)
    profesor = Profesor.query.get_or_404(id)
    return render_template("detalle.html", profesor=profesor)


@app.route("/ver_alumno/<int:id>")
def ver_alumno(id):
    # Recupera el alumno segun el id proporcionado
    alumno = Alumno.query.get_or_404(id)
    return render_template("detalle_alumno.html", alumno=alumno)


@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    profesor = Profesor()
    profesorForm = ProfesorForm(obj=profesor)
    if request.method == "POST":
        if profesorForm.validate_on_submit():
            profesorForm.populate_obj(profesor)
            # Insertar a la bd
            db.session.add(profesor)
            db.session.commit()
            print(f"Persona a insertar: {profesor}")
            return redirect(url_for("index"))
    return render_template("formulario_profesor.html", form=profesorForm)


@app.route("/agregar_alumno", methods=["GET", "POST"])
def agregar_alumno():
    alumno = Alumno()
    alumnoForm = AlumnoForm(obj=alumno)

    # obtener la lista de profesores para el select
    profesores = Profesor.query.all()
    if request.method == "POST":
        if alumnoForm.validate_on_submit():
            alumnoForm.populate_obj(alumno)

            # Obtener el ID del profesor seleccionado desde el formulario
            profesor_id = request.form.get("profesor_id")

            # Recuperar el objeto profesor
            profesor = Profesor.query.get(profesor_id)

            # Asignar el profesor al alumno
            alumno.profesor = profesor

            # Insertar a la bd
            db.session.add(alumno)
            db.session.commit()
            print(f"Persona a insertar: {alumno}")
            return redirect(url_for("alumnos"))
    return render_template(
        "insertar_alumno.html", form=alumnoForm, profesores=profesores
    )


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    # Recuperar el profesor segun su id
    profesor = Profesor.query.get_or_404(id)
    profesorForm = ProfesorForm(obj=profesor)
    if request.method == "POST":
        if profesorForm.validate_on_submit():
            profesorForm.populate_obj(profesor)
            # Insertar a la bd
            db.session.commit()
            print(f"Persona a Editar: {profesor}")
            return redirect(url_for("index"))
    return render_template("editar.html", form=profesorForm)


@app.route("/editar_alumno/<int:id>", methods=["GET", "POST"])
def editar_alumno(id):
    alumno = Alumno.query.get_or_404(id)
    alumnoForm = AlumnoForm(obj=alumno)

    # obtener la lista de profesores para el select
    profesores = Profesor.query.all()
    alumnoForm.profesor_id.choice = [
        (profesor.id, profesor.nombre) for profesor in profesores
    ]
    if request.method == "POST":
        if alumnoForm.validate_on_submit():
            alumnoForm.populate_obj(alumno)

            # Obtener el ID del profesor seleccionado desde el formulario
            profesor_id = request.form.get("profesor_id")

            # Recuperar el objeto profesor
            profesor = Profesor.query.get(profesor_id)

            # Asignar el profesor al alumno
            alumno.profesor = profesor

            # Insertar a la bd
            db.session.commit()
            print(f"Persona a insertar: {alumno}")
            return redirect(url_for("alumnos"))
    return render_template(
        "editar_alumno.html", form=alumnoForm, profesores=profesores, alumno=alumno
    )


@app.route("/eliminar/<int:id>", methods=["GET"])
def eliminar(id):
    profesor = Profesor.query.get_or_404(id)
    db.session.delete(profesor)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/eliminar_alumno/<int:id>", methods=["GET"])
def eliminar_alumno(id):
    alumno = Alumno.query.get_or_404(id)
    db.session.delete(alumno)
    db.session.commit()
    return redirect(url_for("alumnos"))


if __name__ == "__main__":
    app.run(debug=True)
