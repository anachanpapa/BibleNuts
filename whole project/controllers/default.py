# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
    user = User(a0 or me)
    if not user or not user.id==me :
        login = 'No'
    else:
        login = 'Yes'      

    #book = 'Gen'     
    #SELECTED = db(Book).select(orderby=KJV.no)
    return locals()


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())
    
def select():
    return locals()

def lookup():
    return locals()    
    

def Questioning():
    import datetime
    import time
    activeNo = int(request.vars.activeNo)
    question = str(request.vars.question)
    
    a = db(db.info.info_name == "total_question").select().first()
    total_question = a.value
    total_question = total_question + 1
    db(db.info.info_name == "total_question").update(value=total_question)
    
    n = User[me].myQuestion_num
    n = n + 1
    db(User.id == me).update(myQuestion_num=n)
    list = User[me].myQuestion_list
    if list == None: list = []
    list.insert(0,n)
    db(User.id == me).update(myQuestion_list=list)
    
    list_all = a.list
    if list_all == None: list_all = []
    list_all.insert(0,total_question)
    db(db.info.info_name == "total_question").update(list=list_all)    
    
    posting = db.question.validate_and_insert(
        vno=activeNo,
        body=question,
        posted_on=datetime.datetime.utcnow(),
        posted_by=me,
        question_no=total_question,
        myQuestion_no=n        
    )
    return

def postReply():
    import datetime
    import time
    import re
    qid = int(request.vars.qid)
    _rid = request.vars.rid
    
    if len(db(Question.id == qid).select()) == 0: return
    reply = str(request.vars.reply)
        
    n = User[me].myReply_num
    n = n + 1
    db(User.id == me).update(myReply_num=n)
    list = User[me].myReply_list
    if list == None: list = []
    list.insert(0,n)
    db(User.id == me).update(myReply_list=list)    
    
    posting = db.reply.validate_and_insert(
        question=qid,
        body=reply,
        posted_on=datetime.datetime.utcnow(),
        posted_by=me,
        myReply_no=n
    )

    if posting.errors: pass
    else:
        question = Question[qid]
        questioner = question.posted_by
        address = User[questioner].email        
        v = db(KJV.vno==question.vno).select().first()
        book = str(v.book)
        chapter = str(v.chapter)
        verse = str(v.verse)
        text = str(v.text)
        qbody = question.body
        qbody = qbody.replace('&nbsp;',' ')
        qbody = re.sub(r'<.+?>', '', qbody) 
        reply = reply.replace('&nbsp;',' ')
        reply = re.sub(r'^\s+', '', reply)
        reply = re.sub(r'<div class="infoArea.+</div>', '', reply) 
        reply = re.sub(r'<blockquote.+</blockquote>', '', reply) 
        reply = re.sub(r'<.+?>', '', reply)
        replyer = str(name_of(User[me]))
        
        mail.send(to=[address],
            subject='BibleNuts.com: you have a reply.',
            message=
            '[ ' + book + ' ' + chapter + ':' + verse + ' ]\n' + 
            text + '\n\n' +
            '[ your question ]' + '\n' +
            qbody + '\n\n' +
            '[ reply from <' + replyer + '> ]' + '\n' +
            reply + '\n\n\n' +
            'Please check: http://www.biblenuts.com/')

        if str(_rid) != 'undef':
            rid = int(_rid)
            rbody = Reply[rid].body
            rbody = rbody.replace('&nbsp;',' ')
            rbody = re.sub(r'^\s+', '', rbody)
            rbody = re.sub(r'<blockquote.+</blockquote>', '', rbody) 
            rbody = re.sub(r'<div class="infoArea.+?</div>', '', rbody) 
            rbody = re.sub(r'<.+?>', '', rbody)
            rby = Reply[rid].posted_by
            raddress = User[rby].email
            qname = str(name_of(questioner))
            mail.send(to=[raddress],
                subject='BibleNuts.com: you have a reply.',
                message=
                '[ ' + book + ' ' + chapter + ':' + verse + ' ]\n' + 
                text + '\n\n' +
                '[ question by <' + qname + '>]' + '\n' +
                qbody + '\n\n' +
                '[ your message ]' + '\n' +
                rbody + '\n\n' +
                '[ reply from <' + str(name_of(User[me])) + '> ]' + '\n' + 
                reply + '\n\n\n' +
                'Please check: http://www.biblenuts.com/')            
            
        time.sleep(0.2)
        reply_num = len(db(Reply.question==qid).select())
        return str(qid) + ":" + str(reply_num)
        
