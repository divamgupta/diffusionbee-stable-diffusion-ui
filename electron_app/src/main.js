



import Vue from 'vue'




Vue.config.productionTip = false
Vue.config.performance = true

// setup the vue libs 
import {} from "./init_vue_libs.js"


// include the py vue bridge 
import {} from "./py_vue_bridge.js"

import App from './App.vue'
new Vue({
    render: h => h(App),
}).$mount('#app')