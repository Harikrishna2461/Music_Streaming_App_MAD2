export default {
    template: `
    <div class="mt-4">
    <h2>Update Song</h2>
    <form @submit.prevent="updateSong">
        <div class="form-group">
            <label for="song">Select Song:</label>
            <select class="form-control" id="song" v-model="selectedSong" required>
                <option v-for="song in songs" :key="song.id" :value="song">{{ song.name }}</option>
            </select>
        </div>
        <div class="form-group">
            <label for="name">Name:</label>
            <input type="text" class="form-control" id="name" v-model="songData.name" required>
        </div>
        <div class="form-group">
            <label for="lyrics">Lyrics:</label>
            <textarea class="form-control" id="lyrics" v-model="songData.lyrics" required></textarea>
        </div>
        <div class="form-group">
            <label for="genre">Genre:</label>
            <input type="text" class="form-control" id="genre" v-model="songData.genre" required>
        </div>
        <div class="form-group">
            <label for="duration">Duration:</label>
            <input type="number" class="form-control" id="duration" v-model="songData.duration" required>
        </div>
        <div class="form-group" style="margin-bottom: 20px;"> 
            <label for="album">Album:</label>
            <select class="form-control" id="album" v-model="songData.album" required>
                <option v-for="album in albums" :key="album.id" :value="album">{{ album.name }}</option>
            </select>
        </div>
        <button type="submit" class="btn btn-primary">Update Song</button>
    </form>
    </div>
    `,
    data() {
        return {
            songs: [], // Array to store the songs fetched from the backend
            selectedSong: '', // Variable to store the selected song ID
            songData: {
                name: '',
                lyrics: '',
                genre: '',
                duration: '',
                album: ''
            },
            albums: [], // Array to store the albums fetched from the backend
            isCreator: false // Flag to indicate if the current user is the creator of the selected song
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
            this.fetchAlbums();
        }
    },
    watch: {
        selectedSong(newVal) {
            console.log('Selected Song:', newVal);
            console.log('All Songs:', this.songs);
            if (newVal) {
                this.isCreator = this.songs.find(song => song.id === newVal.id).creator_id === this.currentUserId;
            } else {
                this.isCreator = false;
            }
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
                }
            } catch (error) {
                console.error('Error occurred while fetching songs:', error);
            }
        },
        async fetchAlbums() {
            try {
                const response = await fetch('/api/albums');
                const data = await response.json();
                if (response.ok) {
                    this.albums = data.albums;
                } else {
                    console.error('Failed to fetch albums:', data.error);
                }
            } catch (error) {
                console.error('Error occurred while fetching albums:', error);
            }
        },
        async updateSong() {
            try {
                // Check if the selected song and updated song data are valid
                if (!this.selectedSong) {
                    console.error('Please select a song to update.');
                    return;
                }

                // Proceed with the update request
                const response = await fetch('/api/admin-update-song', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        songId: this.selectedSong.id,
                        // Include other fields you want to update
                        name: this.songData.name,
                        lyrics: this.songData.lyrics,
                        genre: this.songData.genre,
                        duration: this.songData.duration,
                        album: this.songData.album
                    })
                });
                const data = await response.json();
                console.log(data)
                if (response.ok) {
                    console.log('Song updated successfully:', data.message);
                    alert('Song updated successfully.')
                    // Reset form or update UI as needed
                    this.resetForm();
                } else if (response.status === 400) {
                    console.error('An album with that name already exists,please choose a different name.');
                    alert('An album with that name already exists,please choose a different name.');
                } else {
                    console.error('A song with that name already exists,please choose a different name:', data.error);
                    alert('A song with that name already exists,please choose a different name.')
                }
            } catch (error) {
                console.error('Error occurred while updating song:', error);
                alert('Error occurred while updating song.')
            }
        },        
        resetForm() {        // Reset form fields after successful addition
            this.songData = {
                name: '',
                lyrics: '',
                genre: '',
                duration: '',
                album: ''  
            };
        }
    }
};