from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from datetime import date, timedelta, datetime, timezone
import random
import uuid
import json
from pathlib import Path


# ============================================================
# E-COMMERCE ORDERING API
# ============================================================
#
# Purpose:
# Simulate incremental e-commerce orders for an AWS
# Data Engineering project.
#
# Main flow:
#
# Client
#   |
#   | POST /orders
#   v
# FastAPI
#   |
#   +--> Generate Order
#   +--> Generate OrderDetails
#   +--> Generate Payment
#   +--> Generate Shipment
#   |
#   +--> Save complete transaction as JSON
#
# AWS ingestion flow:
#
# AWS Lambda
#   |
#   | GET /api/orders?from_order_id=2000001&limit=100
#   v
# FastAPI
#   |
#   v
# JSON response
#   |
#   v
# AWS Lambda
#   |
#   v
# S3
#
# ============================================================


app = FastAPI(
    title="E-Commerce Ordering API",
    description="API for generating incremental e-commerce order data",
    version="2.0.0"
)


# ============================================================
# CONFIGURATION
# ============================================================

# These IDs should match your historical data.

MIN_CUSTOMER_ID = 1
MAX_CUSTOMER_ID = 500000

MIN_PRODUCT_ID = 1
MAX_PRODUCT_ID = 10000

MIN_SHIPPER_ID = 1
MAX_SHIPPER_ID = 1000


# ------------------------------------------------------------
# Continue IDs after historical data
# ------------------------------------------------------------

NEXT_ORDER_ID = 2000001
NEXT_ORDER_DETAIL_ID = 5000001
NEXT_PAYMENT_ID = 2000001
NEXT_SHIPMENT_ID = 500001


# ------------------------------------------------------------
# Local output directory
# ------------------------------------------------------------

OUTPUT_DIR = Path("api_output")

OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# PRODUCT CATALOG
# ============================================================

# Demo product catalog.
#
# Later you can replace this with your real products.csv
# or products loaded from S3.

random.seed(42)

PRODUCTS = {}

for product_id in range(
    MIN_PRODUCT_ID,
    MAX_PRODUCT_ID + 1
):

    PRODUCTS[product_id] = {
        "product_id": product_id,
        "unit_price": round(
            random.uniform(10, 1000),
            2
        ),
        "stock": random.randint(
            10,
            100
        )
    }


# ============================================================
# VALID VALUES
# ============================================================

VALID_PAYMENT_METHODS = {
    "Credit Card",
    "Debit Card",
    "Cash on Delivery",
    "PayPal",
    "Bank Transfer"
}


VALID_STATUSES = {
    "Pending",
    "Confirmed",
    "Processing",
    "Shipped",
    "Delivered",
    "Cancelled"
}


# 95% payment success rate

PAYMENT_SUCCESS_RATE = 0.95


# ============================================================
# REQUEST MODELS
# ============================================================

class OrderItem(BaseModel):

    product_id: int = Field(
        gt=0
    )

    quantity: int = Field(
        gt=0,
        le=100
    )

    discount: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0
    )


class OrderRequest(BaseModel):

    customer_id: int = Field(
        gt=0
    )

    items: List[OrderItem] = Field(
        min_length=1,
        max_length=20
    )

    payment_method: str = "Credit Card"

    shipping_required: bool = True


# ============================================================
# ID GENERATORS
# ============================================================

def get_next_order_id():

    global NEXT_ORDER_ID

    value = NEXT_ORDER_ID

    NEXT_ORDER_ID += 1

    return value


def get_next_order_detail_id():

    global NEXT_ORDER_DETAIL_ID

    value = NEXT_ORDER_DETAIL_ID

    NEXT_ORDER_DETAIL_ID += 1

    return value


def get_next_payment_id():

    global NEXT_PAYMENT_ID

    value = NEXT_PAYMENT_ID

    NEXT_PAYMENT_ID += 1

    return value


def get_next_shipment_id():

    global NEXT_SHIPMENT_ID

    value = NEXT_SHIPMENT_ID

    NEXT_SHIPMENT_ID += 1

    return value


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

def validate_customer(customer_id: int):

    if not MIN_CUSTOMER_ID <= customer_id <= MAX_CUSTOMER_ID:

        raise HTTPException(
            status_code=400,
            detail=(
                f"CustomerID {customer_id} does not exist "
                f"in the configured historical range."
            )
        )


# ============================================================
# CALCULATIONS
# ============================================================

