<template>

    <span>
        <component   :is="config.component" :config="config"  :form_values="form_values" ></component>
    </span>

</template>
<script>

import Dropdown from "./Dropdown.vue"
import Slider from "./Slider.vue"
import Textbox from "./Textbox.vue"
import Textarea from "./Textarea.vue"
import ImageInput from "./ImageInput.vue"
import Checkbox from "./Checkbox.vue"
import FilePathTextBox from "./FilePathTextBox.vue"
// import InputWithDesc from "./InputWithDesc.vue"
import OutputText from "./OutputText.vue"
import OutputImage from "./OutputImage.vue"
import BetterSelector from "./BetterSelector.vue"


export default {
    name: 'ResolveInputComponent',
    props: {
        config: Object , 
        form_values: Object,
    },
    components: { 'Dropdown':Dropdown , 'Slider':Slider, 'Textbox':Textbox , 'Textarea':Textarea, 'ImageInput':ImageInput , 'Checkbox':Checkbox , 'FilePathTextBox':FilePathTextBox , OutputText:OutputText, OutputImage:OutputImage , BetterSelector:BetterSelector },
    beforeCreate: function () {
         this.$options.components.InputWithDesc = require('./InputWithDesc.vue').default // use this as circular
         this.$options.components.Accordian = require('./Accordian.vue').default // use this as circular
    },

    mounted() {

    },
    data() {
        return {};
    },
    methods: {

    },
}
</script>
<style>

.b-dropdown ::-webkit-scrollbar {
    appearance: none;
    width: 7px;
}
.b-dropdown ::-webkit-scrollbar-thumb {
    border-radius: 4px;
    background-color: rgba(0, 0, 0, .5);
    box-shadow: 0 0 1px rgba(255, 255, 255, .5);
}
.options_title {
    display: flex;
    flex-direction: row;
    align-items: center;
/*    justify-content: space-around;*/
    width: 100%;
}

.options_title_full{
     display: flex;
     flex-direction: column;
     width: 100%;
}

.options_title_box span {
    font-weight: 600;
    font-size: 14px;
    line-height: 19px;
}

.options_title_box .options_desc {
    font-weight: 400;
    font-size: 12px;
}

.custom-select {
    appearance: none;
    outline: none;
    border: none;
    background: none;
    min-width: 20px;
    font-weight: 600;
    font-size: 14px;
    line-height: 19px;
    text-align: center;
    cursor: pointer;
    padding-left: 32px;

}

.options_input svg {
    margin-right: -32px;
}

.custom-input {
    border: none;
    background: none;
    min-width: 20px;
    font-weight: 600;
    font-size: 14px;
    line-height: 19px;
    text-align: center;
}

.custom-input::-webkit-outer-spin-button,
.custom-input::-webkit-inner-spin-button {
    appearance: none;
    margin: 0;
}

.slider {
    background: linear-gradient(to right, var(--slider-progress) 0%, var(--slider-progress) 0%, var(--slider-progress_end) 0%, var(--slider-progress_end) 100%);
    border-radius: 8px;
    height: 15px;
    margin-top: 4px;
    outline: none;
    transition: background 450ms ease-in;
    appearance: none;
    cursor: pointer;
}

.slider::-webkit-slider-thumb {
    appearance: none;
    width: 25px;
    height: 25px;
    border-radius: 50%;
    border: 3px solid var(--slider-border);
    background: var(--slider-circle);
}

#tickmarks {
    display: flex;
    justify-content: space-between;
    padding: 0 10px;
    font-size: 12px;
    margin-top: -10px ;
}

</style>
<style scoped>
</style>