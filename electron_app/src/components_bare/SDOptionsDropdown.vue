<template>
    <div style="float:right;margin-top: -5px;">
        <b-dropdown id="dropdown-form" variant="link" ref="dropdown" toggle-class="text-decoration-none" no-caret>

            <template #button-content>
                <div class="l_button" style="">Options</div>
            </template>

            <b-dropdown-form style="min-width: 350px;max-height: calc(100vh - 300px); overflow-y: scroll;">
                <br>
                <div style="display: flex;flex-wrap: wrap;justify-content: center;gap: 15px;">
                    <span v-if="!elements_hidden.includes('inp_img_strength')">
                        <div style="display: flex;flex-direction: column;width: 300px;">
                            <div class="options_title_box">
                                <span>Input Strength</span>
                                <span class="options_desc">How  closely to stick to the input image.  (lower
                                    numbers makes the AI do more change)</span>
                            </div>
                            <input type="range" min="10" max="90"  :value="options_model_values.inp_img_strength*100"   step='0.01' class="slider"
                                @input="SetStrength" list='tickmarks'>
                            <div id="tickmarks">
                                <p>10</p>
                                <p>30</p>
                                <p>40</p>
                                <p>70</p>
                                <p>90</p>
                            </div>
                        </div>
                    </span>


                    <span v-if="!elements_hidden.includes('num_imgs')">
                        <div class="options_title">
                            <div class="options_title_box" style="width: 205px;">
                                <span>Number of images</span>
                                <span class="options_desc">How many images are generated in total.</span>
                            </div>
                            <div class="options_input" style="width: 75px;">
                                <svg width="18" height="19" viewBox="0 0 18 19" fill="none"
                                    xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 5.5H12.01" stroke="#A2A3AA" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round" />
                                    <path
                                        d="M14 1.5H4C2.34315 1.5 1 2.84315 1 4.5V14.5C1 16.1569 2.34315 17.5 4 17.5H14C15.6569 17.5 17 16.1569 17 14.5V4.5C17 2.84315 15.6569 1.5 14 1.5Z"
                                        stroke="#A2A3AA" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round" />
                                    <path
                                        d="M1 12.5L5 8.50001C5.45606 8.06117 5.97339 7.83014 6.5 7.83014C7.02661 7.83014 7.54394 8.06117 8 8.50001L13 13.5"
                                        stroke="#A2A3AA" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round" />
                                    <path
                                        d="M11 11.5L12 10.5C12.4561 10.0612 12.9734 9.83014 13.5 9.83014C14.0266 9.83014 14.5439 10.0612 15 10.5L17 12.5"
                                        stroke="#A2A3AA" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round" />
                                </svg>
                                <b-form-select v-model="options_model_values.num_imgs" id="num_imgs"
                                    :options="[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 30, 50, 100]"
                                    required>
                                </b-form-select>

                            </div>
                        </div>
                    </span>

                    <span v-if="!elements_hidden.includes('batch_size')">
                        <div class="options_title">
                            <div class="options_title_box" style="width: 205px;">
                                <span>Batch size</span>
                                <span class="options_desc">How many images are created at the sametime. (Leave at 1 if
                                    you have 16GB or less RAM)</span>
                            </div>
                            <div class="options_input" style="width: 75px;">
                                <svg width="18" height="19" viewBox="0 0 18 19" fill="none"
                                    xmlns="http://www.w3.org/2000/svg">
                                    <path
                                        d="M15 5.5H7C5.89543 5.5 5 6.39543 5 7.5V15.5C5 16.6046 5.89543 17.5 7 17.5H15C16.1046 17.5 17 16.6046 17 15.5V7.5C17 6.39543 16.1046 5.5 15 5.5Z"
                                        stroke="#A2A3AA" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round" />
                                    <path
                                        d="M13 5.5V3.5C13 2.96957 12.7893 2.46086 12.4142 2.08579C12.0391 1.71071 11.5304 1.5 11 1.5H3C2.46957 1.5 1.96086 1.71071 1.58579 2.08579C1.21071 2.46086 1 2.96957 1 3.5V11.5C1 12.0304 1.21071 12.5391 1.58579 12.9142C1.96086 13.2893 2.46957 13.5 3 13.5H5"
                                        stroke="#A2A3AA" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round" />
                                </svg>
                                <b-form-select v-model="options_model_values.batch_size" :options="[1, 2, 3, 4, 5, 6]"
                                    required></b-form-select>
                            </div>
                        </div>

                    </span>

                    <span v-if="!elements_hidden.includes('img_h')">
                        <div class="options_title">
                            <div class="options_title_box" style="width: 115px;">
                                <span>Resolution</span>
                            </div>
                            <div style="display: inline-flex;gap: 22px;">
                                <div class="options_input" style="justify-content: center;width: 75px;">
                                    <svg width="18" height="20" viewBox="0 0 13 13" fill="none"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <path
                                            d="M2.74162 6.09644V3.05541C2.74162 2.78657 2.84842 2.52873 3.03852 2.33863C3.22862 2.14853 3.48646 2.04173 3.7553 2.04173H9.83736C10.1062 2.04173 10.364 2.14853 10.5541 2.33863C10.7442 2.52873 10.851 2.78657 10.851 3.05541V6.09644"
                                            stroke="#A2A3AA" stroke-width="1.01368" stroke-linecap="round"
                                            stroke-linejoin="round" />
                                        <path d="M5.78269 9.1374H2.23482" stroke="#A2A3AA" stroke-width="1.01368"
                                            stroke-linecap="round" stroke-linejoin="round" />
                                        <path d="M11.3579 9.1374H7.81006" stroke="#A2A3AA" stroke-width="1.01368"
                                            stroke-linecap="round" stroke-linejoin="round" />
                                        <path d="M3.75533 7.61689L2.23482 9.1374L3.75533 10.6579" stroke="#A2A3AA"
                                            stroke-width="1.01368" stroke-linecap="round" stroke-linejoin="round" />
                                        <path d="M9.83737 7.61689L11.3579 9.1374L9.83737 10.6579" stroke="#A2A3AA"
                                            stroke-width="1.01368" stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>


                                    <b-form-select v-model="options_model_values.img_w"
                                        :options="[64 * 4, 64 * 5, 64 * 6, 64 * 7, 64 * 8, 64 * 9, 64 * 10, 64 * 11, 64 * 12]"
                                        required></b-form-select>
                                </div>
                                <div class="options_input" style="justify-content: center;width: 75px;">
                                    <svg width="18" height="20" viewBox="0 0 14 13" fill="none"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <path
                                            d="M7.05545 10.1511H4.01442C3.74558 10.1511 3.48775 10.0443 3.29765 9.85425C3.10755 9.66414 3.00075 9.40631 3.00075 9.13747V3.05541C3.00075 2.78657 3.10755 2.52873 3.29765 2.33863C3.48775 2.14853 3.74558 2.04173 4.01442 2.04173H7.05545"
                                            stroke="#A2A3AA" stroke-width="1.01368" stroke-linecap="round"
                                            stroke-linejoin="round" />
                                        <path d="M10.0965 7.11V10.6579" stroke="#A2A3AA" stroke-width="1.01368"
                                            stroke-linecap="round" stroke-linejoin="round" />
                                        <path d="M10.0965 1.53483V5.0827" stroke="#A2A3AA" stroke-width="1.01368"
                                            stroke-linecap="round" stroke-linejoin="round" />
                                        <path d="M8.57599 9.1374L10.0965 10.6579L11.617 9.1374" stroke="#A2A3AA"
                                            stroke-width="1.01368" stroke-linecap="round" stroke-linejoin="round" />
                                        <path d="M8.57599 3.05534L10.0965 1.53483L11.617 3.05534" stroke="#A2A3AA"
                                            stroke-width="1.01368" stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>
                                    <b-form-select v-model="options_model_values.img_h"
                                        :options="[64 * 4, 64 * 5, 64 * 6, 64 * 7, 64 * 8, 64 * 9, 64 * 10, 64 * 11, 64 * 12]"
                                        required></b-form-select>
                                </div>
                            </div>

                        </div>
                    </span>


                    <b-form-group inline label="" style="margin-bottom: 6px;">
                        <span v-if="!elements_hidden.includes('batch_size')">
                            <div class="options_title">
                                <div class="options_title_box" style="width: 205px;">
                                    <span>Steps</span>
                                    <span class="options_desc">Iterations of the image (more steps means more detail &
                                        more processing time - best to start around 10)</span>
                                </div>
                                <div class="options_input" style="width: 75px;">
                                    <svg width="18" height="15" viewBox="0 0 18 15" fill="none"
                                        xmlns="http://www.w3.org/2000/svg">
                                        <path d="M1 13.5H5V9.5H9V5.5H13V1.5H17" stroke="#A2A3AA" stroke-width="2"
                                            stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>

                                    <b-form-select v-model="options_model_values.dif_steps"
                                        :options="[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]"
                                        required></b-form-select>
                                </div>
                            </div>

                        </span>

                    </b-form-group>

                    <b-form-group inline label="" style="margin-bottom: 6px;">
                        <div style="display: flex;flex-direction: column;width: 300px;">
                            <div class="options_title_box">
                                <span>Guidance scale</span>
                                <span class="options_desc">How closely to follow your prompt (lower
                                    numbers give the AI more creativity)</span>
                            </div>
                            <input type="range" min="0" max="20" v-model="options_model_values.guidence_scale" step='0.01' class="slider"
                                @input="SetGuidenceScale" list='tickmarks'>
                            <div id="tickmarks">
                                <p>0</p>
                                <p>5</p>
                                <p>10</p>
                                <p>15</p>
                                <p>20</p>
                            </div>
                        </div>
                    </b-form-group>

                    <div class="options_title">
                        <div class="options_title_box" style="width: 155px;">
                            <span>Seed</span>
                            <span class="options_desc">Starting point for iterations (any random
                                number will do; DB will pick one if left blank)</span>
                        </div>
                        <div class="options_input" style="width: 125px;">
                            <svg style="height: auto;" width="20" height="20" viewBox="0 0 20 19" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M10 7.5C10 5.9087 9.36786 4.38258 8.24264 3.25736C7.11742 2.13214 5.5913 1.5 4 1.5H1V3.5C1 5.0913 1.63214 6.61742 2.75736 7.74264C3.88258 8.86786 5.4087 9.5 7 9.5H10"
                                    stroke="#A2A3AA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                                <path
                                    d="M10 11.5C10 9.9087 10.6321 8.38258 11.7574 7.25736C12.8826 6.13214 14.4087 5.5 16 5.5H19V6.5C19 8.0913 18.3679 9.61742 17.2426 10.7426C16.1174 11.8679 14.5913 12.5 13 12.5H10"
                                    stroke="#A2A3AA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                                <path d="M10 17.5V7.5" stroke="#A2A3AA" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" />
                            </svg>

                            <b-form-input onkeypress="return event.keyCode != 13;" class="custom-input"
                                v-model="options_model_values.seed" type="number" width="70" value="100" maxlength="5"
                                placeholder="-1"></b-form-input>
                        </div>
                    </div>


                    <div class="options_title">
                        <div class="options_title_box" style="width: 165px;">
                            <span>Custom Model</span>
                            <span class="options_desc">You can use a custom stable diffusion models. Open settings to add a ckpt model.</span>
                        </div>
                        <div class="options_input" style="width: 115px;">
                            <svg width="18" height="19" viewBox="0 0 18 19" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <path d="M12 5.5H12.01" stroke="#A2A3AA" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" />
                                <path
                                    d="M14 1.5H4C2.34315 1.5 1 2.84315 1 4.5V14.5C1 16.1569 2.34315 17.5 4 17.5H14C15.6569 17.5 17 16.1569 17 14.5V4.5C17 2.84315 15.6569 1.5 14 1.5Z"
                                    stroke="#A2A3AA" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" />
                                <path
                                    d="M1 12.5L5 8.50001C5.45606 8.06117 5.97339 7.83014 6.5 7.83014C7.02661 7.83014 7.54394 8.06117 8 8.50001L13 13.5"
                                    stroke="#A2A3AA" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" />
                                <path
                                    d="M11 11.5L12 10.5C12.4561 10.0612 12.9734 9.83014 13.5 9.83014C14.0266 9.83014 14.5439 10.0612 15 10.5L17 12.5"
                                    stroke="#A2A3AA" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" />
                            </svg>

                            <b-form-select v-model="options_model_values.selected_model"
                                :options="['Default'].concat(Object.keys(options_model_values.app_state.app_data.custom_models))"
                                required></b-form-select>
                        </div>
                    </div>

                    <div class="options_title">
                        <div class="options_title_box" style="width: 205px;">
                            <span>Negative Prompt</span>
                            <span class="options_desc">Negative prompt allows adding things to avoid in the image,</span>
                        </div>
                        <div class="options_input" style="width: 75px;">
                            <div v-if="(!options_model_values.is_negative_prompt_avail) && !elements_hidden.includes('nagative_prompt')"
                                class="l_button"
                                @click="options_model_values.is_negative_prompt_avail = !options_model_values.is_negative_prompt_avail">
                                Enable </div>
                            <div v-else class="l_button"
                                @click="options_model_values.is_negative_prompt_avail = !options_model_values.is_negative_prompt_avail">
                                Disable</div>
                        </div>
                    </div>



                    
                </div>
                <br>
            </b-dropdown-form>
        </b-dropdown>
    </div>