def getQA():
    no = int(request.vars.activeNo)
    book = str(request.vars.book)
    book = books[book]
    chapter = str(request.vars.chapter)
    verse = str(request.vars.verse)

    #_target = str(book) + ":" + str(chapter) + ":" + str(verse)
    _target = book + ":" + chapter + ":" + verse
    data = _target + "&&&"
    
    QAs = db(Question.vno == no).select(orderby=~Question.posted_on)
    flag = 0
    for p in QAs:
        id = str(p.id)
        #reply_num = str(p.reply_num)
        reply_num = str(len(db(Reply.question == p.id).select()))
        posted_on = str(p.posted_on)
        posted_by = str(name_of(p.posted_by))
        body = str(p.body)
        body = MARKMIN(body)
        one = id + "|||" + reply_num + "|||" + posted_on + "|||" + posted_by + "|||" + str(body)
        if flag == 0:
            data = data + one
        else:
            data = data + "<>" + one
        flag = 1    
    return data

def getQA2():
    book = str(request.vars.book)
    chapter = str(request.vars.chapter)
    verse = str(request.vars.verse)
    Qbook = KJV.book==books2[book]
    Qchapter = KJV.chapter==int(chapter)
    Qverse = KJV.verse==int(verse)
    query = Qbook & Qchapter & Qverse 
    target = db(query).select().first()
    vno = target.vno
    _target = str(vno) + ":" + books2[book] + ":" + chapter + ":" + verse
    data = _target + "&&&"
    QAs = db(Question.vno == vno).select(orderby=~Question.posted_on)
    flag = 0
    for p in QAs:
        id = str(p.id)
        #reply_num = str(p.reply_num)
        reply_num = str(len(db(Reply.question == p.id).select()))
        posted_on = str(p.posted_on)
        posted_by = str(name_of(p.posted_by))
        body = str(p.body)
        body = MARKMIN(body)
        one = id + "|||" + reply_num + "|||" + posted_on + "|||" + posted_by + "|||" + str(body)
        if flag == 0:
            data = data + one
        else:
            data = data + "<>" + one
        flag = 1    
    return data    

def getVno():
    book = str(request.vars.book)
    chapter = str(request.vars.chapter)
    verse = str(request.vars.verse)
    Qbook = KJV.book==books2[book]
    Qchapter = KJV.chapter==int(chapter)
    Qverse = KJV.verse==int(verse)
    query = Qbook & Qchapter & Qverse 
    target = db(query).select().first()
    vno = target.vno
    return str(vno)
    
def getReply():
    qid = request.vars.qid
    qid = long(qid)
    Rpls = db(Reply.question == qid).select(orderby=Reply.posted_on)
    data = ""
    flag = 0
    for r in Rpls:
        rid = str(r.id)
        question = str(r.question)
        posted_on = str(r.posted_on)
        posted_by = str(name_of(r.posted_by))
        body = str(r.body)
        body = MARKMIN(body)
        one = rid + "|||" + question + "|||" + posted_on + "|||" + posted_by + "|||" + str(body)
        if data == "":
            data = one
        else:
            data = data + "<>" + one    
    return data

