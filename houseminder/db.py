from pymongo import MongoClient

from flask import current_app, g

def get_db(): 
    if 'db' not in g:         
        g.db = MongoClient(current_app.config['MONGO_URI'], tls=True, tlsAllowInvalidCertificates=True)
    return g.db 

def close_db(e=None): 
    db = g.pop('db', None)

    if db is not None: 
        db.close()

def init_app(app): 
    app.teardown_appcontext(close_db)

