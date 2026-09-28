import csv
import random
import os
from datetime import date, timedelta
from faker import Faker


fake = Faker()

# ============================================================
# CONFIGURATION

# ============================================================

OUTPUT_DIR = "ecommerce_data"

NUM_CUSTOMERS = 10000
NUM_CATEGORIES = 20
NUM_PRODUCTS = 1000
NUM_DEPARTMENTS = 10
NUM_EMPLOYEES = 200
NUM_SUPPLIERS = 100
NUM_ORDERS = 50000
NUM_ORDER_DETAILS = 100000
NUM_PAYMENTS = 45000
NUM_SHIPPERS = 10
NUM_SHIPMENTS = 40000

os.makedirs(OUTPUT_DIR, exist_ok=True)

random.seed(42)
Faker.seed(42)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_date(start_date=date(2020, 1, 1),
                end_date=date(2026, 9, 15)):

    days = (end_date - start_date).days

    return start_date + timedelta(
        days=random.randint(0, days)
    )


def write_csv(filename, headers, rows):

    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow(headers)

        writer.writerows(rows)

    print(f"Created: {filepath} ({len(rows)} rows)")


# ============================================================
# 1. CATEGORIES
# ============================================================

category_names = [
    "Electronics",
    "Computers",
    "Mobile Phones",
    "Home Appliances",
    "Furniture",
    "Clothing",
    "Shoes",
    "Sports",
    "Books",
    "Beauty",
    "Toys",
    "Gaming",
    "Accessories",
    "Kitchen",
    "Garden",
    "Automotive",
    "Health",
    "Office",
    "Jewelry",
    "Pet Supplies"
]

categories = []

for category_id in range(1, NUM_CATEGORIES + 1):

    categories.append([
        category_id,
        category_names[(category_id - 1) % len(category_names)]
    ])

write_csv(
    "categories.csv",
    [
        "CategoryID",
        "CategoryName"
    ],
    categories
)


# ============================================================
# 2. CUSTOMERS
# ============================================================

countries = [
    "Egypt",
    "Saudi Arabia",
    "UAE",
    "Jordan",
    "Kuwait",
    "Qatar",
    "Germany",
    "France",
    "United Kingdom",
    "United States"
]

cities = [
    "Cairo",
    "Giza",
    "Alexandria",
    "Dubai",
    "Abu Dhabi",
    "Riyadh",
    "Jeddah",
    "Amman",
    "Berlin",
    "London"
]

customers = []

for customer_id in range(1, NUM_CUSTOMERS + 1):

    first_name = fake.first_name()
    last_name = fake.last_name()

    customers.append([
        customer_id,
        first_name,
        last_name,
        f"{first_name.lower()}.{last_name.lower()}{customer_id}@example.com",
        random.choice(cities),
        random.choice(countries),
        random_date()
    ])

write_csv(
    "customers.csv",
    [
        "CustomerID",
        "FirstName",
        "LastName",
        "Email",
        "City",
        "Country",
        "RegistrationDate"
    ],
    customers
)


# ============================================================
# 3. PRODUCTS
# ============================================================

brands = [
    "Samsung",
    "Apple",
    "Dell",
    "HP",
    "Lenovo",
    "Sony",
    "LG",
    "Nike",
    "Adidas",
    "Microsoft",
    "Logitech",
    "Canon",
    "Bose"
]

product_names = [
    "Laptop",
    "Smartphone",
    "Tablet",
    "Monitor",
    "Keyboard",
    "Mouse",
    "Headphones",
    "Smart Watch",
    "Camera",
    "Printer",
    "Television",
    "Gaming Console",
    "Chair",
    "Desk",
    "Backpack"
]

products = []

for product_id in range(1, NUM_PRODUCTS + 1):

    category_id = random.randint(1, NUM_CATEGORIES)

    price = round(random.uniform(20, 3000), 2)

    cost = round(price * random.uniform(0.5, 0.85), 2)

    stock = random.randint(0, 500)

    product_name = random.choice(product_names)

    brand = random.choice(brands)

    products.append([
        product_id,
        category_id,
        f"{brand} {product_name} {product_id}",
        brand,
        price,
        cost,
        stock
    ])

write_csv(
    "products.csv",
    [
        "ProductID",
        "CategoryID",
        "ProductName",
        "Brand",
        "Price",
        "Cost",
        "Stock"
    ],
    products
)


# ============================================================
# 4. DEPARTMENTS
# ============================================================

department_names = [
    "IT",
    "Finance",
    "Sales",
    "Marketing",
    "HR",
    "Operations",
    "Procurement",
    "Customer Service",
    "Logistics",
    "Management"
]

departments = []

for department_id in range(1, NUM_DEPARTMENTS + 1):

    departments.append([
        department_id,
        department_names[(department_id - 1) % len(department_names)]
    ])

write_csv(
    "departments.csv",
    [
        "DepartmentID",
        "DepartmentName"
    ],
    departments
)


# ============================================================
# 5. EMPLOYEES
# ============================================================

employees = []

for employee_id in range(1, NUM_EMPLOYEES + 1):

    # First employee has no manager
    if employee_id == 1:
        manager_id = None
    else:
        # Manager must already exist
        manager_id = random.randint(1, employee_id - 1)

    department_id = random.randint(1, NUM_DEPARTMENTS)

    employees.append([
        employee_id,
        manager_id,
        department_id,
        fake.first_name(),
        fake.last_name(),
        round(random.uniform(400, 10000), 2),
        random_date(
            date(2018, 1, 1),
            date(2026, 1, 1)
        )
    ])

