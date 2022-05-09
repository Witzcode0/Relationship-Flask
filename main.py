# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#installation
from flask import Flask, render_template, jsonify, request, redirect
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)

# https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/#configuration-keys
# Connecting to a database in flask using Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/flasksqlalchemy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1fb3225920d5b944fed8994e03b03312'
db = SQLAlchemy(app)

person_channel = db.Table('person_channel', 
    db.Column('id', db.Integer, primary_key=True),
    db.Column('person_id', db.Integer, db.ForeignKey('person.id')),
    db.Column('channel_id', db.Integer, db.ForeignKey('channel.id')),
    )

# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
class Person(db.Model):
    __tablename__ = 'person'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String, nullable=True)
    addresses = db.relationship('Address')
    following = db.relationship('Channel', backref='followers', secondary='person_channel')

    def __repr__(self):
        return f'{self.id}:{self.name}'

    def __init__(self,name):
        self.name = name

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cname =  db.Column(db.String(50))

    def __repr__(self):
        return f'{self.id} : {self.cname}'

    def __init__(self, cname):
        self.cname = cname

class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'),
        nullable=False)

    def __repr__(self):
        return f'{self.id}: {self.email}'

    def __init__(self, email, person_id):
        self.email = email
        self.person_id = person_id

class AddressSchema(Schema):
    id = fields.Int(dump_only = True)
    email = fields.String()
    person_id = fields.Integer()

address_schema= AddressSchema(many=True)  

class ChannelSchema(Schema):
    id = fields.Int(dump_only = True)
    cname = fields.String()

channels_schema = ChannelSchema(many=True) 
channel_schema = ChannelSchema()

class PersonSchema(Schema):
    id = fields.Int(dump_only = True)
    name = fields.String()
    following = fields.String()
    addresses = fields.String()

persons_schema = PersonSchema(many=True) 
person_schema = PersonSchema()

class PersonChannelSchema(Schema):
    id = fields.Int(dump_only = True)
    person_id = fields.Integer()
    channel_id = fields.Integer()

persons_channel_schema = PersonChannelSchema(many=True)
person_channel_schema = PersonChannelSchema()

    

@app.route("/")
def index(): 
    return '<a href="/users">Users</a><br><a href="/channels">Channels</a><br> <a href="/addresses">Addresses</a><br><a href="/pc">person_chanels</a>'

@app.route("/users", methods=["GET"])
def users():
    all_users = Person.query.all()
    return jsonify(persons_schema.dump(all_users))

@app.route("/channels", methods=["GET"])
def channels():
    all_channel = Channel.query.all()
    return jsonify(channels_schema.dump(all_channel))

@app.route("/addresses", methods=["GET"])
def addresses():
    all_addresses = Address.query.all()
    return jsonify(address_schema.dump(all_addresses))

@app.route("/pc", methods=["GET"])
def pc():
    all_pc = db.session.query(person_channel).all()
    return jsonify(persons_channel_schema.dump(all_pc))

@app.route("/usercrud/<id>", methods=["GET", "POST", "PUT", "DELETE"])
def usercrud(id):
    if request.method == 'POST':
        name = request.json['name']
        NewPerson = Person(name)
        db.session.add(NewPerson)
        db.session.commit()
        return redirect('')
    elif request.method == 'PUT':
        GetPerson = Person.query.get(id)
        GetPerson.name = request.json['name']
        db.session.commit()
        return redirect('')
    elif request.method == 'DELETE':
        GetPerson = Person.query.get(id)
        db.session.delete(GetPerson)
        db.session.commit()
        return redirect('')
    else:
        if request.method == 'GET':
            person = Person.query.get(id)
            return jsonify(person_schema.dump(person))

@app.route("/channelcrud/<id>", methods=["GET", "POST", "PUT", "DELETE"])
def channelcrud(id):
    if request.method == 'POST':
        cname = request.json['cname']
        NewChannel = Channel(cname)
        db.session.add(NewChannel)
        db.session.commit()
        return redirect('')
    elif request.method == 'PUT':
        GetChannel = Channel.query.get(id)
        GetChannel.name = request.json['cname']
        db.session.commit()
        return redirect('')
    elif request.method == 'DELETE':
        GetChannel = Channel.query.get(id)
        db.session.delete(GetChannel)
        db.session.commit()
        return redirect('')
    else:
        if request.method == 'GET':
            channel = Channel.query.get(id)
            return jsonify(channel_schema.dump(channel))

@app.route("/pcadd", methods=["POST"])
def pcadd():
    if request.method == 'POST':
        person_id = request.json['person_id']
        channel_id = request.json['channel_id']
        statement = person_channel.insert().values(person_id=person_id, channel_id=channel_id)
        db.session.execute(statement)
        db.session.commit()
        return redirect('')

# @app.route("/pcupdate/<id>", methods=["PUT"])
# def pcupdate(id):
#     if request.method == 'PUT':
#         PersonChannelUpdate = db.session.query(person_channel).filter(id).one()
#         person_id = request.json['person_id']
#         channel_id = request.json['channel_id']
#         PersonChannelUpdate.person_id = person_id
#         PersonChannelUpdate.channel_id = channel_id
#         db.session.commit()
#         return redirect('')


    

if __name__ == '__main__':
    app.run(port=8000, debug=True)