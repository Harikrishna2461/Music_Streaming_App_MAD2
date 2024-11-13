export default {
    template: `
    <div class="mt-4">
    <h2>Add Album</h2>
    <form @submit.prevent="addAlbum">
        <div class="form-group" style="margin-bottom: 20px;">
            <label for="name">Name:</label>
            <input type="text" class="form-control" id="name" v-model="albumData.name" required>
        </div>
        <button type="submit" class="btn btn-primary btn-lg">Add Album</button>
    </form>
    </div>
    `,
    data() {
        return {
            albumData: {
                name: '',
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
                const response = await fetch('/api/add-album', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        name: this.albumData.name,
                    })
                });

                const data = await response.json();
                if (response.ok) {
                    console.log('Album added successfully:', data.message);
                    alert('Album added successfully.')
                    this.resetForm(); // Assuming you have a resetForm method to clear the form fields
                } else if (response.status === 400) {
                    console.error('An album with that name already exists,please choose a different name.');
                    alert('An album with that name already exists,please choose a different name.');
                } else {
                    console.error('An album with that name already exists,please choose a different name:', data.message);
                    alert('An album with that name already exists,please choose a different name')
                }
            } catch (error) {
                console.error('Error occurred while adding album:', error);
                alert('Error occurred while adding album.')
            }
        },
        resetForm() {
            // Reset the form fields after saving
            this.songData = {
                name: '',
                lyrics: '',
                genre: '',
                duration: '',
            };
        }
    }
};
