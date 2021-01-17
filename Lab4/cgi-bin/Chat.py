from Message import *
from User import *

from time import sleep
import sys
import pickle, cgitb, codecs, datetime
import cgi
import os
import html
import json
import os
cgitb.enable()

user=User()

restFlag=False;#Флаг, который будет переключаться в зависимости от того,
#через какой мы клиент подключились (рест или веб, если веб то false, если rest то true)

from urllib.parse import parse_qs


#Для разного типа подключения (рест или веб) разный тип отправляемых данных
htmlContent='Content-type: text/html\n'
jsonContent='Content-type: application/json\n'

#with open('log.json', 'w', encoding='utf-8') as f:
#    json.dump(res, f)

res={}#переменная для записи запроса, здесь будут хранится отправляемые данные из рест клиента

action=''
sysmess=''

#здесь будут храниться отправляемые данные в рест клиент
json_data={
    'result':{
        'id_To': 0,
        'id_From':  0, 
        'Data': ''
    },
    'sys':''
}

#принимается запрос и данные из веб\рест клиента
content_len = os.environ.get('CONTENT_LENGTH', '0')#длина отправляемых данных
method = os.environ.get('REQUEST_METHOD', '')#метод (Пост или Гет)
query_string = os.environ.get('QUERY_STRING', '') #ссылка запроса (в ссылке запроса могут содержаться данные)
x_header = os.environ.get('HTTP_X_MARVIN_STATUS', '') #Пока что ненужные нам данные
if (content_len!=''): #Если мы из какого то клиента отправили данные (методом пост), то ...
    body = sys.stdin.read(int(content_len)) #Записываем эти данные в переменную body
else:
    body=query_string #если не отправляли данные, то записываем ссылку запроса (то, что идет после localhost/..../Chat.py?)

#...


cmd='' #переменная, в которой будут хранится данные из веб клиеента в виде строки с ключами и значениями


if (query_string.find('console=1')!=-1): #Если мы отправили запрос из рест клиента
    if (query_string.find('action=getdata')!=-1): #Если мы отправили запрос GET (т.е. просто запрос с сылкой без каких либо данных)
        action='getdata' #действие будет getdata
    else:
        res = json.loads(body) #если отправили ПОСТ запрос, то мы в res записываем отправленные данные в виде json
        action=res['action'] #в json если ключ action, значение этого ключа записываем в переменную action
    restFlag=True #указываем, что дальнейшая работа будет с Rest
else:
#    index=body.find('action')
    cmd=parse_qs(body) #если получили запрос от веб клиента (браузера), то парсим данные (т.е. превращаем строку типа action=Init  в строку ['action']: 'Init')
    try:
        action=cmd['action'][0] #Получаем action по ключу и нулевому значению (в одном клбче могут быть много значений, порядок начинается с 0 как в массивах)
    except:
        action=''
#if (console=='1'):
    
#    res = json.loads(body)
#    restFlag=True
#else:
 #   action=form.getvalue('action')



def LoadTpl(tplName): #Функция загрузки tpl файла
    docrootname = 'PATH_TRANSLATED'
    with open(os.environ[docrootname]+'/tpl/'+tplName+'.tpl', 'rt') as f:
        return f.read().replace('{selfurl}', os.environ['SCRIPT_NAME'])

#Главная функция
def Proc(act, content):
    print(content)

    #Говорим, что работаем с глобавльными перменными, которые были описаны в начале файла
    global sysmess
    global json_data

    #если действие равно 'Init'
    if act == "Init":
            #Тут все как в третьей лабе (передаем запрос серверу по сокету)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    SendMessage(s, 0, user.MyId, Messages.M_INIT)
                    m=Receive(s)
                    if (m.m_Header.m_Type==Messages.M_CONFIRM):
                        if (user.find):
                            user.register(m.m_Header.m_To)
                            
                        sysmess="Succes Init"
                    else:
                        sysmess="Something went wrong"

                    #Записываем в json_data нужное нам значение, чтобы считать его с рест клиента     
                    json_data['result']['id_To']=user.MyId
                    
    #если действие равно 'publish' (Отправить данные)                 
    if act=="publish":
        #В зависимости от того, с каким клиентом работаем, записываем в переменные m_To и m_Data данные
        if restFlag==False:
            #cmd=parse_qs(body)
            try:
                #Если мы работаем с веб клиентом, то должны считывать данные из cmd
                m_To=cmd['m_To'][0] 
                m_Data = cmd['m_Data'][0]
            except:
                m_To=None
                m_Data=None
        else:
            #Если работаем с рест клиентом, то считываем из res
            try:
                m_To=res['m_To']
                m_Data=res['m_Data']
            except:
                m_To=None
                m_Data=None
        if m_Data is not None and m_To is not None:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    SendMessage(s, int(m_To), int(user.MyId), Messages.M_TEXT, m_Data)
                    if Receive(s).m_Header.m_Type==Messages.M_CONFIRM:
                        user.AddMessage(m_To, user.MyId, m_Data)
                        sysmess="Succes"
                    else:
                        sysmess="Something went wrong"
                        
            except:
                sysmess="Something went wrong, try to Init again"
                

    #Действие получения сообщения            
    if act=="getdata":
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                SendMessage(s, 0, user.MyId, Messages.M_GETDATA)
                m=Receive(s)
                if (m.m_Header.m_Type==Messages.M_TEXT):
                    user.AddMessage(m.m_Header.m_To, m.m_Header.m_From, m.m_Data.decode('utf-8'))
                    #Записываем в наш json_data нужные данные для отправки в рест клиент
                    json_data['result']['id_From']=int(m.m_Header.m_From)
                    json_data['result']['Data']=str(m.m_Data)
                    sysmess='WebClient received a message'
                    
        except: 
            sysmess="Something went wrong, try to Init again"
    
        
    

#тут сама работа
if restFlag==True: #Если мы рабьотаем с рест клиентом, то отправляем jsonContent, который был описан в начале,
#Чтобы программа понимала, что мы будем обмениваться json данными
    Proc(action, jsonContent)
    json_data['sys']=sysmess

    #Здесь мы отправляем рест клиенту наши данные
    print(json.dumps(json_data))
else:
    #Тут работа с веб клиентом
    Proc(action, htmlContent)
    cmd=parse_qs(body)
    #print(cmd['m_Data'][0])
    #print(res)
    #print(restFlag)
    #print('con',console)
    #print('act',action)
    if user.MyId != 0:
        pub = '''
        <form method="post" action="/cgi-bin/Chat.py">
            <input type="text" name="m_To">
            <textarea name="m_Data"></textarea>
            <input type="hidden" name="action" value="publish">
            <input type="submit" value="Send">
        </form>
        '''
        getdt='''
        <form method="get" action="/cgi-bin/Chat.py">
            <input type="hidden" name="action" value="getdata"> 
            <input type="submit" value="Get Data">
        </form>    
        '''
    else:
        pub = ''
        getdt=''


    if user.MyId != 0:
        print('Active User:', user.MyId, '<br>')
    else: 
        print('Press Init For Init to Server', '<br>')
        
    print(LoadTpl('index').format(posts=user.MessList(), publish=pub, getdata=getdt))

