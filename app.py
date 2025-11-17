from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Float, Table, Column
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError



# Initialize my flask app
app = Flask(__name__)
# connected to db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mechanic_app.db'

# Create a base class for my models
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
ma = Marshmallow()

db.init_app(app)
ma.init_app(app)

class Customers(Base):
    __tablename__ = "customers"

    id : Mapped[int] = mapped_column(primary_key=True)
    first_name : Mapped[str] = mapped_column(String(250), nullable=False)
    last_name : Mapped[str] = mapped_column(String(250), nullable=False)
    email : Mapped[str] = mapped_column(String(350), nullable=False, unique=True)
    phone : Mapped[str] = mapped_column(String(50), nullable=False)
    address : Mapped[str] = mapped_column(String(500), nullable=True)
    # relationship with service_tickets
    service_tickets : Mapped[list["Service_tickets"]] = relationship("Service_tickets", back_populates="customer")

ticket_mechanic = Table(
    "ticket_mechanic",
    Base.metadata,
    Column("service_ticket_id", Integer, ForeignKey("service_tickets.id"),nullable=False),
    Column("mechanic_id", Integer, ForeignKey("mechanics.id"),nullable=False)
)


class Service_tickets(Base):
    __tablename__ = "service_tickets"

    id : Mapped[int] = mapped_column(primary_key=True)
    customer_id : Mapped[int] = mapped_column(Integer, ForeignKey('customers.id'), nullable=False)
    service_desc : Mapped[str] = mapped_column(String(400), nullable=True)
    price : Mapped[float] = mapped_column(Float, nullable=False)
    VIN : Mapped[str] = mapped_column(String(100), nullable=False)
    # relationship with customer
    customer : Mapped["Customers"] = relationship("Customers", back_populates="service_tickets")
    # relationship with mechanics
    mechanics : Mapped[list["Mechanics"]] = relationship("Mechanics", secondary= ticket_mechanic, back_populates="tickets")


class Mechanics(Base):
    __tablename__ = "mechanics"

    id : Mapped[int] = mapped_column(primary_key=True)
    first_name : Mapped[str] = mapped_column(String(250), nullable=False)
    last_name : Mapped[str] = mapped_column(String(250), nullable=False)
    email : Mapped[str] = mapped_column(String(350), nullable=False, unique=True)
    phone : Mapped[str] = mapped_column(String(50), nullable=False)
    address : Mapped[str] = mapped_column(String(500), nullable=True)
    salary : Mapped[float] = mapped_column(Float, nullable=False)
    # relationship with service_tickets
    tickets : Mapped[list["Service_tickets"]] = relationship("Service_tickets", secondary=ticket_mechanic, back_populates="mechanics")


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

@app.route('/customers', methods=["POST"])
def create_customer():
    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_customer = Customers(**data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

@app.route('/customers', methods=["GET"])
def read_customers():
    customers = db.session.query(Customers).all()
    return customers_schema.jsonify(customers), 200

@app.route('/customers/<int:customer_id>', methods=["GET"])
def read_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    if customer:
        return customer_schema.jsonify(customer), 200
    else:
        return jsonify({"error" : f"Customer {customer_id} not found."}), 400

@app.route('/customers/<int:customer_id>', methods=["DELETE"])
def delete_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    if customer:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message" : f"Successfully deleted customer {customer_id}"}), 200
    else:
        return jsonify({"error" : f"Customer {customer_id} not found."}), 400
    
@app.route('/customers/<int:customer_id>', methods=["PUT"])
def update_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    if data["first_name"]:
        customer.first_name = data["first_name"]
    if data["last_name"]:
        customer.last_name = data["last_name"]
    if data["email"]:
        customer.email = data["email"]
    if data["phone"]:
        customer.phone = data["phone"]
    if data["address"]:
        customer.address = data["address"]
    db.session.commit()
    return jsonify({"message" : f"Successfully customer {customer_id} updated."})




with app.app_context():
    # Create all tables
    db.create_all()


app.run(debug=True)



