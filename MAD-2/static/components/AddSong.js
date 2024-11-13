export default {
    template: `
    <div class="mt-4">
        <h2>Add Song</h2>
        <form @submit.prevent="addSong">
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
                <select class="form-control" id="album" v-model="selectedAlbum" @change="updateSelectedAlbum" required>
                    <option v-for="album in albums" :key="album.id" :value="album.id">{{ album.name }}</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary">Add Song</button>
        </form>
    </div>
    `,
    data() {
        return {
            songData: {
                name: '',
                lyrics: '',
                genre: '',
                duration: '',
                album: null  // Initialize as null
            },
            albums: [], // Array to store the albums fetched from the backend
            selectedAlbum: null  // Variable to store the ID of the selected album
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
            this.fetchAlbums();
        }
    },
    methods: {
        async fetchAlbums() {
            try {
                const response = await fetch('/api/albums');
                const data = await response.json();
                if (response.ok) {
                    this.albums = data.albums;
                } else {
                    console.error('Failed to fetch albums:', data.error);
                    alert('Failed to fetch albums')
                }
            } catch (error) {
                console.error('Error occurred while fetching albums:', error);
                alert('Error occurred while fetching albums:')
            }
        },
        updateSelectedAlbum() {
            // Find the album object corresponding to the selected ID
            this.songData.album = this.albums.find(album => album.id === this.selectedAlbum);
            console.log(JSON.stringify(this.songData.album));
        },
        async addSong() {
            try {
                const response = await fetch('/api/add-song', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.songData)
                });
                console.log(JSON.stringify(this.songData.album));
                const data = await response.json();
                if (response.ok) {
                    console.log(JSON.stringify(this.songData.album));
                    console.log('Song added successfully.', data.message);
                    alert('Song added successfully.')
                    // Clear form after successful addition
                    this.resetForm();
                } else if (response.status === 400) {
                    console.error('A song with that name already exists,please choose a different name.');
                    alert('A song with that name already exists,please choose a different name.');
                } else if (response.status === 403) {
                    alert('You are not authorized to add songs to this album.');
                } else {
                    console.error('A song with that name already exists,please choose a different name:', data.error);
                    alert('A song with that name already exists,please choose a different name.')
                }
            } catch (error) {
                console.error('Error occurred while adding song:', error);
                alert('Error occurred while adding song.')
            }
        },
        resetForm() {        // Reset form fields after successful addition
            this.songData = {
                name: '',
                lyrics: '',
                genre: '',
                duration: '',
                album: null  // Reset to null
            };
        }
    }
};