def getMyQuestion():
    import re
    theten = int(request.vars.theten)
    list = User[me].myQuestion_list
        
    if len(list) == 0: 
        return 'no_question'
    else:     
        num = len(list)
        if num%10 == 0:
            decades = num/10
        else:
            decades = num/10+1

        start = list[(theten-1)*10]
        length = len(list)
        if theten*10 > length:
            end = list[length-1]
        else:
            end = list[theten*10-1]
    
        q_my = Question.posted_by == me
        q_st = Question.myQuestion_no <= start
        q_ed = Question.myQuestion_no >= end
        query = q_my & q_st & q_ed
        Qs = db(query).select(orderby=~Question.myQuestion_no)
        Qs_str= str(decades) + "$$$"
        flag = 0
        for q in Qs:
            qid=q.id
            vno=q.vno
            v = db(KJV.vno==vno).select().first()
            book=v.book
            chapter=v.chapter
            verse=v.verse
            on=q.posted_on
            body=str(q.body)
            body = re.sub('<.+?>','',body)
            if len(body) >80: body=body[0:80]+"..."
            #rplNum = q.reply_num
            rplNum = len(db(Reply.question == q.id).select())
            line = str(qid)+"|||"+str(vno)+"|||"+str(book)+"|||"+str(chapter)+"|||"+str(verse)+"|||"+str(on)+"|||"+body+"|||"+str(rplNum)
            if flag == 0: Qs_str = Qs_str + line
            else: Qs_str = Qs_str + '<>' + line
            flag = 1
        return Qs_str 

def getMyReply():
    import re
    theten = int(request.vars.theten)
    list = User[me].myReply_list
        
    if len(list) == 0: 
        return 'no_reply'
    else:     
        num = len(list)
        if num%10 == 0:
            decades = num/10
        else:
            decades = num/10+1

        start = list[(theten-1)*10]
        length = len(list)
        if theten*10 > length:
            end = list[length-1]
        else:
            end = list[theten*10-1]
    
        r_my = Reply.posted_by == me
        r_st = Reply.myReply_no <= start
        r_ed = Reply.myReply_no >= end
        query = r_my & r_st & r_ed
        Rs = db(query).select(orderby=~Reply.myReply_no)
        Rs_str= str(decades) + "$$$"
        flag = 0
        for r in Rs:
            rid=r.id
            qid=r.question
            vno=qid.vno
            v = db(KJV.vno==vno).select().first()
            book=v.book
            chapter=v.chapter
            verse=v.verse
            on=r.posted_on
            body=str(r.body)
            body = re.sub('<.+?>','',body)
            if len(body) >80: body=body[0:80]+"..."
            line = str(rid)+"|||"+str(qid)+"|||"+str(vno)+"|||"+str(book)+"|||"+str(chapter)+"|||"+str(verse)+"|||"+str(on)+"|||"+body
            if flag == 0: Rs_str = Rs_str + line
            else: Rs_str = Rs_str + '<>' + line
            flag = 1
        return Rs_str 

def deleteQuestion():
    qid = int(request.vars.qid)
    list = User[me].myQuestion_list
    delno = Question[qid].myQuestion_no
    list.remove(delno)
    db(User.id == me).update(myQuestion_list=list)    

    a = db(db.info.info_name == "total_question").select().first()
    list_all = a.list
    delno_all = Question[qid].question_no
    list_all.remove(delno_all)
    db(db.info.info_name == "total_question").update(list=list_all)
    
    db(Question.id==qid).delete()
    
    return
    
def deleteReply():
    rid = int(request.vars.rid)
    list = User[me].myReply_list
    delno = Reply[rid].myReply_no
    list.remove(delno)
    db(User.id == me).update(myReply_list=list)
    db(Reply.id==rid).delete()    
    return

