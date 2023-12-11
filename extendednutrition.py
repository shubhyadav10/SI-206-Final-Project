import sqlite3
import json
import requests
import os
import matplotlib.pyplot

def fetch_fruit_list():
    conn  = sqlite3.connect("fruityvice.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT name FROM Fruit''')
    rows = cursor.fetchall()
    fruit_names = [row[0] for row in rows]
    return fruit_names

def extended_nutrition_data(fruit_name):
         querystring = {"query": fruit_name}
         headers = {
             "X-RapidAPI-Key": "40c8134c4emsh4899fe1bb95ab0dp1fc1ecjsn91d0a197f64a",
             "X-RapidAPI-Host": "nutrition-by-api-ninjas.p.rapidapi.com"
         }
         response = requests.get("https://nutrition-by-api-ninjas.p.rapidapi.com/v1/nutrition",headers=headers,params=querystring)
         if response.status_code == 200:
             data = response.json()
             return data
         return []
    
def create_and_populate_extended_nutrition(fruit_names):
        conn = sqlite3.connect("fruityvice.db")
        cursor = conn.cursor()
        query = ''' CREATE TABLE IF NOT EXISTS ExtendedNutrition (
        name TEXT UNIQUE,
        calories REAL,
        serving_size_g REAL,
        fat_total_g REAL,
        fat_saturated_g REAL,
        protein_g REAL,
        cholesterol_mg INTEGER,
        carbohydrates_total_g REAL,
        sugar_g REAL
        )
        '''
        cursor.execute(query)
        total_count = 0
        for fruit_name in fruit_names[:25]:
            fruit_data = extended_nutrition_data(fruit_name)
            if fruit_data and fruit_data[0]["name"].lower() == fruit_name.lower():
                  data = fruit_data[0]
                  cursor.execute("INSERT OR IGNORE INTO ExtendedNutrition(name,calories,serving_size_g,fat_total_g,fat_saturated_g, protein_g,cholesterol_mg,carbohydrates_total_g,sugar_g) VALUES(?,?,?,?,?,?,?,?,?)", (fruit_name, data["calories"], data["serving_size_g"], data["fat_total_g"], data["fat_saturated_g"], data["protein_g"], data["cholesterol_mg"], data["carbohydrates_total_g"], data["sugar_g"]))
           
        conn.commit()
        conn.close()

fruit_names = fetch_fruit_list()
create_and_populate_extended_nutrition(fruit_names)