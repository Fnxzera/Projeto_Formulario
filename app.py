from flask import Flask, render_template, request,flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
import sqlite3
import re

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///../database/form_data.db'
app.config['SECRET_KEY'] = 'LUCASMORAES'
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'form83937@gmail.com'
app.config['MAIL_PASSWORD'] = 'fhilmfbvccjqjcbl'
app.config['MAIL_DEFAULT_SENDER'] = ('Form Automation', 'form83937@gmail.com')

mail = Mail(app)

class Person(db.Model):
    __tablename__ = "person_data"
    id = db.Column(db.Integer, primary_key =  True,autoincrement=True) # Primary Key
    nome = db.Column(db.String(12), unique = True) 
    apelido = db.Column(db.String(200)) 
    email = db.Column(db.String(200))
    telefone = db.Column(db.Integer)

def validar_email(email): # Função para validar email fornecido
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    if re.match(regex, email):
        return True
    else:
        return False


def enviar_email_para_usuario(nome, email):
    msg = Message('Confirmação de Preenchimento de Formulário',
                  recipients=[email])  # E-mail do usuário como destinatário
    msg.body = f'Olá {nome},\n\nObrigado por preencher o formulário. Seus dados foram recebidos com sucesso.\n\nAtenciosamente,\nEquipe'
    mail.send(msg)

def enviar_email_para_admin(nome, apelido, email, telefone):
    admin_email = 'form83937@gmail.com'  # E-mail do administrador
    msg = Message('Novo Formulário Preenchido',
                  recipients=[admin_email])  # E-mail do administrador como destinatário
    msg.body = (f'Um novo formulário foi preenchido.\n\n'
                f'Nome: {nome} {apelido} \n'
                f'E-mail: {email}\n'
                f'Telefone: {telefone}\n')
    mail.send(msg)
    


@app.route('/registo' , methods=['GET' , 'POST'])
def registo():
    nome =          request.form.get('cliente-nome')
    apelido =       request.form.get('cliente-apelido')
    email =         request.form.get('cliente-email')
    confirm_email = request.form.get('confirm-email')
    telefone =      request.form.get('cliente-telefone')
    if nome and apelido and email and confirm_email and telefone:
        if email == confirm_email:
            if validar_email(email) == True:
                connection = sqlite3.connect('database/form_data.db') 
                cursor = connection.cursor()
                cursor.execute('SELECT email FROM person_data')        # Query para busca de emails
                lista_email = [row[0] for row in cursor.fetchall()] 
                presente = False
                for user in lista_email:       
                    if user == email:
                        presente = True
                        break
                if presente:
                    flash('Email já utilizado.')
                    return render_template('registo.html')
                else:
                    
                    new_person = Person(nome = nome, apelido = apelido, email = confirm_email, telefone = telefone)
                    novos_dados = {
                        'Nome': [nome],
                        'Email': [email],
                        'Telefone': [telefone]
                    }
                    df_novos_dados = pd.DataFrame(novos_dados)
                    arquivo_excel = 'dados_formulario.xlsx'
                    if os.path.exists(arquivo_excel):
                        df_existente = pd.read_excel(arquivo_excel)
                        df_atualizado = pd.concat([df_existente, df_novos_dados], ignore_index=True)
                        df_atualizado.to_excel(arquivo_excel, index=False)
                    else:
                        df_novos_dados.to_excel(arquivo_excel, index=False)
                            
                    # Enviar e-mail de confirmação para o usuário
                    enviar_email_para_usuario(nome, email)

                    # Enviar e-mail de notificação para o administrador
                    enviar_email_para_admin(nome, apelido, email, telefone)
                    
                    with app.app_context():
                        db.session.add(new_person)
                        db.session.commit()                
                    return render_template('confirm.html')
            else: 
                flash('Insira um email válido.')
            return render_template('registo.html')
        else:
            flash('Os endereços de email precisam ser iguais.')
            return render_template('registo.html')
    else:
        flash('Todos os campos são obrigatórios.')
        return render_template('registo.html')
    
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('registo.html')



with app.app_context():
    db.create_all()
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)

