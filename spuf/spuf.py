#!/usr/bin/env python
#coding: utf-8

#author: Mateus Ferreira Silva
#author: Arthur Assuncao

import gtk 
import webkit
import settings
import re
import requests
import os
import popupUsuario
import json

class spuf:
    
    def stopAnimation(self, view=None, frame=None):
        self.spinner.stop()

    def startAnimation(self, view=None, frame=None):
        self.spinner.start()
    
    def __init__(self):
        self.buscaAtual = '' # armazena o conteúdo pesquisado atualmente
        
        self.view = webkit.WebView() 
        self.view.connect('navigation-requested', self.on_click_link)

        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.set_title('SPUF - Sistema de Pesquisa de Usuários do Facebook')
        self.win.set_size_request(800, 600)
        self.win.set_position(gtk.WIN_POS_CENTER)
        self.win.set_resizable(False)
        self.view.props.settings.props.enable_default_context_menu = False
        
        self.view.connect("load-finished", self.stopAnimation)
        self.view.connect("load-started", self.startAnimation)

        vbox = gtk.VBox(False, 2)
        hbox = gtk.HBox()
        
        # Barra de menu
        menuBar = gtk.MenuBar()
        menuArquivo = gtk.Menu()
        arquivo = gtk.MenuItem('Arquivo')
        arquivo.set_submenu(menuArquivo)

        limparPesquisa = gtk.MenuItem('Limpar Pesquisa')
        limparPesquisa.connect('activate', self.limparWebView)
        menuArquivo.append(limparPesquisa)

        sep = gtk.SeparatorMenuItem()
        menuArquivo.append(sep)
        
        sair = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        sair.connect('activate', gtk.main_quit)
        menuArquivo.append(sair)

        menuCreditos = gtk.Menu()
        sobre = gtk.MenuItem('Sobre')
        sobre.set_submenu(menuCreditos)
        sobre.connect('activate', self.sobre)
        menuBar.append(arquivo)
        menuBar.append(sobre)
        vbox.pack_start(menuBar, False, False, 0)

        # Campo de busca
        labelUsuario = gtk.Label('Usuário:')
        self.campoBuscar = gtk.Entry()
        self.campoBuscar.connect('activate', self.buscar)
        self.spinner = gtk.Spinner()
        btBuscar = gtk.Button('Buscar')
        btBuscar.connect("clicked", self.buscar)
        btBuscar.set_size_request(80, 25)
        hbox.pack_start(labelUsuario, False, False, 5)
        hbox.pack_start(self.campoBuscar, True, True, 0)
        hbox.pack_start(self.spinner, False, False, 1)
        hbox.pack_start(btBuscar, False, False, 1)

        # Barra de Rolagem na webView
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        scrolledwindow.add(self.view)

        # Adicionar hbox e scrolledwindow
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_end(scrolledwindow, True, True, 0)

        self.win.add(vbox)
        self.win.connect("destroy", gtk.main_quit) # Fechar ao clicar
        self.win.show_all()

    def on_click_link(self, view, frame, req, data=None):
        '''
        Listener para links. 
        Toda vez que um link é clicado no webView, ele é chamado.
        '''

        uri = req.get_uri()
        if uri.startswith("file:///"):
            self.buscar(None)
            return False
        elif uri.startswith("program:/"):
            print uri.split("/")[1]
        else: 
            popupUsuario.popup(uri)
        return True

    def limparWebView(self, view):
        self.view.load_html_string('', settings.URL_BASE)
        self.campoBuscar.set_text('')
        self.buscaAtual = ''

    def sobre(self, view):
        sobre = open('./HTML/sobre.html', 'r').read() 
        self.view.load_html_string(sobre, settings.URL_BASE)
        self.buscaAtual = ''

    def buscar(self, button):
        busca = self.campoBuscar.get_text().strip().lower()

        if len(busca) == 0:
            pass
        elif self.buscaAtual == busca:
            pass
        else:
            print 'Realizando pesquisa para "{}"'.format(busca)
            self.buscaAtual = busca
            # Recebimento da resposta de busca
            resposta, conteudo = self.busca(busca)
            if resposta == 200:
                conteudo = self.estrutura_resultado(conteudo)
            elif resposta == 404:
                conteudo = self.estrutura_resultado(None)
                print 'URL inválida, verifique o ACCESS_TOKEN no arquivo de configurações.'
            self.view.load_html_string(conteudo, settings.URL_BASE)


    def estrutura_resultado(self, usuarios):
        if len(usuarios['data']) == 0:
            conteudo = open('./HTML/naoEncontrado.html', 'r').read() 
            return conteudo
        else:
            conteudo = open('./HTML/usuarios.html', 'r').read() 
            lista = []
            for usuario in usuarios['data']:
                url = self.gera_url_detalhada(usuario['uid'])
                item = '<a href="{url}"><li class="well well-small titulo"><img src="{img}" height="44" width="32" /><span>{nome} - ({username})</span></li></a>'.format(
                    img=usuario['pic_square'], url=url, nome=usuario['name'], username=usuario['username'])
                lista.append(item)
            texto_conteudo = '<br>'.join(lista)
            conteudo = conteudo % texto_conteudo
            return conteudo

    def retorna_lista(self, url):
        r = requests.get(url)
        usuarios = {}
        if 200 == r.status_code:
            r = r.content
            usuarios = json.loads(r)
            resposta = 200
        else:
            resposta = 404
        return resposta, usuarios

    def gera_url_detalhada(self, pesquisa):
        OpenGraphURL = 'https://graph.facebook.com/'
        fqlQuery = 'fql?q=SELECT username, name, pic_big, profile_url, sex, friend_count FROM user WHERE uid={0}'.format(pesquisa) 
        accessToken = '&access_token={0}'.format(settings.ACCESS_TOKEN)
        return '{0}{1}{2}'.format(OpenGraphURL, fqlQuery, accessToken)


    def gera_url_comum(self, pesquisa):
        pesquisa = pesquisa.strip()
        if len(pesquisa) > 0:
            OpenGraphURL = 'https://graph.facebook.com/'
            fqlQuery = 'fql?q=SELECT uid, username, name, pic_square FROM user WHERE contains(\'{0}\')'.format(pesquisa) 
            accessToken = '&access_token={0}'.format(settings.ACCESS_TOKEN)
            return '{0}{1}{2}'.format(OpenGraphURL, fqlQuery, accessToken)
        else:
            return None
            
    def busca(self, texto):
        url = self.gera_url_comum(texto)
        return self.retorna_lista(url)

if __name__ == "__main__":
    spuf()
    gtk.main()
