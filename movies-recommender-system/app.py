import pickle
import pandas as pd
import streamlit as st
import requests
from streamlit_lottie import st_lottie
import streamlit.components.v1 as components
import base64


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def fetch_movie_details(movie_id):
    api_key = "6cfeaa18912df6c0a6aea1c4d38df932"

    # Poster
    details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    details_data = requests.get(details_url).json()
    poster_path = details_data.get('poster_path')
    poster_url = "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else "https://via.placeholder.com/500x750?text=No+Image"

    # Trailer
    videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}&language=en-US"
    videos_data = requests.get(videos_url).json()
    trailer_url = None
    for video in videos_data.get('results', []):
        if video['type'] == "Trailer" and video['site'] == "YouTube":
            trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
            break

    return poster_url, trailer_url

# Recommendation logic
def recommend(movie):
    if movie not in movies['title'].values:
        st.error("Selected movie not found in the dataset.")
        return [], [], []

    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_trailers = []

    for i in distances[1:51]:
        movie_id = movies.iloc[i[0]].movie_id
        poster, trailer = fetch_movie_details(movie_id)
        recommended_movie_posters.append(poster)
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_trailers.append(trailer)

    return recommended_movie_names, recommended_movie_posters, recommended_movie_trailers


st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")


# Load Lottie animation
lottie_movie = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_rp7zqvxh.json")

# Load popcorn image for typewriter cursor
with open(r"C:\Users\Rohan\Documents\machine-learning-projects\movies-recommender-system\popcorn-emoji-492x512-rszsmz15.png", "rb") as img_file:
    # Read the image and encode it to base64
    encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
with open(r"C:\Users\Rohan\Documents\machine-learning-projects\movies-recommender-system\horror-movie-collage-a75hl41trttus1sy.jpg", "rb") as img_file:
    encoded_bg = base64.b64encode(img_file.read()).decode()   


# Typewriter Heading with Popcorn Cursor
components.html(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600&display=swap');

.typewriter-container {{
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 1rem;
}}

.typewriter {{
  font-family: 'Orbitron', sans-serif;
  font-size: 2.375rem;
  color: #FF4B4B;
  white-space: nowrap;
  overflow: hidden;
  position: relative;
}}

.text {{
  display: inline-block;
  overflow: hidden;
  border-right: none;
  animation: typeLoop 10s steps(30) infinite;
}}

.cursor {{
  display: inline-block;
  position: relative;
  top: -2px;
  margin-left: 5px;
  width: 28px;
  height: 28px;
  animation: blink 1s infinite;
}}

.cursor img {{
  width: 100%;
}}

@keyframes typeLoop {{
  0%   {{ width: 0 }}
  25%  {{ width: 100% }}   /* Typing done */
  45%  {{ width: 100% }}   /* Hold full text */
  65%  {{ width: 0 }}      /* Deleting done */
  100% {{ width: 100% }}   /* Typing starts again immediately */
}}

@keyframes blink {{
  0%, 100% {{ opacity: 0 }}
  50% {{ opacity: 1 }}
}}
</style>

<div class="typewriter-container">
  <div class="typewriter">
    <span class="text">Movie Recommender System</span>
    <span class="cursor"><img src="data:image/png;base64,{encoded_image}" /></span>
  </div>
</div>
""", height=100)





# Subtitle
st.markdown(
    "<p style='text-align: center; font-size: 18px;'>Find similar movies to your favorites instantly!</p>",
    unsafe_allow_html=True
)

if lottie_movie:
    st_lottie(lottie_movie, height=200, key="movie", speed=1)

# Load data
movies_dict = pickle.load(open(r'C:\Users\Rohan\Documents\machine-learning-projects\movies-recommender-system\movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open(r'C:\Users\Rohan\Documents\machine-learning-projects\movies-recommender-system\similarity.pkl', 'rb'))

# Dropdown
st.subheader("🎥 Choose a movie:")
selected_movie = st.selectbox("Type or select a movie", movies['title'].values)

# Show recommendations
if st.button("✨ Show Recommendations"):
    names, posters, trailers = recommend(selected_movie)

    if names:
        st.markdown("---")
        st.subheader("🔮 You might also like:")

    for row in range(10):
        cols = st.columns(5)
        for col in range(5):
            idx = row * 5 + col
            if idx < len(names):
                with cols[col]:
                    st.image(posters[idx])
                    st.markdown(f"<p style='text-align: center; font-weight: bold;'>{names[idx]}</p>", unsafe_allow_html=True)

                    if trailers[idx]:
                        with st.expander("🎞️ Watch Trailer"):
                            youtube_id = trailers[idx].split("v=")[-1]
                            st.video(f"https://www.youtube.com/embed/{youtube_id}")
