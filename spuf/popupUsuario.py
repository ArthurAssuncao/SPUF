#coding: utf-8

#author: Mateus Ferreira Silva
#author: Arthur Assuncao

import gtk
import webkit
import settings
import json
import requests

class popup:
    def __init__(self, url):
        r = requests.get(url)
        if 200 == r.status_code:
            dados = r.content
            dados = json.loads(dados)
            
            foto = 'Não Definido'
            nome = 'Não Definido'
            username = 'Não Definido'
            sexo = 'Não Definido'
            amigos = 'Não Definido'
            profile = 'Não Definido'

            for dado in dados['data']:
                if 'pic_big' in dado and dado['pic_big'] != 'null':
                    foto = dado['pic_big']
                if 'name' in dado and dado['name'] != 'null':
                    nome = dado['name']
                if 'username' in dado and dado['username'] != 'null':
                    username = dado['username']
                if 'sex' in dado and dado['sex'] != 'null':
                    if dado['sex'] == 'male':
                        sexo = 'Masculino'
                    else:
                        sexo = 'Feminino'
                if 'friend_count' in dado and dado['friend_count'] != 'null':
                    amigos = dado['friend_count']
                if 'profile_url' in dado and dado['profile_url'] != 'null':
                    profile = dado['profile_url']
            
        else:
            print 'Erro: {}'.format(r.status_code)
            return

        conteudo = open('./HTML/descricaoUsuario.html', 'r').read()
        conteudo = conteudo.replace('{foto}', foto)
        conteudo = conteudo.replace('{nome}', nome)
        conteudo = conteudo.replace('{profile}', profile)
        conteudo = conteudo.replace('{sexo}', sexo)
        conteudo = conteudo.replace('{username}', username)
        conteudo = conteudo.replace('{amigos}', str(amigos))

        self.view = webkit.WebView() 

        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.set_title(nome)
        self.win.set_size_request(500, 480)
        self.win.set_position(gtk.WIN_POS_CENTER)
        self.win.set_resizable(False)
        color = gtk.gdk.color_parse('#fff')
        self.win.modify_bg(gtk.STATE_NORMAL, color)
        self.view.props.settings.props.enable_default_context_menu = False

        vbox = gtk.VBox(False, 1)

        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        scrolledwindow.add(self.view)

        vbox.pack_end(scrolledwindow, True, True, 0)

        self.win.add(vbox)
        self.win.show_all()

        self.view.load_html_string(conteudo, settings.URL_BASE)
