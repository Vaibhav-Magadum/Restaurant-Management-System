import PySimpleGUI as sg
import mysql.connector

# Connect to MySQL
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",  # INSERT YOUR USERNAME
    password="root",  # INSERT YOUR PASSWORD
    database="restaurant"
)

cursor = db_connection.cursor()

def register_customer():
    """Register a new customer."""
    layout = [
        [sg.Text("Enter your name:"), sg.InputText(key="name")],
        [sg.Text("Enter your contact info:"), sg.InputText(key="contact")],
        [sg.Text("Enter your email:"), sg.InputText(key="email")],
        [sg.Text("Enter your password:"), sg.InputText(key="password", password_char='*')],
        [sg.Button("Register"), sg.Button("Cancel")]
    ]
    window = sg.Window("Customer Registration", layout)
    event, values = window.read()
    window.close()

    if event == "Register":
        name = values["name"]
        contact = values["contact"]
        email = values["email"]
        password = values["password"]

        query = "INSERT INTO Customers (CustomerName, ContactInfo, Email, Password) VALUES (%s, %s, %s, %s)"
        query_values = (name, contact, email, password)

        try:
            cursor.execute(query, query_values)
            db_connection.commit()
            sg.popup("Registration successful!")
        except mysql.connector.Error as err:
            sg.popup(f"Error: {err}")
            db_connection.rollback()

def login_customer():
    """Customer login."""
    layout = [
        [sg.Text("Enter your email:"), sg.InputText(key="email")],
        [sg.Text("Enter your password:"), sg.InputText(key="password", password_char='*')],
        [sg.Button("Login"), sg.Button("Cancel")]
    ]
    window = sg.Window("Customer Login", layout)
    event, values = window.read()
    window.close()

    if event == "Login":
        email = values["email"]
        password = values["password"]

        query = "SELECT CustomerID FROM Customers WHERE Email = %s AND Password = %s"
        cursor.execute(query, (email, password))
        result = cursor.fetchone()

        if result:
            sg.popup("Login successful!")
            return result[0]
        else:
            sg.popup("Invalid email or password.")
            return None

def display_menu():
    """Display the menu items."""
    query = "SELECT * FROM MenuItems"
    cursor.execute(query)
    results = cursor.fetchall()
    menu_text = "\n--- Menu ---\n"
    for row in results:
        menu_text += f"ID: {row[0]} | Name: {row[1]} | Description: {row[2]} | Price: ₹{row[3]} | Category: {row[4]}\n"
    sg.popup("Menu", menu_text)

def menu_item_details():
    """Display detailed information about a menu item."""
    item_id = sg.popup_get_text("Enter the item ID to view details:")
    query = "SELECT * FROM MenuItems WHERE ItemID = %s"
    cursor.execute(query, (item_id,))
    result = cursor.fetchone()
    if result:
        details = f"\n--- Details for Item {item_id} ---\n"
        details += f"Name: {result[1]}\nDescription: {result[2]}\nPrice: ₹{result[3]}\nCategory: {result[4]}\n"
        sg.popup("Item Details", details)
    else:
        sg.popup("Item not found.")

def place_order(customer_id):
    """Place an order."""
    cart = []
    total_amount = 0.0

    display_menu()
    while True:
        layout = [
            [sg.Text("Enter Item ID:"), sg.InputText(key="item_id")],
            [sg.Text("Enter Quantity:"), sg.InputText(key="quantity")],
            [sg.Button("Add to Cart"), sg.Button("Done")]
        ]
        window = sg.Window("Add Item to Cart", layout)
        event, values = window.read()
        window.close()

        if event == "Done":
            break

        item_id = values["item_id"]
        quantity = values["quantity"]

        try:
            quantity = int(quantity)
            cursor.execute("SELECT ItemName, Price FROM MenuItems WHERE ItemID = %s", (item_id,))
            item = cursor.fetchone()
            if item:
                cart.append({'item_id': item_id, 'quantity': quantity, 'price': item[1], 'name': item[0]})
                total_amount += float(item[1]) * float(quantity)
                sg.popup(f"Added {quantity} of {item[0]} to cart.")
            else:
                sg.popup("Invalid item ID.")
        except ValueError:
            sg.popup("Invalid input. Please enter numeric values for quantity.")

    if cart:
        cart_text = "\n--- Cart ---\n"
        for item in cart:
            cart_text += f"Item: {item['name']} | Quantity: {item['quantity']} | Price: ₹{item['price'] * item['quantity']}\n"
        cart_text += f"Total Amount: ₹{total_amount}"
        sg.popup("Cart", cart_text)

        confirm = sg.popup_yes_no("Do you want to place the order?")
        if confirm == 'Yes':
            order_query = "INSERT INTO Orders (CustomerID, OrderDate, TotalAmount) VALUES (%s, NOW(), %s)"
            order_values = (customer_id, total_amount)
            cursor.execute(order_query, order_values)
            order_id = cursor.lastrowid

            for item in cart:
                order_item_query = "INSERT INTO OrderItems (OrderID, ItemID, Quantity) VALUES (%s, %s, %s)"
                order_item_values = (order_id, item['item_id'], item['quantity'])
                cursor.execute(order_item_query, order_item_values)

            db_connection.commit()
            sg.popup("Order placed successfully!")
        else:
            sg.popup("Order cancelled.")
    else:
        sg.popup("No items in cart.")

