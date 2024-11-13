export default {
    template: `
    <div>
        <h1>Manage Songs</h1>
        <div v-for="(button, index) in buttons" :key="button.label" class="button-container">
            <button :style="{ ...buttonStyle, backgroundColor: buttonColors[index % buttonColors.length] }" class="action-button" @click="navigate(button.route)">{{ button.label }}</button>
        </div>
    </div>
    `,
    data() {
        return {
            buttons: [],
            buttonColors: ['#4CAF50', '#008CBA', '#f44336', '#ff9800', '#9c27b0'] // Define your colors here
        };
    },
    computed: {
        buttonStyle() {
            return {
                border: 'none',
                color: 'white',
                padding: '15px 32px',
                textAlign: 'center',
                textDecoration: 'none',
                display: 'inline-block',
                fontSize: '16px',
                margin: '4px 2px',
                transitionDuration: '0.4s',
                cursor: 'pointer'
            };
        }
    },
    created() {
        this.fetchButtons();
    },
    methods: {
        async fetchButtons() {
            try {
                const response = await fetch('/api/manage-songs');
                const data = await response.json();
                if (response.ok) {
                    this.buttons = data.buttons;
                } else {
                    console.error('Failed to fetch buttons:', data.message);
                }
            } catch (error) {
                console.error('Error occurred while fetching buttons:', error);
            }
        },
        navigate(route) {
            this.$router.push(route);
        }
    }
};
