# 📄 README: alx-backend-graphql_crm

## CRM System with Django + GraphQL

A backend project using Django, GraphQL (via Graphene), and django-filter that is a fully functional Customer Relationship Management (CRM) API.

---

## 🚀 Project Overview

This project demonstrates how to use GraphQL in a Django application to create, query, filter, and manage data for:

- Customers
- Products
- Orders

You can:

- Create data using mutations
- Query data with exact or partial matches
- Filter results by name, price, date, and more
- Seed the database with sample data

Perfect for learning GraphQL vs REST, schema design, validation, and API filtering.

---

## 🛠️ Tech Stack

- **Python + Django** – Backend web framework
- **Graphene-Django** – Adds GraphQL support to Django
- **django-filter** – Enables powerful filtering in queries
- **SQLite** – Default database (easy setup)
- **GraphiQL** – Built-in UI to test GraphQL queries

---

## 📦 Features

✅ GraphQL Queries & Mutations  
✅ Customer, Product, Order Management  
✅ Bulk Customer Creation (with partial success)  
✅ Nested Order Creation with Total Calculation  
✅ Validation (Email uniqueness, Phone format, Price > 0, etc.)  
✅ Filtering & Searching (by name, email, price range, date, etc.)  
✅ Error Handling with User-Friendly Messages  
✅ Database Seeding Script  

---

## 📁 Project Structure

``` alx-backend-graphql_crm/
├── graphql_crm/           # Django project config
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── schema.py          # Main GraphQL schema
├── crm/                   # CRM app
│   ├── __init__.py
│   ├── models.py          # Customer, Product, Order
│   ├── schema.py          # GraphQL types, queries, mutations
│   ├── filters.py         # Filtering logic
│   └── seed_db.py         # Script to populate sample data
├── manage.py
└── requirements.txt       # Dependencies
```

---

## 🔧 Setup & Installation

1. **Clone the repo**

```bash
git clone https://github.com/WuorBhang/alx-backend-graphql_crm.git

cd alx-backend-graphql_crm
```

1. **Create and activate virtual environment**

```bash
python -m venv venv

#On Mac/Linux:

source venv/bin/activate

# On Windows:

venv\Scriptsctivate
```

1. **Install dependencies**

```bash

pip install -r requirements.txt
```

1. **Make migrations and apply them**
  
```bash
python manage.py makemigrations crm

python manage.py migrate
```

⚠️ Always specify the app (`crm`) when creating migrations after adding models.

---

## 🌱 Seed Sample Data

```bash
python manage.py shell -c "from crm.seed_db import seed; seed()"
```

Creates:

- 2 customers: Alice, Bob
- 2 products: Laptop, Mouse
- 1 order (Alice buys Laptop + Mouse)

---

## ▶️ Run the Server

```bash
python manage.py runserver
```

Visit GraphQL interface: [http://localhost:8000/graphql](http://localhost:8000/graphql)

---

## 🧪 Example GraphQL Queries & Mutations

### 🔍 Query: Get All Customers

```graphql
{
  allCustomers {
    edges {
      node {
        id
        name
        email
        phone
        createdAt
      }
    }
  }
}
```

### 🔍 Query: Filter Customers by Name

```graphql
{
  allCustomers(nameIcontains: "Ali") {
    edges {
      node {
        name
        email
      }
    }
  }
}
```

### 🔍 Query: Filter Products by Price Range

```graphql
{
  allProducts(priceGte: 100, priceLte: 1000) {
    edges {
      node {
        name
        price
        stock
      }
    }
  }
}
```

### ✏️ Mutation: Create a Customer

```graphql
mutation {
  createCustomer(input: {
    name: "Carol"
    email: "carol@example.com"
    phone: "+1987654321"
  }) {
    customer {
      id
      name
      email
      phone
    }
    message
  }
}
```

### ✏️ Mutation: Bulk Create Customers

```graphql
mutation {
  bulkCreateCustomers(input: [
    { name: "Dave", email: "dave@example.com" },
    { name: "Eve", email: "eve@example.com", phone: "555-123-4567" }
  ]) {
    customers {
      name
      email
    }
    errors
  }
}
```

### ✏️ Mutation: Create a Product

```graphql
mutation {
  createProduct(input: {
    name: "Keyboard"
    price: 75.99
    stock: 20
  }) {
    product {
      name
      price
      stock
    }
  }
}
```

### ✏️ Mutation: Create an Order

```graphql
mutation {
  createOrder(input: {
    customerId: "1"
    productIds: ["1", "2"]
  }) {
    order {
      id
      customer {
        name
      }
      products {
        name
        price
      }
      totalAmount
      orderDate
    }
  }
}
```

---

## 🔍 Filtering Options

**allCustomers:** `nameIcontains`, `emailIcontains`, `createdAtGte`, `createdAtLte`, `phoneStartsWithPlusOne` 

**allProducts:** `nameIcontains`, `priceGte`, `priceLte`, `stockGte`, `stockLte`  

**allOrders:** `totalAmountGte`, `totalAmountLte`, `orderDateGte`, `orderDateLte`, `customerName`, `productName`, `hasProductId`  

✅ All filters are case-insensitive.

---

## 📌 Notes

- Designed for learning and development.
- Never disable CSRF in production without proper authentication.
- Use `graphene-django-optimizer` to solve N+1 queries.
- Consider adding authentication for production use.

---

## 📬 Feedback & Contributions

Contributions welcome! Submit issues or PRs for:

- Bug fixes
- New features
- Documentation improvements

---

## 🏁 License

MIT License  
Open-source for educational use.  
© 2025 ALX, All rights reserved.