def view_order_history(customer_id):
    """View the customer's order history."""
    query = """
    SELECT Orders.OrderID, Orders.OrderDate, Orders.TotalAmount, Orders.Status, MenuItems.ItemName, OrderItems.Quantity
    FROM Orders
    JOIN OrderItems ON Orders.OrderID = OrderItems.OrderID
    JOIN MenuItems ON OrderItems.ItemID = MenuItems.ItemID
    WHERE Orders.CustomerID = %s
    ORDER BY Orders.OrderDate DESC
    """
    cursor.execute(query, (customer_id,))
    results = cursor.fetchall()
    history_text = "\n--- Order History ---\n"
    for row in results:
        history_text += f"Order ID: {row[0]} | Date: {row[1]} | Total: ₹{row[2]} | Status: {row[3]} | Item: {row[4]} | Quantity: {row[5]}\n"
    sg.popup("Order History", history_text)

def update_profile(customer_id):
    """Update customer profile information."""
    name = sg.popup_get_text("Enter your new name (leave blank to keep current):")
    contact = sg.popup_get_text("Enter your new contact info (leave blank to keep current):")
    email = sg.popup_get_text("Enter your new email (leave blank to keep current):")
    password = sg.popup_get_text("Enter your new password (leave blank to keep current):", password_char='*')

    query = "SELECT CustomerName, ContactInfo, Email, Password FROM Customers WHERE CustomerID = %s"
    cursor.execute(query, (customer_id,))
    current_info = cursor.fetchone()

    name = name if name else current_info[0]
    contact = contact if contact else current_info[1]
    email = email if email else current_info[2]
    password = password if password else current_info[3]

    update_query = "UPDATE Customers SET CustomerName = %s, ContactInfo = %s, Email = %s, Password = %s WHERE CustomerID = %s"
    update_values = (name, contact, email, password, customer_id)
    cursor.execute(update_query, update_values)
    db_connection.commit()
    sg.popup("Profile updated successfully.")

def search_menu():
    """Search for menu items by name or category."""
    keyword = sg.popup_get_text("Enter a keyword to search for (name or category):")
    query = "SELECT * FROM MenuItems WHERE ItemName LIKE %s OR Category LIKE %s"
    like_pattern = f"%{keyword}%"
    cursor.execute(query, (like_pattern, like_pattern))
    results = cursor.fetchall()

    if results:
        search_text = "\n--- Search Results ---\n"
        for row in results:
            search_text += f"ID: {row[0]} | Name: {row[1]} | Description: {row[2]} | Price: ₹{row[3]} | Category: {row[4]}\n"
        sg.popup("Search Results", search_text)
    else:
        sg.popup("No items found matching the search criteria.")

def main():
    sg.theme("DarkBlue")

    layout = [
        [sg.Button("Register"), sg.Button("Login"), sg.Button("Exit")]
    ]

    window = sg.Window("Restaurant Management System", layout)

    while True:
        event, _ = window.read()
        if event == sg.WINDOW_CLOSED or event == "Exit":
            break
        elif event == "Register":
            register_customer()
        elif event == "Login":
            customer_id = login_customer()
            if customer_id:
                while True:
                    layout = [
                        [sg.Button("View Menu")],
                        [sg.Button("View Item Details")],
                        [sg.Button("Place Order")],
                        [sg.Button("View Order History")],
                        [sg.Button("Update Profile")],
                        [sg.Button("Search Menu")],
                        [sg.Button("Logout")]
                    ]

                    logged_in_window = sg.Window("Customer Menu", layout)

                    event, _ = logged_in_window.read()
                    logged_in_window.close()

                    if event == sg.WINDOW_CLOSED or event == "Logout":
                        break
                    elif event == "View Menu":
                        display_menu()
                    elif event == "View Item Details":
                        menu_item_details()
                    elif event == "Place Order":
                        place_order(customer_id)
                    elif event == "View Order History":
                        view_order_history(customer_id)
                    elif event == "Update Profile":
                        update_profile(customer_id)
                    elif event == "Search Menu":
                        search_menu()

    window.close()

# Run the main function
main()

# Close the connection
db_connection.close()
