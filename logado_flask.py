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

storage = firebase.storage()

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
				session['permission']=userfields['nivel']
				if(session.get('permission') == 1):
						if (session.get('conf') == 2):
								umessage_conf = 'Favor, envie documentação comprobatória assinada digitalmente'
								return render_template('home.html',
												the_title='Bem-vindo, ',
												the_user=session.get('username'),
												the_completename=session.get('nomecompl'),
												umessage_name=umessage_conf)
						elif (session.get('conf') == 3):
								smessage_conf = 'Dados confirmados.'
								return render_template('home.html',
												the_title='Bem-vindo, ',
												the_user=session.get('username'),
												the_completename=session.get('nomecompl'),
												smessage_name=smessage_conf)
						else:
								amessage_conf = 'Não há informações inseridas no cadastro.'
								return render_template('home.html',
												the_title='Bem-vindo, ',
												the_user=session.get('username'),
												the_completename=session.get('nomecompl'),
												amessage_name=amessage_conf)
				else:
						if (session.get('conf') == 2):
								umessage_conf = 'Favor, envie documentação comprobatória assinada digitalmente'
								return render_template('home_atend.html',
												the_title='Bem-vindo, ',
												the_user=session.get('username'),
												the_completename=session.get('nomecompl'),
												umessage_name=umessage_conf)
						elif (session.get('conf') == 3):
								smessage_conf = 'Dados confirmados.'
								return render_template('home_atend.html',
												the_title='Bem-vindo, ',
												the_user=session.get('username'),
												the_completename=session.get('nomecompl'),
												smessage_name=smessage_conf)
						else:
								amessage_conf = 'Não há informações inseridas no cadastro.'
								return render_template('home_atend.html',
												the_title='Bem-vindo, ',
												the_user=session.get('username'),
												the_completename=session.get('nomecompl'),
												amessage_name=amessage_conf)
			except:
				unsuccessful = 'Favor, verifique e-mail e senha informados.'
				return render_template('entry.html', umessage=unsuccessful)
	return render_template('entry.html')

@app.route('/enable_atend', methods=['GET', 'POST'])

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
					'confirmed':1,
					'nivel':1
					})
				auth.send_email_verification(user['idToken'])
				return render_template('entry.html', the_title='Verifique sua caixa de e-mail e faça seu login:')
			except:
				unsuccessful = 'Favor, verifique e-mail e senha informados.'
				return render_template('pre_entry.html', umessage=unsuccessful)
	return render_template('pre_entry.html')


@app.route('/buscar_usuario', methods=['GET', 'POST'])
@check_logged_in
def buscar_usuario() -> 'html':
	return render_template('find_user.html', the_title='Selecionar usuário.')

@app.route('/autorizar_atend', methods=['GET', 'POST'])
@check_logged_in
def autorizar_atend() -> 'html':
	if (request.method == 'POST'):
			session['email_atend'] = request.form['email_atend']
			init_query = db.collection('sistemusers').document(session.get('email_atend'))
			init_docs=init_query.get()
			atend_docs=init_docs.to_dict()
			session['atendname']=atend_docs['nickname']
			session['atendcompl']=atend_docs['completename']
			session['atendconf']=atend_docs['confirmed']
			session['atendperm']=atend_docs['nivel']
			try:
				user_query = db.collection('sistemusers').document(session.get('email_atend'))
				docs = user_query.get()
				if docs.exists:
						return render_template('info_atend.html',
												the_email = session.get('email_atend'),
												the_nickname = session.get('atendname'),
												the_completename = session.get('atendcompl'),
												the_confirmed = session.get('atendconf'),
												the_nivel = session.get('atendperm'))							
			except: 
				unsuccessful = 'Atendente não cadastrado.'
				return render_template('find_user.html',
										umassage=unsuccessful,
										the_title=session.get('email_atend'))																	
	return render_template('find_user.html')

@app.route('/salvar_atendente', methods=['GET', 'POST'])
@check_logged_in
def salvar_atendente() -> 'html':
	if (request.method == 'POST'):
			nivelsalvo = request.form['nivelsalvo']
			try:
				user_query = db.collection('sistemusers').document(session.get('email_atend'))
				user_query.update({'nivel':nivelsalvo})
				if(nivelsalvo == '2'):
						nivmessage="Nível 2-'Atendente' salvo com sucesso."
				else:
						nivmessage="Nível 1-'Usuário comum' salvo com sucessso."
				return render_template('info_atend.html',
										aumessage = nivmessage,
										the_email = session.get('email_atend'),
										the_nickname = session.get('atendname'),
										the_completename = session.get('atendcompl'),
										the_confirmed = session.get('atendconf'),
										the_nivel = nivelsalvo)
			except:
				umassage='Não foi possível salvar o nível do usuário.'
				return render_template('info_atend.html',
										aumessage = umassage,
										the_email = session.get('email_atend'),
										the_nickname = session.get('atendname'),
										the_completename = session.get('atendcompl'),
										the_confirmed = session.get('atendconf'),
										the_nivel = session.get('atendperm'))
	return render_template('find_user.html')

@app.route('/pre_atualizar', methods=['GET', 'POST'])
@check_logged_in
def pre_atualizar() -> 'html':
	return render_template('update_userinfo.html')

