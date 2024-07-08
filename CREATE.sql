CREATE TABLE customers (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerName VARCHAR(255) NOT NULL,
    ContactInfo VARCHAR(255),
    Email VARCHAR(255) UNIQUE,
    Password VARCHAR(255) NOT NULL
);


CREATE TABLE menuitems (
    ItemID INT AUTO_INCREMENT PRIMARY KEY,
    ItemName VARCHAR(255) NOT NULL,
    ItemDescription TEXT,
    Price DECIMAL(10, 2) NOT NULL,
    Category VARCHAR(255)
);


CREATE TABLE orderitems (
    OrderItemID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT,
    ItemID INT,
    Quantity INT,
    FOREIGN KEY (OrderID) REFERENCES orders(OrderID),
    FOREIGN KEY (ItemID) REFERENCES menuitems(ItemID)
);


CREATE TABLE orders (
    OrderID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT,
    OrderDate DATETIME,
    TotalAmount DECIMAL(10, 2),
    Status VARCHAR(255) DEFAULT 'Pending',
    FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID)
);
