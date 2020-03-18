import uuid

from flask import Flask
import datetime
# 10from flask.ext.bcrypt import generate_password_hash

from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from uuid import uuid4
import bcrypt
from sqlalchemy.dialects.postgresql import UUID

# from views import bcrypt_flask_ not used

db = SQLAlchemy()


class Credential(db.Model):
    ####MODEL OF DATABASE##

    __tablename__ = 'credentials1'

    # id1 = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String, primary_key=True, default=uuid4)

    # salt = db.Column(db.String,nullable = False)
    email_address = db.Column(db.String(128), unique=True, nullable=False)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)

    password = db.Column(db.String, nullable=True)
    account_created = db.Column(db.String(128))
    account_updated = db.Column(db.String(128))

    # MODEL constructor OF TABLE
    def __init__(self, data):
        id = data.get('id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email_address = data.get('email_address')

        password = data.get('password')
        password= str(password)
        pwd = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        print(pwd)
        pwd = str(pwd, 'utf-8')
        password = pwd

        account_created = str(datetime.datetime.now().isoformat())
        account_updated = str(datetime.datetime.now().isoformat())

        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email_address
        self.password = password
        self.account_created = account_created
        self.account_updated = account_updated

    def __repr(self):
        return '<id {}>'.format(self.id)

    @staticmethod
    def execute_query(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def select_all_user():
        return Credential.query.all()

    @staticmethod
    def select_user_by_emailandpass(useremail, password):
        return Credential.query.filter_by(email_address=useremail, password=password).first()

    @staticmethod
    def select_user_by_email(useremail):
        return Credential.query.filter_by(email_address=useremail).first()

    @staticmethod
    def updating(self, data_jason):
        self.first_name = data_jason.get('first_name')
        self.last_name = data_jason.get('last_name')
        password =data_jason.get('password')
        password = password.encode('utf8')
        pwd = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        # pwd = str(pwd, 'utf-8')
        self.password = str(pwd)
        self.account_updated = datetime.datetime.isoformat()
        db.session.commit()

    @staticmethod
    def select_pass_by_emailandpass(useremail, password):
        result = Credential.query(Credential.password).filter_by(email_address=useremail, password=password).first()
        return result


class Credentialschema(Schema):
    id = fields.Str(dump_only=True)

    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)

    email_address = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    account_created = fields.Str(dump_only=True)
    account_updated = fields.Str(dump_only=True)


class Credentialschema1(Schema):
    # id = fields.Str(dump_only=True)
    #
    # first_name = fields.Str(required=True)
    # last_name = fields.Str(required=True)
    #
    # email_address = fields.Email(required=True)
    password = fields.Str(required=True, load_only=False)
    # account_created = fields.Str(dump_only=True)
    # account_updated = fields.Str(dump_only=True)


class Bills(db.Model):
    ####MODEL OF DATABASE##

    __tablename__ = 'bills'
    #
    id = db.Column(db.String, primary_key=True)
    #id = db.Column(UUID(as_uuid=True), primary_key=True)
    owner_id = db.Column(db.String)

    # salt = db.Column(db.String,nullable = False)
    vendor = db.Column(db.String(128))
    bill_date = db.Column(db.String(128), nullable=False)
    due_date = db.Column(db.String(128), nullable=False)
    amount_due = db.Column(db.FLOAT)
    categories = db.Column(db.String)

    created_ts = db.Column(db.String(128))
    updated_ts = db.Column(db.String(128))
    paymentStatus = db.Column(db.String)

    # MODEL constructor OF TABLE

    def __init__(self, data, id, owner_id):
        vendor = data.get('vendor')

        bill_date = data.get('bill_date')

        due_date = str(data.get('due_date'))
        amount_due = str(data.get('amount_due'))
        cat = data.get('categories')



        categories = str(cat)
        paymentStatus = str(data.get('paymentStatus'))

        if paymentStatus!="paid" or paymentStatus!="due" or paymentStatus!="no_payment" or paymentStatus!="no_payment_required":
            paymentStatus="due"


        created_ts = datetime.datetime.now().isoformat()
        updated_ts = datetime.datetime.now().isoformat()

        self.id = id
        self.owner_id = owner_id
        self.vendor = vendor
        self.bill_date = bill_date
        self.due_date = due_date
        self.amount_due = amount_due
        self.categories = categories
        self.paymentStatus = paymentStatus
        self.created_ts = created_ts
        self.updated_ts = updated_ts

    def __repr(self):
        return '<id {}>'.format(self.id)

    def execute_bill_query(self):
        db.session.add(self)
        db.session.commit()
        db.create_all()

    @staticmethod
    def select_all_user():
        return Bills.query.all()

    @staticmethod
    def select_user_by_ownerid(owner_id):
        return Bills.query.filter_by(owner_id=owner_id)

    @staticmethod
    def select_user_by_billid(bill_id):
        return Bills.query.filter_by(id=bill_id).first()

    @staticmethod
    def delete_bills(bill_id):
        Bills.query.filter_by(id=bill_id).delete()
        db.session.commit()

    # def select_user_by_email(useremail):
    #     return Credential.query.filter_by(email_address=useremail).first()

class Billschema(Schema):
    #id = fields.UUID()
    id = fields.Str()
    owner_id = fields.Str(many=True)

    vendor = fields.Str(required=True)
    bill_date = fields.Str(required=True)
    due_date = fields.Str(required=True)
    amount_due = fields.Float(required=True)
    categories = fields.Str()
    paymentStatus = fields.Str(required=True)
    created_ts = fields.Str(dump_only=True)
    updated_ts = fields.Str(dump_only=True)


class Bills_schema(Schema):
    class Meta:
        fields =('id','owner_id','vendor')



class File(db.Model):



    ####MODEL OF DATABASE##

    __tablename__ = 'file'
    #
    id = db.Column(db.String, primary_key=True)

    #id = db.Column(UUID(as_uuid=True), primary_key=True)
    bill_id = db.Column(db.String)

    # salt = db.Column(db.String,nullable = False)
    filename = db.Column(db.String(128))
    upload_date = db.Column(db.String(128), nullable=False)
    url = db.Column(db.String, nullable=False)
    size = db.Column(db.FLOAT)
    md5hash = db.Column(db.String)




    # MODEL constructor OF TABLE

    def __init__(self, id, bill_id,filename,upload_date,url,size,md5hash):

        self.id=id
        self.bill_id=bill_id
        self.filename=filename
        self.upload_date=upload_date
        self.url=url
        self.size=size
        self.md5hash=md5hash

    def __repr(self):
        return '<id {}>'.format(self.id)




    @staticmethod
    def select_file_by_file_id(file_id):
        return File.query.filter_by(id=file_id).first()

    @staticmethod
    def select_file_by_billid(bill_id):
        return File.query.filter_by(bill_id=bill_id).first()

    @staticmethod
    def delete_file(file_id):
        File.query.filter_by(id=file_id).delete()
        db.session.commit()

    @staticmethod
    def delete_file_by_bill(billid):
        File.query.filter_by(bill_id=billid).delete()
        db.session.commit()

class Fileschema(Schema):
    #id = fields.UUID()
    id = fields.Str()
    bill_id = fields.Str(many=False)

    filename = fields.Str(required=True)
    upload_date = fields.Str(required=True)
    url = fields.Str(required=True)
    size = fields.Float(required=True)
    md5hash = fields.Str(required=True)

class File_schema_output(Schema):
    class Meta:
        fields =('filename','id','url','upload_date')




