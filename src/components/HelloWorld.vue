<template>
  <div ref="el" class="bg-gray-100">
    <div class="">
      <canvas ref="can" style="border: 1px solid black"></canvas>
      <div
        class="pallete sm:absolute right-0 top-0"
        :style="{
          'max-width':
            width - canvasWidth < 10 ? null : `${width - canvasWidth}px`,
        }"
      >
        <div class="pallete-panel grid grid-cols-4">
          <button
            v-for="color in colors"
            v-on:click="setColor(color)"
            class="text-center border border-blue-400 w-12 h-12 rounded"
            :class="{
              'bg-gray-200': color !== drawColor,
              'bg-blue-200': color === drawColor,
            }"
          >
            <svg
              class="inline-block"
              :style="{ color: color }"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              class="w-6 h-6"
              fill="currentColor"
            >
              <circle cx="10" cy="10" r="10" />
            </svg>
          </button>
        </div>
        <div class="mt-4 pallete-panel grid grid-cols-4">
          <button
            v-for="size in brushSizes"
            v-on:click="setSize(size)"
            class="border border-blue-400 w-12 h-12 rounded"
            :class="{
              'bg-gray-200': size !== drawSize,
              'bg-blue-200': size === drawSize,
            }"
          >
            <svg
              class="inline-block"
              :style="{ color: drawColor }"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              class="w-6 h-6"
              fill="currentColor"
            >
              <circle cx="10" cy="10" :r="Math.ceil(size / 4)" />
            </svg>
          </button>
        </div>

        <div class="pallete-panel mt-3">
          <button
            v-for="color in colors"
            v-on:click="fill(color)"
            class="text-center border border-blue-400 w-12 h-12 rounded"
          >
            <svg
              :style="{ color: color }"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              class="inline-block w-6 h-6"
              fill="currentColor"
            >
              <rect width="20" height="20" />
            </svg>
          </button>
        </div>
        <div class="pallete-panel mt-3">
          <label
            class="text-center flex flex-col items-center border border-blue-400 w-12 h-12 rounded"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
            <input type="file" v-on:change="onUpload" class="hidden" />
          </label>
        </div>
      </div>
    </div>
    <!-- <footer class="px-6 py-2 bg-gray-800 text-gray-100">
         <div
         class="flex flex-col justify-between items-center container mx-auto md:flex-row"
         >
         <p class="mt-2 md:mt-0">All rights reserved 2020.</p>
         </div>
         </footer> -->
  </div>
</template>

<script>
import { fabric } from 'fabric';

fabric.Image.filters.Redify = fabric.util.createClass(
  fabric.Image.filters.BaseFilter,
  {
    type: 'Redify',

    /**
     * Fragment source for the redify program
     */
    fragmentSource: `

    precision highp float;
    uniform sampler2D uTexture;
    varying vec2 vTexCoord;
    void main() {

      vec4 sample = texture2D(uTexture, vTexCoord);

      float x = 0.21 * sample.r + 0.71 * sample.g + 0.07 * sample.b;
      gl_FragColor = vec4(
        (step(vec3(0.33), vec3(x))  +step(vec3(0.66), vec3(x))) / vec3(2.0),
        1.0);
    }`,

    applyTo2d: function (options) {
      var imageData = options.imageData,
        data = imageData.data,
        i,
        len = data.length;
      for (i = 0; i < len; i += 4) {
        data[i + 1] = 0;
        data[i + 2] = 0;
      }
    },
  },
);
fabric.Image.filters.Redify.fromObject =
  fabric.Image.filters.BaseFilter.fromObject;

