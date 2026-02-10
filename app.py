import utils.transport
import utils.session
import streamlit as st
import pickle
import pandas as pd
import requests

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="🎬 Movie Recommender System",
    page_icon="🎬",
    layout="wide",
)

# ──────────────────────────────────────────────
# Custom CSS for better styling
# ──────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .main-header h1 {
        color: #E50914;
        font-size: 2.5rem;
        font-weight: 800;
    }
    .main-header p {
        color: #999;
        font-size: 1.1rem;
    }
    .movie-card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(229, 9, 20, 0.3);
    }
    .movie-title {
        color: #fff;
        font-size: 0.95rem;
        font-weight: 600;
        margin-top: 8px;
        line-height: 1.3;
    }
    .stButton > button {
        background-color: #E50914;
        color: white;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.6rem 2rem;
        border-radius: 8px;
        border: none;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #b20710;
        color: white;
    }
    .footer {
        text-align: center;
        color: #666;
        padding: 2rem 0 1rem;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Load Data
# ──────────────────────────────────────────────
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity


movies, similarity = load_data()


# ──────────────────────────────────────────────
# Fetch movie poster from TMDB API
# ──────────────────────────────────────────────
def fetch_poster(movie_id):
    """Fetch movie poster from TMDB API."""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(url, timeout=5)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except Exception:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"


def fetch_movie_details(movie_id):
    """Fetch movie details from TMDB API."""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(url, timeout=5)
        data = response.json()
        return {
            'poster': f"https://image.tmdb.org/t/p/w500{data.get('poster_path', '')}",
            'rating': data.get('vote_average', 'N/A'),
            'release_date': data.get('release_date', 'N/A'),
            'overview': data.get('overview', 'No overview available.'),
        }
    except Exception:
        return {
            'poster': "https://via.placeholder.com/500x750?text=No+Poster",
            'rating': 'N/A',
            'release_date': 'N/A',
            'overview': 'No overview available.',
        }


# ──────────────────────────────────────────────
# Recommend function
# ──────────────────────────────────────────────
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    recommended_ids = []
    for idx, score in movies_list:
        movie_id = movies.iloc[idx].movie_id
        recommended_movies.append(movies.iloc[idx].title)
        recommended_posters.append(fetch_poster(movie_id))
        recommended_ids.append(movie_id)
    return recommended_movies, recommended_posters, recommended_ids


# ──────────────────────────────────────────────
# UI Layout
# ──────────────────────────────────────────────

# Header
st.markdown("""
<div class="main-header">
    <h1>🎬 Movie Recommender System</h1>
    <p>Select a movie you like and discover similar movies you'll love!</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Movie selection
col1, col2 = st.columns([3, 1])
with col1:
    selected_movie = st.selectbox(
        "🔍 Type or select a movie",
        movies['title'].values,
        index=None,
        placeholder="Search for a movie..."
    )
with col2:
    st.write("")  # spacing
    recommend_btn = st.button("🎯 Recommend", use_container_width=True)

# Show recommendations
if recommend_btn and selected_movie:
    with st.spinner("🔄 Finding similar movies..."):
        names, posters, ids = recommend(selected_movie)

    st.markdown("### 🍿 Recommended Movies")
    st.divider()

    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.image(posters[i], use_container_width=True)
            st.markdown(f"""
            <div style="text-align:center;">
                <p class="movie-title">{names[i]}</p>
            </div>
            """, unsafe_allow_html=True)

    # Show details in expanders
    st.markdown("### 📋 Movie Details")
    for i, name in enumerate(names):
        details = fetch_movie_details(ids[i])
        with st.expander(f"🎥 {name}"):
            detail_col1, detail_col2 = st.columns([1, 3])
            with detail_col1:
                st.image(posters[i], width=150)
            with detail_col2:
                st.markdown(f"**⭐ Rating:** {details['rating']}/10")
                st.markdown(f"**📅 Release Date:** {details['release_date']}")
                st.markdown(f"**📝 Overview:** {details['overview']}")

elif recommend_btn and not selected_movie:
    st.warning("⚠️ Please select a movie first!")

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    Built with ❤️ using Streamlit & TMDB API | Content-Based Filtering with Cosine Similarity
</div>
""", unsafe_allow_html=True)
