export default {
    template : `
        <div class="mt-4">
        <h2>Delete Album</h2>
        <form @submit.prevent="deleteAlbum">
        <div class="form-group" style="margin-bottom: 20px;">
            <label for="albumName">Album Name:</label>
            <input type="text" class="form-control" id="albumName" v-model="albumName" required>
        </div>
        <button type="submit" class="btn btn-danger">Delete Album</button>
        </form>
        </div>
    `,
        data() {
        return {
        albumName: ''
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
            async deleteAlbum() {
            try {
            const response = await fetch('/api/admin-delete-album', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                albumName: this.albumName
            })
            });
            const data = await response.json();
            if (response.ok) {
            console.log('Album deleted successfully:', data.message);
            alert('Album deleted successfully.')
              // Optionally, you can navigate to another page or perform additional actions here
            } else {
            console.error('Failed to delete album:', data.message);
            alert('Failed to delete album.')
            }
        } catch (error) {
            console.error('Error occurred while deleting album:', error);
            alert('Error occurred while deleting album.')
        }
        }
    }
    };