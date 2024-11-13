import signup from './components/signup.js'
import login from './components/login.js'
import adminHome from './components/admin-home.js'
import adminDashboard from './components/dashboard.js'
import adminManageSongs from './components/manage-songs.js'
import adminAddAlbum from './components/adminAddAlbum.js'
import adminUpdateAlbum from './components/adminUpdateAlbum.js' 
import adminDeleteAlbum from './components/adminDeleteAlbum.js' 
import adminAddSong from './components/adminAddSong.js'
import adminUpdateSong from './components/adminUpdateSong.js' 
import adminDeleteSong from './components/adminDeleteSong.js' 
import userHome from './components/user-home.js'
import creatorHome from './components/creator-home.js'
import PlaylistPage from './components/playlists.js'
import Workshop from './components/workshop.js'
import AddAlbum from './components/AddAlbum.js'
import AddSong from './components/AddSong.js'
import UpdateAlbum from './components/UpdateAlbum.js'
import UpdateSong from './components/UpdateSong.js'
import DeleteAlbum from './components/DeleteAlbum.js'
import DeleteSong from './components/DeleteSong.js'
import songStatistics from './components/songStatistics.js'

const routes = [
{ path: '/', component: signup, name: 'signup' },
{ path: '/login', component: login, name: 'login' },
{ path: '/admin-home', component: adminHome, name: 'admin-home' },
{ path: '/dashboard', component: adminDashboard, name: 'dashboard' },
{ path: '/manage-songs', component: adminManageSongs, name: 'manage-songs' },
{ path: '/admin-add-album', component: adminAddAlbum, name: 'admin-add-album' },
{ path: '/admin-update-album', component: adminUpdateAlbum, name: 'admin-update-album' },
{ path: '/admin-delete-album', component: adminDeleteAlbum, name: 'admin-delete-album' },
{ path: '/admin-add-song', component: adminAddSong, name: 'admin-add-song' },
{ path: '/admin-update-song', component: adminUpdateSong, name: 'admin-update-song' },
{ path: '/admin-delete-song', component: adminDeleteSong, name: 'admin-delete-song' },
{ path: '/song-statistics', component: songStatistics, name: 'song-statistics' },
{ path: '/user-home', component: userHome, name: 'user-home' },
{ path: '/creator-home', component: creatorHome, name: 'creator-home' },
{ path: '/playlist/:id', component: PlaylistPage, name: 'playlist'},
{ path: '/workshop', component: Workshop, name: 'workshop'},
{ path: '/add-album', component: AddAlbum, name: 'add-album'},
{ path: '/add-song', component: AddSong, name: 'add-song'},
{ path: '/update-album', component: UpdateAlbum, name: 'update-album'},
{ path: '/update-song', component: UpdateSong, name: 'update-song'},
{ path: '/delete-album', component: DeleteAlbum, name: 'delete-album'},
{ path: '/delete-song', component: DeleteSong, name: 'delete-song'},
]

const router = new VueRouter({
    routes,
});

// Navigation guard to check authentication
router.beforeEach((to, from, next) => {
    const isAuthenticated = localStorage.getItem('auth-token') !== null;
    const isAdmin = localStorage.getItem('user-role') === 'admin';
    
    // Check if the route requires authentication
    if (to.meta.requiresAuth) {
      // Check if the user is authenticated
    if (isAuthenticated) {
        // Check if the route is restricted to admin only
        if (to.meta.isAdmin && isAdmin) {
          next(); // Allow access to the route
        } else if (!to.meta.isAdmin) {
          next(); // Allow access to the route for non-admin users
        } else {
          // Redirect to unauthorized page
        next('/unauthorized');
        }
    } else {
        // Redirect to login page
        next('/login');
    }
    } else {
      next(); // Allow access to public routes
    }
});  

export default router;