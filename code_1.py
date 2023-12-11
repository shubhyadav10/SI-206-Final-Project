import sqlite3
import json
import requests
import os
import matplotlib.pyplot

def fetch_stored_fruit_ids(cursor):
    cursor.execute("SELECT id FROM Fruit")
    return {row[0] for row in cursor.fetchall()}

def fetch_data():
    response = requests.get('https://www.fruityvice.com/api/fruit/all')
    if response.status_code == 200:
        return response.json()
    return []

conn = sqlite3.connect('fruityvice.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS Fruit (
                    id INTEGER PRIMARY KEY,
                    genus TEXT,
                    name TEXT,
                    family TEXT,
                    "order" TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS Nutrition (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fruit_id INTEGER,
                    carbohydrates REAL,
                    protein REAL,
                    fat REAL,
                    calories INTEGER,
                    sugar REAL,
                    FOREIGN KEY(fruit_id) REFERENCES Fruit(id))''')

stored_fruit_ids = fetch_stored_fruit_ids(cursor)
new_fruits = fetch_data()
added_count = 0

for fruit in new_fruits:
    if fruit['id'] not in stored_fruit_ids and added_count < 25:
        cursor.execute("INSERT OR IGNORE INTO Fruit (id, genus, name, family, \"order\") VALUES (?, ?, ?, ?, ?)",
                       (fruit['id'], fruit['genus'], fruit['name'], fruit['family'], fruit['order']))
        cursor.execute("INSERT INTO Nutrition (fruit_id, carbohydrates, protein, fat, calories, sugar) VALUES (?, ?, ?, ?, ?, ?)",
                       (fruit['id'], fruit['nutritions']['carbohydrates'], fruit['nutritions']['protein'], 
                        fruit['nutritions']['fat'], fruit['nutritions']['calories'], fruit['nutritions']['sugar']))
        added_count += 1

conn.commit()
conn.close()


conn1 = sqlite3.connect('fruityvice.db')
cursor1 = conn1.cursor()

cursor1.execute('''
    SELECT name FROM Fruit''')
fruits_list = cursor1.fetchall()
fruits_list_names = [i[0] for i in fruits_list]

conn1.close()

def fetch_new_id_for_fruit(fruit_name):
    # Prepare the querystring
    querystring = {"query": fruit_name, "addChildren" : "false", "number" : "1"}
    # API headers - Replace with your actual headers
    headers = {
	    "X-RapidAPI-Key": "a4cbf2e947msh1137ebac823845cp11fc10jsn7b0278f5c02f",
	    "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
    }
    # Send the request
    response = requests.get("https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/food/ingredients/search", headers=headers, params=querystring)
    if response.status_code == 200:
        # Extract the new ID from the response
        data = response.json()
        # Assuming the new ID is in the response, you need to adjust the path to the ID based on the actual response structure
        if data['results']:
            new_id = data['results'][0]['id'] 
            return new_id
    return None

# Function to create and populate the new table
def create_and_populate_new_table(fruit_names_with_new_ids):
    conn = sqlite3.connect('fruityvice.db')
    cursor = conn.cursor()
    # Create a new table
    cursor.execute('''CREATE TABLE IF NOT EXISTS NewFruitIDs (
                        name TEXT UNIQUE,
                        new_id INTEGER,
                        estimated_cost REAL)''')
    cursor.execute('''UPDATE NewFruitIDs
                    SET estimated_cost = 0''')
    # Insert data
    for name, new_id in fruit_names_with_new_ids:
        # Check if the fruit name already exists in the table
        # cursor.execute("SELECT name FROM NewFruitIDs WHERE name = ?", (name,))
        # if not cursor.fetchone():  # If the name does not exist, insert the new record
        cursor.execute("INSERT OR REPLACE INTO NewFruitIDs (name, new_id) VALUES (?, ?)", (name, new_id))

    conn.commit()
    conn.close()

# Main logic
fruit_names = fruits_list_names
fruit_names_with_new_ids = []

for fruit_name in fruit_names:
    new_id = fetch_new_id_for_fruit(fruit_name)
    if new_id is not None:
        fruit_names_with_new_ids.append((fruit_name, new_id))

create_and_populate_new_table(fruit_names_with_new_ids)

def get_new_ids_from_db():
    conn = sqlite3.connect('fruityvice.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, new_id FROM NewFruitIDs")
    data = cursor.fetchall()
    conn.close()
    return data

def update_estimated_cost(fruit_data):
    conn = sqlite3.connect('fruityvice.db')
    cursor = conn.cursor()

    # Add a new column for estimated cost if it doesn't exist
    #cursor.execute("ALTER TABLE NewFruitIDs ADD COLUMN estimated_cost REAL")

    for name, new_id in fruit_data:
        query_string = {"amount": "100", "unit": "grams"}
        headers = {
        "X-RapidAPI-Key": "a4cbf2e947msh1137ebac823845cp11fc10jsn7b0278f5c02f",
	    "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
        }
        response = requests.get(f"https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/food/ingredients/{new_id}/information", headers=headers, params=query_string)
        
        if response.status_code == 200:
            data = response.json()
            estimated_cost = data.get('estimatedCost', {}).get('value', 0)
            
            # Update the estimated cost in the database
            cursor.execute("UPDATE NewFruitIDs SET estimated_cost = ? WHERE new_id = ?", (estimated_cost, new_id))

    conn.commit()
    conn.close()

fruit_data = get_new_ids_from_db()
update_estimated_cost(fruit_data)


    

# {
#   "results": [
#     {
#       "id": 9040,
#       "name": "banana",
#       "image": "bananas.jpg"
#     }
#   ],
#   "offset": 0,
#   "number": 1,
#   "totalResults": 14
# }

