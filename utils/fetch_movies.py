import json
import http.client
from decouple import config

# Establish connection
conn = http.client.HTTPSConnection("list-movies-v3.p.rapidapi.com")
api_key = config("RAPID_API_KEY", default=None)

# Set headers
headers = {
    'x-rapidapi-key': api_key,
    'x-rapidapi-host': "list-movies-v3.p.rapidapi.com"
}

formatted_movies = []

for i in range(2, 11):
    # Make the request
    conn.request("GET", f"/api/v2/list_movies.json?limit=20&page={i}&quality=all&minimum_rating=0&query_term=0&genre=all&sort_by=date_added&order_by=desc&with_rt_ratings=false", headers=headers)

    # Get the response
    res = conn.getresponse()
    data = res.read()

    # Decode response and load into dictionary
    response_dict = json.loads(data.decode("utf-8"))

    # Process and format the data
    for movie in response_dict.get('data', {}).get('movies', []):
        formatted_movie = {
            "title": movie.get('title'),
            "releaseYear": movie.get('year'),
            "genre": ', '.join([genre for genre in movie.get('genres', [])]),
            "coverUrl": movie.get('medium_cover_image')
        }
        formatted_movies.append(formatted_movie)

# Save the formatted data to a JSON file
with open('movies_data3.json', 'w') as json_file:
    json.dump(formatted_movies, json_file, indent=4)

print("Data has been saved to movies_data2.json")
