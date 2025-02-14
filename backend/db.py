from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv

def search_computer_in_mongo(user_query):
    # Conectar a MongoDB
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("MONGO_DB")]
    collection = db[os.getenv("MONGO_COLLECTION")]
    
    # Crear una consulta con $or para que se cumpla al menos uno de los criterios
    or_conditions = []
    
    for key, value in user_query.items():
        # Cada clave se convierte en una condición con $regex para buscar el valor dentro del campo
        or_conditions.append({key: {"$regex": value, "$options": "i"}})  # "$options": "i" hace la búsqueda insensible a mayúsculas/minúsculas
    
    # Usar $or para que la consulta sea verdadera si al menos una condición es verdadera
    query = {"$or": or_conditions}
    
    # Buscar productos que coincidan con al menos uno de los criterios
    matching_products = collection.find(query)
    
    # Clasificar los productos por cuántos criterios coinciden
    scored_products = []
    for product in matching_products:
        score = 0
        for key, value in user_query.items():
            if key in product and value.lower() in str(product[key]).lower():  # Realizar una búsqueda insensible a mayúsculas
                score += 1
        scored_products.append((product, score))
    
    # Ordenar por la cantidad de criterios coincidentes (más puntuación es mejor)
    scored_products.sort(key=lambda x: x[1], reverse=True)
    
    return scored_products
