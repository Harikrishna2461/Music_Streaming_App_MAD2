export default {
    template: `
    <div>
    <h1>Playlist Details</h1>
    <div v-if="playlist">
        <h2>{{ playlist.name }}</h2>
        <ul>
            <li v-for="song in playlist.songs" :key="song.id">
                <div style="margin-bottom: 10px;"> <!-- Adjust the margin as needed -->
                    <span>{{ song.name }} - {{ song.artist }}</span>
                    <button class="btn btn-danger" @click="deleteSong(song.id)">Delete</button>
                </div>
            </li>
        </ul>
    </div>
    <div v-else>
        <p>Loading...</p>
    </div>
    </div>
    `,
    data() {
        return {
            playlist: null,
            error: null
        };
    },
    mounted() {
        // Check if the auth token is present in the local storage
        const authToken = localStorage.getItem('auth-token');
        if (!authToken) {
            // Redirect the user to the login page if the auth token is missing
            alert('You are not logged in!')
            this.$router.push('/login');
        } else {
            // Fetch songs and playlists if the auth token is present
            this.fetchPlaylist();
        }
    },
    created() {
        this.fetchPlaylist();
    },
    methods: {
        async fetchPlaylist() {
            try {
                const playlistId = this.$route.params.id;
                const response = await fetch(`/api/playlists/${playlistId}`);
                const data = await response.json();
                if (response.ok) {
                    this.playlist = data.playlist;
                } else {
                    console.error('Failed to fetch playlist:', data.message);
                    this.error = data.message;
                }
            } catch (error) {
                console.error('Error occurred while fetching playlist:', error);
                this.error = 'Error occurred while fetching playlist';
            }
        },
        async deleteSong(songId) {
            try {
                const playlistId = this.$route.params.id;
                const response = await fetch(`/api/playlists/${playlistId}/${songId}`, {
                    method: 'POST'
                });
                const data = await response.json();
                if (response.ok) {
                    // Remove the deleted song from the playlist
                    this.playlist.songs = this.playlist.songs.filter(song => song.id !== songId);
                } else {
                    console.error('Failed to delete song from playlist:', data.message);
                    this.error = data.message;
                }
            } catch (error) {
                console.error('Error occurred while deleting song from playlist:', error);
                this.error = 'Error occurred while deleting song from playlist';
            }
        }
    }
};
