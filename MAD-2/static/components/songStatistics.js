export default {
    template: `
    <div>
        <h1>Song Statistics : </h1>
        <div>
        <h2>Most Streamed Song : </h2>
        <p>{{ mostStreamedSong }}</p>
        </div>
        <div>
        <h2>Most Streamed Album : </h2>
        <p>{{ mostStreamedAlbum }}</p>
        </div>
        <div>
        <h2>Most Active User : </h2>
        <p>{{ mostActiveUser }}</p>
        </div>
        <div>
        <h2>Most Streamed Song in Last Month : </h2>
        <p>{{ mostStreamedSongLastMonth }}</p>
        </div>
        <div>
        <h2>Most Streamed Album in Last Month : </h2>
        <p>{{ mostStreamedAlbumLastMonth }}</p>
        </div>
        <div>
        <h2>Most Active User in Last Month : </h2>
        <p>{{ mostActiveUserLastMonth }}</p>
        </div>
        <div>
        <h2>Highest Rated Songs : </h2>
        <ul>
        <li v-for="song in highest_rated_songs" :key="song">{{ song }}</li>
        </ul>
        </div>
    </div>
    `,
    data() {
    return {
        mostStreamedSong: '',
        mostStreamedAlbum: '',
        mostActiveUser: '',
        mostStreamedSongLastMonth: '',
        mostStreamedAlbumLastMonth: '',
        mostActiveUserLastMonth: '',
        highest_rated_songs: []
    };
    },
    mounted() {
    this.fetchSongStatistics();
    },
    methods: {
    async fetchSongStatistics() {
        try {
        const response = await fetch('/api/song-statistics');
        const data = await response.json();
        if (response.ok) {
            this.mostStreamedSong = data.mostStreamedSong;
            this.mostStreamedAlbum = data.mostStreamedAlbum;
            this.mostActiveUser = data.mostActiveUser;
            this.mostStreamedSongLastMonth = data.mostStreamedSongLastMonth;
            this.mostStreamedAlbumLastMonth = data.mostStreamedAlbumLastMonth;
            this.mostActiveUserLastMonth = data.mostActiveUserLastMonth;
            this.highest_rated_songs = data.highest_rated_songs;
        } else {
            console.error('Failed to fetch song statistics:', data.message);
        }
        } catch (error) {
        console.error('Error fetching song statistics:', error);
        }
    },
    },
};
