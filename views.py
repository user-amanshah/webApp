import bcrypt , uuid# from model import db, User1, UserSchema
from model import db, Credential, Credentialschema , Credentialschema1 ,Bills, Billschema , Bills_schema,File,Fileschema,File_schema_output
from flask import Flask, jsonify, request, Response
import threading
import re, json , datetime
import hashlib, shutil
from werkzeug.utils import secure_filename
import os , boto3,time
import  psycopg2
import statsd
import bcrypt , uuid
import logging


"""instantiate statsd client to enable logging """
c = statsd.StatsClient('localhost',8125)

"""initialise flask environment to the current module """
app = Flask(__name__)

"""enable log configuration and put logging level to info """
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()
logger.addHandler(logging.FileHandler('logger.txt', 'a'))  # console all logs in a text file for cloudwatch

print = logger.info         # replacing stdout print with logger 


"""get all env variables"""
driver = 'postgresql+psycopg2://'
bucket=os.environ['S3BUCKET_NAME']
db_user= os.environ['RDS_USERNAME']
print(db_user)
db_host= os.environ['RDSHOST_NAME']
print(db_host)
db_pass=os.environ['RDS_PASSWORD']
print(db_pass)
db_name=os.environ['RDS_DBNAME']
app.logger.info(db_name)
app.config['SQLALCHEMY_DATABASE_URI'] = driver+db_user+':'+db_pass+'@'+db_host+'/'+db_name
print(app.config['SQLALCHEMY_DATABASE_URI'])
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/signin'
# app.config['SQLALCHEMY_DATABASE_URI'] =  'postgresql://postgres@localhost/circle_test'
# app.config['UPLOAD_FOLDER']="/home/aman/IdeaProjects/circleCI/attachments/"

root_dir = os.path.dirname(os.path.abspath(__file__))

db.init_app(app)



""" function to prepare response data type and http status code"""

def custom_http_code(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )


""" authentication"""
def checkauthentication(useremail,password):
    user_sc = Credentialschema1()
    result=Credential.select_user_by_email(useremail)
    data = user_sc.dump(result)
    pwd_db=data.get('password')

    flag=bcrypt.checkpw(password.encode('utf8'),pwd_db.encode())
    return flag

#welome page route
@app.route('/', methods=['GET'])
def hello():
    start=time.time()
    page="hello world"
    page2="this is homepage"
    page=page+page2
    c.incr("homecount")
    dur=(time.time()-start)*1000
    c.timing("hometime",dur)
    return  page

#POST user data as sign in method
"""
IN each route instantiate two metrics , couter and timer for starting metric calculation
"""
@app.route('/v1/user', methods=['POST'])
def page():

    start=time.time()
    db.create_all()
    user_sc = Credentialschema(many=False)
    dur=(time.time()-start)*1000
    c.timing("dbconnect",dur)

    data = request.get_json()
    check_email = data.get('email_address')
    check_pass = data.get('password')

    #check if valid email
    def check(emailid):
        regexp = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if re.search(regexp, emailid):
            return True

        else:
            return False
    flagging = check(check_email)

    
    def checkpass(passwd):
        if len(passwd) <= 7:
            return False
        elif not re.search("[A-Z]", passwd):
            return False
        elif not re.search("[0-9]", passwd):
            return False
        return True

    flagging1 = checkpass(check_pass)
    dbtime=time.time()
    if Credential.select_user_by_email(check_email):
        dur=(time.time()-dbtime)*1000
        c.timing("dbconnect",dur)

        return custom_http_code('Bad resquest',400)

    if flagging==False or flagging1==False:
        return  custom_http_code('Bad request',400)
    else:
        load_data = user_sc.load(data)
        new_user = Credential(load_data)
        # Credential.execute_query()
        dbtime=time.time()
        db.session.add(new_user)
        db.session.commit()

        dur=(time.time()-dbtime)*1000
        c.timing("dbconnect",dur)


        #   result=Credential.query.filter_by(first_name='Jane').first()
        result= Credential.select_user_by_email(check_email)
        print(result)
        data = user_sc.dump(result)
        print(data)
        # output=Credential.select_user_by_email(check_email)
        print("done")
        c.incr("createuser")
        dur=(time.time()-start)*1000
        c.timing("createusertime",dur)
        return jsonify(data)

"""
basic auth type authentication to retriever credential
"""

