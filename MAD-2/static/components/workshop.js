export default {
    template: `
    <div class="mt-4">
    <h1>Welcome to Workshop Page</h1>
    <div class="mt-4">
        <button class="btn btn-primary" @click="goToAddSong">Add Song</button>
    </div>
    <div class="mt-4">
        <button class="btn btn-success" @click="goToUpdateSong">Update Song</button>
    </div>
    <div class="mt-4">
        <button class="btn btn-danger" @click="goToDeleteSong">Delete Song</button>
    </div>
    <div class="mt-4">
        <button class="btn btn-warning" @click="goToAddAlbum">Add Album</button>
    </div>
    <div class="mt-4">
        <button class="btn btn-info" @click="goToUpdateAlbum">Update Album</button>
    </div>
    <div class="mt-4">
        <button class="btn btn-secondary" @click="goToDeleteAlbum">Delete Album</button>
    </div>
    <div class="mt-4">
        <button class="btn btn-dark" @click="goToCreatorHome">Go to Creator's Home</button>
    </div>
    </div>
    `,
    methods: {
        goToAddSong() {
            // Navigate to Add Song page
            this.$router.push({ name: 'add-song' });
        },
        goToUpdateSong() {
            // Navigate to Add Song page
            this.$router.push({ name: 'update-song' });
        },
        goToDeleteSong() {
            // Navigate to Add Song page
            this.$router.push({ name: 'delete-song' });
        },
        goToAddAlbum() {
            // Navigate to Add Song page
            this.$router.push({ name: 'add-album' });
        },
        goToUpdateAlbum() {
            // Navigate to Add Song page
            this.$router.push({ name: 'update-album' });
        },
        goToDeleteAlbum() {
            // Navigate to Add Song page
            this.$router.push({ name: 'delete-album' });
        },
        goToCreatorHome() {
            this.$router.push({ name: 'creator-home' });
        }
    }
};
