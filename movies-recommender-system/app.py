import pickle
import pandas as pd
import streamlit as st
import requests

# Function to fetch poster from TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    if poster_path:
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    return "https://via.placeholder.com/500x750?text=No+Image"

# Recommendation logic
def recommend(movie):
    if movie not in movies['title'].values:
        st.error("Selected movie not found in the dataset.")
        return [], []

    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

# App UI
st.header('🎬 Movie Recommender System')

# Load movie data
movies_dict = pickle.load(open(r'C:\Users\Rohan\Documents\machine-learning-projects\movies-recommender-system\movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Load similarity matrix
similarity = pickle.load(open(r'C:\Users\Rohan\Documents\machine-learning-projects\movies-recommender-system\similarity.pkl', 'rb'))

# Dropdown to select a movie
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "🎥 Type or select a movie from the dropdown",
    movie_list
)

# Show recommendations on button click
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    
    if recommended_movie_names:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(recommended_movie_names[i])
                st.image(recommended_movie_posters[i])
