import frappe
import razorpay


@frappe.whitelist()
def create_order(amount):
    try:
        order = create_razorpay_order(amount)
        return {'order_id': order}
    except Exception as e:
        frappe.log_error(f"Razorpay Error: {str(e)}", "Razorpay Payment")
        return {'error': str(e)}
    
import razorpay

def create_razorpay_order(amount, currency='INR'):
    client = razorpay.Client(auth=("rzp_test_0192t3DsBOafwr", "dV0XYpHi6UlGIYQWaNFtq2li"))
    order_data = {
        'amount': amount,  # Razorpay accepts amounts in paise, so multiply by 100
        'currency': currency,
        'payment_capture': 1
    }
    order = client.order.create(data=order_data)
    return order
