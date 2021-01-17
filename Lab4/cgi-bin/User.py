
import json
import random
import time
import pickle
from Message import Message

class User:
    DateBase = 'Info.db'
    
    def __init__(self):
        try:
            self.load()
        except:
            self.MyId=0
            self.Posts={"posts": []}
            self.store()
                
    def load(self):
        with open(self.DateBase, 'rb') as f:
            (self.MyId, self.Posts) = pickle.load(f)
    
    def store(self):
        with open(self.DateBase, 'wb') as f:
            pickle.dump((self.MyId, self.Posts), f) 

         
    def register(self, ID):
        self.MyId=ID
        self.store()
        

    def find(self):
        if self.MyId==0:
            return True
        else: return False
        
    def AddMessage(self, To, From, Data):
        self.load()
        self.Posts["posts"].append({'From': int(From), 'To': int(To), 'Data': Data})
        self.store()
    
    
    def MessList(self):
        self.load()
        posts=[]
        for post in self.Posts["posts"]:
            content='Message from '+str(post['From'])+' to client '+str(post['To'])+': '+post['Data']
            posts.append(content)
        return '<br>'.join(posts)
        
    