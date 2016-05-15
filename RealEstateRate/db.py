# coding=utf-8
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

db = SQLAlchemy()

class kyiv_crimes_new(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place = db.Column(db.UnicodeText)
    date = db.Column(db.Date)
    time = db.Column(db.Integer)
    crime_type_id = db.Column(db.Integer)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    region_id = db.Column(db.Integer)
    area_id = db.Column(db.Integer)

    def __repr__(self):
        return '<kyiv_crimes %r>' % self.id


class crime_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crime_type_name = db.Column(db.UnicodeText)
    main_crime_type_id = db.Column(db.Integer)
    sub_crime_type_name = db.Column(db.UnicodeText)

    def __repr__(self):
        return '<crime_types %r>' % self.id


class main_crime_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText)
    global_crime_type_id = db.Column(db.Integer)
    def __repr__(self):
        return '<main_crime_types %r>' % self.id


class global_crime_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText)
    weight = db.Column(db.Float)

    def __repr__(self):
        return '<global_crime_types %r>' % self.id


class areas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText)
    population = db.Column(db.Integer)

    def __repr__(self):
        return '<regions %r>' % self.id

class transport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer)
    time_public = db.Column(db.Integer)
    time_personal = db.Column(db.Integer)

    def __repr__(self):
        return '<regions %r>' % self.id