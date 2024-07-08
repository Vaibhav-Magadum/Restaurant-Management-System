import mysql.connector
from getpass import getpass

# Connect to MySQL
db_connection = mysql.connector.connect(
    host="localhost",
    user="", #INSERET YOUR USERNAME
    password="", #INSERET YOUR PASSWORD
    database="restaurant"
)

cursor = db_connection.cursor()

def register_customer():
    """Register a new customer."""
    print("\n--- Customer Registration ---")
    name = input("Enter your name: ")
    contact = input("Enter your contact info: ")
    email = input("Enter your email: ")
    password = getpass("Enter your password: ")
    
    query = "INSERT INTO Customers (CustomerName, ContactInfo, Email, Password) VALUES (%s, %s, %s, %s)"
    values = (name, contact, email, password)
    
    try:
        cursor.execute(query, values)
        db_connection.commit()
        print("Registration successful!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db_connection.rollback()

def login_customer():
    """Customer login."""
    print("\n--- Customer Login ---")
    email = input("Enter your email: ")
    password = getpass("Enter your password: ")
    
    query = "SELECT CustomerID FROM Customers WHERE Email = %s AND Password = %s"
    cursor.execute(query, (email, password))
    result = cursor.fetchone()
    
    if result:
        print("Login successful!")
        return result[0]
    else:
        print("Invalid email or password.")
        return None

def display_menu():
    """Display the menu items."""
    query = "SELECT * FROM MenuItems"
    cursor.execute(query)
    results = cursor.fetchall()
    print("\n--- Menu ---")
    for row in results:
        print(f"ID: {row[0]} | Name: {row[1]} | Description: {row[2]} | Price: ₹{row[3]} | Category: {row[4]}")
    print("----------------")

def menu_item_details(item_id):
    """Display detailed information about a menu item."""
    query = "SELECT * FROM MenuItems WHERE ItemID = %s"
    cursor.execute(query, (item_id,))
    result = cursor.fetchone()
    if result:
        print(f"\n--- Details for Item {item_id} ---")
        print(f"Name: {result[1]}")
        print(f"Description: {result[2]}")
        print(f"Price: ₹{result[3]}")
        print(f"Category: {result[4]}")
        print("-------------------------------")
    else:
        print("Item not found.")

def place_order(customer_id):
    """Place an order."""
    cart = []
    total_amount = 0.0

    display_menu()
    while True:
        item_id = input("Enter the item ID to add to cart (or 'done' to finish): ")
        if item_id.lower() == 'done':
            break
        try:
            quantity = int(input("Enter the quantity: "))
            cursor.execute("SELECT ItemName, Price FROM MenuItems WHERE ItemID = %s", (item_id,))
            item = cursor.fetchone()
            if item:
                cart.append({'item_id': item_id, 'quantity': quantity, 'price': item[1], 'name': item[0]})
                total_amount += float(str(item[1])) * float(str(quantity))
                print(f"Added {quantity} of {item[0]} to cart.")
            else:
                print("Invalid item ID.")
        except ValueError:
            print("Invalid input. Please enter numeric values for quantity.")

    if cart:
        print("\n--- Cart ---")
        for item in cart:
            print(f"Item: {item['name']} | Quantity: {item['quantity']} | Price: ₹{item['price'] * item['quantity']}")
        print(f"Total Amount: ₹{total_amount}")

        confirm = input("Do you want to place the order? (yes/no): ").lower()
        if confirm == 'yes':
            order_query = "INSERT INTO Orders (CustomerID, OrderDate, TotalAmount) VALUES (%s, NOW(), %s)"
            order_values = (customer_id, total_amount)
            cursor.execute(order_query, order_values)
            order_id = cursor.lastrowid

            for item in cart:
                order_item_query = "INSERT INTO OrderItems (OrderID, ItemID, Quantity) VALUES (%s, %s, %s)"
                order_item_values = (order_id, item['item_id'], item['quantity'])
                cursor.execute(order_item_query, order_item_values)

            db_connection.commit()
            print("Order placed successfully!")
        else:
            print("Order cancelled.")
    else:
        print("No items in cart.")

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
    print("\n--- Order History ---")
    for row in results:
        print(f"Order ID: {row[0]} | Date: {row[1]} | Total: ₹{row[2]} | Status: {row[3]} | Item: {row[4]} | Quantity: {row[5]}")
    print("---------------------")

def update_profile(customer_id):
    """Update customer profile information."""
    print("\n--- Update Profile ---")
    name = input("Enter your new name (leave blank to keep current): ")
    contact = input("Enter your new contact info (leave blank to keep current): ")
    email = input("Enter your new email (leave blank to keep current): ")
    password = getpass("Enter your new password (leave blank to keep current): ")

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
    print("Profile updated successfully.")

def search_menu():
    """Search for menu items by name or category."""
    keyword = input("Enter a keyword to search for (name or category): ")
    query = "SELECT * FROM MenuItems WHERE ItemName LIKE %s OR Category LIKE %s"
    like_pattern = f"%{keyword}%"
    cursor.execute(query, (like_pattern, like_pattern))
    results = cursor.fetchall()

    if results:
        print("\n--- Search Results ---")
        for row in results:
            print(f"ID: {row[0]} | Name: {row[1]} | Description: {row[2]} | Price: ₹{row[3]} | Category: {row[4]}")
        print("----------------------")
    else:
        print("No items found matching the search criteria.")

def main():
    

    while True:
        print("\n--- Welcome to the Restaurant ---")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':
            register_customer()
        elif choice == '2':
            customer_id = login_customer()
            if customer_id:
                while True:
                    print("\n--- Customer Menu ---")
                    print("1. View Menu")
                    print("2. View Item Details")
                    print("3. Place Order")
                    print("4. View Order History")
                    print("5. Update Profile")
                    print("6. Search Menu")
                    print("7. Logout")
                    
                    customer_choice = input("Enter your choice: ")
                    if customer_choice == '1':
                        display_menu()
                    elif customer_choice == '2':
                        item_id = input("Enter the item ID to view details: ")
                        menu_item_details(item_id)
                    elif customer_choice == '3':
                        place_order(customer_id)
                    elif customer_choice == '4':
                        view_order_history(customer_id)
                    elif customer_choice == '5':
                        update_profile(customer_id)
                    elif customer_choice == '6':
                        search_menu()
                    elif customer_choice == '7':
                        print("Logged out successfully.")
                        break
                    else:
                        print("Invalid choice. Please try again.")
        elif choice == '3':
            print("Thank you for visiting! Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# Run the main function
main()

# Close the connection
db_connection.close()