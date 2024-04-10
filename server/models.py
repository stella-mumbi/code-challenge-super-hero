from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy_serializer import SerializerMixin
# from models import db, Hero, Power, HeroPower


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # Define relationship with HeroPower
    hero_powers = relationship("HeroPower", back_populates="hero")

    # Define serialization rules
    serialize_rules = ('-hero_powers',)
    def to_dict_basic(self):
        return{
            "id":self.id,
            "name":self.name,
            "super_name":self.super_name
        }
    def to_dict_with_powers(self):
        return{

            "id":self.id,
            "name":self.name,
            "super_name":self.super_name,
            "hero_powers":[hero_power.to_dict() for hero_power in self.hero_powers]
        }



    def __repr__(self):
        return f'<Hero {self.id}>'

class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # Define relationship with HeroPower
    hero_powers = relationship("HeroPower", back_populates="power")

    # Define serialization rules
    serialize_rules = ('-hero_powers',)

    # Define validation
    @validates('name')
    def validate_name(self, key, name):
        assert len(name) > 0, "Name must not be empty"
        return name

    @validates('description')
    def validate_description(self, key, description):
        if len(description) < 20:
            raise ValueError("Description must be at least 20 characters long")
        return description

    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # Define foreign key relationships
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'))

    # Define relationship with Hero and Power
    hero = relationship("Hero", back_populates="hero_powers")
    power = relationship("Power", back_populates="hero_powers")

    # Define serialization rules
    serialize_rules = ('-hero', '-power',)

    # Define validation
    @validates('strength')
    def validate_strength(self, key, strength):
        allowed_strengths = ["Strong", "Weak", "Average"]
        if strength not in allowed_strengths:
            raise ValueError("Strength must be one of 'Strong', 'Weak', or 'Average'")
        return strength

    def to_dict(self):
        data = {
            'id': self.id,
            'strength': self.strength,
            'hero_id': self.hero_id,
            'power_id': self.power_id
        }
        return data

    def __repr__(self):
        return f'<HeroPower {self.id}>'