@app.route('/atualizar_dados', methods=['GET', 'POST'])
@check_logged_in
def atualizar_dados() -> 'html':
	if (request.method == 'POST'):
			session['completename'] = request.form['completename']
			try:
				dados_query = db.collection('sistemusers').document(session.get('useremail'))
				dados_query.update({'completename':session.get('completename'),
									'confirmed':2})
				unsuccessful = 'Favor, envie documentação comprobatória assinada digitalmente.'
				return render_template('home.html',
										the_title='Bem-vindo, ',
										the_user=session.get('username'),
										the_completename=session.get('completename'),
										umessage_name=unsuccessful)
			except:
				unsuccessful = "Não foi possível atalizar os dados."
				return render_template('home.html',
										umessage=unsuccessful, 
										the_title='Bem-vindo, ',
										the_user=session.get('username'))
	return render_template('home.html')

@app.route('/enviar_doc', methods=['GET', 'POST'])
def enviar_doc() -> 'html':
	if request.method == 'POST':
		upload = request.files['upload']
		caminho = "{EMAIL_USUARIO}{NOME_COMPLETO}/new.pdf".format(EMAIL_USUARIO=session.get('useremail'),NOME_COMPLETO=session.get('completename'))
		storage.child(caminho).put(upload)
		links = storage.child(caminho).get_url(None)
		dmessage = "Documento recebido. Aguarde a confirmação dos dados."
		return render_template('home.html',
						the_title='Bem-vindo, ',
						the_user=session.get('username'),
						the_completename=session.get('nomecompl'),
						smessage_name = dmessage,
						l=links)
	return render_template('home.html',
						the_title='Bem-vindo, ',
						the_user=session.get('username'),
						the_completename=session.get('nomecompl'))
						
@app.route('/exibir_pendentes', methods=['GET', 'POST'])
@check_logged_in
def exibir_pendentes() -> 'html':
	if (request.method == 'POST'):
			try:
				pend_query = db.collection('sistemusers').where('confirmed', '==', 2)
				docs= pend_query.stream()
				session['docs_pend'] = {doc.id:doc.to_dict() for doc in docs}
				return render_template('show_pend.html',
										array_pendentes = session.get('docs_pend'))
			except:
				umessage = 'Não foi possível realizar a consulta'
				return render_template('home_atend.html',
										the_title='Bem-vindo, ',
										the_user=session.get('atendname'),
										the_completename=session.get('nomecompl'),
										smessage_name=umessage)
	return render_template('show_pend.html',
							array_pendentes = session.get('docs_pend'))

@app.route('/confirmar_dados', methods=['GET', 'POST'])
def confirmar_dados() -> 'html':
	if (request.method == 'POST'):
			session['dados_email']=request.form['atual']
			try:
				dados_atual = db.collection('sistemusers').document(session.get('dados_email'))
				dados_atual.update({'confirmed':3})
				asmessage = "Dados do usuário {DADOS_EMAIL} confirmados com sucesso!".format(DADOS_EMAIL=session.get('dados_email'))
				return render_template('show_result.html',
										smessage = asmessage)
			except: 
				aumessage = "Não foi possível confirmar os dados"
				return render_template('show_pend.html',
										umassage = aumessage,
										array_pendentes = session.get('docs_pend'))
	return render_template ('show_pend.html',
						   array_pendentes = session.get('docs_pend'))

@app.route('/todos_usuarios', methods=['GET', 'POST'])
def todos_usuarios() -> 'html':
	if(request.method=='POST'):
			try:
				todos_query = db.collection('sistemusers')
				docs = todos_query.stream()
				docs_todos = {doc.id:doc.to_dict() for doc in docs}
				return render_template('show_allusers.html',
										array_todos = docs_todos)
			except:
				aumessage =	'Não foi possível acessar a lista de usuários.'
				return render_template('show_result.html',
										umessage = aumessage)
	return render_template ('home.html')

@app.route('/exibir_usuario', methods=['GET', 'POST'])
def exibir_usuario() -> 'html':
	if(request.method=='POST'):
			session['email_exibir']=request.form['usuario']
			try: 
				one_query = db.collection('sistemusers').document(session.get('email_exibir'))
				init_docs=one_query.get()
				user_docs=init_docs.to_dict()
				session['username']=user_docs['nickname']
				session['usercompl']=user_docs['completename']
				session['userconf']=user_docs['confirmed']
				session['userperm']=user_docs['nivel']
				return render_template('show_one.html',
										the_email = session.get('email_exibir'),
										the_nickname = session.get('username'),
										the_completename = session.get('usercompl'),
										the_confirmed = session.get('userconf'),
										the_nivel = session.get('userperm'))
			except:
				aumessage =	'Não foi possível acessar os dados do usuário.'
				return render_template('home_atend.html',
										umassage=aumessage)
	return render_template ('home_atend.htm')


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
	return render_template('home_atend.html',
					the_title='Bem-vindo, ',
					the_user=session.get('username'),
					the_completename=session.get('nomecompl'))

app.secret_key = 'V3rd3-Pr4t4-Pr3t0-8r4nc0.$0m3nte-F14t'

if __name__ == '__main__':
	app.run(debug=True)