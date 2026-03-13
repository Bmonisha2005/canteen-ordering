# Smart Canteen Management System

## Overview

The Smart Canteen Management System is a web-based application developed to simplify the process of ordering food in a canteen. Customers can view the menu, place orders, choose a payment method, and receive a token number for their order. The admin can manage and deliver orders through an admin dashboard.

This project helps reduce waiting time and improves the efficiency of food ordering in canteens.

---

## Features

### Customer Side

* View canteen menu with food items
* Select food and place order
* Choose payment method:

  * Cash on Delivery
  * Online Payment (Dummy UPI ID)
* Generate order token number
* Order confirmation page

### Admin Side

* Secure admin login
* View all orders
* Deliver orders
* View order history
* Generate simple sales report

---

## Technologies Used

| Technology | Purpose            |
| ---------- | ------------------ |
| HTML       | Web page structure |
| CSS        | Styling            |
| Bootstrap  | Responsive design  |
| Python     | Backend logic      |
| Flask      | Web framework      |
| SQLite     | Database           |

---

## Project Structure

```
canteen/
│
├── app.py
├── canteen.db
│
├── templates/
│   ├── menu.html
│   ├── payment.html
│   ├── order_success.html
│   ├── admin_login.html
│   ├── dashboard.html
│   ├── report.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── images/
│       └── food images
```

---

## How to Run the Project

1. Install Python
2. Install Flask

```
pip install flask
```

3. Run the application

```
python app.py
```

4. Open the browser

```
http://127.0.0.1:5000
```

---

## Payment Method

The system includes a **dummy online payment page** using a sample UPI ID for demonstration purposes.

Example:

```
UPI ID : canteen@upi
```

After clicking **Payment Completed**, the order is confirmed.

---

## Admin Login

Admin can log in to manage orders.

Example password:

```
admin123
```

---

## Future Enhancements

* Real payment gateway integration
* Mobile application
* QR-based payment system
* Live order tracking
* Online food delivery integration

---

## Conclusion

The Smart Canteen Management System demonstrates how digital technology can improve food ordering and management in canteens. It simplifies the ordering process, reduces waiting time, and helps administrators manage orders efficiently.


## 👨‍💻 Developed By

JANAGASRI K
KEERTHANA P
MONISHA B
Final Year Project – 2026  
Smart Canteen Management System
