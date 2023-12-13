import Vue from 'vue'




// add the fond awesome stuff
import { library } from '@fortawesome/fontawesome-svg-core'
import { faChevronRight, faStopCircle, faPlayCircle , faPlus , faChevronLeft , 
	faFileImage  , faFileAudio , faFile , faBars , faAngleDown , faTrash, faChevronDown ,
	faGlobe, faFolder, faCamera, faKeyboard,
	faMusic , faMicrophone , faTimes , faCheck , faHandPaper , faExpandArrowsAlt, faEraser , faUndo , faRedo, faImage, faMicrochip , faCube , 
	faMagic, faSave, faHistory, faCubes, faImages, faHome , faPaintBrush, faCircle , faMask, faTools, faThList, faEllipsisV, faInbox} from '@fortawesome/free-solid-svg-icons'
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
library.add(faExpandArrowsAlt)
library.add(faEraser)
library.add(faHandPaper)
library.add(faImage)
library.add(faMicrochip)
library.add(faCube)
library.add(faMagic)
library.add(faSave)
library.add(faUndo)
library.add(faRedo)

library.add(faAngleDown)
library.add(faTrash)
library.add(faChevronDown)
library.add(faMusic)
library.add(faCamera)
library.add(faTimes)
library.add(faCheck)
library.add(faHistory)
library.add(faCubes)
library.add(faImages)
library.add(faHome)
library.add(faPaintBrush)
library.add(faCircle)
library.add(faMask)
library.add(faTools)
library.add(faThList)
library.add(faEllipsisV)
library.add(faInbox)

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


import VueToast from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';

Vue.use(VueToast);



export {}