def getRcQueston():
    theten = int(request.vars.theten)
    a = db(db.info.info_name == "total_question").select().first()
    list_all = a.list
    total_question_num = a.value
    
    num = len(list_all)
    if num%10 == 0:
        decades = num/10
    else:
        decades = num/10+1
    
    start = list_all[(theten-1)*10]
    if theten*10 > num:
        end = list_all[num-1]
    else:
        end = list_all[theten*10-1]
        
    q_st = Question.question_no <= start
    q_ed = Question.question_no >= end
    query = q_st & q_ed

    Qs = db(query).select(orderby=~Question.question_no)
   
    Qs_str= str(decades) + "$$$"    
    flag = 0
    for result in Qs:
        qid = result.id    
        on = result.posted_on
        by = result.posted_by
        by = name_of(by)
        vno = result.vno
        v = db(KJV.vno==vno).select().first()
        book=v.book
        fbook = books[book]
        chapter=v.chapter
        verse=v.verse
        text = v.text
        body = result.body
        rplNum = len(db(Reply.question == result.id).select())
        question_no = result.question_no
        line =  str(vno) + "|||" + str(on) + "|||" + str(by) + "|||" + str(book) + "|||" + str(fbook) + "|||" + str(chapter) + "|||" + str(verse) + "|||" + str(text) + "|||" + str(rplNum) + "|||" + str(body) + "|||" + str(qid) + "|||" + str(question_no) 
        if flag == 0: Qs_str = Qs_str + line
        else: Qs_str = Qs_str + '<>' + line
        flag = 1
    return Qs_str
 
def get_biblia_key():
    return '155c4187b8bc42a8c935672b83bcbe7d'
 
def Gen(): return dict(form=auth())
def Exo(): return dict(form=auth())
def Lev(): return dict(form=auth())
def Num(): return dict(form=auth())
def Deu(): return dict(form=auth())
def Jos(): return dict(form=auth())
def Jdg(): return dict(form=auth())
def Rut(): return dict(form=auth())
def Sa1(): return dict(form=auth())
def Sa2(): return dict(form=auth())
def Kg1(): return dict(form=auth())
def Kg2(): return dict(form=auth())
def Ch1(): return dict(form=auth())
def Ch2(): return dict(form=auth())
def Ezr(): return dict(form=auth())
def Neh(): return dict(form=auth())
def Est(): return dict(form=auth())
def Job(): return dict(form=auth())
def Psa(): return dict(form=auth())
def Pro(): return dict(form=auth())
def Ecc(): return dict(form=auth())
def Sol(): return dict(form=auth())
def Isa(): return dict(form=auth())
def Jer(): return dict(form=auth())
def Lam(): return dict(form=auth())
def Eze(): return dict(form=auth())
def Dan(): return dict(form=auth())
def Hos(): return dict(form=auth())
def Joe(): return dict(form=auth())
def Amo(): return dict(form=auth())
def Oba(): return dict(form=auth())
def Jon(): return dict(form=auth())
def Mic(): return dict(form=auth())
def Nah(): return dict(form=auth())
def Hab(): return dict(form=auth())
def Zep(): return dict(form=auth())
def Hag(): return dict(form=auth())
def Zac(): return dict(form=auth())
def Mal(): return dict(form=auth())
def Mat(): return dict(form=auth())
def Mar(): return dict(form=auth())
def Luk(): return dict(form=auth())
def Joh(): return dict(form=auth())
def Act(): return dict(form=auth())
def Rom(): return dict(form=auth())
def Co1(): return dict(form=auth())
def Co2(): return dict(form=auth())
def Gal(): return dict(form=auth())
def Eph(): return dict(form=auth())
def Phi(): return dict(form=auth())
def Col(): return dict(form=auth())
def Th1(): return dict(form=auth())
def Th2(): return dict(form=auth())
def Ti1(): return dict(form=auth())
def Ti2(): return dict(form=auth())
def Tit(): return dict(form=auth())
def Plm(): return dict(form=auth())
def Heb(): return dict(form=auth())
def Jam(): return dict(form=auth())
def Pe1(): return dict(form=auth())
def Pe2(): return dict(form=auth())
def Jo1(): return dict(form=auth())
def Jo2(): return dict(form=auth())
def Jo3(): return dict(form=auth())
def Jde(): return dict(form=auth())
def Rev(): return dict(form=auth())

