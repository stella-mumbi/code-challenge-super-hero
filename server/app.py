#!/usr/bin/env python3
from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

class HeroResource(Resource):
    def get(self, hero_id=None):
        if hero_id is not None:
            hero = Hero.query.filter_by(id=hero_id).first()
            if hero:
                return hero.to_dict_with_powers(), 200
            else:
                return {"error": "Hero not found"}, 404  # Return 404 if hero is not found
        else:
            heroes = Hero.query.all()
            return [hero.to_dict_basic() for hero in heroes], 200
    
    def post(self):
        data = request.get_json()
        hero = Hero(name=data.get('name'), super_name=data.get('super_name'))
        db.session.add(hero)
        db.session.commit()
        return hero.to_dict(), 201

class PowerResource(Resource):
    def get(self, power_id=None):
        if power_id is not None:
            power = Power.query.filter_by(id=power_id).first()
            if power:
                return power.to_dict(), 200
            else:
                return {"error": "Power not found"}, 404
        else:
            powers = Power.query.all()
            return [power.to_dict() for power in powers], 200
    
    def post(self):
        data = request.get_json()
        power = Power(name=data.get('name'), description=data.get('description'))
        db.session.add(power)
        db.session.commit()
        return power.to_dict(), 201
    
    def patch(self, power_id):
        power = Power.query.filter_by(id=power_id).first()

        if not power:
            return {"error": "Power not found"}, 404

        data = request.get_json()

        if 'description' in data:
            new_description = data['description']

            if not new_description or len(new_description) < 20:
                return {"errors": ["validation errors"]}, 400

            power.description = new_description
        try:
            db.session.commit()
            return power.to_dict(), 200
        except:
            return {"errors": ["An error occurred while updating the power"]}, 500
        

class HeroPowerResource(Resource):
    def post(self):
        data = request.get_json()
        hero_id = data.get('hero_id')
        power_id = data.get('power_id')
        strength = data.get('strength')

        if not all([hero_id, power_id]):
            return {"error": "Missing field(s)"}, 400

        hero = Hero.query.filter_by(id=hero_id).first()
        power = Power.query.filter_by(id=power_id).first()
        if not hero or not power:
            return {"error": "Invalid hero or power id."}, 404

        valid_strengths = ['Weak', 'Average', 'Strong']
        if strength not in valid_strengths:
            return {"errors": ["validation errors"]}, 400

        hero_power = HeroPower(hero=hero, power=power, strength=strength)
        try:
            db.session.add(hero_power)
            db.session.commit()
            return {
                "id": hero_power.id,
                "hero_id": hero_power.hero_id,
                "power_id": hero_power.power_id,
                "strength": hero_power.strength,
                "hero": hero.to_dict(),
                "power": power.to_dict()
            }, 200
        except:
            return {"errors": ["An error occurred while creating HeroPower"]}, 500

api = Api(app)
api.add_resource(HeroResource, '/heroes', '/heroes/<int:hero_id>')
api.add_resource(PowerResource, '/powers', '/powers/<int:power_id>')
api.add_resource(HeroPowerResource, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
