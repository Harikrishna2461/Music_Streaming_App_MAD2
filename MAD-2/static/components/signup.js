export default {
    template: `
    <div id="musicapp">
        <div class="mb-3">
            <div class='d-flex justify-content-center' style="margin-top: 25vh">
                <form @submit.prevent="signup">
                    <div class="mb-3">
                        <label for="username">Username:</label><br>
                        <input type="text" v-model="userData.username" id="username" name="username" required><br>
                    </div>
                    <div class="mb-3">
                        <label for="email">Email:</label><br>
                        <input type="email" v-model="userData.email" id="email" name="email" required><br>
                    </div>
                    <div class="mb-3">
                        <label for="password">Password:</label><br>
                        <input type="password" v-model="userData.password" id="password" name="password" required><br>
                    </div>
                    <div class="mb-3">
                        <label for="role">Role:</label><br>
                        <select v-model="userData.role" id="role" name="role" required>
                            <option value="Creator">Creator</option>
                            <option value="User">User</option>
                        </select><br>
                    </div>
                    <button type="submit">Sign Up</button>
                    <p v-if="error" style="color: red;">{{ error }}</p>
                </form>
            </div>
            <div class="mt-3 d-flex justify-content-center">
                <!-- Corrected router-link to navigate to the login page -->
                <router-link to="/login" class="btn btn-primary">Already have an account? Login</router-link>
            </div>
        </div>
    </div>
    `,
    data() {
        return {
            userData: {
                username: null,
                email: null,
                password: null,
                role: 'User',
            },
            error: null,
        }
    },
    methods: {
        async signup() {
            try {
                const response = await fetch('/api/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.userData),
                });
                const data = await response.json();
                
                // Handle successful signup (e.g., redirect to login page)
                if (response.ok) {
                    // Redirect to the login page after successful signup
                    this.$router.push('/login');
                } else {
                    this.error = data.error;
                }
            } catch (error) {
                // Handle network errors
                this.error = 'An error occurred while signing up';
            }
        }      
    }
}
