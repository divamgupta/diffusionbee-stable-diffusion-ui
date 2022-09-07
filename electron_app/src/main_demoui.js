import Vue from 'vue'

Vue.config.productionTip = false

// setup the vue libs 
import {} from "./init_vue_libs.js"

import AppDemoUI from './AppDemoUI.vue'


new Vue({
  render: h => h(AppDemoUI),
}).$mount('#app')
