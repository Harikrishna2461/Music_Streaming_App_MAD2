export default {
    template: `
    <div class="mt-4">
    <h2>Update Album</h2>
    <form @submit.prevent="updateAlbum">
        <div class="form-group">
                <label for="artist">Present Album Name</label>
                <input type="text" class="form-control" id="present_album_name" v-model="albumData.present_album_name" required>
        </div>
        <div class="form-group">
                <label for="artist">New Album Name</label>
                <input type="text" class="form-control" id="new_album_name" v-model="albumData.new_album_name" required>
        </div>
        <div class="form-group" style="margin-bottom: 20px;">
                <label for="artist">New Artist Name</label>
                <input type="text" class="form-control" id="new_artist_name" v-model="albumData.new_artist_name" required>
        </div>
        <button type="submit" class="btn btn-primary">Update Album</button>
    </form>
    </div>
    `,
    data() {
        return {
            albumData: {
                new_album_name: '',
                new_artist_name: '',
                present_album_name : ''
            },
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
        async updateAlbum() {
            try {
                const response = await fetch('/api/admin-update-album', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        // Only send the selected album ID to the backend
                        present_album_name: this.albumData.present_album_name,
                        new_album_name: this.albumData.new_album_name,
                        new_artist_name: this.albumData.new_artist_name,
                    })
                });
                const data = await response.json();
                if (response.ok) {
                    console.log('Album updated successfully:', data.message);
                    // Clear selected album after successful update
                    this.resetForm();
                    alert('Album updated successfully.')
                } else if (response.status === 400) {
                    console.error('An album with that name already exists,please choose a different name.');
                    alert('An album with that name already exists,please choose a different name.');
                } else {
                    console.error('An album with that name already exists,please choose a different name:', data.error);
                    alert('An album with that name already exists,please choose a different name.')
                }
            } catch (error) {
                console.error('Error occurred while updating album:', error);
                alert('Error occurred while updating album.')
            }
        },
        resetForm() {
            // Reset the form fields after saving
            this.albumData = {
                new_album_name: '',
                new_artist_name: '',
                present_album_name : ''
            };
        }
    },
};