@app.route('/v1/user/self', methods=['GET'])
def getinfo():
    start=time.time()
    username = request.authorization.username
    passwordinfo = request.authorization.password


    user_sc = Credentialschema(many=False)
    dbtime=time.time()
    flag=checkauthentication(username,passwordinfo)
    dur=(time.time()-dbtime)*1000
    c.timing("dbconnect",dur)
    #if flag==True:


    #auth=Credential.select_user_by_email(username)
    if flag==True:
        dbtime=time.time()
        data = user_sc.dump(Credential.select_user_by_email(username))
        dur=(time.time()-dbtime)*1000
        c.timing("dbconnect",dur)
        # output=Credential.select_user_by_email(check_email)
        print("done")
        dur=(time.time()-start)*1000
        c.timing("getusertime",dur)

        c.incr("getusercount")
        return jsonify(data)

    else:
        c.incr("getusercount")
        return custom_http_code('Unauthorized',401)


@app.route('/v1/user/self', methods=['PUT'])
def updateinfo():
    start=time.time()
    username = request.authorization.username
    passwordinfo = request.authorization.password
    user_sc = Credentialschema(many=False)
    #auth=Credential.select_user_by_emailandpass(username,passwordinfo)
    dbtime=time.time()
    flag=checkauthentication(username,passwordinfo)
    dur=(time.time()-dbtime)*1000
    c.timing("dbconnect",dur)



    if flag==True:
        user_sc = Credentialschema(many=False)
        data = request.get_json()
        # id=data.get('email_address')
        accountupdated_date=datetime.datetime.now().isoformat()
        password_new = data.get('password')

        pwd=bcrypt.hashpw(password_new.encode('utf8'),bcrypt.gensalt())
        pwd=str(pwd,'utf-8')
        # self.password=pwd



        firstname = data.get('first_name')
        lastname=data.get('last_name')
        date1=data.get('account_created')
        date2=data.get('account_modified')

        def checkpass(passwd):

            if len(passwd) <= 7:
                return False
            elif not re.search("[A-Z]", passwd):
                return False
            elif not re.search("[0-9]", passwd):
                return False
            return True

        flagging1 = checkpass(password_new)


        fetch_keys = list(data.keys())
        if ("account_updated" in fetch_keys  or "account_created" in fetch_keys):
            return custom_http_code({'Bad request'}, 400)



        elif flagging1==True:

            schema_of_partial =user_sc.load(data,partial=True)

            #stmt=db.session.update().where(Credential.c.email_address==id).values(password=password_new, first_name= firstname, last_name=last_name,account_updated=account_updated_date,)

            # Credential.first_name=firstname
            # Credential.
            # Credential.last_name

            # Credential.updating(data)
            # db.session.commit()

            dbtime=time.time()
            state = Credential.query.filter_by(email_address=username).update(dict(password=pwd,first_name=firstname,last_name=lastname))


            #    db.session.update(first_name=firstname)
            db.session.commit()
            dur=(time.time()-dbtime)*1000
            c.timing("dbconnect",dur)


            dur=(time.time()-start)*1000
            c.timing("putusertime",dur)
            c.incr("putuserapi")
            return custom_http_code('done update',204)

        else:

            c.incr("putuserapi")
            dur=(time.time()-start)*1000
            c.timing("putusertime",dur)
            return custom_http_code('bad request',400)

    else:
        return custom_http_code("not authorized",401)



@app.route('/v1/bill', methods=['POST'])
def billcreate():
    #db.create_all()
    start=time.time()
    username = request.authorization.username
    passwordinfo = request.authorization.password
    bill_sc = Billschema(many=False)
    data = request.get_json()
    dbtime=time.time()
    flag=checkauthentication(username,passwordinfo)
    dur=(time.time()-dbtime)*1000
    c.timing("dbconnect",dur)


    if flag==True:
        # file = request.files['file']
        #

        data1 = request.get_json()
        list_var=data1["categories"]
        list_var=str(list_var)
        list_var=((list_var.strip("[")).strip("]")).strip("'")
        data1["categories"]=list_var



        result=Credential.select_user_by_email(username)
        user_sc = Credentialschema()
        #user_sc = Credentialschema(many=False)
        bill_scs = Billschema(many=False)
        data = user_sc.dump(result)
        owner_id=data.get('id')
        #data=str(owner_id)
        id=str(uuid.uuid4().hex)

        load_data = bill_sc.load(data1)
        new_bill = Bills(load_data,id,owner_id)

        dbtime=time.time()
        db.session.add(new_bill)
        db.session.commit()
        dur=(time.time()-dbtime)*1000
        c.timing("dbconnect",dur)

        result=Bills.select_user_by_billid(id)
        print(owner_id)
        print(id)
        if result:
            print("there")
        else:
            print("empt")
        data = bill_sc.dumps(result)
        # print(result)
        # print(data)
        # # output=Credential.select_user_by_email(check_email)
        # print("done")

        attachmentfile= {}

        final=json.loads(data)
        final["attachments"]=attachmentfile


        c.incr("postbillcount")
        dur=(time.time()-start)*1000
        c.timing("postbilltime",dur)
        return custom_http_code(final,200)

    else:
        c.incr("postbillcount")
        dur=(time.time()-start)*1000
        c.timing("postbilltime",dur)
        return custom_http_code("not authorized",401)


