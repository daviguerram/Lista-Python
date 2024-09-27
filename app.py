from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Modelo de Tarefas
class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Rota para página inicial
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# Rota de Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(password) < 8:
            flash('A senha deve ter pelo menos 8 caracteres.', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Usuário registrado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Nome de usuário já existe', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html')

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Nome de usuário ou senha incorretos.', 'danger')
            
    return render_template('login.html')

# Rota de Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Rota para obter tarefas do usuário logado
@app.route('/tarefas', methods=['GET'])
def get_tarefas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    tarefas = Tarefa.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{'id': t.id, 'titulo': t.titulo, 'descricao': t.descricao} for t in tarefas])

# Rota para adicionar uma nova tarefa
@app.route('/tarefas', methods=['POST'])
def add_tarefa():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        nova_tarefa = request.json
        
        # Verifique se 'titulo' e 'descricao' estão presentes no JSON
        if not nova_tarefa or 'titulo' not in nova_tarefa or 'descricao' not in nova_tarefa:
            return jsonify({'error': 'Título e descrição são obrigatórios'}), 400
        
        tarefa = Tarefa(titulo=nova_tarefa['titulo'], descricao=nova_tarefa['descricao'], user_id=session['user_id'])
        db.session.add(tarefa)
        db.session.commit()
        return jsonify({'id': tarefa.id, 'titulo': tarefa.titulo, 'descricao': tarefa.descricao}), 201
    except Exception as e:
        print(f"Erro ao adicionar tarefa: {e}")
        return jsonify({'error': 'Erro ao adicionar tarefa'}), 500

# Rota para deletar uma tarefa
@app.route('/tarefas/<int:id>', methods=['DELETE'])
def delete_tarefa(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    tarefa = Tarefa.query.get(id)
    if tarefa and tarefa.user_id == session['user_id']:
        db.session.delete(tarefa)
        db.session.commit()
        return jsonify({'message': 'Tarefa deletada com sucesso!'})
    return jsonify({'message': 'Tarefa não encontrada ou não pertence ao usuário!'}), 404

# Rota para editar uma tarefa existente
@app.route('/tarefas/<int:id>', methods=['PUT'])
def update_tarefa(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    tarefa = Tarefa.query.get(id)
    if tarefa and tarefa.user_id == session['user_id']:
        tarefa.titulo = request.json.get('titulo', tarefa.titulo)
        tarefa.descricao = request.json.get('descricao', tarefa.descricao)
        db.session.commit()
        return jsonify({'id': tarefa.id, 'titulo': tarefa.titulo, 'descricao': tarefa.descricao})
    return jsonify({'message': 'Tarefa não encontrada ou não pertence ao usuário!'}), 404

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)