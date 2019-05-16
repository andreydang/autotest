import sqlite3,requests,json
from robot.api import logger


DATABASE='.\\..\\\web\\clients.db'
BASE_URL='http://localhost:5000'
HEADERS = {'User-Agent': 'Mozilla/5.0','Content-Type': 'application/json'}


def select_client_with_balance():
    """Выбор клиента с положительным балансом и не полным набором услуг ,если его нету то он будет создан"""
    balance_cli=5
    conn = sqlite3.connect(DATABASE)
    with conn:
        curs = conn.cursor()
        curs.execute("SELECT cl.CLIENT_ID,bl.BALANCE from CLIENTS cl "
                     "inner join BALANCES bl where "
                     "cl.CLIENT_ID=bl.CLIENTS_CLIENT_ID and bl.BALANCE>0 and"
                     " (select count(SERVICE_ID) from SERVICES)!=(SELECT count"
                     "(SERVICES_SERVICE_ID) from CLIENT_SERVICE WHERE CLIENTS_CLIENT_ID =cl.CLIENT_ID)")
        clients_with_balance=curs.fetchall()

        if clients_with_balance:
            client_id=clients_with_balance[0][0]
            balance_client=clients_with_balance[0][1]
            logger.info([client_id,balance_client])
            return client_id
        if len(clients_with_balance) == 0:

            curs.execute("SELECT max(CLIENT_ID)+1 FROM CLIENTS")
            id_cli=curs.fetchone()[0]

            curs.execute("INSERT INTO CLIENTS(CLIENT_ID,CLIENT_NAME) VALUES"
                         " ({client_id},'Andrey Martynenko')".format(client_id=id_cli))
            curs.execute("INSERT INTO BALANCES (CLIENTS_CLIENT_ID,BALANCE)"
                         " VALUES ({client_id},{balance_cl})".format(client_id=id_cli,balance_cl=balance_cli))

            conn.commit()
            curs.execute("SELECT cl.CLIENT_ID,bl.BALANCE from CLIENTS cl "
                         "inner join BALANCES bl where "
                         "cl.CLIENT_ID=bl.CLIENTS_CLIENT_ID and cl.CLIENT_ID=({client_id})".format(client_id=id_cli))
            clients_with_balance_added=curs.fetchone()
            logger.info("Создан новый клиент")
            logger.info(clients_with_balance_added)
            return clients_with_balance_added[0]


def client_balance(client_id):
    """Баланс клиента"""
    conn = sqlite3.connect(DATABASE)
    with conn:
        curs = conn.cursor()
        curs.execute("SELECT BALANCE from BALANCES where CLIENTS_CLIENT_ID={client_id}".format(client_id=client_id))
        balance=curs.fetchone()
    logger.info(balance[0])
    return balance[0]


def check_connected_service(client_id,service_id):
    """Проверка подключенной услуги клиенту в бд"""
    conn = sqlite3.connect(DATABASE)
    with conn:
        curs = conn.cursor()
        curs.execute("select SERVICES_SERVICE_ID from CLIENT_SERVICE where CLIENTS_CLIENT_ID={client_id} and"
                     " SERVICES_SERVICE_ID={service_id}".format(client_id=client_id,service_id=service_id))
        service=curs.fetchone()
    return service[0]


def req_post_list_service(client_id):
    """Список подключенных услуг клиенту"""
    response = requests.post(BASE_URL + '/client/services',data=json.dumps({"client_id":client_id}),headers=HEADERS)
    logger.info(response.json()['items'])
    return response.json()['items']


def req_get_list_service():
    """Полный список услуг"""
    response = requests.get(BASE_URL + '/services')
    logger.info(response.json()['items'])
    return response.json()['items']


def req_post_add_service(client_id,service_id):
    """Подключение услуги клиенту"""
    response = requests.post(BASE_URL + '/client/add_service',
                             data=json.dumps({"client_id":client_id,"service_id":service_id}),headers=HEADERS)
    return response.status_code


def list_unconnected_service(client_id):
    """Список неподключенных услуг клиенту"""
    list_unconnected_n=[]
    full_list_service=requests.get(BASE_URL + '/services').json()['items']
    list_connected=requests.post(BASE_URL + '/client/services',data=json.dumps({"client_id":client_id})
                                 ,headers=HEADERS).json()['items']
    list_unconnected = [x for x in full_list_service if x not in list_connected]
    for unconnected_service in list_unconnected:
        id,cost=unconnected_service['id'],unconnected_service['cost']
        list_unconnected_n.append({'id':id,'cost':cost})
    logger.info(list_unconnected_n)
    return list_unconnected_n[0]['id']



def cost_service(service_id):
    """Стоимость услуги"""
    response = requests.get(BASE_URL + '/services').json()['items']
    return [service['cost'] for service in response if service['id'] == service_id][0]


def check_connected_service_api(client_id,service_id):
    """Проверка подключенной услуги клиенту через API"""
    response = requests.post(BASE_URL + '/client/services',data=json.dumps({"client_id":client_id})
                             ,headers=HEADERS).json()['items']
    return [True for service in response if service['id'] == service_id][0]
