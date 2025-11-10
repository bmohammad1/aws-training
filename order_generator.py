"""
Random Order Generator
Generates realistic random order JSON files with configurable parameters
for testing, data engineering, and development purposes.
"""

import json
import random
import argparse
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
import uuid
from faker import Faker

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Faker for realistic data generation
fake = Faker()


class OrderGenerator:
    """Class to generate realistic random orders."""
    
    def __init__(self):
        """Initialize the order generator with sample data."""
        self.product_catalog = [
            {
                "category": "Electronics",
                "subcategory": "Computers",
                "products": [
                    {"sku": "LAP-DELL-XPS13", "name": "Dell XPS 13 Laptop", "brand": "Dell", "price_range": (800, 1200)},
                    {"sku": "LAP-MAC-PRO", "name": "MacBook Pro", "brand": "Apple", "price_range": (1200, 2500)},
                    {"sku": "LAP-HP-SPEC", "name": "HP Spectre x360", "brand": "HP", "price_range": (900, 1400)},
                    {"sku": "LAP-LEN-THINK", "name": "Lenovo ThinkPad", "brand": "Lenovo", "price_range": (700, 1300)},
                ]
            },
            {
                "category": "Electronics",
                "subcategory": "Accessories",
                "products": [
                    {"sku": "ACC-MOUSE-LOG", "name": "Logitech MX Master 3 Mouse", "brand": "Logitech", "price_range": (80, 120)},
                    {"sku": "ACC-KEY-MECH", "name": "Mechanical Gaming Keyboard", "brand": "Razer", "price_range": (100, 200)},
                    {"sku": "ACC-HEAD-SONY", "name": "Sony WH-1000XM4 Headphones", "brand": "Sony", "price_range": (250, 350)},
                    {"sku": "ACC-DOCK-USB", "name": "USB-C Docking Station", "brand": "Generic", "price_range": (150, 300)},
                ]
            },
            {
                "category": "Books",
                "subcategory": "Technology",
                "products": [
                    {"sku": "BOOK-PYTHON-ADV", "name": "Advanced Python Programming", "brand": "O'Reilly", "price_range": (40, 60)},
                    {"sku": "BOOK-AWS-CERT", "name": "AWS Certification Guide", "brand": "Wiley", "price_range": (35, 55)},
                    {"sku": "BOOK-DATA-ENG", "name": "Data Engineering Handbook", "brand": "Manning", "price_range": (45, 70)},
                ]
            },
            {
                "category": "Accessories",
                "subcategory": "Bags",
                "products": [
                    {"sku": "BAG-CASE-PRO", "name": "Professional Laptop Bag", "brand": "Generic", "price_range": (60, 100)},
                    {"sku": "BAG-BACK-TECH", "name": "Tech Backpack", "brand": "Peak Design", "price_range": (150, 250)},
                    {"sku": "BAG-BRIEF-LEA", "name": "Leather Briefcase", "brand": "Samsonite", "price_range": (200, 400)},
                ]
            }
        ]
        
        self.payment_methods = ["credit_card", "debit_card", "paypal", "apple_pay", "google_pay"]
        self.card_types = ["Visa", "Mastercard", "American Express", "Discover"]
        self.shipping_methods = ["Standard", "Express", "Overnight", "Ground", "Priority"]
        self.carriers = ["FedEx", "UPS", "USPS", "DHL"]
        self.order_statuses = ["pending", "confirmed", "processing", "shipped", "delivered", "completed"]
        self.warehouse_ids = ["WH-SEATTLE-001", "WH-NYC-002", "WH-CHICAGO-003", "WH-LA-004", "WH-MIAMI-005"]
    
    def generate_customer(self) -> Dict[str, Any]:
        """Generate a random customer."""
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        billing_address = {
            "street": fake.street_address(),
            "apartment": fake.secondary_address() if random.choice([True, False]) else None,
            "city": fake.city(),
            "state": fake.state_abbr(),
            "zipCode": fake.zipcode(),
            "country": "USA"
        }
        
        # Sometimes use different shipping address
        if random.choice([True, False, False]):  # 1/3 chance of different shipping
            shipping_address = {
                "street": fake.street_address(),
                "apartment": fake.secondary_address() if random.choice([True, False]) else None,
                "city": fake.city(),
                "state": fake.state_abbr(),
                "zipCode": fake.zipcode(),
                "country": "USA"
            }
        else:
            shipping_address = billing_address.copy()
        
        return {
            "customerId": f"CUST-{random.randint(100000, 999999)}",
            "personalInfo": {
                "firstName": first_name,
                "lastName": last_name,
                "email": fake.email(),
                "phone": fake.phone_number()
            },
            "addresses": {
                "billing": billing_address,
                "shipping": shipping_address
            },
            "preferences": {
                "emailNotifications": random.choice([True, False]),
                "smsAlerts": random.choice([True, False]),
                "loyaltyMember": random.choice([True, False]),
                "loyaltyTier": random.choice(["bronze", "silver", "gold", "platinum"]) if random.choice([True, False]) else None
            }
        }
    
    def generate_items(self, min_items: int = 1, max_items: int = 5) -> List[Dict[str, Any]]:
        """Generate random order items."""
        num_items = random.randint(min_items, max_items)
        items = []
        
        for i in range(num_items):
            # Select random category and product
            category = random.choice(self.product_catalog)
            product = random.choice(category["products"])
            
            # Generate pricing
            base_price = random.uniform(*product["price_range"])
            quantity = random.randint(1, 3)
            
            # Generate discount (sometimes)
            discount_type = None
            discount_value = 0
            discount_amount = 0
            discount_reason = None
            
            if random.choice([True, False, False, False]):  # 25% chance of discount
                discount_type = random.choice(["percentage", "fixed"])
                if discount_type == "percentage":
                    discount_value = random.randint(5, 30)
                    discount_amount = (base_price * quantity * discount_value) / 100
                    discount_reason = random.choice(["Sale", "Student Discount", "First Time Customer", "Bulk Discount"])
                else:
                    discount_amount = random.uniform(10, 50)
                    discount_value = discount_amount
                    discount_reason = "Promotional Discount"
            
            subtotal = (base_price * quantity) - discount_amount
            
            # Generate product specifications
            specifications = self._generate_product_specs(category["category"], category["subcategory"])
            
            items.append({
                "itemId": f"ITEM-{str(i+1).zfill(3)}",
                "productInfo": {
                    "sku": product["sku"],
                    "name": product["name"],
                    "category": category["category"],
                    "subcategory": category["subcategory"],
                    "brand": product["brand"]
                },
                "pricing": {
                    "unitPrice": round(base_price, 2),
                    "quantity": quantity,
                    "discount": {
                        "type": discount_type,
                        "value": discount_value,
                        "amount": round(discount_amount, 2),
                        "reason": discount_reason
                    },
                    "subtotal": round(subtotal, 2)
                },
                "specifications": specifications
            })
        
        return items
    
    def _generate_product_specs(self, category: str, subcategory: str) -> Dict[str, Any]:
        """Generate realistic product specifications based on category."""
        specs = {}
        
        if category == "Electronics" and subcategory == "Computers":
            specs = {
                "processor": random.choice(["Intel i5-1135G7", "Intel i7-1165G7", "AMD Ryzen 5 5600U", "Apple M1"]),
                "memory": random.choice(["8GB RAM", "16GB RAM", "32GB RAM"]),
                "storage": random.choice(["256GB SSD", "512GB SSD", "1TB SSD"]),
                "display": random.choice(["13.3-inch FHD", "14-inch QHD", "15.6-inch 4K"])
            }
        elif category == "Electronics" and subcategory == "Accessories":
            specs = {
                "connectivity": random.choice(["Bluetooth", "USB", "Wireless", "USB-C"]),
                "batteryLife": f"{random.randint(10, 100)} hours" if random.choice([True, False]) else None,
                "compatibility": random.choice(["Windows/Mac", "Universal", "PC Only"]),
                "color": random.choice(["Black", "White", "Silver", "Blue"])
            }
        elif category == "Books":
            specs = {
                "pages": random.randint(200, 800),
                "publisher": random.choice(["O'Reilly", "Manning", "Wiley", "Packt"]),
                "isbn": fake.isbn13(),
                "language": "English"
            }
        elif subcategory == "Bags":
            specs = {
                "material": random.choice(["Nylon", "Leather", "Canvas", "Polyester"]),
                "dimensions": f"{random.randint(12, 18)} x {random.randint(8, 14)} x {random.randint(2, 6)} inches",
                "weight": f"{random.uniform(1.0, 4.0):.1f} lbs",
                "compartments": random.randint(2, 8)
            }
        
        return specs
    
    def generate_payment(self, total_amount: float, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Generate payment information."""
        payment_method = random.choice(self.payment_methods)
        
        payment = {
            "paymentId": f"PAY-{datetime.now().strftime('%Y%m%d')}{random.randint(10000, 99999)}",
            "method": payment_method,
            "status": random.choice(["pending", "completed", "failed"]),
            "processedAt": fake.date_time_between(start_date='-1h', end_date='now').isoformat() + 'Z'
        }
        
        if payment_method in ["credit_card", "debit_card"]:
            payment["cardDetails"] = {
                "type": random.choice(self.card_types),
                "lastFourDigits": random.randint(1000, 9999),
                "expiryMonth": random.randint(1, 12),
                "expiryYear": random.randint(2025, 2030),
                "cardholderName": f"{customer['personalInfo']['firstName']} {customer['personalInfo']['lastName']}",
                "billingAddress": customer["addresses"]["billing"]
            }
        
        # Generate transaction details
        subtotal = total_amount
        
        # Taxes
        sales_tax_rate = random.uniform(0.06, 0.10)
        state_tax_rate = random.uniform(0.02, 0.05)
        local_tax_rate = random.uniform(0.01, 0.03)
        
        sales_tax = subtotal * sales_tax_rate
        state_tax = subtotal * state_tax_rate
        local_tax = subtotal * local_tax_rate
        total_tax = sales_tax + state_tax + local_tax
        
        # Shipping
        shipping_method = random.choice(self.shipping_methods)
        shipping_cost = self._calculate_shipping_cost(shipping_method)
        carrier = random.choice(self.carriers)
        
        # Fees
        processing_fee = random.uniform(2.50, 5.00)
        handling_fee = random.uniform(3.00, 7.00)
        
        # Final total
        final_total = subtotal + total_tax + shipping_cost + processing_fee + handling_fee
        
        payment["transactionDetails"] = {
            "subtotal": round(subtotal, 2),
            "taxes": {
                "salesTax": round(sales_tax, 2),
                "stateTax": round(state_tax, 2),
                "localTax": round(local_tax, 2),
                "totalTax": round(total_tax, 2)
            },
            "shipping": {
                "method": shipping_method,
                "cost": round(shipping_cost, 2),
                "estimatedDelivery": self._calculate_delivery_date(shipping_method),
                "carrier": carrier,
                "trackingNumber": self._generate_tracking_number(carrier)
            },
            "fees": {
                "processingFee": round(processing_fee, 2),
                "handlingFee": round(handling_fee, 2),
                "totalFees": round(processing_fee + handling_fee, 2)
            },
            "discounts": {
                "itemDiscounts": 0,  # Will be calculated from items
                "shippingDiscount": 0,
                "promoCode": None,
                "totalDiscounts": 0
            },
            "finalTotal": round(final_total, 2)
        }
        
        # Receipt
        payment["receipt"] = {
            "receiptNumber": f"REC-{payment['paymentId']}",
            "downloadUrl": f"https://orders.example.com/receipts/{payment['paymentId']}.pdf",
            "emailSent": random.choice([True, False]),
            "printRequested": random.choice([True, False])
        }
        
        return payment
    
    def _calculate_shipping_cost(self, method: str) -> float:
        """Calculate shipping cost based on method."""
        costs = {
            "Standard": random.uniform(5.99, 12.99),
            "Express": random.uniform(15.99, 25.99),
            "Overnight": random.uniform(25.99, 45.99),
            "Ground": random.uniform(8.99, 15.99),
            "Priority": random.uniform(18.99, 29.99)
        }
        return costs.get(method, 9.99)
    
    def _calculate_delivery_date(self, method: str) -> str:
        """Calculate estimated delivery date based on shipping method."""
        days_map = {
            "Standard": random.randint(5, 7),
            "Express": random.randint(2, 3),
            "Overnight": 1,
            "Ground": random.randint(3, 5),
            "Priority": random.randint(2, 4)
        }
        days = days_map.get(method, 5)
        delivery_date = datetime.now() + timedelta(days=days)
        return delivery_date.strftime("%Y-%m-%d")
    
    def _generate_tracking_number(self, carrier: str) -> str:
        """Generate realistic tracking number for carrier."""
        patterns = {
            "FedEx": f"1Z{random.randint(100000000, 999999999)}",
            "UPS": f"1Z999AA{random.randint(1000000000, 9999999999)}",
            "USPS": f"9400{random.randint(1000000000000000, 9999999999999999)}",
            "DHL": f"DHL{random.randint(1000000000, 9999999999)}"
        }
        return patterns.get(carrier, f"TRK{random.randint(1000000000, 9999999999)}")
    
    def generate_fulfillment(self, items: List[Dict[str, Any]], payment: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fulfillment information."""
        warehouse_id = random.choice(self.warehouse_ids)
        status = random.choice(["pending", "processing", "packed", "shipped", "delivered"])
        
        # Generate packages
        packages = []
        items_per_package = random.randint(1, 3)
        
        for i in range(min(2, len(items))):  # Max 2 packages
            package_items = items[i:i+items_per_package] if i+items_per_package <= len(items) else items[i:]
            if not package_items:
                break
                
            packages.append({
                "packageId": f"PKG-{str(i+1).zfill(3)}",
                "items": [item["itemId"] for item in package_items],
                "dimensions": {
                    "length": random.randint(10, 20),
                    "width": random.randint(8, 16),
                    "height": random.randint(2, 8),
                    "unit": "inches"
                },
                "weight": {
                    "value": round(random.uniform(1.0, 8.0), 1),
                    "unit": "lbs"
                }
            })
        
        # Generate shipping details
        shipped_date = fake.date_time_between(start_date='-2d', end_date='+1d').isoformat() + 'Z'
        estimated_delivery = payment["transactionDetails"]["shipping"]["estimatedDelivery"] + "T17:00:00Z"
        
        return {
            "warehouseId": warehouse_id,
            "fulfillmentStatus": status,
            "packaging": {
                "packageCount": len(packages),
                "packages": packages
            },
            "shipping": {
                "shippedDate": shipped_date,
                "estimatedDelivery": estimated_delivery,
                "carrier": payment["transactionDetails"]["shipping"]["carrier"],
                "service": payment["transactionDetails"]["shipping"]["method"],
                "tracking": {
                    "trackingNumber": payment["transactionDetails"]["shipping"]["trackingNumber"],
                    "trackingUrl": f"https://www.{payment['transactionDetails']['shipping']['carrier'].lower()}.com/track?number={payment['transactionDetails']['shipping']['trackingNumber']}",
                    "lastUpdate": fake.date_time_between(start_date='-1d', end_date='now').isoformat() + 'Z',
                    "currentStatus": random.choice(["In Transit", "Out for Delivery", "Delivered", "Processing"])
                }
            }
        }
    
    def generate_metadata(self) -> Dict[str, Any]:
        """Generate order metadata."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        
        created_time = fake.date_time_between(start_date='-7d', end_date='now')
        updated_time = created_time + timedelta(minutes=random.randint(1, 60))
        completed_time = updated_time + timedelta(minutes=random.randint(1, 30))
        
        return {
            "source": random.choice(["web", "mobile", "api", "phone"]),
            "deviceInfo": {
                "userAgent": random.choice(user_agents),
                "ipAddress": fake.ipv4(),
                "sessionId": f"sess_{uuid.uuid4().hex[:12]}"
            },
            "timestamps": {
                "created": created_time.isoformat() + 'Z',
                "updated": updated_time.isoformat() + 'Z',
                "completed": completed_time.isoformat() + 'Z'
            },
            "notes": {
                "customerNotes": fake.text(max_nb_chars=100) if random.choice([True, False]) else None,
                "internalNotes": fake.text(max_nb_chars=80) if random.choice([True, False]) else None,
                "specialInstructions": fake.text(max_nb_chars=120) if random.choice([True, False]) else None
            }
        }
    
    def generate_order(self, min_items: int = 1, max_items: int = 5) -> Dict[str, Any]:
        """Generate a complete random order."""
        # Generate order ID and basic info
        order_id = f"ORD-{datetime.now().year}-{random.randint(100000, 999999)}"
        order_number = f"AWL-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        order_date = fake.date_time_between(start_date='-30d', end_date='now').isoformat() + 'Z'
        status = random.choice(self.order_statuses)
        currency = "USD"
        
        # Generate customer
        customer = self.generate_customer()
        
        # Generate items
        items = self.generate_items(min_items, max_items)
        
        # Calculate total amount from items
        total_amount = sum(item["pricing"]["subtotal"] for item in items)
        
        # Generate payment
        payment = self.generate_payment(total_amount, customer)
        
        # Update payment with item discounts
        item_discounts = sum(item["pricing"]["discount"]["amount"] for item in items)
        payment["transactionDetails"]["discounts"]["itemDiscounts"] = round(item_discounts, 2)
        payment["transactionDetails"]["discounts"]["totalDiscounts"] = round(item_discounts, 2)
        
        # Generate fulfillment
        fulfillment = self.generate_fulfillment(items, payment)
        
        # Generate metadata
        metadata = self.generate_metadata()
        
        return {
            "order": {
                "orderId": order_id,
                "orderNumber": order_number,
                "orderDate": order_date,
                "status": status,
                "totalAmount": payment["transactionDetails"]["finalTotal"],
                "currency": currency,
                "customer": customer,
                "items": items,
                "payment": payment,
                "fulfillment": fulfillment,
                "metadata": metadata
            }
        }


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate random order JSON files with configurable parameters.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python order_generator.py --count 10
  python order_generator.py --count 5 --output orders --min-items 2 --max-items 8
  python order_generator.py --count 1 --output sample_order.json --detailed
  python order_generator.py --batch 100 --output-dir batch_orders
        """
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=1,
        help='Number of orders to generate (default: 1)'
    )
    
    parser.add_argument(
        '--output',
        default='test_output/generated_orders.json',
        help='Output file name (default: test_output/generated_orders.json)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory for batch generation (creates separate files)'
    )
    
    parser.add_argument(
        '--min-items',
        type=int,
        default=1,
        help='Minimum items per order (default: 1)'
    )
    
    parser.add_argument(
        '--max-items',
        type=int,
        default=5,
        help='Maximum items per order (default: 5)'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Generate separate JSON file for each order'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Print detailed information about generated orders'
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Format JSON output with pretty printing'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducible generation'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set random seed for reproducibility
    if args.seed:
        random.seed(args.seed)
        fake.seed_instance(args.seed)
        logger.info(f"Using random seed: {args.seed}")
    
    try:
        generator = OrderGenerator()
        
        logger.info(f"Generating {args.count} order(s)...")
        logger.info(f"Items per order: {args.min_items} - {args.max_items}")
        
        if args.batch or args.output_dir:
            # Generate separate files for each order
            output_dir = Path(args.output_dir) if args.output_dir else Path("generated_orders")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            generated_files = []
            for i in range(args.count):
                order = generator.generate_order(args.min_items, args.max_items)
                
                filename = f"order_{i+1:04d}_{order['order']['orderNumber']}.json"
                file_path = output_dir / filename
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    if args.pretty:
                        json.dump(order, f, indent=2, ensure_ascii=False)
                    else:
                        json.dump(order, f, ensure_ascii=False)
                
                generated_files.append(str(file_path))
                
                if args.detailed:
                    print(f"\n📦 Order {i+1}: {order['order']['orderNumber']}")
                    print(f"   Customer: {order['order']['customer']['personalInfo']['firstName']} {order['order']['customer']['personalInfo']['lastName']}")
                    print(f"   Items: {len(order['order']['items'])}")
                    print(f"   Total: ${order['order']['totalAmount']:.2f}")
                    print(f"   Status: {order['order']['status']}")
                    print(f"   File: {file_path}")
            
            print(f"\n✅ Generated {args.count} orders in separate files:")
            print(f"📁 Output directory: {output_dir}")
            
        else:
            # Generate single file with all orders
            if args.count == 1:
                # Single order
                order = generator.generate_order(args.min_items, args.max_items)
                orders_data = order
            else:
                # Multiple orders in array
                orders = []
                for i in range(args.count):
                    order = generator.generate_order(args.min_items, args.max_items)
                    orders.append(order)
                orders_data = {"orders": orders}
            
            # Write to file
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                if args.pretty:
                    json.dump(orders_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(orders_data, f, ensure_ascii=False)
            
            print(f"\n✅ Generated {args.count} order(s)")
            print(f"📄 Output file: {output_path}")
            print(f"📊 File size: {output_path.stat().st_size:,} bytes")
            
            if args.detailed:
                if args.count == 1:
                    order = orders_data['order']
                    print(f"\n📦 Order Details:")
                    print(f"   ID: {order['orderNumber']}")
                    print(f"   Customer: {order['customer']['personalInfo']['firstName']} {order['customer']['personalInfo']['lastName']}")
                    print(f"   Email: {order['customer']['personalInfo']['email']}")
                    print(f"   Items: {len(order['items'])}")
                    print(f"   Total: ${order['totalAmount']:.2f}")
                    print(f"   Status: {order['status']}")
                    print(f"   Payment: {order['payment']['method']}")
                else:
                    total_amount = sum(order['order']['totalAmount'] for order in orders_data['orders'])
                    print(f"\n📊 Batch Summary:")
                    print(f"   Total Orders: {len(orders_data['orders'])}")
                    print(f"   Total Value: ${total_amount:.2f}")
                    print(f"   Average Order: ${total_amount/len(orders_data['orders']):.2f}")
        
        logger.info("Order generation completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Generation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()