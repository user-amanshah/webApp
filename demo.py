
import bcrypt , uuid# from model import db, User1, UserSchema
from model import db, Credential, Credentialschema , Credentialschema1 ,Bills, Billschema , Bills_schema,File,Fileschema,File_schema_output
from flask import Flask, jsonify, request, Response
import re, json , datetime
import hashlib, shutil
from werkzeug.utils import secure_filename
import os , boto3
import  psycopg2



import bcrypt , uuid


app = Flask(__name__)

driver = 'postgresql+psycopg2://'
#comment
bucket=os.environ['S3BUCKET_NAME']
db_user= os.environ['RDS_USERNAME']
print(db_user)
db_host= os.environ['RDSHOST_NAME']
print(db_host)
db_pass=os.environ['RDS_PASSWORD']
print(db_pass)
db_name=os.environ['RDS_DBNAME']
print(db_name)
app.config['SQLALCHEMY_DATABASE_URI'] = driver+db_user+':'+db_pass+'@'+db_host+'/'+db_name
print(app.config['SQLALCHEMY_DATABASE_URI'])
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/signin'
#app.config['SQLALCHEMY_DATABASE_URI'] =  'postgresql://postgres@localhost/circle_test'
app.config['UPLOAD_FOLDER']="/home/aman/IdeaProjects/circleCI/attachments/"

root_dir = os.path.dirname(os.path.abspath(__file__))

db.init_app(app)


def custom_http_code(res, status_code):
    """
    Custom Response Function
    """
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )


def checkauthentication(useremail,password):
    user_sc = Credentialschema1()
    result=Credential.select_user_by_email(useremail)
    data = user_sc.dump(result)
    pwd_db=data.get('password')

    flag=bcrypt.checkpw(password.encode('utf8'),pwd_db.encode())
    return flag


@app.route('/v1/user', methods=['POST'])
def page():
    db.create_all()
    user_sc = Credentialschema(many=False)
    data = request.get_json()

    check_email = data.get('email_address')
    check_pass = data.get('password')



    def check(emailid):
        regexp = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if re.search(regexp, emailid):
            return True

        else:
            return False
    #
    flagging = check(check_email)

    #
    def checkpass(passwd):
        """

        """
        if len(passwd) <= 7:
            return False
        elif not re.search("[A-Z]", passwd):
            return False
        elif not re.search("[0-9]", passwd):
            return False
        return True

    flagging1 = checkpass(check_pass)

    if Credential.select_user_by_email(check_email):
        return custom_http_code('Bad resquest',400)

    if flagging==False or flagging1==False:
        return  custom_http_code('Bad request',400)
    else:
        load_data = user_sc.load(data)
        new_user = Credential(load_data)
        # Credential.execute_query()
        db.session.add(new_user)
        db.session.commit()

        #   result=Credential.query.filter_by(first_name='Jane').first()
        result= Credential.select_user_by_email(check_email)
        print(result)
        data = user_sc.dump(result)
        print(data)
        # output=Credential.select_user_by_email(check_email)
        print("done")
        return jsonify(data)



@app.route('/v1/user/self', methods=['GET'])
def getinfo():
    username = request.authorization.username
    passwordinfo = request.authorization.password
    user_sc = Credentialschema(many=False)

    flag=checkauthentication(username,passwordinfo)
    #if flag==True:


    #auth=Credential.select_user_by_email(username)




    if flag==True:
        data = user_sc.dump(Credential.select_user_by_email(username))
        # output=Credential.select_user_by_email(check_email)
        print("done")
        return jsonify(data)

    else:
        return custom_http_code('Unauthorized',401)


@app.route('/v1/user/self', methods=['PUT'])
def updateinfo():
    username = request.authorization.username
    passwordinfo = request.authorization.password
    user_sc = Credentialschema(many=False)
    #auth=Credential.select_user_by_emailandpass(username,passwordinfo)

    flag=checkauthentication(username,passwordinfo)


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


            state = Credential.query.filter_by(email_address=username).update(dict(password=pwd,first_name=firstname,last_name=lastname))

            #    db.session.update(first_name=firstname)
            db.session.commit()
            return custom_http_code('done update',204)

        else:
            return custom_http_code('bad request',400)

    else:
        return custom_http_code("not authorized",401)



