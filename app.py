from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db' 
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui' 
db = SQLAlchemy(app)

# Configuración de Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo de Usuario
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Modelo de Tarea
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default="sin iniciar")
    created_at = db.Column(db.String(50), default=datetime.now().strftime("%Y-%m-%d"))
    deadline = db.Column(db.String(50))
    category = db.Column(db.String(50), default="Personal")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Cargar usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Crear la base de datos solo la primera vez
with app.app_context():
    db.create_all()

# - - - - - - - - End points - - - - - - - -
 
# Index endpoint
@app.route("/")
@login_required
def index():
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", todos = todos)

# Add endpoint
@app.route("/add", methods = ['POST'])
@login_required
def add():
    todo = request.form['todo']
    new_todo = Todo(
        task=todo,
        user_id=current_user.id,
        created_at=datetime.now().strftime("%Y-%m-%d"),
        deadline=request.form.get("deadline", ""),
        category=request.form.get("category", "Personal")
    )
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("index"))

# Edit endpoint
@app.route("/edit/<int:index>", methods = ['GET', 'POST'])
@login_required
def edit(index):
    todo = Todo.query.get_or_404(index)
    if request.method == "POST":
        todo.task = request.form["todo"]
        todo.deadline = request.form["deadline"]
        todo.category = request.form["category"]
        db.session.commit()
        return redirect(url_for("index"))
    else:
        return render_template("edit.html", todo = todo, index = index)
    
# Check task endpoint
@app.route("/check/<int:index>")
@login_required
def check(index):
    todo = Todo.query.get_or_404(index)
    todo.done = not todo.done
    db.session.commit()
    return redirect(url_for('index'))

# Delete task endpoint
@app.route("/delete/<int:index>")
@login_required
def delete(index):
    todo = Todo.query.get_or_404(index)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))

# Change status task endpoint
@app.route("/change_status/<int:index>", methods=['POST'])
@login_required
def change_status(index):
    todo = Todo.query.get_or_404(index)
    new_status = request.form['status']
    todo.status = new_status
    db.session.commit()
    return redirect(url_for('index'))

# New users endpoint
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso.', 'error')
            return redirect(url_for('register'))

        # Crear nuevo usuario con contraseña hasheada
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        flash('Registro exitoso. Por favor, inicia sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login endpoint
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'error')

    return render_template('login.html')


# Logout endpoint
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('login'))

# API: Todos endpoint
@app.route("/api/todos", methods=["GET"])
@login_required
def api_todos():
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    todos_list = [{"id": todo.id, "task": todo.task, "status": todo.status, "done": todo.done} for todo in todos]
    return jsonify(todos_list)

# API: Add todo endpoint
@app.route("/api/todo", methods=["POST"])
@login_required
def api_add_todo():
    data = request.get_json()
    todo = Todo(task=data["task"], user_id=current_user.id, status="sin iniciar")
    db.session.add(todo)
    db.session.commit()
    return jsonify({"message": "Tarea añadida"}), 201

# API: Edit todo endpoint
@app.route("/api/todo/<int:id>", methods=["PUT"])
@login_required
def api_edit_todo(id):
    data = request.get_json()
    todo = Todo.query.get_or_404(id)
    todo.task = data["task"]
    todo.status = data["status"]
    db.session.commit()
    return jsonify({"message": "Tarea actualizada"})

# API: Delete todo endpoint
@app.route("/api/todo/<int:id>", methods=["DELETE"])
@login_required
def api_delete_todo(id):
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    return jsonify({"message": "Tarea eliminada"})

# API: Change status endpoint
@app.route("/api/todo/<int:id>/done", methods=["PATCH"])
@login_required
def api_change_done(id):
    todo = Todo.query.get_or_404(id)
    todo.done = not todo.done
    db.session.commit()
    return jsonify({"message": "Estado de la tarea cambiado"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2540, debug=True)

    