def calculate_item_amount(
    unit_price,
    quantity,
    discount
):

    gross = unit_price * quantity

    discount_amount = (
        gross * (discount / 100)
    )

    return round(
        gross - discount_amount,
        2
    )


# ============================================================
# SAVE TRANSACTION
# ============================================================

def save_transaction(transaction):

    """
    Save one complete API transaction locally.

    Example:

    api_output/
        order_2000001.json
        order_2000002.json
        order_2000003.json
    """

    order_id = transaction["order"]["OrderID"]

    file_path = (
        OUTPUT_DIR /
        f"order_{order_id}.json"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            transaction,
            f,
            indent=4
        )

    return str(file_path)


# ============================================================
# HOME ENDPOINT
# ============================================================

@app.get("/")
def home():

    return {

        "message": "E-Commerce Ordering API is running",

        "version": "2.0.0",

        "endpoints": {

            "create_order":
                "POST /orders",

            "get_orders":
                "GET /api/orders?from_order_id=2000001&limit=100",

            "get_single_order":
                "GET /api/orders/{order_id}",

            "generate_batch":
                "POST /orders/test-batch/{number_of_orders}",

            "health":
                "GET /health",

            "docs":
                "/docs"
        }
    }


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get("/health")
def health():

    return {

        "status": "OK",

        "timestamp":
            datetime.now(timezone.utc).isoformat()
    }


# ============================================================
# PRODUCT ENDPOINT
# ============================================================

@app.get("/products/{product_id}")
def get_product(product_id: int):

    product = PRODUCTS.get(product_id)

    if product is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"ProductID {product_id} "
                f"not found."
            )
        )

    return product


# ============================================================
# CREATE ORDER
# ============================================================

