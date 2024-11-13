export default {
    template: `
    <div class='d-flex justify-content-center' style="margin-top: 25vh">
        <div class="mb-3 p-5 bg-light">
            <div class='text-danger'>*{{error}}</div>
            <label for="user-email" class="form-label">Email address</label>
            <input type="email" class="form-control" id="user-email" placeholder="name@example.com" v-model="cred.email">
            <label for="user-password" class="form-label">Password</label>
            <input type="password" class="form-control" id="user-password" v-model="cred.password">
            <button class="btn btn-primary mt-2" @click='login' > Login </button>
            <router-link to="/" class="btn btn-secondary mt-2">Don't have an account yet,Signup</router-link>
            </div> 
    </div>
    `,
    data() {
        return {
            cred: {
                email: null,
                password: null,
            },
            error: null,
        }
    },
    methods: {
        async login() {
            try {
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.cred),
                });
                const data = await res.json();
                if (res.ok) {
                    this.token = data.token;
                    const token = data.token;
                    if (!token) {
                        throw new Error('Token is missing');
                    }
                    localStorage.setItem('auth-token', token);
                    localStorage.setItem('role', data.role);
                    localStorage.setItem('current_user_id', data.user_id);
                    switch (data.role) {
                        case 'Admin':
                            this.$router.push({ path: '/admin-home' });
                            break;
                        case 'User':
                            this.$router.push({ path: '/user-home' });
                            break;
                        case 'Creator':
                            this.$router.push({ path: '/creator-home' });
                            break;
                        default:
                            this.$router.push({ path: '/' });
                            break;
                    }
                } else {
                    this.error = data.message;
                }
            } catch (error) {
                console.error('Error occurred during login:', error);
                this.error = 'An unexpected error occurred. Please try again later.';
            }
        },
    },
}
