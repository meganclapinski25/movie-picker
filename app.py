from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
import os

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
            # Skip movies without posters or overviews
            if not movie.get('poster_path') or not movie.get('overview'):
                continue
            
            # Check overview word count
            overview_words = movie['overview'].split()
            if len(overview_words) > 100:
                movie['overview'] = "No description available."

            # Add movie to the list
            movies.append(movie)

        return render_template('index.html', movies=movies)

    except requests.RequestException as e:
        return render_template('index.html', error="Error fetching data from the API.")



if __name__ == '__main__':
    app.run(debug=True)
