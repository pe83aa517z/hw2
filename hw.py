import socket, argparse, getpass, time, threading


class client:
    def __init__(self, host='', port=1060):
        self.port = port
        self.sock = None
        self.host = host
        self.userName =''

    def login(self):
        self.userName = input('User name:')
        password = getpass.getpass()
        
        self.sock.send((self.userName + '\n' + password).encode())
        reply = self.sock.recv(1024).decode()
        return bool(reply=='True')

    def getUsername(self):
        return self.userName

    def connection(self, timeout=0.5):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.settimeout(timeout)
            self.sock.connect((self.host, self.port))
        except:
            self.sock.close()
            return False
        finally:
            self.sock.settimeout(None)
        return True

    def recvMessage(self):
        while True:
            data = self.sock.recv(1024).decode()
            print(data)
        
    def chat(self):
        threading.Thread(None, self.recvMessage).start()
        while True:
            message = input()
            self.sock.send(message.encode())

class server:
 
    userDict = {'Billy':'1234', 'Mark':'qwer', 'Ada':'asdf', 'Afra':'zxcv'}
    userLogin = {}
    messageDict = {}
    
    def __init__(self, host='', port=1060):
        self.port = port
        self.host = host
        
    def listuser(self, sock, arg=None):
        if arg != []:
            return (False,)
        temp = self.getuserLogin()
        names = ''
        keys = temp.keys()
        for ls in keys:
            names += temp[ls][0] +' '
        sock.send(names.encode())
        return (True,)
        
    def talk(self, sock=None, arg=None):
        if len(arg) != 1:
            return (False,)
        if arg[0] in self.getUserDict():
            users = self.getuserLogin()
            users[sock][1] += 1
            hissc = self.getPersonSc(arg[0])         
            if hissc ==None:
                users[sock].append([None, arg[0], ''])
                sock.send('He/She is offline'.encode())
                return (True,)
            users[sock].append([hissc, arg[0], ''])
            return (True,)            
        sock.send('Not find the people'.encode())
        return (False,)

    def getPersonSc(self, arg):
        users = self.getuserLogin()
        keys = users.keys()
        for sc in keys:
            if users[sc][0] == arg:
                return sc
        return None
            

    def logout(self, sock, arg=None):
        if arg != []:
            return (False,)
        ontemp = self.getuserLogin()
        print(ontemp[sock][0]+' is offline')
        keys = ontemp.keys()
        for sc in keys:
            for i in range(len(ontemp[sc])-2):
                if ontemp[sc][2+i][1] == ontemp[sock][0]:
                    sc.send((ontemp[sock][0]+' is offline').encode())
                    ontemp[sc][2+i][0] = None
        for i in range(len(ontemp[sock])-2):
            self.messageDict[ontemp[sock][i+2][1]] = ontemp[sock][i+2][2]
        del ontemp[sock]
        return (True, None)
        
    def send(self, sock, arg=None):
        if len(arg) < 2:
            return (False,)
        users = self.getUserDict()
        ontemp = self.getuserLogin()
        if not self.isInUser(arg[0]):
            return (False,)
        data = ontemp[sock][0] + 'say: '
        for i in range(len(arg)-1):
            data += arg[i+1] + ' '
        keys = ontemp.keys()
        for sc in keys:
            if ontemp[sc][0] == arg[0]:
                try:
                    sc.send(data.encode())
                except:
                    sock.send((arg[0]+' is offline').encode())
                    self.getmessageDict()[arg[0]] = data
                return (True,None,None)
        sock.send((arg[0]+' is offline').encode())
        self.getmessageDict()[arg[0]] = data
        return (True,None,None)

        

    def broadcast(self, sock, arg=None):
        if arg == []:
            return (False,)
        ontemp = self.getuserLogin()
        data = ontemp[sock][0] + 'say: '
        for i in range(len(arg)):
            data += arg[i] + ' '
        ontemp = self.getuserLogin()
        keys = ontemp.keys()
        for sc in keys:
            if sc != sock:
                sc.send(data.encode())
        return (True,None,None)
            

    commandDict = {'listuser':'listuser', 'talk':'talk', 'logout':'logout', 'send':'send', 'broadcast':'broadcast'}

    def isInUser(self, name):
        users = self.getUserDict()
        for i in users:
            if i == name:
                return True
        return False
    
    def getmessageDict(self):
        return self.messageDict

    def getUserDict(self):
        return self.userDict

    def getcommandDict(self):
        return self.commandDict

    def getuserLogin(self):
        return self.userLogin

    def istalk(self, sc):
        return self.getuserLogin()[sc][1]

    def checkMessage(self, sock):
        offtemp = self.getmessageDict()
        ontemp = self.getuserLogin()
        nkeys = offtemp.keys()
        for name in nkeys:
            if name == ontemp[sock][0]:
                sock.send(offtemp[name].encode())
                del offtemp[name]
        keys = ontemp.keys()
        for sc in keys:
            for i in range(len(ontemp[sc])-2):
                if ontemp[sc][i+2][1] == ontemp[sock][0]:
                    ontemp[sc][i+2][0] = sock
                    sock.send(ontemp[sc][i+2][2].encode())
                    ontemp[sc][i+2][2]=''

    def setuserLogin(self, uid, uidSock, mode=1):
        if mode == 1:
            self.userLogin[uidSock] = [uid, 0]
        else:
            del self.userLogin[uidSock]
        
    def startServer(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)

    def waitConnection(self):
        while True:
            sc, scName= self.sock.accept()
            threading.Thread(None, self.service, args=(sc,scName)).start()

            
    def service(self, sc, scName):
        try:
            while True:
                if self.login(sc):
                    break
            self.checkMessage(sc)
            while True:
                data = sc.recv(1024).decode()
                insIFValue = self.insIdentification(data, sc)
                if len(insIFValue) == 2:
                    sc.close()
                    return
                if len(insIFValue) == 3:
                    continue
                if not insIFValue[0]:
                    who = self.istalk(sc)
                    if who != 0:
                        psc = self.getuserLogin()[sc][who+1][0]
                        data = self.getuserLogin()[sc][0] + ' say: '+ data
                        if psc != None:
                            psc.send(data.encode())
                            '''
                            try:
                                psc.send(data.encode())
                            except:
                                self.getuserLogin()[sc][who+1][0] = None
                                self.getuserLogin()[sc][who+1][2] += data+'\n'
                            '''
                        else:
                            
                            self.getuserLogin()[sc][who+1][2] += data+'\n'
        except:
            #print('Client is over')
            self.logout(sc,[])
            
    def insIdentification(self, text, sock):
        temp = text.split()
        comlist = self.getcommandDict()
        if temp[0] in comlist:
            func = getattr(self, comlist[temp[0]])
            return func(sock, temp[1:])
        return (False,)
            
            
    def IDConfirmation(self, uid, upw):
        users = self.getUserDict()
        if uid in users:
            if users[uid] == upw:
                return True
        return False

    def login(self, sc):
        data = sc.recv(1024).decode()
        uid, upw = data.split(None,1)
        if self.IDConfirmation(uid, upw):
            self.setuserLogin(uid, sc, 1)
            print(uid + ' is login')
            sc.send('True'.encode())
            return True
        sc.send('False'.encode())
        return False


def clientInterface(port):
    ci = client('127.0.0.1')
    timeout = 0.5
    while True:
        if not ci.connection(timeout):
            print('Not connect server')
            timeout *= 2
            time.sleep(3)
            print('connect again...')
            continue
        break
    while True:
        if not ci.login():
            print('Username or passward wrong')
            continue
        break
    print('Welcome, ' + ci.getUsername())
    try:
        ci.chat()
    except:
        print('logout')
    finally:
        ci.sock.send('bye'.encode())
        time.sleep(3)
        #ci.sock.close()


def serverInterface(port):
    si = server('',port)
    si.startServer()
    si.waitConnection()
    


if __name__ == '__main__':
    choices = {'client':clientInterface, 'server':serverInterface}
    parser = argparse.ArgumentParser(description='TCP Chat locally')
    parser.add_argument('role', choices=choices, help='which role to play')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port(default 1060)')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.p)
    
