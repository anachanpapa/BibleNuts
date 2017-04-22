# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    from google.appengine.api import memcache

    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
auth.settings.extra_fields['auth_user']= [
    Field('myQuestion_num', 'integer', default=0, readable=False, writable=False),
    Field('myQuestion_list', 'list:integer', readable=False, writable=False),
    Field('myReply_num', 'integer', default=0, readable=False, writable=False),
    Field('myReply_list', 'list:integer', readable=False, writable=False)
]

crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'gae'
mail.settings.sender = 'info.pbsn@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

db.define_table('kjv',
    Field('vno', 'integer', readable=False, writable=False),
    Field('book', 'string', length=12, readable=False, writable=False),
    Field('chapter', 'integer', readable=False, writable=False),
    Field('verse', 'integer', readable=False, writable=False),
    Field('text', 'text', requires=IS_LENGTH(1028), readable=False, writable=False))

db.define_table('question',
    Field('vno', 'integer',  readable=False, writable=False),
    Field('body', 'text', requires=IS_NOT_EMPTY(), label='Please share your question about this verse (up to 2000 letters)'),
    Field('posted_on', 'datetime', readable=False, writable=False),
    Field('posted_by', 'reference auth_user', readable=False, writable=False),
    Field("question_no",  'integer', default=0, readable=False, writable=False),
    Field("myQuestion_no",  'integer', default=0, readable=False, writable=False),
    Field("finish_flag",  'integer', default=0, readable=False, writable=False),
    Field("delete_flag",  'integer', default=0, readable=False, writable=False))

db.define_table('reply',
    Field('question', 'reference question',  readable=False, writable=False),
    Field('body', 'text', requires=IS_NOT_EMPTY(), label='Please share your question about this verse (up to 2000 letters)'),
    Field('posted_on', 'datetime', readable=False, writable=False),
    Field('posted_by', 'reference auth_user', readable=False, writable=False),
    Field("myReply_no",  'integer', default=0, readable=False, writable=False),
    Field("finish_flag",  'integer', default=0, readable=False, writable=False),
    Field("delete_flag",  'integer', default=0, readable=False, writable=False))

db.define_table('info',
    Field("info_name",  'string', readable=False, writable=False),
    Field("value",  'integer', default=0, readable=False, writable=False),
    Field('list', 'list:integer', readable=False, writable=False))

a =  db(db.info.info_name == "total_question").select()   
if len(a) == 0: init_info = db.info.validate_and_insert(info_name="total_question", value=0)    
    
def name_of(user): return '%(first_name)s %(last_name)s' % user
    
## after defining tables, uncomment below to enable auditing
auth.enable_record_versioning(db)

KJV = db.kjv
User = db.auth_user
Question = db.question
Reply = db.reply
Info = db.info
me, a0, a1 = auth.user_id, request.args(0), request.args(1)

books = {
'Gen':'Genesis',
'Exo':'Exodus',
'Lev':'Leviticus',
'Num':'Numbers',
'Deu':'Deuteronomy',
'Jos':'Joshua',
'Jdg':'Judges',
'Rut':'Ruth',
'Sa1':'1 Samuel',
'Sa2':'2 Samuel',
'Kg1':'1 Kings',
'Kg2':'2 Kings',
'Ch1':'1 Chronicles',
'Ch2':'2 Chronicles',
'Ezr':'Ezra',
'Neh':'Nehemiah',
'Est':'Esther',
'Job':'Job',
'Psa':'Psalm',
'Pro':'Proverbs',
'Ecc':'Ecclesiastes',
'Sol':'Song of Solomon',
'Isa':'Isaiah',
'Jer':'Jeremiah',
'Lam':'Lamentations',
'Eze':'Ezekiel',
'Dan':'Daniel',
'Hos':'Hosea',
'Joe':'Joel',
'Amo':'Amos',
'Oba':'Obadiah',
'Jon':'Jonah',
'Mic':'Micah',
'Nah':'Nahum',
'Hab':'Habakkuk',
'Zep':'Zephaniah',
'Hag':'Haggai',
'Zac':'Zechariah',
'Mal':'Malachi ',
'Mat':'Matthew',
'Mar':'Mark',
'Luk':'Luke',
'Joh':'John',
'Act':'Acts',
'Rom':'Romans',
'Co1':'1 Corinthians',
'Co2':'2 Corinthians',
'Gal':'Galatians',
'Eph':'Ephesians',
'Phi':'Philippians',
'Col':'Colossians',
'Th1':'1 Thessalonians',
'Th2':'2 Thessalonians',
'Ti1':'1 Timothy',
'Ti2':'2 Timothy',
'Tit':'Titus',
'Plm':'Philemon',
'Heb':'Hebrews',
'Jam':'James',
'Pe1':'1 Peter',
'Pe2':'2 Peter',
'Jo1':'1 John',
'Jo2':'2 John',
'Jo3':'3 John',
'Jde':'Jude',
'Rev':'Revelation'}

books2 = {
'Genesis':'Gen',
'Exodus':'Exo',
'Leviticus':'Lev',
'Numbers':'Num',
'Deuteronomy':'Deu',
'Joshua':'Jos',
'Judges':'Jdg',
'Ruth':'Rut',
'1 Samuel':'Sa1',
'2 Samuel':'Sa2',
'1 Kings':'Kg1',
'2 Kings':'Kg2',
'1 Chronicles':'Ch1',
'2 Chronicles':'Ch2',
'Ezra':'Ezr',
'Nehemiah':'Neh',
'Esther':'Est',
'Job':'Job',
'Psalm':'Psa',
'Proverbs':'Pro',
'Ecclesiastes':'Ecc',
'Song of Solomon':'Sol',
'Isaiah':'Isa',
'Jeremiah':'Jer',
'Lamentations':'Lam',
'Ezekiel':'Eze',
'Daniel':'Dan',
'Hosea':'Hos',
'Joel':'Joe',
'Amos':'Amo',
'Obadiah':'Oba',
'Jonah':'Jon',
'Micah':'Mic',
'Nahum':'Nah',
'Habakkuk':'Hab',
'Zephaniah':'Zep',
'Haggai':'Hag',
'Zechariah':'Zac',
'Malachi ':'Mal',
'Matthew':'Mat',
'Mark':'Mar',
'Luke':'Luk',
'John':'Joh',
'Acts':'Act',
'Romans':'Rom',
'1 Corinthians':'Co1',
'2 Corinthians':'Co2',
'Galatians':'Gal',
'Ephesians':'Eph',
'Philippians':'Phi',
'Colossians':'Col',
'1 Thessalonians':'Th1',
'2 Thessalonians':'Th2',
'1 Timothy':'Ti1',
'2 Timothy':'Ti2',
'Titus':'Tit',
'Philemon':'Plm',
'Hebrews':'Heb',
'James':'Jam',
'1 Peter':'Pe1',
'2 Peter':'Pe2',
'1 John':'Jo1',
'2 John':'Jo2',
'3 John':'Jo3',
'Jude':'Jde',
'Revelation':'Rev'}