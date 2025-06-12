from app import app
from flask import render_template, request, redirect, flash, get_flashed_messages, jsonify
from database import connect_db
from viacep import gerador_endereco
from workalendar.america import Brazil
from datetime import datetime

@app.route("/")
def homepage():
    conn = connect_db()
    cur = conn.cursor()

    #Cliente com status Aberto
    cur.execute("""
        SELECT id_orcamento, nome_cliente, valor, data, telefone
        FROM orcamento
        WHERE status_cliente = 'Aberto'
        ORDER BY data DESC
    """)
    orcamentos_abertos = cur.fetchall()

    #Coleta de dados para orcamentos abertos e nao finalizados
    cur.execute("""
        SELECT id_orcamento, nome_cliente, data, valor, dias_uteis
        FROM orcamento
        WHERE status_cliente = 'Fechado' AND obra_entregue = False
        ORDER BY data DESC
    """)

    obras = []
    cal = Brazil()
    for row in cur.fetchall():
        id_obra, nome_cliente, data_fechamento, valor, dias_uteis = row
        data_entrega = cal.add_working_days(data_fechamento, int(dias_uteis))
        dias_restantes = cal.get_working_days_delta(datetime.now().date(), data_entrega)
        
        obras.append((
            id_obra,
            nome_cliente,
            data_fechamento,
            float(valor),
            data_entrega,
            dias_restantes
        ))   
    
    #Registro de Auditoria 
    cur.execute("""SELECT data_hora, mensagem FROM auditoria ORDER BY data_hora DESC LIMIT 10""")
    registro_auditoria = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("homepage.html",orcamentos = orcamentos_abertos, obras=obras, registro_auditoria=registro_auditoria)

@app.route('/selecionar_tabela', methods=['POST'])
def selecionar_tabela():
    tabela = request.form['tabela']
    if tabela == 'orcamento':
        return redirect('/orcamento')
    elif tabela == 'funcionario':
        return redirect('/funcionario')  
    else:
        return "Tabela inválida", 400

