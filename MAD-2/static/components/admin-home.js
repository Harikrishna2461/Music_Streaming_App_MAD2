export default {
    template: `
    <div>
        <h1>Admin Home Page</h1>
        <div v-for="button in buttons" :key="button.label">
            <button class="btn btn-primary btn-block mt-2" @click="navigate(button.route)">{{ button.label }}</button>
        </div>
    </div>
    `,
    data() {
        return {
            buttons: [
                { label: 'Admin Dashboard', route: 'dashboard' },
                { label: 'View Song and other App Statistics', route: 'song-statistics' },
                { label: 'Manage Songs', route: 'manage-songs' }
            ]
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
        navigate(route) {
            // Navigate to the selected route
            this.$router.push(route); 
        }
    }
};