def Gen_2(): return dict(form=auth())
def Exo_2(): return dict(form=auth())
def Lev_2(): return dict(form=auth())
def Num_2(): return dict(form=auth())
def Deu_2(): return dict(form=auth())
def Jos_2(): return dict(form=auth())
def Jdg_2(): return dict(form=auth())
def Rut_2(): return dict(form=auth())
def Sa1_2(): return dict(form=auth())
def Sa2_2(): return dict(form=auth())
def Kg1_2(): return dict(form=auth())
def Kg2_2(): return dict(form=auth())
def Ch1_2(): return dict(form=auth())
def Ch2_2(): return dict(form=auth())
def Ezr_2(): return dict(form=auth())
def Neh_2(): return dict(form=auth())
def Est_2(): return dict(form=auth())
def Job_2(): return dict(form=auth())
def Psa_2(): return dict(form=auth())
def Pro_2(): return dict(form=auth())
def Ecc_2(): return dict(form=auth())
def Sol_2(): return dict(form=auth())
def Isa_2(): return dict(form=auth())
def Jer_2(): return dict(form=auth())
def Lam_2(): return dict(form=auth())
def Eze_2(): return dict(form=auth())
def Dan_2(): return dict(form=auth())
def Hos_2(): return dict(form=auth())
def Joe_2(): return dict(form=auth())
def Amo_2(): return dict(form=auth())
def Oba_2(): return dict(form=auth())
def Jon_2(): return dict(form=auth())
def Mic_2(): return dict(form=auth())
def Nah_2(): return dict(form=auth())
def Hab_2(): return dict(form=auth())
def Zep_2(): return dict(form=auth())
def Hag_2(): return dict(form=auth())
def Zac_2(): return dict(form=auth())
def Mal_2(): return dict(form=auth())
def Mat_2(): return dict(form=auth())
def Mar_2(): return dict(form=auth())
def Luk_2(): return dict(form=auth())
def Joh_2(): return dict(form=auth())
def Act_2(): return dict(form=auth())
def Rom_2(): return dict(form=auth())
def Co1_2(): return dict(form=auth())
def Co2_2(): return dict(form=auth())
def Gal_2(): return dict(form=auth())
def Eph_2(): return dict(form=auth())
def Phi_2(): return dict(form=auth())
def Col_2(): return dict(form=auth())
def Th1_2(): return dict(form=auth())
def Th2_2(): return dict(form=auth())
def Ti1_2(): return dict(form=auth())
def Ti2_2(): return dict(form=auth())
def Tit_2(): return dict(form=auth())
def Plm_2(): return dict(form=auth())
def Heb_2(): return dict(form=auth())
def Jam_2(): return dict(form=auth())
def Pe1_2(): return dict(form=auth())
def Pe2_2(): return dict(form=auth())
def Jo1_2(): return dict(form=auth())
def Jo2_2(): return dict(form=auth())
def Jo3_2(): return dict(form=auth())
def Jde_2(): return dict(form=auth())
def Rev_2(): return dict(form=auth())
    
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for e xample:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

def importKJV():
    import csv
    k = int(request.vars.k)
    filename = "kjv.csv"
    csvfile = open(filename)
    reader = csv.reader(csvfile)    
    list = []
    for line in reader:
		list.append(line)
    
    st = k*100
    ed = (k+1)*100
    finish = 'no'
    if ed > len(list): 
        ed = len(list)
        finish = 'yes'
    for i in range(st,ed):
        target = list[i]
        vno = int(target[0])
        book = str(target[1])
        chapter = int(target[2])
        verse = int(target[3])
        text = str(target[4])
            
        versein = db.kjv.validate_and_insert(
            vno=vno,
            book=book,
            chapter=chapter,
            verse=verse,
            text=text        
        )        
    csvfile.close()
    if finish == 'yes': return 'finish'
    return k+1

