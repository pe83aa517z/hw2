import socket, argparse, getpass, time, threading, sys

class client:
    def __init__(self, host='', port=1060):
        self.port = port
        self.host = host
        self.sock = None
        
    def signIn(self):
        self.userName = input('User name:')
        password = getpass.getpass()       
        self.sock.send((self.userName + '\n' + password).encode())
        reply = self.sock.recv(1024).decode()
        return reply
        
    def loginOrRegister(self):
        while True:
            reply = self.signIn()
            if reply == 'new':
                if self.register():
                    break
                continue
            elif reply == 'True':
                break
            print('Username or passward wrong')
        return

    def register(self):
        print('Register....')
        reply = self.signIn()
        if reply == 'Register success':        
            return True
        print('Registration Failed')
        return False

    
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
        try:
            while True:
                data = self.sock.recv(1024).decode()
                if data == 'EOF':
                    self.sock.close()
                    break
                else:
                    print(data)
        except:
            print('Not connect server') 
        print('Logout success')
        sys.exit(0)
            
    def chat(self):
        threading.Thread(None, self.recvMessage).start()
        while True:
            message = input()
            self.sock.send(message.encode())  
                 

class server:
    def __init__(self, host='', port=1060):
        self.port = port
        self.host = host
        self.users = {'Billy':[None, '1234', False, [], ''],
                      'Mark':[None, 'qwer', False, [], ''],
                      'Ada':[None, 'asdf', False, [], '']}
        self.commandDict = {'listuser':'listuser', 'talk':'talk', 'logout':'logout',
                            'send':'send', 'broadcast':'broadcast', 'changeStatus':'changeStatus'}


    #def getUsers(self):
        
    #def setUsers(self):
    
    def listuser(self, uid, arg=[]):
        if arg != []:
            return False
        names = self.users.keys()
        data = ''
        for name in names:
            if self.users[name][2]:
                data += name + ' '
        self.users[uid][0].send(data.encode())
        return True
          
    def talk(self, uid, arg=[]):
        if arg == []:
            return False
        if not self.users[uid][2]:
            return False
        data = ''
        self.users[uid][3].append(uid)
        for name in arg:
            if name in self.users:
                if self.users[name][2]:
                    self.users[uid][3].append(name)
                else:
                    data += name + ' is offline\n'
            else:
                data += name + ' is not find\n'
        if len(self.users[uid][3]) == 1:
            self.users[uid][3] = []
            return False
        for name in self.users[uid][3]:
            if name != uid:
                self.users[name][3] = self.users[uid][3]
        self.users[uid][0].send(data.encode())
        return True
        
        
    def logout(self, uid, arg=[], exce=False, islogin=True):
        if arg != []:
            return False
        if not exce:
            self.users[uid][0].send('EOF'.encode())
        if islogin:
            self.users[uid][0].close()
            self.users[uid][0] = None
            self.users[uid][2] = False
            self.users[uid][3] = []
        return True
        
    def send(self, uid, arg=[]):
        data = uid + ':'
        if len(arg) < 2:
            return False
        for i in range(len(arg)-1):
            data += arg[i+1] + ' '
        if arg[0] in self.users:
            if self.users[arg[0]][0] == None:
                self.users[arg[0]][4] += data +'\n'
            else:
                self.users[arg[0]][0].send(data.encode())
            return True
        return False
        
    def broadcast(self, uid, arg=[]):
        if arg == []:
            return False
        data = uid + ':'
        for i in range(len(arg)):
            data += arg[i] + ' '
        names = self.users.keys()
        for name in names:
            if name != uid:
                if self.users[name][0] != None:
                    self.users[name][0].send(data.encode())
        return True
        
    
    def changeStatus(self, uid, arg=[]):
        if arg != []:
            return False
        self.users[uid][2] = not self.users[uid][2]
        data = 'Is online: ' + str(self.users[uid][2])
        self.users[uid][0].send(data.encode())
        self.users[uid][3] = []
        return True
        
    
    def loginOrRegister(self, sc):
        data = sc.recv(1024).decode()
        data = data.split('\n')
        if data == '':
            return (False,)
        elif data[0] == 'new':
            sc.send('new'.encode())
            data = sc.recv(1024).decode()
            data = data.split()
            if data == '':
                sc.send('fail'.encode())
                return (False,)
            if self.IDConfirmation(data[0], data[1]):
                sc.send('fail'.encode())
                return (False,)
            self.register(sc, data[0], data[1])
            sc.send('Register success'.encode())
            print(data[0]+' is login')
            return (True, data[0])
        if self.IDConfirmation(data[0], data[1]):
            self.setLogin(sc, data[0])
            print(data[0]+' is login')
            sc.send('True'.encode())
            return (True, data[0])
        sc.send('False'.encode())
        return (False,)
    
    def register(self, sc, uid, upw):
        self.users[uid] = [sc, upw, True, [], '']
         
    def setLogin(self, sc, uid):
        self.users[uid][0] = sc
        self.users[uid][2] = True
        
    def IDConfirmation(self, uid, upw):
        if uid in self.users:
            if self.users[uid][1] == upw:
                return True
        return False        
    
    def checkMessage(self, sc, uid):
        data = self.users[uid][4]
        sc.sendall(data.encode())
        
    def sendMessage(self, uid, data):
        data = uid + ':' + data
        offline = []
        for name in self.users[uid][3]:
            if name != uid:
                if self.users[name][2]:
                    self.users[name][0].send(data.encode())
                else:
                    self.users[uid][0].send((name + ' is offline\n').encode())
                    offline.append(name)
        for name in offline:
            self.users[uid][3].remove(name)

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
            uid = 'XXX'
            temp=None
            islogin = False
            while True:
                temp = self.loginOrRegister(sc)
                if temp[0]:
                    break
            islogin = True
            uid = temp[1]
            self.checkMessage(sc, uid)
            while True:
                data = sc.recv(1024).decode()
                if self.insIdentification(data, uid):
                    continue
                self.sendMessage(uid, data)
        except:
            print(uid + ' is over')
            self.logout(uid, [], True, islogin)
            
    def insIdentification(self, text, uid):
        temp = text.split()
        if temp[0] in self.commandDict:
            func = getattr(self, self.commandDict[temp[0]])
            return func(uid, temp[1:])
        return False

def clientInterface(port):
    ci = client('127.0.0.1', port)
    timeout = 0.2
    while True:
        if not ci.connection():
            print('Not connect server')
            timeout *= 2
            time.sleep(3)
            print('connect again...')
            continue
        break
    ci.loginOrRegister()
    print('Welcome!')
    try:
        ci.chat()
    except:
        print('Not connect server')
    
    

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
