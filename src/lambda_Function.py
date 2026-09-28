import json
import boto3
import urllib3


# ============================================================
# CONFIGURATION
# ============================================================

BUCKET = "aws-ecommerce-data-abdelrahman"

ORDERS_PREFIX = "api_raw/orders/"
CHECKPOINT_KEY = "api_raw/checkpoint/last_order_id.txt"

INITIAL_ORDER_ID = 2000000

API_URL = "https://disposal-wimp-clutch.ngrok-free.dev/api/orders"

BATCH_SIZE = 1000


# ============================================================
# AWS CLIENTS
# ============================================================

s3 = boto3.client("s3")

http = urllib3.PoolManager()


# ============================================================
# GET LAST PROCESSED ORDER ID
# ============================================================

def get_last_order_id():

    try:

        response = s3.get_object(
            Bucket=BUCKET,
            Key=CHECKPOINT_KEY
        )

        value = (
            response["Body"]
            .read()
            .decode("utf-8")
            .strip()
        )

        last_order_id = int(value)

        print(
            f"Last processed OrderID: {last_order_id}"
        )

        return last_order_id

    except Exception as e:

        error_message = str(e)

        if (
            "NoSuchKey" in error_message
            or "404" in error_message
            or "Not Found" in error_message
        ):

            print(
                "Checkpoint does not exist."
            )

            print(
                f"Starting from OrderID: {INITIAL_ORDER_ID}"
            )

            return INITIAL_ORDER_ID

        raise


# ============================================================
# SAVE LAST PROCESSED ORDER ID
# ============================================================

def save_last_order_id(last_order_id):

    s3.put_object(
        Bucket=BUCKET,
        Key=CHECKPOINT_KEY,
        Body=str(last_order_id).encode("utf-8"),
        ContentType="text/plain"
    )

    print(
        f"Checkpoint updated: {last_order_id}"
    )


# ============================================================
# CALL ORDERING API
# ============================================================

def get_orders(from_order_id):

    url = (
        f"{API_URL}"
        f"?from_order_id={from_order_id}"
        f"&limit={BATCH_SIZE}"
    )

    print("====================================")
    print("CALLING ORDERING API")
    print("====================================")

    print(
        f"URL: {url}"
    )

    response = http.request(
        "GET",
        url,
        timeout=60.0
    )

    response_body = response.data.decode("utf-8")

    print(
        f"API HTTP Status: {response.status}"
    )

    if response.status != 200:

        raise Exception(
            f"API returned HTTP {response.status}: "
            f"{response_body}"
        )

    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        data = json.loads(
            response_body
        )

    except json.JSONDecodeError as e:

        raise Exception(
            f"Invalid JSON returned by API: {e}"
        )

    print(
        f"API Response Type: {type(data).__name__}"
    )

    # ========================================================
    # API RESPONSE
    #
    # {
    #     "orders": [
    #         {...},
    #         {...}
    #     ]
    # }
    # ========================================================

    if isinstance(data, dict) and "orders" in data:

        orders = data["orders"]

    # ========================================================
    # API RESPONSE IS DIRECT LIST
    #
    # [
    #     {...},
    #     {...}
    # ]
    # ========================================================

    elif isinstance(data, list):

        orders = data

    else:

        raise Exception(
            "Unexpected API response structure."
        )

    if not isinstance(orders, list):

        raise Exception(
            "The 'orders' field is not a list."
        )

    print(
        f"Orders extracted from API: {len(orders)}"
    )

    return orders


# ============================================================
# GET ORDER ID FROM API EVENT
# ============================================================

def get_order_id(order_event):

    # --------------------------------------------------------
    # Expected structure:
    #
    # {
    #     "metadata": {...},
    #     "order": {
    #         "OrderID": 2000111,
    #         ...
    #     },
    #     "order_details": [...],
    #     "payment": {...},
    #     "shipment": {...},
    #     "summary": {...}
    # }
    # --------------------------------------------------------

    if not isinstance(order_event, dict):

        raise Exception(
            f"Order event must be a dictionary. "
            f"Received: {type(order_event).__name__}"
        )

    if "order" not in order_event:

        raise Exception(
            f"'order' field is missing from event: "
            f"{order_event}"
        )

    order_data = order_event["order"]

    if not isinstance(order_data, dict):

        raise Exception(
            "'order' field must be a dictionary."
        )

    if "OrderID" not in order_data:

        raise Exception(
            f"OrderID is missing from nested order: "
            f"{order_data}"
        )

    try:

        order_id = int(
            order_data["OrderID"]
        )

    except (ValueError, TypeError):

        raise Exception(
            f"Invalid OrderID: "
            f"{order_data.get('OrderID')}"
        )

    return order_id


# ============================================================
# VALIDATE API EVENT
# ============================================================

