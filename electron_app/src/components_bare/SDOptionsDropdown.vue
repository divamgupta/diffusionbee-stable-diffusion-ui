<template>
    <div style="float:right; margin-top: -5px;" >
        <b-dropdown id="dropdown-form" variant="link" ref="dropdown" toggle-class="text-decoration-none" no-caret >
        
            <template #button-content>
                <div class="l_button"  style="" >Options</div>
            </template>

            <b-dropdown-form style="min-width: 240px ; ">

                <span v-if="!elements_hidden.includes('inp_img_strength')"> 
                    <b-form-group inline  label="" style="margin-bottom: 6px;" >
                        <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Input Strength: </label>
                        <b-form-select
                        v-model="options_model_values.inp_img_strength"
                        :options="[ 0.1 , 0.2 , 0.3 , 0.4 , 0.5 , 0.6 , 0.7 , 0.8 , 0.9 ]"
                        required
                        ></b-form-select>
                    </b-form-group>
                </span>
                                
                
                <span v-if="!elements_hidden.includes('num_imgs')">
                    <b-form-group inline  label="" style="margin-bottom: 6px;" >
                        <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Num Images: </label>
                        <b-form-select
                        v-model="options_model_values.num_imgs"
                        :options="[1,2,3,4,5,6,7,8,9,10,11,12,13,14, 15 , 20 , 30 , 50 , 100]"
                        required
                        ></b-form-select>
                    </b-form-group>
                </span>

                <span v-if="!elements_hidden.includes('img_h')">
                    <b-form-group inline label=""  style="margin-bottom: 6px;">
                        <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Image Height: </label>
                        <b-form-select
                        v-model="options_model_values.img_h"
                        :options="[ 64*4 , 64*5 , 64*6, 64*7 , 64*8 , 64*9 , 64*10 , 64*11 , 64*12 ]"
                        required
                        ></b-form-select>
                    </b-form-group>
                </span>
                
                <span v-if="!elements_hidden.includes('img_w')">
                    <b-form-group inline label=""  style="margin-bottom: 6px;">
                        <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Image Width: </label>
                        <b-form-select
                        v-model="options_model_values.img_w"
                        :options="[64*4 , 64*5 , 64*6, 64*7 , 64*8 , 64*9 , 64*10 , 64*11 , 64*12 ]"
                        required
                        ></b-form-select>
                    </b-form-group>
                </span>

                <b-form-group inline label=""  style="margin-bottom: 6px;">
                <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Steps: </label>
                <b-form-select
                    v-model="options_model_values.dif_steps"
                    :options="[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49 , 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]"
                    required
                ></b-form-select>
                </b-form-group>

                <span v-if="!elements_hidden.includes('batch_size')">
                    <b-form-group inline label=""  style="margin-bottom: 6px;">
                    <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Batch size: </label>
                    <b-form-select
                        v-model="options_model_values.batch_size"
                        :options="[1, 2, 3, 4, 5, 6]"
                        required
                    ></b-form-select>
                    </b-form-group>
                </span>

                <b-form-group inline  label="" style="margin-bottom: 6px;" >
                <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Guidance Scale: </label>
                <b-form-select
                    v-model="options_model_values.guidence_scale"
                    :options="[1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 7.5 , 8.0 , 9.0 , 10.0 , 11.0 , 12.0 , 13.0 , 15.0 , 20.0 ]"
                    required
                ></b-form-select>
                </b-form-group>

                <b-form-group inline  label="" style="margin-bottom: 6px;" >
                <label class="mr-sm-2" style="margin-right: 8px ;" for="inline-form-custom-select-pref">Seed: </label>
    
                <b-form-input onkeypress="return event.keyCode != 13;"  size="sm" class="mr-sm-2"  v-model="options_model_values.seed" style="max-width: 40px; float: right; margin-right: 30px;" ></b-form-input>

                </b-form-group>

                <div v-if="(!options_model_values.is_negative_prompt_avail) && !elements_hidden.includes('nagative_prompt')" class="l_button" @click="options_model_values.is_negative_prompt_avail=!options_model_values.is_negative_prompt_avail">Enable Negative Prompt</div>
                <div v-else class="l_button" @click="options_model_values.is_negative_prompt_avail=!options_model_values.is_negative_prompt_avail">Disable Negative Prompt</div>

            </b-dropdown-form>
        </b-dropdown>
    </div>
</template>
<script>
export default {
    name: 'SDOptionsDropdown',
    props: {
        options_model_values : Object,
        elements_hidden : Array , 
    },
    components: {},
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
</style>
<style scoped>
</style>