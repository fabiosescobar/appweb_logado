from flask import Flask, render_template, request, session
import pyrebase
import firebase_admin
from checker import check_logged_in
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import firestore_v1

firebaseConfig = {
	
	"apiKey": "AIzaSyCZj19rI-eJuSZhnHfqN7fnQ27khhSqEBA",
  	"authDomain": "logado-ff233.firebaseapp.com",
  	"databaseURL": "https://logado-ff233.firebaseio.com",
  	"projectId": "logado-ff233",
  	"storageBucket": "logado-ff233.appspot.com",
  	"messagingSenderId": "495865982962",
  	"appId": "1:495865982962:web:372a6b24dd6d3f89dc056b",
  	"measurementId": "G-MGGPJ2MPTL"
}


firebase = pyrebase.initialize_app(firebaseConfig)

auth = firebase.auth()

cred = credentials.Certificate('firebase-sdk.json')

firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)



@app.route('/novo', methods = ['GET','POST'])
def incluir() -> 'html':
	if(request.method == 'POST'):
		email = request.form['name']
		pwd1 = request.form['pwd1']
		pwd2 = request.form['pwd2']
		#concorda = request.form['concorda']
		if (pwd1 == pwd2):
				password = pwd2
				try:
					auth.create_user_with_email_and_password(email,password)
					return render_template('pre_entry.html',the_title='Preencha novamente para o envio da confirmação:')
				except Exception as err:
					unsuccessful = str(err)
					return render_template('new_user.html', umessage=unsuccessful)
		else:
				diferent = 'As senhas devem ser iguais, digite novamente.'
				return render_template('new_user.html', the_title='Informe seu e-mail e escolha uma senha:', umessage = diferent)
	return render_template('new_user.html', the_title='Informe seu e-mail e escolha uma senha:')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if (request.method == 'POST'):
            email = request.form['name']
            auth.send_password_reset_email(email)
            return render_template('entry.html')
    return render_template('forgot_password.html')


@app.route('/search4', methods=['GET', 'POST'])

def do_search() -> 'html':
	if (request.method == 'POST'):
			email = request.form['name']
			password = request.form['pwd']
			try:
				user=auth.sign_in_with_email_and_password(email, password)
				session['logged_in'] = True
				account=auth.get_account_info(user['idToken'])
				userinf=account['users']
				userloc=userinf[0]
				session['userid']=userloc['localId']
				session['useremail']=userloc['email']
				query = db.collection('sistemusers').where('userid', '==', session.get('userid'))
				docs= query.stream()
				docs_dict = {doc.id:doc.to_dict() for doc in docs}
				userfields=docs_dict[session.get('useremail')]
				session['username']=userfields['nickname']
				session['nomecompl']=userfields['completename']
				session['conf']=userfields['confirmed']
				if (session.get('conf') == 2):
					umessage_conf = 'Favor, envie documentação comprobatória assinada digitalmente'
				elif (session.get('conf') == 3):
					umessage_conf = 'Dados confirmados.'
				return render_template('home.html',
										the_title='Bem-vindo, ',
										#all_information=account,
										the_user=session.get('username'),
										the_completename=session.get('nomecompl'),
										umessage_name=umessage_conf)
			except:
				unsuccessful = 'Favor, verifique e-mail e senha informados.'
				return render_template('entry.html', umessage=unsuccessful)
	return render_template('entry.html')



@app.route('/verified', methods=['GET', 'POST'])
def do_verification() -> 'html':
	if (request.method == 'POST'):
			email = request.form['name']
			password = request.form['pwd']
			nickname = request.form['nick']
			try:
				user=auth.sign_in_with_email_and_password(email, password)
				account=auth.get_account_info(user['idToken'])
				userinf=account['users']
				userloc=userinf[0]
				userid=userloc['localId']
				useremail=userloc['email']
				doc_ref = db.collection('sistemusers').document(useremail)
				doc_ref.set({
					'userid':userid,
					'nickname':nickname,
					'completename':'',
					'confirmed':1
					'nivel':1
					})
				auth.send_email_verification(user['idToken'])
				return render_template('entry.html', the_title='Verifique sua caixa de e-mail e faça seu login:')
			except:
				unsuccessful = 'Favor, verifique e-mail e senha informados.'
				return render_template('pre_entry.html', umessage=unsuccessful)
	return render_template('pre_entry.html')


@app.route('/consultar_dados', methods=['POST'])
@check_logged_in
def consultar_dados() -> 'html':
	return render_template('meu_cadastro.html', the_title='Meu cadastro ')

@app.route('/pre_atualizar', methods=['GET', 'POST'])
@check_logged_in
def pre_atualizar() -> 'html':
	return render_template('update_userinfo.html')

@app.route('/atualizar_dados', methods=['GET', 'POST'])
@check_logged_in
def atualizar_dados() -> 'html':
	if (request.method == 'POST'):
			completename = request.form['completename']
			try:
				dados_query = db.collection('sistemusers').document(session.get('useremail'))
				dados_query.update({'completename':completename,
									'confirmed':2})
				unsuccessful = ' (Favor, envie documentação comprobatória assinada digitalmente.)'
				return render_template('home.html',
										the_title='Bem-vindo, ',
										the_user=session.get('username'),
										the_completename=completename,
										umessage_name=unsuccessful)
			except:
				unsuccessful = "Não foi possível atalizar os dados."
				return render_template('home.html',
										umessage=unsuccessful, 
										the_title='Bem-vindo, ',
										the_user=session.get('username'))
	return render_template('home.html')

@app.route('/logout', methods=['GET', 'POST'])
def do_logout() -> 'html':
	session.pop('logged_in')
	session.pop('username')
	return render_template('entry.html', the_title='Faça seu login:')

@app.route('/')
@app.route('/entrada')
def entry_page() -> 'html':
	return render_template('entry.html', the_title='Faça seu login:')

@app.route('/minha_pagina', methods=['POST'])
@check_logged_in
def minha_pagina() -> 'html':
	return render_template('home.html',
							the_title='Bem-vindo, ',
							the_user=session.get('username'))

app.secret_key = 'V3rd3-Pr4t4-Pr3t0-8r4nc0.$0m3nte-F14t'

if __name__ == '__main__':
	app.run(debug=True)