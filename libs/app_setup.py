
import keyring



class AppSetup():
    """This class will check wether the current system contains a keyring named
    'rouser', rouser is contained, get the rh username, then request the password
    if not then register 'rouser'

    In Keyring:
        -Username is stored in 'rhuser'
        -password is stored in 'robinhood',rhuser
    """

    def __init__(self):
        """Start the engine and check if the user exist in keyring"""
        self.checkifUserExist()

    def setRobinhoodUserName(self, username):
        """ This method hides the rh plain text user name """
        
        keyring.set_password('rhuser','rhuser',username)
        print('[+] username successfully stored')
    
    def setRobinhoodPassword(self,username, password):
        keyring.set_password('robinhood',username,password)
    
    def getRobinhoodUserName(self):
        """hides plain text rohin hood user name"""
        return keyring.get_password('rhuser','rhuser')

    def getRobinhoodPassword(self):
        return self._getRobinhoodPassword(self.getRobinhoodUserName())

    def _getRobinhoodPassword(self, username):
        return keyring.get_password('robinhood',username)
    
    def changeUserData(self,usr,password):
        """Changes the current keychain saved user data"""
        self.setRobinhoodUserName( usr)
        self.setRobinhoodPassword(usr,password)


    def checkifUserExist(self):
        if keyring.get_password('rhuser','rhuser') == None:
            print('[+] please enter valid user auth data')
            username = str(input("Please Enter your username: "))
            self.setRobinhoodUserName(username)

            password = str(input("Please Enter your password: "))
            self.setRobinhoodPassword(self.getRobinhoodUserName(), password)

            print('[+] Successfully added robinhood user')
        else:
            print("[+] User exist")

    def removeAllPasswords(self):
        """This method cleans up after itself, all hidden passwords
        including rhuser, rohinhood username, robinhood password are deleted"""
        #get the plain text user name
        user = keyring.get_password('rhuser','rhuser')
        #delete the rh password 
        try:
            if not keyring.get_password('robinhood',user) == None: 
                keyring.delete_password('robinhood',user)

            #delete the concelded version

            keyring.delete_password('rhuser','rhuser')
        except Exception as e:
            print(e)

    def cleanUp(self):
        """Facade method for the interface """
        print("[-] Cleaning up all passwords created ...")
        self.removeAllPasswords()
def test():
    x = AppSetup()
    import time
    #time.sleep(30)
    print(x.getRobinhoodUserName())
    print(x.getRobinhoodPassword())
    x.cleanUp()


#test()