@app.route('/v1/bills', methods=['GET'])
def getallbills():
    start=time.time()
    username = request.authorization.username
    passwordinfo = request.authorization.password
    bill_sc = Billschema(many=False)
    data = request.get_json()
    dbtime=time.time()
    flag=checkauthentication(username,passwordinfo)
    dur=(time.time()-dbtime)*1000
    c.timing("dbconnect",dur)

    if flag==True:
        result=Credential.select_user_by_email(username)
        user_sc = Credentialschema()

        data = user_sc.dump(result)
        owner_id=data.get('id')


        bills_schema = Billschema(many=True)
        dbtime=time.time()
        result=Bills.select_user_by_ownerid(owner_id)
        dur=(time.time()-dbtime)*1000
        c.timing("dbconnect",dur)

        data= bills_schema.dumps(result)

        #File.select_file_by_billid()


        c.incr("getallbillcount")
        dur=(time.time()-start)*1000
        c.timing("getallbilltime",dur)


        return jsonify(data)
    else:
        return custom_http_code("unauthorized",401)







@app.route('/v1/bill/<billid>', methods=['DELETE'])
def deletebill(billid):
    start=time.time()
    # print(billid)
    username = request.authorization.username
    passwordinfo = request.authorization.password
    # bill_sc = Billschema(many=False)
    # data = request.get_json()
    dbtime=time.time()
    flag=checkauthentication(username,passwordinfo)
    dur=(time.time()-dbtime)*1000
    c.timing("dbconnect",dur)
    print(billid)
    if flag==True:
        print(billid)
        result=Credential.select_user_by_email(username)
        user_sc = Credentialschema()

        data = user_sc.dump(result)
        owner_id=data.get('id')
        print(owner_id)
        dbtime=time.time()
        result2=Bills.select_user_by_billid(billid)
        dur=(time.time()-dbtime)*1000
        c.timing("dbconnect",dur)
        bill_sc = Billschema(many=False)

        data2 = bill_sc.dump((result2))

        owner_id_test= data2.get('owner_id')
        print(owner_id_test)
        #return "before delete"
        if owner_id== owner_id_test:

            dbtime=time.time()
            Bills.delete_bills(billid)



            result2=File.select_file_by_billid(billid)

            dur=(time.time()-dbtime)*1000
            c.timing("dbconnect",dur)
            file_sc=Fileschema(many=False)
            data2=file_sc.dump(result2)
            file_id=data2.get('id')


            print(result2)

            print(data2)
            if not result2:

                c.incr("getfilecount")
                dur=(time.time()-start)*1000
                c.timing("getfilecount",dur)


                return custom_http_code("file does not exist bad request",404)




            #basedir=app.config['UPLOAD_FOLDER']

            filedir=root_dir+'/'+"attachments/"+file_id+"/"

            if os.path.isdir(filedir):
                shutil.rmtree(filedir)

                # filedir=root_dir+"/"+"attachments"+"/"+file_id+"/"

                bucketkey='fileid'+'/'
                s3 = boto3.resource("s3")
                bucketobj = s3.Bucket(bucket)
                file_key=file_id+'/'
                bucketobj.objects.filter(Prefix=file_key).delete()






            else:
                print("no attachment with bill")
            File.delete_file_by_bill(billid)



            c.incr("deletebillcount")
            dur=(time.time()-start)*1000
            c.timing("deletebillcount",dur)
            return custom_http_code("deleted",204)
        else:
            c.incr("deletebillcount")
            dur=(time.time()-start)*1000
            c.timing("deletebillcount",dur)
            return custom_http_code("bill id invalid or not found",404)



    else:
        return custom_http_code("unauthorized",401)



