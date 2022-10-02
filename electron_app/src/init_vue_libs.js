import Vue from 'vue'



// add the fond awesome stuff
import { library } from '@fortawesome/fontawesome-svg-core'
import { faChevronRight, faStopCircle, faPlayCircle , faPlus , faChevronLeft , 
    faFileImage  , faFileAudio , faFile , faBars , faAngleDown , faTrash, faChevronDown ,
    faGlobe, faFolder, faCamera, faKeyboard,
    faMusic , faMicrophone , faTimes , faCheck } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(faBars)

library.add(faChevronRight)
library.add(faChevronLeft)
library.add(faGlobe)
library.add(faFolder)
library.add(faStopCircle)
library.add(faPlayCircle)
library.add(faFileImage)
library.add(faFileAudio)
library.add(faKeyboard)
library.add(faMicrophone)
library.add(faPlus)
library.add(faFile)

library.add(faAngleDown)
library.add(faTrash)
library.add(faChevronDown)
library.add(faMusic)
library.add(faCamera)
library.add(faTimes)
library.add(faCheck)



Vue.component('font-awesome-icon', FontAwesomeIcon)
Vue.config.productionTip = false


// vue bootstrap 
import { BootstrapVue } from 'bootstrap-vue'

// Import Bootstrap an BootstrapVue CSS files (order is important)
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.use(BootstrapVue)



// vue outside 
import vClickOutside from 'v-click-outside'
Vue.use(vClickOutside)


// // vue toast notification
// import VueToast from 'vue-toast-notification';
// import 'vue-toast-notification/dist/theme-sugar.css';

// Vue.use(VueToast);


export {}