@app.post("/orders")
def create_order(
    order_request: OrderRequest
):

    # --------------------------------------------------------
    # 1. Validate customer
    # --------------------------------------------------------

    validate_customer(
        order_request.customer_id
    )


    # --------------------------------------------------------
    # 2. Validate payment method
    # --------------------------------------------------------

    if (
        order_request.payment_method
        not in VALID_PAYMENT_METHODS
    ):

        raise HTTPException(

            status_code=400,

            detail={

                "message":
                    "Invalid payment method",

                "allowed_values":
                    sorted(
                        VALID_PAYMENT_METHODS
                    )
            }
        )


    # --------------------------------------------------------
    # 3. Validate products and stock
    # --------------------------------------------------------

    for item in order_request.items:

        product = PRODUCTS.get(
            item.product_id
        )

        if product is None:

            raise HTTPException(

                status_code=404,

                detail=(
                    f"ProductID "
                    f"{item.product_id} "
                    f"not found."
                )
            )


        if product["stock"] < item.quantity:

            raise HTTPException(

                status_code=400,

                detail=(
                    f"Insufficient stock for "
                    f"ProductID "
                    f"{item.product_id}. "
                    f"Available: "
                    f"{product['stock']}"
                )
            )


    # --------------------------------------------------------
    # 4. Generate IDs
    # --------------------------------------------------------

    order_id = get_next_order_id()

    order_date = date.today().isoformat()


    # --------------------------------------------------------
    # 5. Create Order
    # --------------------------------------------------------

    order = {

        "OrderID":
            order_id,

        "CustomerID":
            order_request.customer_id,

        "OrderDate":
            order_date,

        "Status":
            "Pending"
    }


    # --------------------------------------------------------
    # 6. Create OrderDetails
    # --------------------------------------------------------

    order_details = []

    subtotal = 0.0

    total_discount = 0.0


    for item in order_request.items:

        product = PRODUCTS[
            item.product_id
        ]

        unit_price = product[
            "unit_price"
        ]


        # Gross amount

        gross_amount = round(

            unit_price *
            item.quantity,

            2
        )


        # Discount

        discount_amount = round(

            gross_amount *
            (item.discount / 100),

            2
        )


        # Net amount

        net_amount = round(

            gross_amount -
            discount_amount,

            2
        )


        # Create OrderDetail

        order_detail = {

            "OrderDetailID":
                get_next_order_detail_id(),

            "OrderID":
                order_id,

            "ProductID":
                item.product_id,

            "Quantity":
                item.quantity,

            "UnitPrice":
                unit_price,

            "Discount":
                item.discount
        }


        order_details.append(
            order_detail
        )


        subtotal += net_amount

        total_discount += (
            discount_amount
        )


        # Reduce inventory

        product["stock"] -= (
            item.quantity
        )


    subtotal = round(
        subtotal,
        2
    )

    total_discount = round(
        total_discount,
        2
    )


    # --------------------------------------------------------
    # 7. Calculate tax and shipping
    # --------------------------------------------------------

    tax_rate = 0.14

    tax_amount = round(

        subtotal *
        tax_rate,

        2
    )


    shipping_cost = (

        50.0

        if order_request.shipping_required

        else 0.0
    )


    total_amount = round(

        subtotal +
        tax_amount +
        shipping_cost,

        2
    )


    # --------------------------------------------------------
    # 8. Payment
    # --------------------------------------------------------

    payment_success = (

        random.random()
        < PAYMENT_SUCCESS_RATE
    )


    payment_status = (

        "Completed"

        if payment_success

        else "Failed"
    )


    payment = {

        "PaymentID":
            get_next_payment_id(),

        "OrderID":
            order_id,

        "PaymentMethod":
            order_request.payment_method,

        "PaymentDate":
            order_date,

        "Amount":
            total_amount,

        "PaymentStatus":
            payment_status
    }


    # --------------------------------------------------------
    # 9. Update order status
    # --------------------------------------------------------

    if not payment_success:

        order["Status"] = "Cancelled"

    elif order_request.shipping_required:

        order["Status"] = "Confirmed"

    else:

        order["Status"] = "Processing"


    # --------------------------------------------------------
    # 10. Shipment
    # --------------------------------------------------------

    shipment = None


    if (
        payment_success
        and order_request.shipping_required
    ):

        ship_date = (

            date.today()
            + timedelta(days=1)
        )


        delivery_date = (

            ship_date
            + timedelta(
                days=random.randint(
                    2,
                    5
                )
            )
        )


        shipment = {

            "ShipmentID":
                get_next_shipment_id(),

            "OrderID":
                order_id,

            "ShipperID":
                random.randint(
                    MIN_SHIPPER_ID,
                    MAX_SHIPPER_ID
                ),

            "ShipDate":
                ship_date.isoformat(),

            "DeliveryDate":
                delivery_date.isoformat()
        }


    # --------------------------------------------------------
    # 11. Metadata
    # --------------------------------------------------------

    metadata = {

        "event_id":
            str(uuid.uuid4()),

        "event_type":
            "ORDER_CREATED",

        "event_timestamp":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "source":
            "ordering_api"
    }


    # --------------------------------------------------------
    # 12. Complete transaction
    # --------------------------------------------------------

    transaction = {

        "metadata":
            metadata,

        "order":
            order,

        "order_details":
            order_details,

        "payment":
            payment,

        "shipment":
            shipment,

        "summary": {

            "subtotal":
                subtotal,

            "discount":
                total_discount,

            "tax_rate":
                tax_rate,

            "tax_amount":
                tax_amount,

            "shipping_cost":
                shipping_cost,

            "total_amount":
                total_amount
        }
    }


    # --------------------------------------------------------
    # 13. Save locally
    # --------------------------------------------------------

    file_path = save_transaction(
        transaction
    )


    # --------------------------------------------------------
    # 14. API response
    # --------------------------------------------------------

    return {

        "message":
            "Order created successfully",

        "order_id":
            order_id,

        "status":
            order["Status"],

        "total_amount":
            total_amount,

        "payment_status":
            payment_status,

        "transaction":
            transaction,

        "local_file":
            file_path
    }


# ============================================================
# GET ORDERS FOR AWS LAMBDA
# ============================================================