@app.route('/v1/bill/<billid>', methods=['GET'])
def getasinglebill(billid):
    start=time.time()

    # print(billid)
    username = request.authorization.username
    passwordinfo = request.authorization.password
    # bill_sc = Billschema(many=False)
    # data = request.get_json()
    dbtime=time.time()
    flag=checkauthentication(username,passwordinfo)

    dur=(time.time()-dbtime)*1000
    c.timing("dbconnect",dur)

    print(billid)
    if flag==True:
        print(billid)
        dbtime=time.time()
        result=Credential.select_user_by_email(username)
        dur=(time.time()-dbtime)*1000
        c.timing("dbconnect",dur)
        user_sc = Credentialschema()

        data = user_sc.dump(result)
        owner_id=data.get('id')
        print(owner_id)
        dbtime=time.time()
        result2=Bills.select_user_by_billid(billid)
        dur=(time.time()-dbtime)*1000
        c.timing("dbconnect",dur)

        bill_sc = Billschema(many=False)

        data2 = bill_sc.dump((result2))

        owner_id_test= data2.get('owner_id')
        print(owner_id_test)
        #return "before delete"
        if owner_id== owner_id_test:
            bill_schema= Billschema(many=False)

            dbtime=time.time()
            data= Bills.select_user_by_billid(billid)
            dur=(time.time()-dbtime)*1000
            c.timing("dbconnect",dur)

            query_result = bill_schema.dumps(data)
            query_result=json.loads(query_result)


            #check attachment
            dbtime=time.time()
            result= File.select_file_by_billid(billid)
            dur=(time.time()-dbtime)*1000
            c.timing("dbconnect",dur)


            if not result:
                attachmentfile= {}
                query_result["attachments"]=attachmentfile
                return jsonify(query_result)

            #if attachment

            print(result)
            #attachmentb results dump
            file_sc=File_schema_output(many=False)
            data = file_sc.dumps(result)

            #bill info dict
            attachmentfile= query_result

            #attachment dict
            final=json.loads(data)

            #add two dict
            attachmentfile["attachments"]=final



            c.incr("getbillcount")
            dur=(time.time()-start)*1000
            c.timing("getbillcount",dur)
            return jsonify(attachmentfile)



        else:

            c.incr("getbillcount")
            dur=(time.time()-start)*1000
            c.timing("getbillcount",dur)
            return custom_http_code("invalid bill id",404)


    else:
        return custom_http_code("unzauthorized",401)



@app.route('/v1/bill/<bill_id>', methods=['PUT'])
def getbillid(bill_id):
    start=time.time()
    username = request.authorization.username
    passwordinfo = request.authorization.password
    bill_sc = Billschema(many=False)
    data1 = request.get_json()
    dbtime=time.time()
    flag=checkauthentication(username,passwordinfo)
    dur=(time.time()-dbtime)*1000
    c.timing("dbconnect",dur)

    if flag==True:
        result=Credential.select_user_by_email(username)
        user_sc = Credentialschema()

        data = user_sc.dump(result)
        owner_id=data.get('id')


        dbtime=time.time()
        result2=Bills.select_user_by_billid(bill_id)
        dur=(time.time()-dbtime)*1000
        c.timing("dbconnect",dur)

        bill_sc = Billschema(many=False)

        data2 = bill_sc.dump((result2))

        owner_id2= data2.get('owner_id')

        if owner_id==owner_id2:
            json_data = request.get_json()

            list_var=json_data["categories"]
            list_var=str(list_var)
            list_var=((list_var.strip("[")).strip("]")).strip("'")
            json_data["categories"]=list_var

            vendor_name = json_data.get('vendor')
            bill_date = json_data.get('bill_date')
            due_date = json_data.get('due_date')
            amount_due = json_data.get('amount_due')
            categories = json_data.get('categories')
            payment_status = json_data.get('paymentStatus')

            price = json_data.get('amount_due')
            if price <0.1 or price is None:
                return custom_http_code("amount bad request",400)
            if payment_status!="paid" or payment_status!="due" or payment_status!="no_payment" or payment_status!="no_payment_required":
                payment_status="due"


            dbtime=time.time()
            state = Bills.query.filter_by(id=bill_id).update(dict(vendor=vendor_name,bill_date=bill_date,due_date=due_date,amount_due=amount_due,categories=categories,paymentStatus=payment_status))

            db.session.commit()

            dur=(time.time()-dbtime)*1000
            c.timing("dbconnect",dur)

            bill_schema= Billschema(many=False)


            data= Bills.select_user_by_billid(bill_id)
            query_result = bill_schema.dump(data)


            #check attachment
            dbtime=time.time()
            result= File.select_file_by_billid(bill_id)
            dur=(time.time()-dbtime)*1000
            c.timing("dbconnect",dur)

            if not result:
                attachmentfile= {}
                query_result["attachments"]=attachmentfile
                return jsonify(query_result)

            #if attachment

            print(result)
            #attachmentb results dump
            file_sc=File_schema_output(many=False)
            data = file_sc.dumps(result)

            #bill info dict
            attachmentfile= query_result

            #attachment dict
            final=json.loads(data)

            #add two dict
            attachmentfile["attachments"]=final

            c.incr("putbillcount")
            dur=(time.time()-start)*1000
            c.timing("putbillcount",dur)
            return jsonify(attachmentfile)

        else:
            c.incr("putbillcount")
            dur=(time.time()-start)*1000
            c.timing("putbillcount",dur)
            return custom_http_code('Unauthorised',401)

    else:
        return custom_http_code('invalid login',401)



