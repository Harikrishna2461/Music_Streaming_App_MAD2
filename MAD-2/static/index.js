import router from './router.js';
import customnavbar from './components/customnavbar.js';

new Vue({
    el: '#musicapp',
    template: `
    <div style="background-color: #eaf5e2; padding: 20px;">
        <customnavbar :key='changeFlag'/>
        <router-view class="m-3"/>
    </div>`,
    router: router,
    components: {
        customnavbar,  
    },
    data: {
        changeFlag: true,
    },
    watch: {
        '$route'(to, from) {
            this.changeFlag = !this.changeFlag;
        },
    },
});