@app.get("/api/orders")
def get_orders(

    from_order_id: int = 1,

    limit: int = 100
):

    """
    Endpoint used by AWS Lambda.

    Example:

    GET /api/orders?from_order_id=2000001&limit=100

    Returns orders with:

        OrderID >= from_order_id

    up to the requested limit.

    The complete transaction is returned:

        metadata
        order
        order_details
        payment
        shipment
        summary
    """


    # --------------------------------------------------------
    # Validate limit
    # --------------------------------------------------------

    if limit < 1 or limit > 1000:

        raise HTTPException(

            status_code=400,

            detail=(
                "limit must be between "
                "1 and 1000"
            )
        )


    # --------------------------------------------------------
    # Validate from_order_id
    # --------------------------------------------------------

    if from_order_id < 1:

        raise HTTPException(

            status_code=400,

            detail=(
                "from_order_id must be "
                "greater than 0"
            )
        )


    # --------------------------------------------------------
    # Find JSON files
    # --------------------------------------------------------

    files = list(
        OUTPUT_DIR.glob(
            "order_*.json"
        )
    )


    # --------------------------------------------------------
    # Sort by OrderID
    # --------------------------------------------------------

    files = sorted(

        files,

        key=lambda file:
            int(
                file.stem.split("_")[1]
            )
    )


    # --------------------------------------------------------
    # Select orders
    # --------------------------------------------------------

    selected_orders = []

    for file_path in files:

        order_id = int(
            file_path.stem.split("_")[1]
        )


        # Only return orders from requested ID

        if order_id < from_order_id:

            continue


        # Stop when limit reached

        if len(selected_orders) >= limit:

            break


        # Read JSON

        with open(

            file_path,

            "r",

            encoding="utf-8"

        ) as f:

            transaction = json.load(f)


        selected_orders.append(
            transaction
        )


    # --------------------------------------------------------
    # Determine next order ID
    # --------------------------------------------------------

    next_order_id = None


    if selected_orders:

        last_order_id = selected_orders[-1][
            "order"
        ][
            "OrderID"
        ]

        next_order_id = (
            last_order_id + 1
        )


    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "source":
            "ordering_api",

        "count":
            len(selected_orders),

        "from_order_id":
            from_order_id,

        "limit":
            limit,

        "next_order_id":
            next_order_id,

        "orders":
            selected_orders
    }


# ============================================================
# GET ONE ORDER
# ============================================================

@app.get("/api/orders/{order_id}")
def get_order(order_id: int):

    """
    Return one complete transaction.

    Example:

    GET /api/orders/2000001
    """


    file_path = (

        OUTPUT_DIR /
        f"order_{order_id}.json"
    )


    if not file_path.exists():

        raise HTTPException(

            status_code=404,

            detail=(
                f"Order {order_id} "
                f"not found"
            )
        )


    with open(

        file_path,

        "r",

        encoding="utf-8"

    ) as f:

        transaction = json.load(f)


    return transaction


# ============================================================
# GENERATE MULTIPLE TEST ORDERS
# ============================================================

@app.post(
    "/orders/test-batch/{number_of_orders}"
)
def generate_test_batch(
    number_of_orders: int
):

    """
    Generate multiple random orders.

    Example:

    POST /orders/test-batch/10

    Creates up to 10 orders.
    """


    if (
        number_of_orders < 1
        or number_of_orders > 100
    ):

        raise HTTPException(

            status_code=400,

            detail=(
                "number_of_orders "
                "must be between "
                "1 and 100."
            )
        )


    created_orders = []


    for _ in range(
        number_of_orders
    ):


        # ----------------------------------------------------
        # Random customer
        # ----------------------------------------------------

        customer_id = random.randint(

            MIN_CUSTOMER_ID,

            MAX_CUSTOMER_ID
        )


        # ----------------------------------------------------
        # Random number of items
        # ----------------------------------------------------

        number_of_items = random.randint(
            1,
            4
        )


        # ----------------------------------------------------
        # Random products
        # ----------------------------------------------------

        selected_products = random.sample(

            list(PRODUCTS.keys()),

            number_of_items
        )


        items = []


        for product_id in selected_products:

            available_stock = PRODUCTS[
                product_id
            ][
                "stock"
            ]


            if available_stock <= 0:

                continue


            quantity = random.randint(

                1,

                min(
                    5,
                    available_stock
                )
            )


            discount = random.choice(

                [
                    0,
                    0,
                    5,
                    10,
                    15
                ]
            )


            items.append(

                OrderItem(

                    product_id=
                        product_id,

                    quantity=
                        quantity,

                    discount=
                        discount
                )
            )


        # ----------------------------------------------------
        # No available products
        # ----------------------------------------------------

        if not items:

            continue


        # ----------------------------------------------------
        # Create request
        # ----------------------------------------------------

        request = OrderRequest(

            customer_id=
                customer_id,

            items=
                items,

            payment_method=
                random.choice(
                    list(
                        VALID_PAYMENT_METHODS
                    )
                ),

            shipping_required=
                True
        )


        # ----------------------------------------------------
        # Create order
        # ----------------------------------------------------

        try:

            result = create_order(
                request
            )


            created_orders.append({

                "order_id":
                    result[
                        "order_id"
                    ],

                "status":
                    result[
                        "status"
                    ],

                "total_amount":
                    result[
                        "total_amount"
                    ]
            })


        except HTTPException:

            continue


    # --------------------------------------------------------
    # Batch response
    # --------------------------------------------------------

    return {

        "message":
            "Batch generation completed",

        "requested":
            number_of_orders,

        "created":
            len(created_orders),

        "orders":
            created_orders
    }