@app.route('/v1/bill', methods=['POST'])
def billcreate():
    #db.create_all()
    username = request.authorization.username
    passwordinfo = request.authorization.password
    bill_sc = Billschema(many=False)
    data = request.get_json()

    flag=checkauthentication(username,passwordinfo)


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
        db.session.add(new_bill)
        db.session.commit()

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
        return custom_http_code(final,200)

    else:

        return custom_http_code("not authorized",401)







@app.route('/v1/bills', methods=['GET'])
def getallbills():
    username = request.authorization.username
    passwordinfo = request.authorization.password
    bill_sc = Billschema(many=False)
    data = request.get_json()

    flag=checkauthentication(username,passwordinfo)

    if flag==True:
        result=Credential.select_user_by_email(username)
        user_sc = Credentialschema()

        data = user_sc.dump(result)
        owner_id=data.get('id')


        bills_schema = Billschema(many=True)

        result=Bills.select_user_by_ownerid(owner_id)

        data= bills_schema.dumps(result)

        #File.select_file_by_billid()





        return jsonify(data)
    else:
        return custom_http_code("unauthorized",401)







@app.route('/v1/bill/<billid>', methods=['DELETE'])
def deletebill(billid):
    print(billid)
    username = request.authorization.username
    passwordinfo = request.authorization.password
    # bill_sc = Billschema(many=False)
    # data = request.get_json()

    flag=checkauthentication(username,passwordinfo)
    print(billid)
    if flag==True:
        print(billid)
        result=Credential.select_user_by_email(username)
        user_sc = Credentialschema()

        data = user_sc.dump(result)
        owner_id=data.get('id')
        print(owner_id)

        result2=Bills.select_user_by_billid(billid)
        bill_sc = Billschema(many=False)

        data2 = bill_sc.dump((result2))

        owner_id_test= data2.get('owner_id')
        print(owner_id_test)
        #return "before delete"
        if owner_id== owner_id_test:
            Bills.delete_bills(billid)

            File.delete_file_by_bill(billid)

            result2=File.select_file_by_billid(billid)
            file_sc=Fileschema(many=False)
            data2=file_sc.dump(result2)
            file_id=data2.get('id')





            basedir=app.config['UPLOAD_FOLDER']
            filedir=basedir+file_id+"/"
            shutil.rmtree(filedir)








            return custom_http_code("deleted",204)
        else:
            return custom_http_code("bill id invalid or not found",404)



    else:
        return custom_http_code("unauthorized",401)








@app.route('/v1/bill/<billid>', methods=['GET'])
def getasinglebill(billid):


    print(billid)
    username = request.authorization.username
    passwordinfo = request.authorization.password
    # bill_sc = Billschema(many=False)
    # data = request.get_json()

    flag=checkauthentication(username,passwordinfo)
    print(billid)
    if flag==True:
        print(billid)
        result=Credential.select_user_by_email(username)
        user_sc = Credentialschema()

        data = user_sc.dump(result)
        owner_id=data.get('id')
        print(owner_id)

        result2=Bills.select_user_by_billid(billid)
        bill_sc = Billschema(many=False)

        data2 = bill_sc.dump((result2))

        owner_id_test= data2.get('owner_id')
        print(owner_id_test)
        #return "before delete"
        if owner_id== owner_id_test:
            bill_schema= Billschema(many=False)
            data= Bills.select_user_by_billid(billid)
            query_result = bill_schema.dumps(data)
            query_result=json.loads(query_result)


            #check attachment

            result= File.select_file_by_billid(billid)
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
            return jsonify(attachmentfile)







        else:
            return custom_http_code("invalid bill id",404)


    else:
        return custom_http_code("unzauthorized",401)



