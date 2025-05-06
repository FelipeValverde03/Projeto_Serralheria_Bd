from app import app
from flask import render_template, request, redirect, flash, get_flashed_messages
from database import connect_db
from viacep import gerador_endereco

@app.route("/")
def homepage():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id_orcamento, nome_cliente, valor, data
        FROM orcamento
        WHERE status_cliente = 'Aberto'
        ORDER BY data DESC
    """)
    orcamentos_abertos = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("homepage.html",orcamentos = orcamentos_abertos)

@app.route('/selecionar_tabela', methods=['POST'])
def selecionar_tabela():
    tabela = request.form['tabela']
    if tabela == 'orcamento':
        return redirect('/orcamento')
    elif tabela == 'funcionario':
        return redirect('/funcionario')  
    else:
        return "Tabela inválida", 400

#Pagina registro Orcamento
@app.route('/orcamento', methods=['GET', 'POST'])
def orcamento():  

    if request.method == 'POST':
        #Coletar os dados do formulário
        nome_cliente = request.form['nome_cliente'].strip().upper()
        cpf = request.form['cpf'].strip()
        cep = request.form['cep'].strip()
        telefone = request.form['telefone'].strip()
        status_cliente = request.form['status_cliente'].strip().capitalize()
        valor = request.form['valor'].strip()
        forma_pagamento = request.form['forma_pagamento'].strip().capitalize()
        data = request.form['data'].strip()
        cliente_novo = request.form['cliente_novo'].lower() == 'true'
        salvar_cliente = request.form['salvar_cliente'].lower() == 'true'
        endereco = gerador_endereco(cep)

        #Conecta ao Bd
        conn = connect_db()
        cur = conn.cursor()

        #Add valores ao Bd Orcamentos
        cur.execute("""INSERT INTO orcamento(
                nome_cliente, cpf, cep, telefone,
                status_cliente, valor, forma_pagamento, data, cliente_novo, endereco
        )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",(
                nome_cliente, cpf, cep, telefone,
                status_cliente, valor, forma_pagamento, data, cliente_novo, endereco))

        conn.commit()
        flash("✅ Orçamento registrado com sucesso!","success")
        
        
        if salvar_cliente == True:
            #Add Cliente 
            cur.execute("SELECT * FROM cliente WHERE cpf = %s", (cpf,))
            cliente_existente = cur.fetchone()

            if cliente_existente:
                flash("⚠️ Cliente com este CPF já está registrado!", "warning")
            else:
                cur.execute("""INSERT INTO cliente (nome_cliente, cpf, cep, telefone, endereco)
                            VALUES (%s, %s, %s, %s, %s)
                            """, (nome_cliente, cpf, cep, telefone, endereco))
                conn.commit()
                flash("✅ Cliente registrado com sucesso!", "success")
        else: pass
                
        #Fechando Bd
        cur.close()
        conn.close()
        
        return redirect('/aviso')

    return render_template('orcamento.html')

#Pagina registro Funcionario
@app.route("/funcionario", methods=['GET', 'POST'])
def funcionario():
    if request.method == 'POST':
        #Coletar os dados do formulário
        nome_funcionario = request.form['nome_funcionario']
        cpf = request.form['cpf']
        salario = request.form['salario']
        n_faltas = request.form['n_faltas']

        #Conecta ao Bd
        conn = connect_db()
        cur = conn.cursor()

        #Add valores ao Bd
        cur.execute("""INSERT INTO funcionario(
                nome_funcionario, cpf, salario, n_faltas
        )
            VALUES (%s, %s, %s, %s)""",(
                nome_funcionario, cpf, salario,n_faltas))

        conn.commit()

        #Fechando Bd
        cur.close()
        conn.close()
        
        return redirect('/')
    
    return render_template("funcionario.html")

#Pagina do aviso
@app.route("/aviso")
def aviso():
    flash_messages = get_flashed_messages(with_categories=True)
    return render_template("aviso.html", messages=flash_messages)