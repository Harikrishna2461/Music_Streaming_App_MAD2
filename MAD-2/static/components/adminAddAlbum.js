export default {
    template: `
    <div>
        <h1>Add Album</h1>
        <form @submit.prevent="addAlbum">
            <div class="form-group">
                <label for="albumName">Album Name:</label>
                <input type="text" class="form-control" id="albumName" v-model="albumData.name" required>
            </div>
            <div class="form-group">
                <label for="artist">Artist:</label>
                <input type="text" class="form-control" id="artist" v-model="albumData.artist" required>
            </div>
            <div class="form-group" style="margin-bottom: 20px;">
                <label for="creatorId">Creator ID:</label>
                <input type="text" class="form-control" id="creatorId" v-model="albumData.creatorId" required>
            </div>
            <button type="submit" class="btn btn-primary">Add Album</button>
        </form>
    </div>
    `,
    data() {
        return {
            albumData: {
                name: '',
                artist: '',
                creatorId: ''
            }
        };
    },
    mounted() {
        // Check if the auth token is present in the local storage
        const authToken = localStorage.getItem('auth-token');
        if (!authToken) {
            // Redirect the user to the login page if the auth token is missing
            alert('You are not logged in!')
            this.$router.push('/login');
        }
    },
    methods: {
        async addAlbum() {
            try {
                // Validate input data if needed
                
                // Send a request to the backend to add the album
                const response = await fetch('/api/admin-add-album', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.albumData)
                });
                const data = await response.json();
                
                if (response.ok) {
                    console.log('Album added successfully:', data.message);
                    alert('Album added successfully:')
                    // Optionally, redirect the user to another page or show a success message
                } else if (response.status === 400) {
                    console.error('An album with that name already exists,please choose a different name.');
                    alert('An album with that name already exists,please choose a different name.');
                } else {
                    console.error('An album with that name already exists,please choose a different name:', data.message);
                    alert('A song with that name already exists,please choose a different name.')
                    // Optionally, show an error message to the user
                }
            } catch (error) {
                console.error('Error occurred while adding album:', error);
                // Optionally, show an error message to the user
            }
        }
    }
};
