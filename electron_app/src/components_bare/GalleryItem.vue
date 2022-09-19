<template>
  <div
    v-click-outside="unclick_card_body"
    class="responsive_gallery_container"
    v-bind:class="{
      px500_less_size_gallery: is_px500_less_size_gallery,
      is_full_size: is_full_size
    }"
  >
    <div
      v-on:click="
        click_card_body()
        $emit('on_click_cb', item_id)
      "
      class="gallery_card"
      v-bind:class="{ selected: selected }"
    >
      <video
        class="gallery_img"
        v-if="type == 'full_img' && video_url && is_full_size"
        width="100%"
        :src="video_url"
        controls
        disablePictureInPicture
      ></video>
      <img class="gallery_img" v-else-if="type == 'full_img'" :src="url" />

      <div v-if="type == 'img_text'" style="height: 100%">
        <img class="gallery_img" style="height: 70%; max-height: 70%; width: 100%" :src="url" />
        <div class="gall_title">
          <p>
            <b style="white-space: nowrap">{{ title }}</b>
            <br />
            {{ description }}
          </p>
        </div>
      </div>

      <div v-if="type == 'text'">
        <div class="paragraph_container" style="padding: 16px; overflow: hidden">
          <div class="paragraph_container_inner">
            <p
              style="
                font-size: 16px;
                line-height: 22px;
                font-weight: normal;
                color: rgba(0, 0, 0, 0.6);
              "
            >
              {{ description }}
            </p>
          </div>
        </div>
      </div>

      <div v-if="top_right_icon || top_right_button_text" class="gall_top_right_btn_container">
        <div
          v-on:click.stop
          @click="$emit('on_click_top_right_btn', item_id)"
          class="l_button button_grey"
          style="margin-right: 0"
        >
          <font-awesome-icon v-if="top_right_icon" :icon="top_right_icon" />
          {{ top_right_button_text }}
        </div>
      </div>

      <div v-if="audio_url" class="audio_button_container">
        <IconAudioPlayer :audio_url="audio_url"></IconAudioPlayer>
      </div>

      <div v-if="tag" class="gall_tag_container">
        <div class="gall_tag l_button" :style="{ 'background-color': tag_color }">
          <div v-if="tag != '__loading__'">{{ tag }}</div>
          <MoonLoader v-else color="#ffffff" size="17px"></MoonLoader>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import MoonLoader from 'vue-spinner/src/MoonLoader.vue'
import IconAudioPlayer from './IconAudioPlayer.vue'

export default {
  name: 'GalleryItem',
  props: {
    type: { type: String, default: 'full_img' }, // full_img , img_text , text
    tag: String,
    tag_color: String,
    item_id: String,
    url: String,
    audio_url: String,
    video_url: String,
    is_px500_less_size_gallery: Boolean,
    is_full_size: Boolean,
    title: String,
    description: String,
    dont_unselect_on_outside_click: Boolean,
    top_right_icon: String, // if you wannna show a FA icon on top right of the item , eg delete
    top_right_button_text: String // if you wannna show text button on top right
  },

  components: { MoonLoader, IconAudioPlayer },

  data() {
    return {
      selected: false
    }
  },

  methods: {
    // when you click outside the item
    unclick_card_body: function () {
      if (this.dont_unselect_on_outside_click) return
      else this.selected = false
    },

    double_clicked() {
      this.$emit('on_double_click_cb', this.item_id)
    },

    click_card_body: function () {
      if (this.just_selected) {
        this.double_clicked()
        return
      }

      this.just_selected = true
      const thatt = this
      setTimeout(function () {
        thatt.just_selected = false
      }, 200)

      this.selected = true
    }
  }
}
</script>
<style>
@media (min-width: 576px) {
  .responsive_gallery_container {
    -ms-flex: 0 0 50%;
    -webkit-box-flex: 0;
    flex: 0 0 50%;
    max-width: 50%;
  }
}

@media (min-width: 668px) {
  .responsive_gallery_container {
    -ms-flex: 0 0 33.333333%;
    -webkit-box-flex: 0;
    flex: 0 0 33.333333%;
    max-width: 33.333333%;
  }
}

@media (min-width: 892px) {
  .responsive_gallery_container {
    -ms-flex: 0 0 25%;
    -webkit-box-flex: 0;
    flex: 0 0 25%;
    max-width: 25%;
  }
}

@media (min-width: 1100px) {
  .responsive_gallery_container {
    -ms-flex: 0 0 20%;
    -webkit-box-flex: 0;
    flex: 0 0 20%;
    max-width: 20%;
  }
}

@media (min-width: 1600px) {
  .responsive_gallery_container {
    -ms-flex: 0 0 16.6667%;
    -webkit-box-flex: 0;
    flex: 0 0 16.6667%;
    max-width: 16.6667%;
  }
}

@media (min-width: 1900px) {
  .responsive_gallery_container {
    -ms-flex: 0 0 14.2857142857%;
    -webkit-box-flex: 0;
    flex: 0 0 14.2857142857%;
    max-width: 14.2857142857%;
  }
}

