<template>
  <div>
    <div v-if="title != '' || n_count >= 0" class="gallery_title">
      <h2 v-if="title != ''" style="float: left">{{ title }}</h2>
      <div
        v-if="n_count >= 0"
        type="submit"
        class="l_button button_white rounded_button"
        @click="$emit('more_imgs_cb', {})"
        style="margin-right: 20px; float: right"
      >
        {{ n_count }} items
        <i style="margin-left: 5px; color: rgb(58, 164, 251); font-size: 12px">
          <font-awesome-icon icon="chevron-right"
        /></i>
      </div>
    </div>
    <div class="gallery_container">
      <GalleryItem
        v-for="item in items"
        v-bind:is_px500_less_size_gallery="is_px500_less_size_gallery"
        v-bind:key="item.key"
        v-bind:item_id="item.key"
        @on_click_cb="on_click_cb"
        @on_double_click_cb="on_double_click_cb"
        :tag="item.tag"
        :description="item.description"
        :type="item.type || 'full_img'"
        :tag_color="item.tag_color"
        :audio_url="item.audio_url"
        :video_url="item.video_url"
        :title="item.title"
        :ref="item.key"
        :dont_unselect_on_outside_click="keep_one_selected"
        :url="item.url"
      >
      </GalleryItem>
    </div>
  </div>
</template>
<script>
import GalleryItem from './GalleryItem.vue'

export default {
  name: 'GalleryContainerBare',
  components: { GalleryItem },
  props: {
    items: Array,
    title: String,
    n_count: Number,
    is_px500_less_size_gallery: Boolean,
    on_click_callback: Function,
    on_double_click_callback: Function,
    keep_one_selected: Boolean, // if set to true it wont unselect if you click anywhere outside the gallery.
  },
  mounted() {
    if (this.keep_one_selected) {
      if (this.items.length > 0) {
        this.selected_gallery_key = this.items[0].key
        this.$refs[this.items[0].key][0].selected = true
      }
    }
  },
  methods: {
    on_click_cb(k) {
      if (
        this.keep_one_selected &&
        this.selected_gallery_key &&
        this.selected_gallery_key != k
      ) {
        this.$refs[this.selected_gallery_key][0].selected = false
      }
      this.selected_gallery_key = k
      if (this.on_click_callback) this.on_click_callback(k)
    },

    on_double_click_cb(k) {
      if (this.on_double_click_callback) {
        this.on_double_click_callback(k)
      }
    },
  },
}
</script>
<style>
.gallery_title {
  padding-bottom: 10px;
  padding-left: 10px;
  /*display: flex;
    flex-wrap: wrap;*/
}

.gallery_container {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.gallery_title:after {
  content: '';
  display: table;
  clear: both;
}
</style>