</template>
<script>
export default {
    name: 'SDOptionsDropdown',
    props: {
        options_model_values: Object,
        elements_hidden: Array,
    },
    components: {},
    mounted() {
        this.$nextTick(function () {
            var sliders = document.getElementsByClassName('slider');
            for (var i = 0; i < sliders.length; i++) {
                var slider = sliders[i];
                var value = slider.value / (slider.max) * (100 - slider.min);
                slider.style.background = 'linear-gradient(to right, var(--slider-progress) 0%, var(--slider-progress) ' + value + '%, var(--slider-progress_end) ' + value + '%, var(--slider-progress_end) 100%)';
            }
        })
    },
    data() {
        return {};
    },
    methods: {
        SetStrength(e) {
            var value = (e.target.value - e.target.min) / (e.target.max - e.target.min) * 100
            e.target.style.background = 'linear-gradient(to right, var(--slider-progress) 0%, var(--slider-progress) ' + value + '%, var(--slider-progress_end) ' + value + '%, var(--slider-progress_end) 100%)'
            this.options_model_values.inp_img_strength = Number(e.target.value / 100);
        },
        SetGuidenceScale(e) {
            var value = (e.target.value - e.target.min) / (e.target.max - e.target.min) * 100
            e.target.style.background = 'linear-gradient(to right, var(--slider-progress) 0%, var(--slider-progress) ' + value + '%, var(--slider-progress_end) ' + value + '%, var(--slider-progress_end) 100%)'
            // this.options_model_values.guidence_scale = Number(e.target.value)
        }
    },
}
</script>
<style scoped>
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
    justify-content: space-around;
    width: 330px;
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
    background: linear-gradient(to right, var(--slider-progress) 0%, var(--slider-progress) 37.5%, var(--slider-progress_end) 37.5%, var(--slider-progress_end) 100%);
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
}
</style>