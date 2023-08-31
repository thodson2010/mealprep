import sqlite3
import PySimpleGUI as psg
from db_loader import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MealPlanner(object):
    def __init__(self):
        print('App Starup')
        self.cur = None
        self.con = None
        self.chosen_recipes = []
        self.grocery_list = {}
        self.recipe_dict = {}
        self.recipe_data = {}
        self.meal_calories = {}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def startup(self):
        self.con, self.cur = load_db_cursor()
        self.con.row_factory = sqlite3.Row
        # Loads the YAML to the DB
        load_recipe_data(self.con, self.cur)
        load_ingredient_data(self.con, self.cur)

        # Extracts that data out
        self.get_recipe_data()
        self.get_recipe_details()
        # Create the prompt window for the user
        self.create_window()
        # Create the shopping list based on the prompts
        self.get_ingredients()

        self.calculate_calories()
        self.print_shopping_list()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_recipe_data(self):
        results = self.cur.execute('Select * from recipeData;').fetchall()
        # Dict of Dicts....
        for row in results:
            recipe_name = row[0]
            _ingredient = row[1]
            _units = row[2]
            # Add the recipes as the key
            if recipe_name not in self.recipe_data:
                self.recipe_data[recipe_name] = {}

            self.recipe_data[recipe_name][_ingredient] = _units

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_recipe_details(self):
        results = self.cur.execute('Select * from recipeDetails;').fetchall()
        # Dict of Dicts....
        for row in results:
            recipe_name = row[0]
            _servings = row[1]
            _preparation = row[2]
            self.recipe_dict[recipe_name] = {servings: _servings, preparation:_preparation}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def create_window(self):
        cb=[]
        for recipe in self.recipe_dict:
            cb.append(psg.Checkbox(f"{recipe}", key=f'{recipe}'))
        
        b1=psg.Button("OK")
        b2=psg.Button("Exit")
        layout=[[cb],[b1, b2]]
        
        psg.set_options(font=("Arial Bold",14))
        window = psg.Window(title="Recipe List", layout=layout, margins=(500, 500)).read()
    
        results = window[1]
        for selected_recipe in results:
            if results.get(selected_recipe) is True:
                self.chosen_recipes.append(selected_recipe)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_ingredients(self):
        # get the ingredients
        for recipe_name in self.chosen_recipes:
            self.meal_calories[recipe_name] = 0
            _servings = float(self.recipe_dict[recipe_name][servings])
            # Need to get the ingredients of said recipe.
            for _ingredient_details in self.recipe_data.get(recipe_name):
                # Quantity of above ingredient for the recipe
                _qty = float(self.recipe_data.get(recipe_name).get(_ingredient_details))
                stmt = f"Select * from ingredientData where name = '{_ingredient_details}'"
                ingredient_results = self.cur.execute(stmt)

                for row in ingredient_results:
                    _ingredient = row[0]
                    _calories = float(row[1])
                    _units = row[2]
                    self.meal_calories[recipe_name] += (_calories * _qty / _servings)

                    if _ingredient in self.grocery_list:
                        self.grocery_list[_ingredient][qty] += _qty
                        self.grocery_list[_ingredient][units] = _units


                    else:
                        self.grocery_list[_ingredient] = {}
                        self.grocery_list[_ingredient][qty] = _qty
                        self.grocery_list[_ingredient][units] = _units

    def calculate_calories(self):
        pass


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def print_shopping_list(self):
        print()
        print("Your Shopping List:")
        for entry in self.grocery_list:
            print(entry, self.grocery_list.get(entry).get(qty), self.grocery_list.get(entry).get(units))
        print()
        
        for entry in self.chosen_recipes:
            recipe = self.recipe_data.get(entry)
            print(f"Recipe Name: {entry}")
            print(f"Servings: {self.recipe_dict[entry][servings]}")
            print(f"Calories per Serving: {self.meal_calories[entry]:.0f}")
            print(f"Preparation: {self.recipe_dict[entry][preparation]}")
            print()


if __name__ == '__main__':
    app = MealPlanner()
    app.startup()