@media (min-width: 2100px) {
  .responsive_gallery_container {
    -ms-flex: 0 0 12.5%;
    -webkit-box-flex: 0;
    flex: 0 0 12.5%;
    max-width: 12.5%;
  }
}

@media (min-width: 2400px) {
  .responsive_gallery_container {
    -ms-flex: 0 0 11.1111111111%;
    -webkit-box-flex: 0;
    flex: 0 0 11.1111111111%;
    max-width: 11.1111111111%;
  }
}
</style>

<style scoped>
.gall_tag_container {
  position: absolute;
  bottom: 20px;
  left: 20px;
}

.audio_button_container {
  position: absolute;
  top: 10px;
  left: 10px;
}

.gall_top_right_btn_container {
  position: absolute;
  top: 10px;
  right: 10px;
  display: none;
}

.gallery_card:hover > .gall_top_right_btn_container {
  display: block;
}

.gall_tag {
  background: rgba(62, 123, 250, 0.8);
  color: #ffffff;
}

.gallery_card {
  position: relative;
  padding: 0px;
  margin: 7px;
  height: 184px;

  position: relative;
  display: flex;
  flex-direction: column;
  -webkit-box-pack: justify;
  justify-content: space-between;

  background-repeat: no-repeat;
  background-position: center center;
  background-size: cover;

  border-radius: 12px 12px 12px 12px;
  background-color: white;
  border-style: solid;
  border-width: 1px;
  border-color: rgba(0, 0, 0, 0.1);

  overflow: hidden;
  box-shadow: 0px 0px 1.76351px rgba(40, 41, 61, 0.04),
    0px 3.52703px 7.05405px rgba(96, 97, 112, 0.16);
}

.gallery_img {
  object-fit: cover;
  height: 100%;
  max-width: 100%;
  max-height: 100%;
  margin: 0;
  padding: 0px;
}

.selected {
  box-shadow: 0px 0px 0 3px #4ca4ff;
}

.gall_title {
  padding: 10px;
  margin-bottom: 10px;
}

.paragraph_container_inner {
  height: 94px;
}

/*if the gallery is at a location where the width is shortened by 500 px , ie when there a large img on right side*/

@media (min-width: 6px) {
  .responsive_gallery_container.px500_less_size_gallery {
    -ms-flex: 0 0 100%;
    -webkit-box-flex: 0;
    flex: 0 0 100%;
    max-width: 100%;
  }
}

@media (min-width: 900px) {
  .responsive_gallery_container.px500_less_size_gallery {
    -ms-flex: 0 0 50%;
    -webkit-box-flex: 0;
    flex: 0 0 50%;
    max-width: 50%;
  }
}

@media (min-width: 1168px) {
  .responsive_gallery_container.px500_less_size_gallery {
    -ms-flex: 0 0 33.333333%;
    -webkit-box-flex: 0;
    flex: 0 0 33.333333%;
    max-width: 33.333333%;
  }
}

@media (min-width: 1392px) {
  .responsive_gallery_container.px500_less_size_gallery {
    -ms-flex: 0 0 25%;
    -webkit-box-flex: 0;
    flex: 0 0 25%;
    max-width: 25%;
  }
}

@media (min-width: 1600px) {
  .responsive_gallery_container.px500_less_size_gallery {
    -ms-flex: 0 0 20%;
    -webkit-box-flex: 0;
    flex: 0 0 20%;
    max-width: 20%;
  }
}

@media (min-width: 2100px) {
  .responsive_gallery_container.px500_less_size_gallery {
    -ms-flex: 0 0 16.6667%;
    -webkit-box-flex: 0;
    flex: 0 0 16.6667%;
    max-width: 16.6667%;
  }
}

@media (min-width: 2400px) {
  .responsive_gallery_container.px500_less_size_gallery {
    -ms-flex: 0 0 14.2857142857%;
    -webkit-box-flex: 0;
    flex: 0 0 14.2857142857%;
    max-width: 14.2857142857%;
  }
}

@media (min-width: 2600px) {
  .responsive_gallery_container.px500_less_size_gallery {
    -ms-flex: 0 0 12.5%;
    -webkit-box-flex: 0;
    flex: 0 0 12.5%;
    max-width: 12.5%;
  }
}

@media (min-width: 3000px) {
  .responsive_gallery_container.px500_less_size_gallery {
    -ms-flex: 0 0 11.1111111111%;
    -webkit-box-flex: 0;
    flex: 0 0 11.1111111111%;
    max-width: 11.1111111111%;
  }
}

.responsive_gallery_container.is_full_size {
  -ms-flex: 0 0 100%;
  -webkit-box-flex: 0;
  flex: 0 0 100%;
  max-width: 100%;
}

.is_full_size > div > div {
  height: auto;
}

.is_full_size > div {
  height: auto;
}

.is_full_size > div > div > .paragraph_container > .paragraph_container_inner {
  height: auto;
  min-height: 100px;
  margin-bottom: 40px;
}
</style>