#########################file attach



ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/v1/bill/<billId>/file', methods=['POST'])
def upload_file(billId):
    start=time.time()
    bill_id=billId
    username = request.authorization.username
    passwordinfo = request.authorization.password
    bill_sc = Billschema(many=False)
    data1 = request.get_json()
    dbtime=time.time()
    flag=checkauthentication(username,passwordinfo)
    dur=(time.time()-dbtime)*1000
    c.timing("dbconnect",dur)

    if flag==True:                                        #check if user exits
        result=Credential.select_user_by_email(username)
        user_sc = Credentialschema()

        data = user_sc.dump(result)
        owner_id=data.get('id')

        dbtime=time.time()
        result2=Bills.select_user_by_billid(bill_id)

        dur=(time.time()-dbtime)*1000
        c.timing("dbconnect",dur)
        bill_sc = Billschema(many=False)

        data2 = bill_sc.dump((result2))

        owner_id2= data2.get('owner_id')

        if owner_id==owner_id2:                 #authorized against bill and user
            # checking  if the  request has the file part

            file = request.files['file']
            #
            if 'file' not in request.files:
                return custom_http_code('No file part in the request',400)
            elif file.filename == '':
                return custom_http_code('No file part in the request',400)
            elif file and allowed_file(file.filename):
                result= File.select_file_by_billid(bill_id)
                print(result)
                if result:
                    return custom_http_code("file already exists with bill delete first",400)
                filename = secure_filename(file.filename)
                id=str(uuid.uuid4().hex)
                dir="attachments"+"/"+id
                # os.mkdir(dir)
                target=os.path.join(root_dir, dir)
                print(target)
                if not os.path.isdir(target):
                    os.mkdir(target)
                else:
                    return custom_http_code("file already exists",400)
                destination_folder= "/".join([target, filename])
                file.seek(0,os.SEEK_END)
                file_len=file.tell()
                img_key = hashlib.md5(file.read()).hexdigest()
                obj=file.save(destination_folder)
                #file = request.files['file']
                object_name = id+"/"+file.filename
                s3_client = boto3.client('s3')
                name='attachments/'+id+'/'+filename
                #fileobj= open(name,'r')
                #obj=file.save(destination_folder)
                file=request.files['file']

                dbtime=time.time()
                uploading = s3_client.upload_fileobj(file, bucket, object_name)
                #obj=file.save(destination_folder)

                dur=(time.time()-dbtime)*1000
                c.timing("s3time",dur)

                url='https://s3.console.aws.amazon.com/'+bucket+"/attachments/"+id+"/"+filename
                upload_date=datetime.datetime.today().strftime('%Y-%m-%d')
                # img_key = hashlib.md5(file.read()).hexdigest()
                #     print(img_key.encode("utf-8"))

                dbtime=time.time()
                new_bill = File(id,bill_id,filename,upload_date,url,file_len,img_key)
                db.create_all()
                db.session.add(new_bill)
                db.session.commit()



                dur=(time.time()-dbtime)*1000
                c.timing("dbconnect",dur)
                #   result=Credential.query.filter_by(first_name='Jane').first()
                file_sc=File_schema_output(many=False)
                result= File.select_file_by_file_id(id)
                print(result)
                data = file_sc.dump(result)
                print(data)



                # bill_schema= Billschema(many=False)
                # data= Bills.select_user_by_billid(billid)
                #   query_result = bill_schema.dump(data)
                #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))



                c.incr("postfilecount")
                dur=(time.time()-start)*1000
                c.timing("postfilecount",dur)
                return custom_http_code(data,201)




            else:


                c.incr("postfilecount")
                dur=(time.time()-start)*1000
                c.timing("postfilecount",dur)
                return custom_http_code('wrong file extension',400)
        else:


            c.incr("postfilecount")
            dur=(time.time()-start)*1000
            c.timing("postfilecount",dur)
            return custom_http_code('Unauthorised',401)

    else:
        return custom_http_code('invalid login',401)







