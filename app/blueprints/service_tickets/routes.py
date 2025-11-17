from .schemas import service_ticket_schema, service_tickets_schema
from app.blueprints.service_tickets import service_tickets_bp
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Service_tickets, db, Customers
from app.blueprints.customers.schemas import customer_schema

@service_tickets_bp.route('/<int:customer_id>', methods=["POST"])
def create_service_ticket(customer_id):
    customer = db.session.get(Customers, customer_id)
    if not customer:
        return jsonify({"error" : f"Customer with id: {customer_id} not found."}), 404
    try:
        data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error message" : e.messages}), 400
    print(data)

    new_service_ticket = Service_tickets(**data,customer=customer)
    db.session.add(new_service_ticket)
    customer.service_tickets.append(new_service_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_service_ticket), 201



