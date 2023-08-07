from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

# Flask Instances
app = Flask(__name__)

# Configs
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/system'
app.config['SECRET_KEY'] = "Automata"

# Init Database
db = SQLAlchemy(app)
app.config['SQLALCHEMY_BINDS'] = {
    'users': 'sqlite:///users.db',
    'medic_histories': 'sqlite:///medic_histories.db'
}
migrate = Migrate(app, db)

# Create Model
class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(120), nullable=False, unique=True)
    user_Type = db.Column(db.String(50))
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    ci = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.Integer)
    
    @property
    def password(self):
        raise AttributeError('La contraseña no es un atributo leible')

    @password.setter
    def password(self, password_passed):
        self.password_hash = generate_password_hash(password_passed)

    def verify_password(self, password_passed):
        return check_password_hash(self.password_hash, password_passed)


    def __repr__(self):
        return '<Name %r>' % self.name
    
class medic_histories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    ci = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.Integer)
    direction = db.Column(db.Text)
    motive = db.Column(db.Text, nullable=False)
    diseases = db.Column(db.Text, nullable=False)
    background = db.Column(db.Text, nullable=False)
    f_exam = db.Column(db.Text, nullable=False)
    diagnostic = db.Column(db.Text, nullable=False)
    therapy = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return '<Name %r>' % self.name    

# Create the database tables
with app.app_context():
    db.create_all()
    
# Session Management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))    

# Create Form Classes
class RegisterForm(FlaskForm):
    email = StringField("Correo", validators=[DataRequired(), Email()])
    password_hash = PasswordField("Contraseña", validators=[DataRequired(), EqualTo('password_hash2', message='Contraseñas deben coincidir')])
    password_hash2 = PasswordField("Confirmar contraseña", validators=[DataRequired()])
    user_type = StringField("Tipo de usuario", validators=[DataRequired()])
    name = StringField("Nombre", validators=[DataRequired()])
    lastname = StringField("Apellido", validators=[DataRequired()])
    ci = StringField("Cedula", validators=[DataRequired()]) 
    phone = StringField("Numero de telefono", validators=[DataRequired()])
    submit = SubmitField("Enviar")

class LoginForm(FlaskForm):
    email = StringField("Correo", validators=[DataRequired(), Email()])
    password_hash = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Enviar")    

class MedicForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired()])
    lastname = StringField("Apellido", validators=[DataRequired()])
    age = IntegerField("Edad", validators=[DataRequired()])
    ci = StringField("Cédula", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    phone = StringField("Numero de telefono", validators=[DataRequired()])
    direction = TextAreaField("Dirección", validators=[DataRequired()]) 
    motive = TextAreaField("Motivo de Consulta", validators=[DataRequired()])
    diseases = TextAreaField("Enfermedades Actuales", validators=[DataRequired()])
    background = TextAreaField("Antecedentes Medicos", validators=[DataRequired()])
    f_exam = TextAreaField("Examen Fisico", validators=[DataRequired()])
    diagnostic = TextAreaField("Diagnostico", validators=[DataRequired()])
    therapy = TextAreaField("Plan Terapeutico", validators=[DataRequired()])
    submit = SubmitField("Enviar")

# Routes

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    email = None
    password_hash = None
    user_type = None
    name = None
    lastname = None
    ci = None
    phone = None
        
    form = RegisterForm()
    if form.validate_on_submit():
        user = users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash Password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = users(email=form.email.data, password_hash=hashed_pw, user_Type=form.user_type.data, name=form.name.data, lastname=form.lastname.data, ci=form.ci.data, phone=form.phone.data)
            db.session.add(user)
            db.session.commit()
            
        email = form.email.data
        password_hash = form.password_hash.data
        user_type = form.user_type.data
        name = form.name.data
        lastname = form.lastname.data
        ci = form.ci.data
        phone = form.phone.data
        
        form.email.data = ''
        form.password_hash.data = ''  
        form.user_type.data = ''
        form.name.data = ''
        form.lastname.data = ''
        form.ci.data = ''
        form.phone.data = ''
        flash("Usuario registrado satisfactoriamente")      
    return render_template("add_user.html", form=form, email=email, password_hash=password_hash, user_type=user_type, name=name, lastname=lastname, ci=ci, phone=phone)

@app.route('/add_medic_history', methods=['GET', 'POST'])
def add_medic_history():
    name = None
    lastname = None
    age = None
    ci = None
    email = None
    phone = None
    direction = None
    motive = None
    diseases = None
    background = None
    f_exam = None
    diagnostic = None
    therapy = None       
    
    form = MedicForm()
    if form.validate_on_submit():
        history = medic_histories(name=form.name.data, lastname=form.lastname.data, age=form.age.data, ci=form.ci.data, email=form.email.data, phone=form.phone.data, direction=form.direction.data, motive=form.motive.data, diseases=form.diseases.data, background=form.background.data, f_exam=form.f_exam.data, diagnostic=form.diagnostic.data, therapy=form.therapy.data)
        db.session.add(history)
        db.session.commit()
     
        name=form.name.data 
        lastname=form.lastname.data
        age=form.age.data
        ci=form.ci.data
        email=form.email.data
        phone=form.phone.data
        direction=form.direction.data
        motive=form.motive.data
        diseases=form.diseases.data
        background=form.background.data
        f_exam=form.f_exam.data
        diagnostic=form.diagnostic.data
        therapy=form.therapy.data
        
        form.name.data = '' 
        form.lastname.data = '' 
        form.age.data = '' 
        form.ci.data = '' 
        form.email.data = '' 
        form.phone.data = '' 
        form.direction.data = '' 
        form.motive.data = '' 
        form.diseases.data = '' 
        form.background.data = '' 
        form.f_exam.data = '' 
        form.diagnostic.data = '' 
        form.therapy.data = '' 
        flash("Historia Registrada!")
        
    return render_template("add_medic_history.html", form=form, name=name, lastname=lastname, age=age, ci=ci, email=email, phone=phone, direction=direction, motive=motive, diseases=diseases, background=background, f_exam=f_exam, diagnostic=diagnostic, therapy=therapy)

@app.route('/display_histories')
def display_histories():
    our_histories = medic_histories.query.all()
    return render_template("display_histories.html", our_histories=our_histories)

@app.route('/display_users')
def display_users():
    our_users = users.query.all()
    return render_template("display_users.html", our_users=our_users)

@app.route('/update_users/<int:id>', methods=['GET', 'POST'])
def update_users(id):
    form = RegisterForm()
    user_to_update = users.query.get_or_404(id)
    if request.method == "POST":
        user_to_update.email = request.form['email']
        user_to_update.password_hash = request.form['password_hash']
        user_to_update.user_type = request.form['user_type']
        user_to_update.name = request.form['name']
        user_to_update.lastname = request.form['lastname']
        user_to_update.ci = request.form['ci']
        user_to_update.phone = request.form['phone']
        try:
            db.session.commit()
            flash("Usuario actualizado")
            return render_template("update_users.html", form=form, user_to_update=user_to_update)
        except:
            flash("Error de actualizacion de usuario")
            return render_template("update_users.html", form=form, user_to_update=user_to_update)
    else:
        return render_template("update_users.html", form=form, user_to_update=user_to_update)   

@app.route('/update_history/<int:id>', methods=['GET', 'POST'])
@login_required
def update_history(id):
    form = MedicForm()
    history_to_update = medic_histories.query.get_or_404(id)
    if request.method == "POST":
        history_to_update.email = request.form['email']
        history_to_update.age = request.form['age']
        history_to_update.ci = request.form['ci']
        history_to_update.name = request.form['name']
        history_to_update.lastname = request.form['lastname']
        history_to_update.phone = request.form['phone']
        history_to_update.direction = request.form['direction']
        history_to_update.motive = request.form['motive']
        history_to_update.diseases = request.form['diseases']
        history_to_update.background = request.form['background']
        history_to_update.f_exam = request.form['f_exam']
        history_to_update.diagnostic = request.form['diagnostic']
        history_to_update.therapy = request.form['therapy']
        
        try:
            db.session.commit()
            flash("Historia medica actualizada")
            return render_template("update_history.html", form=form, history_to_update=history_to_update)
        except:
            flash("Error de actualizacion de historia medica")
            return render_template("update_history.html", form=form, history_to_update=history_to_update)
    else:
        return render_template("update_history.html", form=form, history_to_update=history_to_update)        
    
@app.route('/delete_users/<int:id>')
def delete_users(id):
    user_to_delete = users.query.get_or_404(id)
    
    email = None
    password_hash = None
    user_type = None
    name = None
    lastname = None
    ci = None
    phone = None
        
    form = RegisterForm()
    
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("Usuario eliminado")
        our_users = users.query.order_by(users.email)      
        return render_template("add_user.html", form=form, email=email, password_hash=password_hash, user_type=user_type, name=name, lastname=lastname, ci=ci, phone=phone, our_users=our_users)
    except:
        flash("Error de eliminacion de usuario")
        return render_template("add_user.html", form=form, email=email, password_hash=password_hash, user_type=user_type, name=name, lastname=lastname, ci=ci, phone=phone, our_users=our_users)
    
@app.route('/delete_medic_histories/<int:id>')
@login_required
def delete_medic_histories(id):
    history_to_delete = medic_histories.query.get_or_404(id)
     
    name = None
    lastname = None
    age = None
    ci = None
    email = None
    phone = None
    direction = None
    motive = None
    diseases = None
    background = None
    f_exam = None
    diagnostic = None
    therapy = None       
    
    form = MedicForm()   

    try:
        db.session.delete(history_to_delete)
        db.session.commit()
        flash("Historia medica eliminada")
        our_histories = medic_histories.query.all()
        return render_template("display_histories.html", form=form, name=name, lastname=lastname, age=age, ci=ci, email=email, phone=phone, direction=direction, motive=motive, diseases=diseases, background=background, f_exam=f_exam, diagnostic=diagnostic, therapy=therapy, our_histories=our_histories)
    except:
        flash("Error de eliminacion de historia medica")
        return render_template("display_histories.html", form=form, name=name, lastname=lastname, age=age, ci=ci, email=email, phone=phone, direction=direction, motive=motive, diseases=diseases, background=background, f_exam=f_exam, diagnostic=diagnostic, therapy=therapy, our_histories=our_histories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password_hash.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash("Datos incorrectos")
        else:
            flash("Usuario inexistente")        
    return render_template("Login.html", form=form)    

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash("Fin the sesion")
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("dashboard.html")
        
# Errors
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Server Exception
@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

# Run the application
if __name__ == '__main__':
    app.run()