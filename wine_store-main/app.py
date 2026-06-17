from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

# ==========================================
# CONFIGURAÇÃO DO FLASK
# ==========================================

app = Flask(__name__)
app.secret_key = "wine_store_2026"

# ==========================================
# CONFIGURAÇÃO DO MYSQL
# ==========================================

bd_config = {
    "port": 3306,
    "user": "root",
    "password": "escola",  
    "database": "wine_store"
}

# ==========================================
# FUNÇÃO DE CONEXÃO
# ==========================================

def conectar_bd():
    return mysql.connector.connect(**bd_config)

# ==========================================
# ROTA DE LOGIN
# ==========================================

@app.route('/login')
def login():
    return render_template('login.html')

# ==========================================
# VALIDAR LOGIN
# ==========================================

@app.route('/autenticar', methods=['POST'])
def autenticar():

    usuario = request.form['usuario']
    senha = request.form['senha']

    conexao = conectar_bd()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM usuarios
        WHERE usuario = %s
        AND senha = %s
        """,
        (usuario, senha)
    )

    usuario_encontrado = cursor.fetchone()

    cursor.close()
    conexao.close()

    if usuario_encontrado:

        session['usuario'] = usuario

        return redirect(url_for('painel'))

    return """
    <h2>Usuário ou senha inválidos</h2>
    <a href='/login'>Tentar novamente</a>
    """

# ==========================================
# CRIAR PAINEL ADMINISTRATIVO
# ==========================================
@app.route('/painel')
def painel():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    return render_template('painel.html')

# ==========================================
# CRIAR LOGOUT
# ==========================================
@app.route('/logout')
def logout():

    session.pop('usuario', None)

    return redirect(url_for('login'))

# ==========================================
# PÁGINA INICIAL
# ==========================================

@app.route('/')
def index():

    try:
        conexao = conectar_bd()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("SELECT * FROM produtos")
        produtos = cursor.fetchall()

        cursor.close()
        conexao.close()

        return render_template(
            'index.html',
            produtos=produtos
        )

    except mysql.connector.Error as erro:
        return f"Erro ao carregar produtos: {erro}"

# ==========================================
# ADICIONAR AO CARRINHO
# ==========================================

@app.route('/adicionar/<int:id>')
def adicionar(id):

    if 'carrinho' not in session:
        session['carrinho'] = []

    session['carrinho'].append(id)
    session.modified = True

    return redirect(url_for('index'))

# ==========================================
# EXIBIR CARRINHO
# ==========================================

@app.route('/carrinho')
def carrinho():

    ids = session.get('carrinho', [])

    if len(ids) == 0:
        return render_template(
            'carrinho.html',
            produtos=[],
            total=0
        )

    try:

        conexao = conectar_bd()
        cursor = conexao.cursor(dictionary=True)

        placeholders = ",".join(["%s"] * len(ids))

        sql = f"""
            SELECT *
            FROM produtos
            WHERE id IN ({placeholders})
        """

        cursor.execute(sql, ids)

        produtos = cursor.fetchall()

        total = sum(float(produto['preco']) for produto in produtos)

        cursor.close()
        conexao.close()

        return render_template(
            'carrinho.html',
            produtos=produtos,
            total=total
        )

    except mysql.connector.Error as erro:
        return f"Erro ao carregar carrinho: {erro}"

# ==========================================
# PÁGINA CHECKOUT
# ==========================================

@app.route('/checkout')
def pagina_checkout():
    return render_template('checkout.html')

# ==========================================
# FINALIZAR PEDIDO
# ==========================================

@app.route('/checkout', methods=['POST'])
def checkout():

    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    endereco = request.form['endereco']

    ids = session.get('carrinho', [])

    if len(ids) == 0:
        return "Carrinho vazio!"

    try:

        conexao = conectar_bd()
        cursor = conexao.cursor()

        # ==========================
        # CLIENTE
        # ==========================

        cursor.execute("""
            INSERT INTO clientes
            (nome, email, telefone, endereco)
            VALUES (%s, %s, %s, %s)
        """, (nome, email, telefone, endereco))

        cliente_id = cursor.lastrowid

        # ==========================
        # TOTAL
        # ==========================

        total = 0

        for produto_id in ids:

            cursor.execute(
                "SELECT preco FROM produtos WHERE id = %s",
                (produto_id,)
            )

            preco = float(cursor.fetchone()[0])
            total += preco

        # ==========================
        # PEDIDO
        # ==========================

        cursor.execute("""
            INSERT INTO pedidos
            (cliente_id, total)
            VALUES (%s, %s)
        """, (cliente_id, total))

        pedido_id = cursor.lastrowid

        # ==========================
        # ITENS DO PEDIDO
        # ==========================

        for produto_id in ids:

            cursor.execute(
                "SELECT preco FROM produtos WHERE id = %s",
                (produto_id,)
            )

            preco = float(cursor.fetchone()[0])

            cursor.execute("""
                INSERT INTO itens_pedido
                (
                    pedido_id,
                    produto_id,
                    quantidade,
                    subtotal
                )
                VALUES (%s, %s, %s, %s)
            """, (
                pedido_id,
                produto_id,
                1,
                preco
            ))

        conexao.commit()

        cursor.close()
        conexao.close()

        session['carrinho'] = []

        return f"""
        <html>
        <head>
            <title>Pedido Confirmado</title>
        </head>

        <body style='font-family:Arial;text-align:center;margin-top:50px;'>

            <h1>🍷 Pedido realizado com sucesso!</h1>

            <h2>Pedido Nº {pedido_id}</h2>

            <h3>Total: R$ {total:.2f}</h3>

            <br>

            <a href='/'>
                Voltar para a loja
            </a>

        </body>
        </html>
        """

    except mysql.connector.Error as erro:
        return f"Erro ao finalizar pedido: {erro}"

# ==========================================
# LIMPAR CARRINHO
# ==========================================

@app.route('/limpar-carrinho')
def limpar_carrinho():

    session['carrinho'] = []

    return redirect(url_for('carrinho'))

# ==========================================
# LISTAR PRODUTOS NO PAINEL
# ==========================================

@app.route('/admin/produtos')
def admin_produtos():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    conexao = conectar_bd()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template(
        'admin_produtos.html',
        produtos=produtos
    )

# ==========================================
# DELETAR PRODUTOS
# ==========================================

@app.route('/admin/deletar/<int:id>')
def deletar_produto(id):

    if 'usuario' not in session:
        return redirect(url_for('login'))

    conexao = conectar_bd()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM produtos WHERE id=%s",
        (id,)
    )

    conexao.commit()

    cursor.close()
    conexao.close()

    return redirect('/admin/produtos')

# ==========================================
# EDITAR PRODUTOS
# ==========================================

@app.route('/admin/editar/<int:id>')
def editar_produto(id):

    if 'usuario' not in session:
        return redirect(url_for('login'))

    conexao = conectar_bd()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM produtos WHERE id=%s",
        (id,)
    )

    produto = cursor.fetchone()

    cursor.close()
    conexao.close()

    return render_template(
        'editar_produto.html',
        produto=produto
    )

# ==========================================
# SALVAR ALTERAÇÕES
# ==========================================

@app.route('/admin/atualizar/<int:id>', methods=['POST'])
def atualizar_produto(id):

    if 'usuario' not in session:
        return redirect(url_for('login'))

    nome = request.form['nome']
    descricao = request.form['descricao']
    preco = request.form['preco']
    estoque = request.form['estoque']

    conexao = conectar_bd()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE produtos
        SET
            nome=%s,
            descricao=%s,
            preco=%s,
            estoque=%s
        WHERE id=%s
    """, (
        nome,
        descricao,
        preco,
        estoque,
        id
    ))

    conexao.commit()

    cursor.close()
    conexao.close()

    return redirect('/admin/produtos')

