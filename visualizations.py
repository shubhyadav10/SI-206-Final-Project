import sqlite3
import json
import requests
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

conn = sqlite3.connect('fruityvice.db')
cursor = conn.cursor()

#initialize 4 variables for the 4 visualizations
# Arjun
avg_bar = {}
# Shubh
highest_line = {}
lowest_line = {}
#Aarin
total_scatter = {}
final_expensive = {}
final_cheap = {}
calories_per_cent_dict = {}
#first function for joining first api stuff, then we create a bar graph on family names and calories

def write_to_file_report():
    #write contents of api1 visualizations into the text file
    with open("calculations_data.txt", "w") as f:
        #write stuff from avg bar
        f.write("Average calories per Fruit Family \n")
        for g,h in avg_bar.items():
            f.write(f"{g}:{h}\n")
        f.write("\n")
        #stuff from highest line
        f.write("Top 10 Most Expensive Fruits\n")
        for a,b in highest_line.items():
            f.write(f"{a}:{b}\n")
        f.write("\n")        
        #stuff from lowest line
        f.write("Top 10 Least Expensive Fruits\n")
        for c,d in lowest_line.items():
            f.write(f"{c}:{d}\n")
        f.write("\n")
        #fourth visualization for scatter plot of nutritional content
        f.write("Nutritional content of each Fruit per 100g in terms of Carbs,Fat and Sugar content in g\n")
        for k,v in total_scatter.items():
            f.write(f"{k}:{v}\n")
        f.write("Calories Per Cent for each Fruit")
        for l,o in calories_per_cent_dict.items():
            f.write(f"{l}:{o}\n")
        f.write("\n") 
    
def avg_cal_fruit_family():
    #we join our two api1 tables by the common integer fruit id
    #then we display the avg calories for each fruit family
    cursor.execute('''
        SELECT family, AVG(calories) AS avg_calories
        FROM fruit
        JOIN nutrition ON fruit.id = nutrition.fruit_id
        GROUP BY family''')
    f1 = cursor.fetchall()
    for k,v in f1:
        avg_bar[k] = v
    #now we plot with families on x axis and avg calories on y axis
    families = list(avg_bar.keys())
    avg_calories = list(avg_bar.values())
    plt.figure(figsize=(6, 5))
    plt.barh(families, avg_calories, color='skyblue')
    plt.ylabel('Family')
    plt.xlabel('Average Calories')
    plt.title('Average Calories per Fruit Family')
    plt.tight_layout() #this is for spacing
    plt.show()
    
def highest_cost_graph():
    cursor.execute("SELECT name, estimated_cost FROM NewFruitIDs ORDER BY estimated_cost DESC LIMIT 10")
    data = cursor.fetchall()
    for k,v in data:
        highest_line[k] = v
    #highest_line = {name: cost for name, cost in data}
    fruits = list(highest_line.keys())
    costs = list(highest_line.values())
    #Plotting
    plt.figure(figsize=(10, 8))
    plt.plot(fruits, costs, marker='o',color='red')
    plt.title('Top 10 Highest-Costing Fruits')
    plt.xlabel('Fruits')
    plt.ylabel('Estimated Cost (US Cents/100g)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()

def lowest_cost_grapth():
    cursor.execute("SELECT name, estimated_cost FROM NewFruitIDs ORDER BY estimated_cost ASC LIMIT 10")
    low_data = cursor.fetchall()
    for k,v in low_data:
        lowest_line[k] = v
    cheap_fruits = list(lowest_line.keys())
    cheap_costs = list(lowest_line.values())
    #Plot
    plt.figure(figsize=(10, 8))
    plt.plot(cheap_fruits, cheap_costs, marker='o', color='green')
    plt.title('Top 10 Lowest-Costing Fruits')
    plt.xlabel('Fruits')
    plt.ylabel('Estimated Cost (US Cents/100g)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()

  
def macro_fruit_scatter():
    given_query = ''' SELECT name,fat_total_g, carbohydrates_total_g, sugar_g from ExtendedNutrition'''
    cursor.execute(given_query)
    rows = cursor.fetchall()
    total_nut_value = 0
    
    for row in rows:
        name,fat_total_g,carbohydrates_total_g,sugar_g = row
        total_nut_value = fat_total_g + carbohydrates_total_g + sugar_g
        total_scatter[name] = total_nut_value

    fruit_names = list(total_scatter.keys())
    fruit_content = list(total_scatter.values())
    plt.figure(figsize=(10, 8))
    plt.scatter(fruit_names,fruit_content,color = "red")
    x,y = np.polyfit(range(len(fruit_names)), fruit_content, 1)
    plt.plot(fruit_names, x*np.arange(len(fruit_names)) + y, color='blue')
    plt.title("Nutritonal Content of Each Fruit per 100g")
    plt.xlabel("Fruit Names")
    plt.ylabel("Total Nutrient Value of Carbs,Fat and Sugar in g")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
   

def plot_average_calories_per_cent():


    # Querying the data from the database
    query = """
        SELECT f.name, n.calories, nf.estimated_cost
        FROM Fruit f
        JOIN Nutrition n ON f.id = n.fruit_id
        JOIN NewFruitIDs nf ON f.name = nf.name
    """

    # Reading the data into a pandas DataFrame
    data = pd.read_sql_query(query, conn)

    # Calculating average calories per cent
    data['calories_per_cent'] = data['calories'] / data['estimated_cost']

    # Plotting the bar graph
    plt.figure(figsize=(12, 10))
    plt.barh(data['name'], data['calories_per_cent'], color='skyblue')
    plt.xlabel('Fruit')
    plt.ylabel('Average Calories per Cent')
    plt.title('Average Calories per Cent of Fruits')
    plt.show()

    # cursor.execute("SELECT f.name, n.calories FROM Fruit f JOIN Nutrition n ON f.id = n.fruit_id")
    # calories_data = cursor.fetchall()

    # cursor.execute("SELECT name, estimated_cost FROM NewFruitIDs")
    # cost_data = cursor.fetchall()

    # # Close the database connection


    # # Process the data into dictionaries
    # calories_dict = {name: calories for name, calories in calories_data}
    # cost_dict = {name: cost for name, cost in cost_data}

    # # Calculate the average calories per cent and store in a dictionary
    # calories_per_cent_dict = {}
    # for name in calories_dict:
    #     if name in cost_dict and cost_dict[name] != 0:  # Check if the fruit is in both dictionaries and cost is not zero
    #         calories_per_cent_dict[name] = calories_dict[name] / cost_dict[name]

    # # Plotting the bar graph
    # plt.figure(figsize=(12, 10))
    # for name in calories_per_cent_dict:
    #     plt.barh(name, calories_per_cent_dict[name], color='skyblue')

    # plt.xlabel('Fruit')
    # plt.ylabel('Average Calories per Cent')
    # plt.title('Average Calories per Cent for Fruits')
    # plt.show()





#here, we call the three functions for 3 api's, then the fourth that writes all calulation visualizations into a text file
avg_cal_fruit_family()
highest_cost_graph()
lowest_cost_grapth()
macro_fruit_scatter()
write_to_file_report()
plot_average_calories_per_cent()
