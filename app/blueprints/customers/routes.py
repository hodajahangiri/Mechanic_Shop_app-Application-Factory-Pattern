from app.blueprints.customers import customers_bp
from app.models import Customers, db
from .schemas import customer_schema, customers_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.blueprints.service_tickets.schemas import service_tickets_schema

@customers_bp.route('', methods=["POST"])
def create_customer():
    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error message" : e.messages}), 400
    new_customer = Customers(**data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

@customers_bp.route('', methods=["GET"])
def read_customers():
    customers = db.session.query(Customers).all()
    return customers_schema.jsonify(customers), 200

@customers_bp.route('/<int:customer_id>', methods=["GET"])
def read_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    if not customer:
        return jsonify({"error" : f"Customer with id: {customer_id} not found."}), 404
    return customer_schema.jsonify(customer), 200

@customers_bp.route('/<int:customer_id>', methods=["DELETE"])
def delete_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    if not customer:
        return jsonify({"error" : f"Customer with id: {customer_id} not found."}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message" : f"Successfully deleted customer with id: {customer_id}"}), 200
    
@customers_bp.route('/<int:customer_id>', methods=["PUT"])
def update_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    if not customer:
       return jsonify({"error" : f"Customer with id: {customer_id} not found."}), 404
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error message" : e.messages}), 400
    for key, value in customer_data.items():
        setattr(customer, key, value)
    db.session.commit()
    return jsonify({"message" : f"Successfully customer with id: {customer_id} updated."}), 200

@customers_bp.route('/service_tickets/<int:customer_id>', methods=["GET"])
def read_customer_service_tickets(customer_id):
    customer = db.session.get(Customers, customer_id)
    if not customer:
        return jsonify({"error" : f"Customer with id: {customer_id} not found."}), 404
    return service_tickets_schema.jsonify(customer.service_tickets), 200