# ==========================================
# PAGINA HARMONIZACAO
# ==========================================

@app.route('/harmonizacao')
def harmonizacao():

    ids = session.get('carrinho', [])

    sugestao = "Ainda não há itens no carrinho."

    if ids:

        conexao = conectar_bd()
        cursor = conexao.cursor(dictionary=True)

        placeholders = ",".join(["%s"] * len(ids))

        cursor.execute(f"""
            SELECT *
            FROM produtos
            WHERE id IN ({placeholders})
        """, ids)

        produtos = cursor.fetchall()

        categorias = []

        for p in produtos:
            nome = p['nome'].lower()

            if "cabernet" in nome or "merlot" in nome:
                categorias.append("tinto")
            elif "chardonnay" in nome or "sauvignon" in nome:
                categorias.append("branco")
            else:
                categorias.append("rosé")

        if "tinto" in categorias:
            sugestao = "🍖 Você tem vinhos tintos no carrinho. Ideal para carnes vermelhas, massas e queijos fortes."
        elif "branco" in categorias:
            sugestao = "🐟 Você tem vinhos brancos. Perfeito com peixes, frango e saladas."
        elif "rosé" in categorias:
            sugestao = "🥗 Você tem vinhos rosés. Ótimos para pratos leves e aperitivos."

        cursor.close()
        conexao.close()

        return render_template(
            "harmonizacao.html",
            sugestao=sugestao,
            produtos=produtos
        )

    return render_template(
        "harmonizacao.html",
        sugestao=sugestao,
        produtos=[]
    )

# ==========================================
# DELETAR ITEM CARRINHO
# ==========================================

@app.route('/remover/<int:id>')
def remover_carrinho(id):

    carrinho = session.get('carrinho', [])

    if id in carrinho:
        carrinho.remove(id)

    session['carrinho'] = carrinho
    session.modified = True

    return redirect(url_for('carrinho'))

# ==========================================
# EXECUTAR SERVIDOR
# ==========================================

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )