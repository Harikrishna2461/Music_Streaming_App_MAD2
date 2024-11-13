export default {
    template: `
    <div>
    <h1>Welcome to User Home Page :</h1>
    
    <div style="margin-bottom: 20px;">
        <button @click="createPlaylist" :style="{ backgroundColor: 'red' }">Create Playlist</button>
        <div v-if="playlists.length >= 0">
            <h2>Playlists : </h2>
            <ul>
                <li v-for="playlist in playlists" :key="playlist.id" style="margin-bottom: 10px;">
                    {{ playlist.name }}
                    <ul>
                        <li v-for="song in playlist.songs" :key="song.id">
                            {{ song.name }} - {{ song.artist }}
                            <button @click="openRatingModal(song)" style="margin-left: 10px;">Rate</button>
                            <span v-if="song.rating !== null" style="margin-left: 10px;">Rating: {{ song.rating }}/5</span>
                            <span>{{ getFlagStatus(song) }}</span>
                            <select v-model="selectedFlagOption" style="margin-left: 10px;">
                                <option value="flag">Flag</option>
                                <option value="unflag">Unflag</option>
                            </select>
                            <button @click="setFlag(song)" style="margin-left: 10px;">Set Flag</button>
                        </li>
                    </ul>
                    <button @click="viewPlaylist(playlist.id)" style="margin-top: 10px; background-color: #ff7f50;">View Playlist</button>
                    <button @click="deletePlaylist(playlist.id)" style="margin-left: 10px; background-color: #6495ed;">Delete Playlist</button>
                </li>
            </ul>
        </div>
    </div>
    
    <div style="margin-bottom: 20px;">
        <input type="text" v-model="searchQuery" placeholder="Search..." style="margin-right: 10px;">
        <button @click="search" style="background-color: darkgoldenrod;">Search</button>
    </div>
    
    <div style="margin-bottom: 20px;">
        <button @click="filterRangeSongs" style="background-color: turquoise; margin-right: 10px;">Filter Songs</button>
        <span>Minimum Rating:</span>
        <select v-model="minRating" @change="filterRangeSongs" style="margin-right: 10px;">
            <option v-for="rating in ratings" :value="rating">{{ rating }}</option>
        </select>
        <span>Maximum Rating:</span>
        <select v-model="maxRating" @change="filterRangeSongs">
            <option v-for="rating in ratings" :value="rating">{{ rating }}</option>
        </select>
    </div>

    <div style="margin-bottom: 20px;">
        <button @click="filterSongs" style="background-color: turquoise; margin-right: 10px;">Sort Songs</button>
        <select v-model="sortingOrder" @change="filterSongs" style="margin-right: 10px;">
            <option value="ascending">Ascending</option>
            <option value="descending">Descending</option>
        </select>
    </div>
    
    <div v-if="filteredAlbums.length >= 0">
        <h2>Songs : </h2>
        <div v-for="album in filteredAlbums" :key="album.name" style="margin-bottom: 30px;">
            <h3>{{ album.name }}</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Lyrics</th>
                        <th>Artist</th>
                        <th>Genre</th>
                        <th>Duration</th>
                        <th>My Rating</th>
                        <th>Average Rating</th>
                        <th>Play Song</th>
                        <th>Flag Status</th> 
                        <th>Add to Playlist</th>
                        <th>Rate Song</th>
                        <th>Set Flag</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="song in sortedSongs(album.songs)" :key="song.id">
                        <td>{{ song.name }}</td>
                        <td>{{ song.lyrics }}</td>
                        <td>{{ song.artist }}</td>
                        <td>{{ song.genre }}</td>
                        <td>{{ song.duration }}</td>
                        <td>{{ song.ratings }}</td>
                        <td>{{ song.average_ratings }}</td>
                        <td>
                            <button @click="playSong(song)" :style="{ backgroundColor: 'orange' }">Play Song</button>
                        </td>
                        <td>
                            {{ song.isFlagged ? 'Flagged' : 'Not Flagged' }}
                        </td>
                        <td>
                            <select v-model="selectedPlaylist">
                                <option v-for="playlist in playlists" :value="playlist.id">{{ playlist.name }}</option>
                            </select>
                            <button @click="addToPlaylist(song.id)">Add</button>
                        </td>
                        <td>
                            <select v-model="selectedRating">
                                <option v-for="rating in ratings" :value="rating">{{ rating }}</option>
                            </select>
                            <button @click="submitRating(song)">Rate</button>
                        </td>
                        <td>
                            <select v-model="selectedFlagOption">
                                <option value="flag">Flag</option>
                                <option value="unflag">Unflag</option>
                            </select>
                            <button @click="setFlag(song)">Set Flag</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    <div v-else>
        <p>No songs available.</p>
    </div>
    </div>
    `,
    data() {
        return {
            songs: [],
            playlists: [],
            selectedPlaylist: null,
            selectedRating: null,
            selectedFlagOption: 'flag', // Default to flagging
            ratings: [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],
            searchQuery: '',
            sortingOrder: 'ascending',
            minRating: 0, 
            maxRating: 5
            
        };
    },
    computed: {
        albums() {
            // Group songs by album
            const groupedSongs = {};
            this.songs.forEach(song => {
                if (song.album && !groupedSongs[song.album.name]) { // Check if song.album is not null
                    groupedSongs[song.album.name] = [];
                }
                if (song.album) { // Check if song.album is not null
                    groupedSongs[song.album.name].push(song);
                }
            });

            // Convert grouped songs to array format for rendering
            return Object.keys(groupedSongs).map(albumName => ({
                name: albumName,
                songs: groupedSongs[albumName]
            }));
        },
        filteredAlbums: {
            get() {
                if (!this.searchQuery) return this.albums;
                const query = this.searchQuery.toLowerCase();
                if (this.searchQuery) {
                return this.albums.filter(album => {
                    // Check if album name matches the query
                    if (album.name.toLowerCase().includes(query)) {
                        return true;
                    }
                    // Check if any song in the album matches the query
                    const matchingSongs = album.songs.filter(song => {
                        return (
                            song.name.toLowerCase().includes(query) ||
                            song.artist.toLowerCase().includes(query)
                        );
                    });
                    // Include the album in the filtered result if any song matches the query
                    return matchingSongs.length > 0;
                });
                }
            },
            set(value) {
                // We add a setter here, but it can be left empty if you don't need to modify the computed property
                // This is just to satisfy Vue's requirement of having both a getter and a setter for computed properties
            }
        },
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
            this.fetchPlaylists();
        }
    },
    methods: {
        async fetchSongs() {
            try {
                const response = await fetch('/api/user-home');
                const data = await response.json();
                if (response.ok) {
                    this.songs = data.songs.map(song => ({
                        ...song,
                        isFlagged: song.isFlagged === "1"
                    }));
                } else {
                    console.error('Failed to fetch songs:', data.message);
                }
            } catch (error) {
                console.error('Error occurred while fetching songs:', error);
            }
        },        
        async fetchPlaylists() {
            try {
                const token = localStorage.getItem('auth-token');
                if (!token) {
                    throw new Error('Token is missing');
                }

                const response = await fetch('/api/playlists', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                });
                const data = await response.json();
                if (response.ok) {
                    this.playlists = data.playlists;
                } else {
                    console.error('Failed to fetch playlists:', data.message);
                }
            } catch (error) {
                console.error('Error occurred while fetching playlists:', error);
            }
        },
        async createPlaylist() {
            const playlistName = prompt('Enter playlist name:');
            if (playlistName) {
                try {
                    const response = await fetch('/api/create-playlist', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ name: playlistName })
                    });
                    const data = await response.json();
                    if (response.ok) {
                        this.fetchPlaylists();
                    } else {
                        console.error('Failed to create playlist:', data.message);
                    }
                } catch (error) {
                    console.error('Error occurred while creating playlist:', error);
                }
            }
        },
        async addToPlaylist(songId) {
            if (!this.selectedPlaylist) {
                alert('Please select a playlist.');
                return;
            }
            try {
                const response = await fetch('/api/add-to-playlist', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ playlistId: this.selectedPlaylist, songId })
                });
                const data = await response.json();
                if (response.ok) {
                    alert('Song added to playlist successfully.');
                } else {
                    console.error('Failed to add song to playlist:', data.message);
                }
            } catch (error) {
                console.error('Error occurred while adding song to playlist:', error);
            }
        },
        async submitRating(song) {
            try {
                const response = await fetch('/api/rate-song', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        song_id: song.id,
                        rating: this.selectedRating
                    })
                });
                const data = await response.json();
                if (response.ok) {
                    song.ratings = this.selectedRating; 
                    Vue.set(song, 'rating', this.selectedRating);// Update the rating in the UI
                    alert('Rating submitted successfully.');
                } else {
                    console.error('Failed to submit rating:', data.message);
                }
            } catch (error) {
                console.error('Error occurred while submitting rating:', error);
            }
        },
        async viewPlaylist(playlistId) {
            this.$router.push({ name: 'playlist', params: { id: playlistId } });
        },
        async deletePlaylist(playlistId) {
            try {
                const confirmed = confirm('Are you sure you want to delete this playlist?');
                if (!confirmed) return;
    
                const response = await fetch(`/api/playlists/${playlistId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                const data = await response.json();
                if (response.ok) {
                    // Remove the deleted playlist from the playlists array
                    this.playlists = this.playlists.filter(playlist => playlist.id !== playlistId);
                    alert('Playlist deleted successfully.');
                } else {
                    console.error('Failed to delete playlist:', data.message);
                }
            } catch (error) {
                console.error('Error occurred while deleting playlist:', error);
            }
        },
        async setFlag(song) {
            try {
                const response = await fetch('/api/set-flag', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        song_id: song.id,
                        flag_option: this.selectedFlagOption
                    })
                });
                const data = await response.json();
                if (response.ok) {
                    // Update the flag status of the song
                    song.isFlagged = this.selectedFlagOption === 'flag';
                    alert('Flag updated successfully.');
                } else {
                    alert('Failed to set Flag: ' + data.message);
                    console.error('Failed to set Flag:', data.message);
                }
            } catch (error) {
                console.error('Error occurred while setting Flag:', error);
                alert('Error occurred while setting Flag: ' + error.message);
            }
        },
        getFlagStatus(song) {
            return song.isFlagged === 'Yes' ? 'Flagged' : 'Not Flagged';
        },
        search() {
            const query = this.searchQuery.toLowerCase().trim();
            if (!query) {
                // If the search query is empty, show all albums
                this.filteredAlbums = this.albums;
                return;
            }
        
            // Filter albums based on the search query
            this.filteredAlbums = this.albums.filter(album => {
                // Check if the album name matches the search query
                const albumNameMatches = album.name.toLowerCase().includes(query);
        
                // Check if any song in the album matches the artist
                const matchingArtists = album.songs.filter(song => {
                    return song.artist.toLowerCase().includes(query);
                });
        
                // Check if any song in the album matches the genre
                const matchingGenres = album.songs.some(song => {
                    return song.genre.toLowerCase().includes(query);
                });
        
                // Include the album in the filtered result if either album name, artist, or genre matches
                return albumNameMatches || matchingArtists.length > 0 || matchingGenres;
            });
        },
        sortedSongs(songs) {
            // Sort songs based on rating in ascending or descending order
            if (this.sortingOrder === 'ascending') {
                const sortedAscending = songs.slice().sort((a, b) => a.ratings - b.ratings);
                return sortedAscending;
            } else {
                const sortedDescending = songs.slice().sort((a, b) => b.ratings - a.ratings);
                console.log("Sorted Songs (Descending):", JSON.stringify(sortedDescending, null, 2));
                return sortedDescending;
            }
        },                     
        filterSongs() {
            console.log('Filtering songs...');
            // Re-render the filter ed albums to apply sorting and filtering
            this.filteredAlbums.forEach(album => {
                album.songs = this.sortedSongs(album.songs);
            });
        
            // Convert the albums array to a string for better logging
            const filteredAlbumsString = JSON.stringify(this.filteredAlbums, null, 2);
            // Return the filtered albums
            return this.filteredAlbums;
        }, 
        filterRangeSongs() {
            console.log('Filtering songs...');
            console.log('Min Rating:', this.minRating);
            console.log('Max Rating:', this.maxRating);
        
            // Convert ratings to numbers
            const min = parseFloat(this.minRating);
            const max = parseFloat(this.maxRating);
        
            // Filter songs based on the selected minimum and maximum ratings for each album
            this.filteredAlbums.forEach(album => {
                // Filter the songs and update the album's songs array directly
                album.songs = album.songs.filter(song => {
                    const rating = parseFloat(song.ratings);
                    return rating >= min && rating <= max;
                });
            });
            return this.filteredAlbums;
            // Log the filtered albums
            //console.log('Filtered Albums:', this.filteredAlbums);
        },                                                           
        async playSong(song) {
            try {
                console.log('Attempting to play song:', JSON.stringify(song)); // Log the song details
                const response = await fetch('/api/play-song', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        song_id: song.id, // Pass the song ID as part of the request body
                        album_id: song.album_id // Pass the album ID as part of the request body
                    })
                }); // Log the response from the backend
                const data = await response.json(); // Parse the response JSON
                if (response.ok) {
                    console.log('Play song response:', JSON.stringify(response));
                    // Update the song statistics table
                    alert('Song played successfully.');
                } else {
                    console.error('Failed to play song:', data.message);
                }
            } catch (error) {
                console.error('Error occurred while playing song:', error);
            }
        }                                                    
    }           
}; 