import { ref } from 'vue';
import { useWindowSize, debouncedWatch } from '@vueuse/core';
const W = 264;
const H = 176;
function rescale_canvas_if_needed({ canvas, width, height }) {
  var optimal_dimensions = [W, H];
  var scaleFactorX = width / optimal_dimensions[0];
  var scaleFactorY = height / optimal_dimensions[1];

  let w = 0;
  let h = 0;
  if (scaleFactorX < scaleFactorY) {
    w = optimal_dimensions[0] * scaleFactorX;
    h = optimal_dimensions[1] * scaleFactorX;
  } else {
    w = optimal_dimensions[0] * scaleFactorY;
    h = optimal_dimensions[1] * scaleFactorY;
  }
  canvas.setZoom(1);
  canvas.setWidth(w + 'px', {
    cssOnly: true,
  });
  canvas.setHeight(h + 'px', {
    cssOnly: true,
  });

  canvas.calcOffset();
  canvas.renderAll();

  return { w, h };
}

export default {
  name: 'HelloWorld',
  props: {
    msg: String,
  },
  methods: {
    setColor(color) {
      this.drawColor = color;
      this.canvas.freeDrawingBrush.color = color;
    },
    setSize(size) {
      this.drawSize = size;
      this.canvas.freeDrawingBrush.width = size;
    },
    fill(color) {
      var rect = new fabric.Rect({
        width: W,
        height: H,
        fill: color,
        opacity: 1,
      });

      this.canvas.add(rect);
    },
    onUpload(e) {
      var reader = new FileReader();
      reader.onload = (event) => {
        var imgObj = new Image();
        imgObj.src = event.target.result;
        imgObj.onload = () => {
          var image = new fabric.Image(imgObj);
          console.log(image.width);
          image.set({
            angle: 0,
            padding: 0,
            cornersize: 0,
          });
          image.scale(this.canvas.width / image.width);
          this.canvas.centerObject(image);
          this.canvas.add(image);
          this.canvas.renderAll();
          e.target.value = null;
        };
      };
      reader.readAsDataURL(e.target.files[0]);
    },
  },
  mounted() {
    const ref = this.$refs.can;
    this.canvas = new fabric.Canvas(ref);
    let canvas = this.canvas;
    //const bw = fabric.Image.filters.BlackWhite;
    canvas.isDrawingMode = true;
    canvas.freeDrawingBrush.width = this.drawSize;
    canvas.freeDrawingBrush.color = this.drawColor;
    canvas.imageSmoothingEnabled = false;
    canvas.enableRetinaScaling = false;
    canvas.setWidth(W); //, { backstoreOnly: true });
    canvas.setHeight(H); //, { backstoreOnly: true });
    canvas.setBackgroundColor('#FFFFFF', canvas.renderAll.bind(canvas));
    canvas.setZoom(1);
    const { width, height } = useWindowSize();
    const onResize = () => {
      this.width = width.value;
      this.height = height.value;
      const { w, h } = rescale_canvas_if_needed({
        canvas,
        width: width.value,
        height: height.value,
      });
      this.canvasWidth = w;
    };
    debouncedWatch([width, height], onResize, { debounce: 500 });
    onResize();

    canvas.on('path:created', function (p) {
      setTimeout(() => {
        const raster = canvas.toDataURL({
          enableRetinaScaling: false,
          multiplier: 1,
          left: 0,
          top: 0,
          width: W,
          height: H,
          withoutTransform: true,
          withoutShadow: true,
        });

        fabric.Image.fromURL(raster, (img) => {
          img.filters.push(
            /* new fabric.Image.filters.Blur({
             *   blur: 0.5,
             * }), */
            new fabric.Image.filters.Redify({
              blur: 0.5,
            }),
          );
          // apply filters and re-render canvas when done
          img.applyFilters();
          canvas.setBackgroundImage(img);
          canvas.getObjects().forEach((o) => canvas.remove(o));
        });
      }, 10);
    });
  },
  data() {
    return {
      canvasWidth: 0,
      width: 0,
      height: 0,
      canvas: null,
      drawColor: '#000000',
      drawSize: 2,
      colors: ['#000000', '#7F7F7F', '#FFFFFF'],
      brushSizes: [2, 4, 6, 8, 16, 20, 30, 40],
    };
  },
};
</script>