@app.route('/v1/bill/<billid>/file/<fileid>', methods=['GET'])
def getfile(billid,fileid):
    start=time.time()
    bill_id=billid
    username = request.authorization.username
    passwordinfo = request.authorization.password
    bill_sc = Billschema(many=False)
    data1 = request.get_json()
    dbtime=time.time()
    flag=checkauthentication(username,passwordinfo)
    dur=(time.time()-dbtime)*1000
    c.timing("dbconnect",dur)

    if flag==True:                                        #check if user exits
        result=Credential.select_user_by_email(username)
        user_sc = Credentialschema()

        data = user_sc.dump(result)
        owner_id=data.get('id')



        result2=Bills.select_user_by_billid(bill_id)
        bill_sc = Billschema(many=False)

        data2 = bill_sc.dump((result2))

        owner_id2= data2.get('owner_id')

        if owner_id==owner_id2:                 #authorized against bill and user
            file_sc=File_schema_output(many=False)
            dbtime=time.time()
            result= File.select_file_by_file_id(fileid)


            dur=(time.time()-dbtime)*1000
            c.timing("dbconnect",dur)
            print(result)
            data = file_sc.dump(result)
            print(data)
            if not result:

                c.incr("getfilecount")
                dur=(time.time()-start)*1000
                c.timing("getfilecount",dur)


                return custom_http_code("file does not exist bad request",404)


            c.incr("getfilecount")
            dur=(time.time()-start)*1000
            c.timing("getfilecount",dur)

            return custom_http_code(data,200)
        else:
            return custom_http_code('Unauthorised',401)

    else:
        return custom_http_code('invalid login',401)


@app.route('/v1/bill/<billid>/file/<fileid>', methods=['DELETE'])
def deletefile(billid,fileid):
    start=time.time()
    bill_id=billid
    username = request.authorization.username
    passwordinfo = request.authorization.password
    bill_sc = Billschema(many=False)
    data1 = request.get_json()
    dbtime=time.time()
    flag=checkauthentication(username,passwordinfo)
    dur=(time.time()-dbtime)*1000
    c.timing("dbconnect",dur)

    if flag==True:                                        #check if user exits
        result=Credential.select_user_by_email(username)
        user_sc = Credentialschema()

        data = user_sc.dump(result)
        owner_id=data.get('id')



        result2=Bills.select_user_by_billid(bill_id)
        bill_sc = Billschema(many=False)

        data2 = bill_sc.dump((result2))

        owner_id2= data2.get('owner_id')

        if owner_id==owner_id2:                 #authorized against bill and user
            file_sc=File_schema_output(many=False)

            dbtime=time.time()
            result= File.select_file_by_file_id(fileid)

            dur=(time.time()-dbtime)*1000
            c.timing("dbconnect",dur)
            print(result)
            if not result:
                return custom_http_code("file does not exist",404)




            filedir=root_dir+"/"+"attachments"+"/"+fileid+"/"

            bucketkey='fileid'+'/'
            s3 = boto3.resource("s3")
            bucketobj = s3.Bucket(bucket)
            file_key=fileid+'/'
            bucketobj.objects.filter(Prefix=file_key).delete()

            if os.path.exists(filedir):
                shutil.rmtree(filedir)
            else:
                print("file id folder noyt found")


            File.delete_file(fileid)


            c.incr("deletefilecount")
            dur=(time.time()-start)*1000
            c.timing("deletefilecount",dur)
            return custom_http_code(data,204)

        else:
            c.incr("deletefilecount")
            dur=(time.time()-start)*1000
            c.timing("deletefilecount",dur)
            return custom_http_code('Unauthorised',401)


    else:
        return custom_http_code('invalid login',401)


