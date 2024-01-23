SELECT
Orders.OrderID,
Orders.OrderDate,
Customers.CompanyName,
Customers.ContactName,
Products.ProductName,
'Order Details'.Quantity,
'Order Details'.UnitPrice
FROM
Orders
JOIN
Customers ON Orders.CustomerID = Customers.CustomerID
JOIN
'Order Details' ON Orders.OrderID = 'Order Details'.OrderID
JOIN Products ON 'Order Details'.ProductID = Products.ProductID
WHERE Customers.CompanyName =?