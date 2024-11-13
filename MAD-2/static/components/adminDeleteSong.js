export default {
    template : `
    <div class="mt-4">
    <h2>Delete Song</h2>
    <form @submit.prevent="deleteSong">
        <div class="form-group" style="margin-bottom: 20px;">
        <label for="song">Select Song:</label>
        <select class="form-control" id="song" v-model="selectedSong" required>
            <option v-for="song in songs" :key="song.id" :value="song">{{ song.name }}</option>
        </select>
        </div>
        <button type="submit" class="btn btn-danger">Delete Song</button>
    </form>
    </div>
    `,
    data() {
        return {
          songs: [], // Array to store the songs fetched from the backend
          selectedSong: '', // Variable to store the selected song
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
                this.fetchSongs();
            }
        },
        methods: {
        async fetchSongs() {
            try {
            const response = await fetch('/api/songs');
            const data = await response.json();
            if (response.ok) {
                this.songs = data.songs;
            } else {
                console.error('Failed to fetch songs:', data.error);
                alert('Failed to fetch songs.')
            }
            } catch (error) {
            console.error('Error occurred while fetching songs:', error);
            alert('Error occurred while fetching songs.')
            }
        },
        async deleteSong() {
            try {
            
            // Check if the selected song is valid
            if (!this.selectedSong) {
                console.error('Please select a song to delete.');
                alert('Please select a song to delete.')
                return;
            }
            
            // Proceed with the delete request
            const response = await fetch('/api/admin-delete-song', {
                method: 'DELETE',
                headers: {
                'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                songId: this.selectedSong.id
                })
            });
            const data = await response.json();
            if (response.ok) {
                console.log('Song deleted successfully:', data.message);
                alert('Song deleted sucessfully.')
              // Reset form or update UI as needed
              this.selectedSong = ''; // Reset selected song after deletion
              this.fetchSongs(); // Refresh the list of songs
            } else {
                console.error('Failed to delete song:', data.error);
                alert('Failed to delete song.')
            }
            } catch (error) {
            console.error('Error occurred while deleting song:', error);
            alert('Error occurred while deleting song.')
            }
        }
        }
}