<template>
    <div>
        <div :class="box_css_class">
            <div class="options_title_box" :style="{width: config.full_width?'100%':'205px'}">
                <span>{{config.title}}</span>
                <span class="options_desc">{{config.description}}</span>
            </div>
            <ResolveInputComponent
                 v-for="child_config in config.children"
                 :form_values="form_values" 
                 :config="child_config"
                 :key="child_config.id"
            > </ResolveInputComponent>
        </div>
        <br>
    </div>

</template>
<script>

import ResolveInputComponent from "./ResolveInputComponent.vue"

export default {
    name: 'InputWithDesc',
    props: {
        config: Object , 
        form_values: Object,
    },
    components: {'ResolveInputComponent':ResolveInputComponent},
    mounted() {

    },
    data() {
        return {
            box_css_class : this.config.full_width? "options_title_full":"options_title"
        };
    },
    methods: {

    },
}
</script>
<style>
</style>
<style scoped>
</style>