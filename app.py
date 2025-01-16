from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
import openai
import os
import random



# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.themoviedb.org/3/search/movie"


app = Flask(__name__)

# Route to serve the HTML file
@app.route('/')
def index():
    return render_template('index.html')  # Render the initial page

# Route to handle movie search
@app.route('/search', methods=['GET'])
def search_movie():
    query = request.args.get('query')
    if not query:
        return render_template('index.html', error="Please enter a movie title.")

    url = f"https://api.themoviedb.org/3/search/movie"
    params = {"api_key": API_KEY, "query": query}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        movies = []
        for movie in data.get('results', []):
            
            if not movie.get('poster_path') or not movie.get('overview'):
                continue
            
           
            overview_words = movie['overview'].split()
            if len(overview_words) > 100:
                movie['overview'] = "No description available."

            
            movies.append(movie)

        return render_template('index.html', movies=movies)

    except requests.RequestException as e:
        return render_template('index.html', error="Error fetching data from the API.")


@app.route('/similar_movie', methods=['GET', 'POST'])
def recommend_movie():
    if request.method == 'GET':
        selected_movie = request.args.get('movie_id')
        type = request.args.get('type')
        
        if not selected_movie or not type:
            return render_template('similar_movie.html', error="Missing movie_id or type.")
        
        if type == 'genre':
            movie_url = f"{BASE_URL}/movie/{selected_movie}"
            response = requests.get(movie_url, params={"api_key": API_KEY})
            movie_data = response.json()
            genres = movie_data.get('genres', [])
            genre_ids = [genre['id'] for genre in genres]

            # Get similar movies by genre
            similar_url = f"{BASE_URL}/discover/movie"
            params = {"api_key": API_KEY, "with_genres": ','.join(map(str, genre_ids))}
            similar_response = requests.get(similar_url, params=params)
            similar_movies = similar_response.json().get('results', [])
            random_movie = random.choice(similar_movies)
            return render_template('similar_movie.html', similar_movies=similar_movies)

    
    return render_template('similar_movie.html', error="Invalid request.")


if __name__ == '__main__':
    app.run(debug=True)