def validate_order_event(order_event):

    # --------------------------------------------------------
    # Check main order
    # --------------------------------------------------------

    order_id = get_order_id(
        order_event
    )

    # --------------------------------------------------------
    # Check order_details
    # --------------------------------------------------------

    if "order_details" not in order_event:

        raise Exception(
            f"order_details missing for "
            f"OrderID {order_id}"
        )

    if not isinstance(
        order_event["order_details"],
        list
    ):

        raise Exception(
            f"order_details must be a list "
            f"for OrderID {order_id}"
        )

    # --------------------------------------------------------
    # Check payment
    # --------------------------------------------------------

    if "payment" not in order_event:

        print(
            f"WARNING: payment missing "
            f"for OrderID {order_id}"
        )

    # --------------------------------------------------------
    # Check shipment
    # --------------------------------------------------------

    if "shipment" not in order_event:

        print(
            f"WARNING: shipment missing "
            f"for OrderID {order_id}"
        )

    # --------------------------------------------------------
    # Check summary
    # --------------------------------------------------------

    if "summary" not in order_event:

        print(
            f"WARNING: summary missing "
            f"for OrderID {order_id}"
        )

    return order_id


# ============================================================
# UPLOAD COMPLETE ORDER EVENT TO S3
# ============================================================

def upload_order(order_event):

    order_id = validate_order_event(
        order_event
    )

    key = (
        f"{ORDERS_PREFIX}"
        f"order_{order_id}.json"
    )

    body = json.dumps(
        order_event,
        ensure_ascii=False
    ).encode("utf-8")

    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=body,
        ContentType="application/json"
    )

    print(
        f"Uploaded OrderID {order_id}"
    )

    print(
        f"s3://{BUCKET}/{key}"
    )

    return order_id


# ============================================================
# LAMBDA HANDLER
# ============================================================

def lambda_handler(event, context):

    print("====================================")
    print("ORDER API INGESTION")
    print("====================================")

    try:

        # ====================================================
        # STEP 1
        # GET CHECKPOINT
        # ====================================================

        last_order_id = get_last_order_id()

        next_order_id = (
            last_order_id + 1
        )

        print(
            f"Next Order ID: {next_order_id}"
        )

        # ====================================================
        # STEP 2
        # CALL API
        # ====================================================

        orders = get_orders(
            next_order_id
        )

        print(
            f"Orders received: {len(orders)}"
        )

        # ====================================================
        # STEP 3
        # NO NEW ORDERS
        # ====================================================

        if not orders:

            print(
                "No new orders found."
            )

            return {

                "statusCode": 200,

                "body": json.dumps({

                    "message":
                        "No new orders",

                    "last_order_id":
                        last_order_id,

                    "orders_received":
                        0,

                    "orders_uploaded":
                        0

                })

            }

        # ====================================================
        # STEP 4
        # PROCESS ORDERS
        # ====================================================

        uploaded_count = 0

        max_order_id = (
            last_order_id
        )

        for order_event in orders:

            # ------------------------------------------------
            # Get nested OrderID
            # ------------------------------------------------

            order_id = get_order_id(
                order_event
            )

            print(
                f"Processing OrderID: {order_id}"
            )

            # ------------------------------------------------
            # Skip old orders
            # ------------------------------------------------

            if order_id <= last_order_id:

                print(
                    f"Skipping old OrderID: "
                    f"{order_id}"
                )

                continue

            # ------------------------------------------------
            # Upload complete API event
            # ------------------------------------------------

            upload_order(
                order_event
            )

            uploaded_count += 1

            # ------------------------------------------------
            # Update maximum OrderID
            # ------------------------------------------------

            if order_id > max_order_id:

                max_order_id = order_id

        # ====================================================
        # STEP 5
        # UPDATE CHECKPOINT
        # ====================================================

        if uploaded_count > 0:

            save_last_order_id(
                max_order_id
            )

        # ====================================================
        # STEP 6
        # LOG RESULTS
        # ====================================================

        print("====================================")
        print("INGESTION COMPLETED")
        print("====================================")

        print(
            f"Orders received: "
            f"{len(orders)}"
        )

        print(
            f"Orders uploaded: "
            f"{uploaded_count}"
        )

        print(
            f"Previous checkpoint: "
            f"{last_order_id}"
        )

        print(
            f"New checkpoint: "
            f"{max_order_id}"
        )

        # ====================================================
        # SUCCESS RESPONSE
        # ====================================================

        return {

            "statusCode": 200,

            "body": json.dumps({

                "message":
                    "Orders processed successfully",

                "orders_received":
                    len(orders),

                "orders_uploaded":
                    uploaded_count,

                "previous_order_id":
                    last_order_id,

                "last_order_id":
                    max_order_id

            })

        }

    except Exception as e:

        # ====================================================
        # ERROR HANDLING
        # ====================================================

        print("====================================")
        print("INGESTION ERROR")
        print("====================================")

        print(
            f"Error Type: {type(e).__name__}"
        )

        print(
            f"Error Message: {str(e)}"
        )

        return {

            "statusCode": 500,

            "body": json.dumps({

                "message":
                    "Failed to process orders",

                "error":
                    str(e),

                "error_type":
                    type(e).__name__

            })

        }
