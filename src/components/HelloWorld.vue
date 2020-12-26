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
              :style="{ color: color }"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              class="inline-block w-6 h-6"
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
              :style="{ color: drawColor }"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 40 40"
              class="inline-block w-10 h-10"
              fill="currentColor"
            >
              <circle cx="20" cy="20" :r="Math.ceil(size / 2)" />
            </svg>
          </button>
        </div>

        <!-- <div class="pallete-panel mt-3">
             <button
             disabled="disabled"
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
             </div> -->
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
        <img ref="wc" style="width: 100%" />
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
        vec3(x),
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
//        (step(vec3(0.33), vec3(x))  +step(vec3(0.66), vec3(x))) / vec3(2.0),

fabric.Image.filters.Redify.fromObject =
  fabric.Image.filters.BaseFilter.fromObject;

/* function getImageData(img) {
 *   // 1) Create a canvas, either on the page or simply in code
 *   var canvas = document.createElement('canvas');
 *   var ctx = canvas.getContext('2d');
 *
 *   // 2) Copy your image data into the canvas
 *   var myImgElement = document.getElementById('foo');
 *   ctx.drawImage(img, 0, 0);
 *
 *   // 3) Read your image data
 *   var w = img.width,
 *     h = img.height;
 *    return ctx.getImageData(0, 0, w, h);
 *  } */

function floyd_steinberg(image) {
  var imageData = image.data;
  var imageDataLength = imageData.length;
  var w = image.width;
  var lumR = [],
    lumG = [],
    lumB = [];

  var newPixel, err;

  for (var i = 0; i < 256; i++) {
    lumR[i] = i * 0.299;
    lumG[i] = i * 0.587;
    lumB[i] = i * 0.11;
  }

  // Greyscale luminance (sets r pixels to luminance of rgb)
  for (var i = 0; i <= imageDataLength; i += 4) {
    imageData[i] = Math.floor(
      lumR[imageData[i]] + lumG[imageData[i + 1]] + lumB[imageData[i + 2]],
    );
  }

  for (
    var currentPixel = 0;
    currentPixel <= imageDataLength;
    currentPixel += 4
  ) {
    // threshold for determining current pixel's conversion to a black or white pixel
    newPixel = imageData[currentPixel] < 150 ? 0 : 255;
    err = Math.floor((imageData[currentPixel] - newPixel) / 23);
    imageData[currentPixel + 0 * 1 - 0] = newPixel;
    imageData[currentPixel + 4 * 1 - 0] += err * 7;
    imageData[currentPixel + 4 * w - 4] += err * 3;
    imageData[currentPixel + 4 * w - 0] += err * 5;
    imageData[currentPixel + 4 * w + 4] += err * 1;
    // Set g and b values equal to r (effectively greyscales the image fully)
    imageData[currentPixel + 1] = imageData[currentPixel + 2] =
      imageData[currentPixel];
  }

  return image;
}

import { ref } from 'vue';
import { useWindowSize, debouncedWatch } from '@vueuse/core';
import { customAlphabet } from 'nanoid';

const W = 264;
const H = 176;

function rescale_canvas_if_needed({ canvas, width, height }) {
  var optimal_dimensions = [W, H];
  const portrait = width < height;
  var scaleFactorX = (width - (portrait ? 0 : 200)) / optimal_dimensions[0];
  var scaleFactorY = (height - (portrait ? 300 : 0)) / optimal_dimensions[1];

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
        left: 0,
        top: 0,
        width: W,
        height: H,
        fill: color,
        opacity: 1,
      });

      this.canvas.add(rect);
      this.onUpdate();
    },
    onUpdate() {
      const raster = this.canvas.toDataURL();

      fabric.Image.fromURL(raster, (img) => {
        //        img.filters.push(new fabric.Image.filters.Redify());
        // apply filters and re-render canvas when done
        //        img.applyFilters();
        this.canvas.getObjects().forEach((o) => this.canvas.remove(o));
        this.dbImage.set({
          image: img.toDataURL(),
          clientId: this.clientId,
        });
        this.canvas.setBackgroundImage(img);
      });
    },
    onUpload(e) {
      var reader = new FileReader();
      reader.onload = (event) => {
        var imgObj = new Image();
        imgObj.src = event.target.result;
        imgObj.onload = () => {
          /* const imgCtx = getImageData(imgObj);
           * this.canvas.getContext().drawImage(imgCtx.canvas, 0, 0); */
          var image = new fabric.Image(imgObj);

          image.set({
            angle: 0,
            padding: 0,
            cornersize: 0,
          });
          image.scale(this.canvas.width / image.width);
          this.canvas.centerObject(image);
          this.canvas.add(image);
          this.canvas.renderAll();
          this.onUpdate();
          e.target.value = null;
        };
      };
      reader.readAsDataURL(e.target.files[0]);
    },
  },
  mounted() {
    const database = firebase.database();
    const storage = firebase.storage();
    this.dbImage = firebase.database().ref('board/0');
    //this.wcImage = firebase.database().ref('wc/0');

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

    setInterval(() => {
      storage
        .ref('images/wc.jpg')
        .getDownloadURL()
        .then((url) => {
          this.$refs.wc.src = url + '?' + new Date().getTime();
        })
        .catch(function (error) {
          // Handle any errors
        });
    }, 5000);

    this.dbImage.on('value', (db2) => {
      const res = db2.val();
      if (this.clientId !== res.clientId) {
        fabric.Image.fromURL(res.image, (img) => {
          this.canvas.setBackgroundImage(img);
          this.canvas.renderAll();
        });
      }
    });

    //    const onUpdate = () => ;
    canvas.on('path:created', this.onUpdate);
  },
  data() {
    return {
      showWebcam: false,
      clientId: customAlphabet('0123456789abcdefghijklmnopqrstuvwxyz', 6)(),
      canvasWidth: 0,
      dbImage: null,
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