write_csv(
    "employees.csv",
    [
        "EmployeeID",
        "ManagerID",
        "DepartmentID",
        "FirstName",
        "LastName",
        "Salary",
        "HireDate"
    ],
    employees
)


# ============================================================
# 6. SUPPLIERS
# ============================================================

supplier_names = [
    "Global Electronics",
    "Tech Distribution",
    "Middle East Supplies",
    "Smart Products Ltd",
    "Future Trading",
    "Digital World",
    "Global Wholesale",
    "Prime Suppliers",
    "Tech Source",
    "International Goods"
]

suppliers = []

for supplier_id in range(1, NUM_SUPPLIERS + 1):

    suppliers.append([
        supplier_id,
        f"{random.choice(supplier_names)} {supplier_id}",
        random.choice(countries)
    ])

write_csv(
    "suppliers.csv",
    [
        "SupplierID",
        "SupplierName",
        "Country"
    ],
    suppliers
)


# ============================================================
# 7. PRODUCT SUPPLIERS
# ============================================================

product_suppliers = []

for product_id in range(1, NUM_PRODUCTS + 1):

    # Every product gets 1-3 suppliers
    number_of_suppliers = random.randint(1, 3)

    selected_suppliers = random.sample(
        range(1, NUM_SUPPLIERS + 1),
        number_of_suppliers
    )

    for supplier_id in selected_suppliers:

        product_suppliers.append([
            product_id,
            supplier_id
        ])

write_csv(
    "product_suppliers.csv",
    [
        "ProductID",
        "SupplierID"
    ],
    product_suppliers
)


# ============================================================
# 8. ORDERS
# ============================================================

statuses = [
    "Pending",
    "Processing",
    "Shipped",
    "Delivered",
    "Cancelled"
]

orders = []

for order_id in range(1, NUM_ORDERS + 1):

    customer_id = random.randint(1, NUM_CUSTOMERS)

    order_date = random_date(
        date(2024, 1, 1),
        date(2026, 9, 15)
    )

    status = random.choice(statuses)

    orders.append([
        order_id,
        customer_id,
        order_date,
        status
    ])

write_csv(
    "orders.csv",
    [
        "OrderID",
        "CustomerID",
        "OrderDate",
        "Status"
    ],
    orders
)


# ============================================================
# 9. ORDER DETAILS
# ============================================================

order_details = []

for order_detail_id in range(1, NUM_ORDER_DETAILS + 1):

    order_id = random.randint(1, NUM_ORDERS)

    product_id = random.randint(1, NUM_PRODUCTS)

    quantity = random.randint(1, 10)

    # Find product price
    product_price = products[product_id - 1][4]

    unit_price = product_price

    discount = random.choice([
        0,
        0,
        0,
        5,
        10,
        15,
        20
    ])

    order_details.append([
        order_detail_id,
        order_id,
        product_id,
        quantity,
        unit_price,
        discount
    ])

write_csv(
    "order_details.csv",
    [
        "OrderDetailID",
        "OrderID",
        "ProductID",
        "Quantity",
        "UnitPrice",
        "Discount"
    ],
    order_details
)


# ============================================================
# 10. PAYMENTS
# ============================================================

payment_methods = [
    "Credit Card",
    "Debit Card",
    "Cash",
    "PayPal",
    "Bank Transfer"
]

payments = []

for payment_id in range(1, NUM_PAYMENTS + 1):

    order_id = random.randint(1, NUM_ORDERS)

    payment_method = random.choice(payment_methods)

    payment_date = random_date(
        date(2024, 1, 1),
        date(2026, 9, 15)
    )

    amount = round(random.uniform(20, 5000), 2)

    payments.append([
        payment_id,
        order_id,
        payment_method,
        payment_date,
        amount
    ])

write_csv(
    "payments.csv",
    [
        "PaymentID",
        "OrderID",
        "PaymentMethod",
        "PaymentDate",
        "Amount"
    ],
    payments
)


# ============================================================
# 11. SHIPPERS
# ============================================================

shipper_names = [
    "DHL",
    "FedEx",
    "Aramex",
    "UPS",
    "Amazon Logistics",
    "Egypt Post",
    "Fetchr",
    "Bosta",
    "ShipBlu",
    "Mylerz"
]

shippers = []

for shipper_id in range(1, NUM_SHIPPERS + 1):

    shippers.append([
        shipper_id,
        shipper_names[(shipper_id - 1) % len(shipper_names)]
    ])

write_csv(
    "shippers.csv",
    [
        "ShipperID",
        "CompanyName"
    ],
    shippers
)


# ============================================================
# 12. SHIPMENTS
# ============================================================

shipments = []

for shipment_id in range(1, NUM_SHIPMENTS + 1):

    order_id = random.randint(1, NUM_ORDERS)

    shippers_id = random.randint(1, NUM_SHIPPERS)

    ship_date = random_date(
        date(2024, 1, 1),
        date(2026, 9, 15)
    )

    delivery_date = ship_date + timedelta(
        days=random.randint(1, 10)
    )

    shipments.append([
        shipment_id,
        order_id,
        shippers_id,
        ship_date,
        delivery_date
    ])

write_csv(
    "shipments.csv",
    [
        "ShipmentID",
        "OrderID",
        "ShipperID",
        "ShipDate",
        "DeliveryDate"
    ],
    shipments
)


# ============================================================
# FINISHED
# ============================================================

print()
print("=" * 60)
print("E-COMMERCE DATA GENERATION COMPLETED")
print("=" * 60)
print(f"Output directory: {OUTPUT_DIR}")
print()