@app.route('/all',methods=["GET"])
def all():
    # start=time.time()
    # result=db.session.execute("select * from bills ")
    #
    # for row in result:
    #     response = dict(row.items())
    #     print(response)
    #     return "okay"
    connecting()
    return  "ok"

    # Output the query result as JSON
    # print(json.dumps(response))
    # return json.dumps(response)



@app.route('/v1/bills/due/<days>',methods=["GET"])
def daycheck(days):
    username = request.authorization.username
    passwordinfo = request.authorization.password
    flag=checkauthentication(username,passwordinfo)

    if flag==True:
        result=Credential.select_user_by_email(username)
        user_sc = Credentialschema()

        data = user_sc.dump(result)
        owner_id=data.get('id')


        bills_schema = Billschema(many=True)
        dbtime=time.time()
        result=Bills.select_user_by_ownerid(owner_id)


        if not result:
            return custom_http_code("no bills for user",401)

        else:

            sqs = boto3.resource('sqs',region_name='us-east-1')
            #sqs = boto3.resource('sqs',region_name='us-east-1')
            # Get the queue. This returns an SQS.Queue instance
            queue = sqs.get_queue_by_name(QueueName='lambdaQueue')
            message = {}
            message["email"]=username
            message["days"]=days
            message['owner_id']=owner_id
            message = json.dumps(message)
            response = queue.send_message(MessageBody=message)
            id=response.get('MessageId')
            print(id)
            print(response.get('MD5OfMessageBody'))
            th = threading.Thread(target=threadFunc , args=(username,))

            # Start the thread
            th.start()
            return custom_http_code('resquest sent to queue'+id,200)

            # print("helo")
    else:
        return custom_http_code("invalid user")

# def sendtosns():

def threadFunc(email):
    #email='aman@gmail.co'
    # client = boto3.client('sqs', region_name='us-east-1')

    sqs = boto3.resource('sqs' ,region_name='us-east-1')
    #sqs = boto3.resource('sqs',region_name='us-east-1')

    queue = sqs.get_queue_by_name(QueueName='lambdaQueue')
    messages = queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=3)
    while len(messages) > 0:
        print(messages)
        print(type(messages))
        # messages.
        for message in messages:
            # print(messages['Messages'])
            # print(messages)
            message_body = json.loads(message.body)
            message_handle= message.receipt_handle
            print(message_body)
            print(message_handle)
            # queue.delete_messages()
            owner_id=message_body.get('owner_id')
            days=message_body.get('days')
            print(days)
            t2 = threading.Thread(target=connecting, args=(owner_id,days,email,))

            # Start the thread
            t2.start()


            message.delete()
            exit()



def connecting(owner_id,day,email):
    try:
        connection = psycopg2.connect(user=db_user,
                                      password=db_pass,
                                      host=db_host,
                                      port="5432",
                                      database=db_name)
        cursor = connection.cursor()

        date1= datetime.datetime.today()
        date2= date1.strftime('%Y-%m-%d')

        print(date1)
        end_date = date1+ datetime.timedelta(days=int(day))
        end_date=end_date.strftime('%Y-%m-%d')
        compare = "select * from bills where owner_id='"+owner_id+"' and due_date between '"+date2+"' and '"+end_date+"'"
        print(compare)

        cursor.execute(compare)
        print("Selecting rows from mobile table using cursor.fetchall")
        mobile_records = cursor.fetchall()
        print(len(mobile_records))
        l=len(mobile_records)
        print(mobile_records)
        print("Print each row and it's columns values")
        dict ={}

        for i in range(l):
            entry = mobile_records[i]
            billid = entry[0]
            dict[i]=billid

            print(i, billid)
        print(dict)
        dict["emailid"]=email
        print(dict)



        client = boto3.client('sns',region_name="us-east-1")
        response = client.publish(
            TargetArn='arn:aws:sns:us-east-1:719133250724:webapptopic',
            Message=json.dumps({'default': json.dumps(dict)}),
            MessageStructure='json'
        )
        print("published message")
        
    except (Exception, psycopg2.Error) as error :
        print(error)

if __name__ == '__main__':
    # env_name = os.getenv('FLASK_ENV')

    # app = create_app(env_name)
    # run app
    app.run(host='0.0.0.0',port=8080,debug=True)
