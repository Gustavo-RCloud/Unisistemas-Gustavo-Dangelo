from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date

app = Flask(__name__)
DB = 'biblioteca.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            disponivel INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS emprestimos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livro_id INTEGER NOT NULL,
            usuario TEXT NOT NULL,
            data_emprestimo TEXT NOT NULL,
            data_devolucao TEXT,
            FOREIGN KEY (livro_id) REFERENCES livros(id)
        );
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    livros = conn.execute('SELECT * FROM livros').fetchall()
    conn.close()
    return render_template('index.html', livros=livros)

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        conn = get_db()
        conn.execute('INSERT INTO livros (titulo, autor) VALUES (?, ?)', (titulo, autor))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('cadastrar.html')

@app.route('/emprestar/<int:livro_id>', methods=['GET', 'POST'])
def emprestar(livro_id):
    if request.method == 'POST':
        usuario = request.form['usuario']
        conn = get_db()
        conn.execute('INSERT INTO emprestimos (livro_id, usuario, data_emprestimo) VALUES (?, ?, ?)',
                     (livro_id, usuario, str(date.today())))
        conn.execute('UPDATE livros SET disponivel = 0 WHERE id = ?', (livro_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('emprestar.html', livro_id=livro_id)

@app.route('/devolver/<int:livro_id>')
def devolver(livro_id):
    conn = get_db()
    conn.execute('''UPDATE emprestimos SET data_devolucao = ? 
                    WHERE livro_id = ? AND data_devolucao IS NULL''',
                 (str(date.today()), livro_id))
    conn.execute('UPDATE livros SET disponivel = 1 WHERE id = ?', (livro_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/historico')
def historico():
    conn = get_db()
    registros = conn.execute('''
        SELECT e.id, l.titulo, e.usuario, e.data_emprestimo, e.data_devolucao
        FROM emprestimos e JOIN livros l ON e.livro_id = l.id
        ORDER BY e.id DESC
    ''').fetchall()
    conn.close()
    return render_template('historico.html', registros=registros)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
