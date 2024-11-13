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
        // Fetch songs from the backend when the component is mounted
        this.fetchSongs();
        },
        methods: {
        currentUserId() {
          // Implement this method to retrieve the current user ID
            return localStorage.getItem('current_user_id');
        },
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
            const currentUserId = localStorage.getItem('current_user_id'); // Assuming you have implemented currentUserId() method
            
            // Check if the selected song is valid
            if (!this.selectedSong) {
                console.error('Please select a song to delete.');
                alert('Please select a song to delete.')
                return;
            }
            console.log(currentUserId)
            console.log(this.selectedSong.creator_id)

            // Check if the current user is the creator of the selected song
            if (parseInt(this.selectedSong.creator_id) !== parseInt(currentUserId)) {
                console.error('You are not authorized to delete this song.');
                alert('You are not authorized to delete this song.')
                return;
            }
            
            // Proceed with the delete request
            const response = await fetch('/api/delete-song', {
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
                alert('Song Deleted Sucessfully.')
              // Reset form or update UI as needed
              this.selectedSong = ''; // Reset selected song after deletion
              this.fetchSongs(); // Refresh the list of songs
            } else if (response.status === 403) {
                alert('You are not authorized to delete this song.');
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