@app.route('/v1/bill/<bill_id>', methods=['PUT'])
def getbillid(bill_id):
    username = request.authorization.username
    passwordinfo = request.authorization.password
    bill_sc = Billschema(many=False)
    data1 = request.get_json()

    flag=checkauthentication(username,passwordinfo)

    if flag==True:
        result=Credential.select_user_by_email(username)
        user_sc = Credentialschema()

        data = user_sc.dump(result)
        owner_id=data.get('id')



        result2=Bills.select_user_by_billid(bill_id)
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



            state = Bills.query.filter_by(id=bill_id).update(dict(vendor=vendor_name,bill_date=bill_date,due_date=due_date,amount_due=amount_due,categories=categories,paymentStatus=payment_status))

            db.session.commit()

            bill_schema= Billschema(many=False)
            data= Bills.select_user_by_billid(bill_id)
            query_result = bill_schema.dump(data)




            ###


            #check attachment

            result= File.select_file_by_billid(bill_id)
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
            return jsonify(attachmentfile)

        else:
            return custom_http_code('Unauthorised',401)

    else:
        return custom_http_code('invalid login',401)



#########################



ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/v1/bill/<billId>/file', methods=['POST'])
def upload_file(billId):
    bill_id=billId
    username = request.authorization.username
    passwordinfo = request.authorization.password
    bill_sc = Billschema(many=False)
    data1 = request.get_json()

    flag=checkauthentication(username,passwordinfo)

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
                file.save(destination_folder)


                object_name = id+"/"+file_name
                s3_client = boto3.client('s3')
                uploading = s3_client.upload_file(file.read(), bucket, object_name)


                url="/attachments/"+id+"/"+filename
                upload_date=datetime.datetime.today().strftime('%Y-%m-%d')
                img_key = hashlib.md5(file.read()).hexdigest()
                #     print(img_key.encode("utf-8"))


                new_bill = File(id,bill_id,filename,upload_date,url,file_len,img_key)
                db.create_all()
                db.session.add(new_bill)
                db.session.commit()


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
                return custom_http_code(data,201)




            else:
                return custom_http_code('wrong file extension',400)
        else:
            return custom_http_code('Unauthorised',401)

    else:
        return custom_http_code('invalid login',401)





@app.route('/v1/bill/<billid>/file/<fileid>', methods=['GET'])
def getfile(billid,fileid):
    bill_id=billid
    username = request.authorization.username
    passwordinfo = request.authorization.password
    bill_sc = Billschema(many=False)
    data1 = request.get_json()

    flag=checkauthentication(username,passwordinfo)

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
            result= File.select_file_by_file_id(fileid)
            print(result)
            data = file_sc.dump(result)
            print(data)
            if not result:
                return custom_http_code("file does not exist bad request",404)

            return custom_http_code(data,200)
        else:
            return custom_http_code('Unauthorised',401)

    else:
        return custom_http_code('invalid login',401)


@app.route('/v1/bill/<billid>/file/<fileid>', methods=['DELETE'])
def deletefile(billid,fileid):
    bill_id=billid
    username = request.authorization.username
    passwordinfo = request.authorization.password
    bill_sc = Billschema(many=False)
    data1 = request.get_json()

    flag=checkauthentication(username,passwordinfo)

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
            result= File.select_file_by_file_id(fileid)
            print(result)
            if not result:
                return custom_http_code("file does not exist",404)



            basedir=app.config['UPLOAD_FOLDER']

            filedir=root_dir+"/"+"attachments"+"/"+fileid+"/"
            shutil.rmtree(filedir)
            File.delete_file(fileid)

            return custom_http_code(data,204)
        else:
            return custom_http_code('Unauthorised',401)

    else:
        return custom_http_code('invalid login',401)





@app.route('/all',methods=["GET"])
def all():
    result=db.session.execute("select bills.id,bills.vendor,bills.amount_due,file.url from bills LEFT JOIN file on file.bill_id=bills.id")

    for row in result:
        response = dict(row.items())
        return jsonify(response)

        # Output the query result as JSON
    # print(json.dumps(response))
    # return json.dumps(response)





if __name__ == '__main__':
    # env_name = os.getenv('FLASK_ENV')

    # app = create_app(env_name)
    # run app
    app.run(host='0.0.0.0',port=8080,debug=True)