@app.route("/entregar_obra", methods=["POST"])
def entregar_obra():
    data = request.get_json()
    id_obra = data.get("id_obra")

    if not id_obra:
        return jsonify(success=False, message="ID da obra não fornecido"), 400

    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE orcamento
            SET obra_entregue = TRUE
            WHERE id_orcamento = %s
        """, (id_obra,))
        
        cur.execute("INSERT INTO auditoria (mensagem) VALUES (%s)", (
            f"Obra com ID {id_obra} marcada como entregue.",))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
    
@app.route("/mudar_status_ajax", methods=["POST"])
def mudar_status_ajax():
    data = request.get_json()
    id_orcamento = data.get("id_orcamento")
    novo_status = data.get("novo_status")

    if not id_orcamento or novo_status not in ['Fechado', 'Negado']:
        return jsonify(success=False, message="Dados inválidos"), 400

    conn = None
    try:
        conn = connect_db()
        cur = conn.cursor()
        
        # Coleta de dados completos do orçamento
        cur.execute("""
            SELECT nome_cliente, cpf_cnpj, cep, telefone, endereco 
            FROM orcamento 
            WHERE id_orcamento = %s
        """, (id_orcamento,))
        orcamento = cur.fetchone()

        if not orcamento:
            return jsonify(success=False, message="Orçamento não encontrado"), 404

        # Atualizar status
        
        if novo_status == "Fechado":
            cur.execute(
                "UPDATE orcamento SET status_cliente = %s, data = %s WHERE id_orcamento = %s",
                (novo_status, datetime.now(), id_orcamento)
            )
        else:
            cur.execute(
                "UPDATE orcamento SET status_cliente = %s WHERE id_orcamento = %s",
                (novo_status, id_orcamento)
            )

        # Cadastro do cliente caso Feche o orcamento
        if novo_status == 'Fechado':
            nome_cliente, cpf_cnpj, cep, telefone, endereco = orcamento
            
            # Verificação mais robusta de cliente existente
            cur.execute("SELECT 1 FROM cliente WHERE cpf_cnpj = %s LIMIT 1", (cpf_cnpj,))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO cliente 
                    (nome_cliente, cpf_cnpj, cep, telefone, endereco)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nome_cliente, cpf_cnpj, cep, telefone, endereco))
                
                # Registrar na auditoria
                cur.execute("""
                    INSERT INTO auditoria (mensagem)
                    VALUES (%s)
                """, (f"Cliente {nome_cliente} cadastrado via atualização de status",))

        conn.commit()
        return jsonify(
            success=True,
            message=f"Status atualizado para {novo_status}" + 
                   (" e cliente cadastrado" if novo_status == 'Fechado' else "")
        )
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify(success=False, message="Erro interno ao processar"), 500
    finally:
        if conn:
            conn.close()

#Pagina registro Orcamento
@app.route('/orcamento', methods=['GET', 'POST'])
def orcamento():  

    if request.method == 'POST':
        #Coletar os dados do formulário
        nome_cliente = request.form['nome_cliente'].strip().upper()
        cpf_cnpj = request.form['cpf_cnpj'].strip()
        cep = request.form['cep'].strip()
        telefone = request.form['telefone'].strip()
        status_cliente = request.form['status_cliente'].strip().capitalize()
        valor = request.form['valor'].strip()
        forma_pagamento = request.form['forma_pagamento'].strip().capitalize()
        data = request.form['data'].strip()
        cliente_novo = request.form['cliente_novo'].lower() == 'true'
        endereco = gerador_endereco(cep)
        dias_uteis = request.form['dias_uteis'].strip()
        obra_entregue = request.form['obra_entregue'].lower() == 'true'

        #Conecta ao Bd
        conn = connect_db()
        cur = conn.cursor()
        
        #Salvando os clientes no registro de auditoria
        mensagem_cliente = f"Cliente {nome_cliente} adicionado"
        mensagem_orcamento = f"Orçamento de R$ {valor} para {nome_cliente} adicionado"

        cur.execute("INSERT INTO auditoria (mensagem) VALUES (%s)", (mensagem_orcamento,))

        #Forma de Pagamento Outro
        if forma_pagamento == "Outro":
            forma_pagamento = request.form["outra_forma"]

        #Add valores ao Bd Orcamentos
        cur.execute("""INSERT INTO orcamento(
                nome_cliente, cpf_cnpj, cep, telefone,
                status_cliente, valor, forma_pagamento, data, cliente_novo, endereco, obra_entregue, dias_uteis
        )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",(
                nome_cliente, cpf_cnpj, cep, telefone,
                status_cliente, valor, forma_pagamento, data, cliente_novo, endereco, obra_entregue, dias_uteis))

        conn.commit()
        flash("✅ Orçamento registrado com sucesso!","success")
        
        
        if status_cliente == 'Fechado':
            #Add Cliente 
            cur.execute("SELECT * FROM cliente WHERE cpf_cnpj = %s", (cpf_cnpj,))
            cliente_existente = cur.fetchone()

            if cliente_existente:
                flash("⚠️ Cliente com este documento já está registrado!", "warning")
            else:
                cur.execute("""INSERT INTO cliente (nome_cliente, cpf_cnpj, cep, telefone, endereco)
                            VALUES (%s, %s, %s, %s, %s)
                            """, (nome_cliente, cpf_cnpj, cep, telefone, endereco))
                cur.execute("INSERT INTO auditoria (mensagem) VALUES (%s)", (mensagem_cliente,))
                conn.commit()
                flash("✅ Cliente registrado com sucesso!", "success")
        else: pass
                
        #Fechando Bd
        cur.close()
        conn.close()
        
        return redirect('/aviso')

    return render_template('orcamento.html')

#Pagina do aviso
@app.route("/aviso")
def aviso():
    flash_messages = get_flashed_messages(with_categories=True)
    return render_template("aviso.html", messages=flash_messages)