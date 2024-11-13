export default {
    template: `
    <div>
        <h1>Admin Dashboard</h1>
        <div class="statistic">
            <p>Number of Users: {{ statistics.num_users }}</p>
        </div>
        <div class="statistic">
            <p>Number of Creators: {{ statistics.num_creators }}</p>
        </div>
        <div class="statistic">
            <p>Number of Songs: {{ statistics.num_songs }}</p>
        </div>
        <div class="statistic">
            <p>Number of Albums: {{ statistics.num_albums }}</p>
        </div>
        <div class="statistic">
            <p>Number of New Users in Last Month : {{ statistics.num_new_users_last_month }}</p>
        </div>
    </div>
    `,
    data() {
        return {
            statistics: {}
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
    created() {
        this.fetchStatistics();
    },
    methods: {
        async fetchStatistics() {
            try {
                const response = await fetch('/api/dashboard');
                const data = await response.json();
                if (response.ok) {
                    this.statistics = data;
                } else {
                    console.error('Failed to fetch statistics:', data.message);
                }
            } catch (error) {
                console.error('Error occurred while fetching statistics:', error);
            }
        }
    },
    style: `
    .statistic {
        margin-bottom: 20px;
        border: 2px solid #333;
        border-radius: 10px;
        padding: 20px;
    }

    .statistic-label {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #f44336; /* Red color */
    }

    .statistic-value {
        font-size: 28px;
        font-weight: bold;
        color: #4caf50; /* Green color */
    }
`
};
