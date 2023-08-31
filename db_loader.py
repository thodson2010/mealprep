import sqlite3, yaml

# Define some constants for ease of use
ingredients ='ingredients'
servings = 'servings'
qty = 'qty'
calories = 'calories'
units = 'units'
preparation = 'preparation'


def load_db_cursor():
    con = sqlite3.connect("cookbook.db")
    cur = con.cursor()
    create_db_tables(cur)
    return con, cur

def create_db_tables(cur):
    # Check to create our DB Tables
    cur.execute("CREATE TABLE IF NOT EXISTS recipeData(recipeName, ingredient, qty, PRIMARY KEY (recipeName, ingredient))")
    cur.execute("CREATE TABLE IF NOT EXISTS ingredientData(name TEXT PRIMARY KEY, calories, unit)")
    cur.execute("CREATE TABLE IF NOT EXISTS recipeDetails(name TEXT PRIMARY KEY, servings, steps)")

def load_recipe_data(con, cur):
    """
    Load in the recipe data from YAML
    :return:
    """
    print('Loading Recipes')
    with open("meals.yaml", "r") as stream:
        try:
            meals = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    for meal in meals:
        # Get the number of servings
        _servings = meals.get(meal).get(servings)
        _preparation = meals.get(meal).get(preparation)
        stmt = f"REPLACE INTO recipeDetails VALUES ('{meal}','{_servings}','{_preparation}');"
        #print(stmt)
        cur.execute(stmt)


        for _ingredient in meals.get(meal).get(ingredients):
            qty = meals.get(meal).get(ingredients).get(_ingredient)
            stmt = f"REPLACE INTO recipeData VALUES ('{meal}','{_ingredient}','{qty}');"
            #print(stmt)
            cur.execute(stmt)

    con.commit()

def load_ingredient_data(con, cur):
    """
    Load in the ingrediant data from YAML
    :return:
    """

    print('Loading Ingredients')
    with open("ingredients.yaml", "r") as stream:
        try:
            ingredients = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    for entry in ingredients:
        _calories = ingredients.get(entry).get(calories)
        _units = ingredients.get(entry).get(units)
        stmt = f"REPLACE INTO ingredientData VALUES ('{entry}','{_calories}','{_units}');"
        #print(stmt)
        cur.execute(stmt)
        con.commit()

