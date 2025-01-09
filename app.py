from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
import os
from openai import OpenAI
import openai


# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.themoviedb.org/3/search/movie"
CHAT_AI_API = os.getenv("OPEN_AI_KEY")

client = OpenAI()
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
# Updated API usage
@app.route('/suggest_similar_movie', methods=['POST'])
def suggest_similar_movie():
    movie_data = request.json
    title = movie_data['title']
    genre = movie_data['genre']
    overview = movie_data['overview']
    button_action = movie_data['button']  # 'random', 'genre', 'rating'

    # Create a prompt for ChatGPT to suggest a similar movie
    prompt = f"Suggest a movie similar to {title}, which is a {genre} movie. The plot of the movie is: {overview}. Please suggest a similar movie for the {button_action} button."

    try:
        # Use the new OpenAI ChatCompletion API
        response = client.chat.completions.create(
            model="gpt-4",  # You can use GPT-3.5 as well
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        print(f"OpenAI Response: {response}")
        
        # Extract the suggested movie from the response
        suggested_movie = response['choices'][0]['message']['content'].strip()
        return jsonify({'suggested_movie': suggested_movie})

    except Exception as e:
        # Log the error
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
