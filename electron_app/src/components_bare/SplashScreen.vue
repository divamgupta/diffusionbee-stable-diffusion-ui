<template>
    <div class="splash_screen">
        <Transition name="fade">
            <img v-if=show width="60%" src="@/assets/logo_splash.svg">
        </Transition>
    </div>
</template>
<script>
export default {
    name: 'SplashScreen',
    props: {},
    components: {},
    mounted() {
        this.show = true;
    },
    data() {
        return {
            show:false
        };
    },
    methods: {

    },
}
</script>
<style>

.fade-enter-active,
.fade-leave-active {
  transition: opacity 2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

</style>
<style scoped>
.splash_screen {
    position: fixed;
    background-color: white;
    top: 0;
    left: 0;
    height: 100%;
    width: 100%;
    background-color: #F2F2F2;

    -webkit-user-select: none;
    -webkit-app-region: drag;
}

img {
    position: absolute;
    margin: auto auto auto auto;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
}



</style>