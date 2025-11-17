from app.blueprints.mechanics import mechanics_bp
from app.models import Mechanics, db
from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError

@mechanics_bp.route('', methods=["POST"])
def create_mechanic():
    try:
        data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error message" : e.messages}), 400
    new_mechanic = Mechanics(**data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201

@mechanics_bp.route('', methods=["GET"])
def read_mechanics():
    mechanics = db.session.query(Mechanics).all()
    return mechanics_schema.jsonify(mechanics), 200

@mechanics_bp.route('/<int:mechanic_id>', methods=["GET"])
def read_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    if not mechanic:
        return jsonify({"error" : f"Mechanic {mechanic_id} not found."}), 404
    return mechanic_schema.jsonify(mechanic), 200

