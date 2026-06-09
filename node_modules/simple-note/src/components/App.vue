<script lang="ts" setup>
import { useColorMode, useToggle } from "@vueuse/core";

const mode = useColorMode({
  attribute: 'data-theme',
  modes: {
    dark: 'dark',
    light: 'light',
  },
})
const toggleDark = useToggle(mode, {
  truthyValue: 'dark',
  falsyValue: 'light'
})

function toggleCurrentTheme(typeTheme: number) {
  switch (typeTheme) {
    case 1:
      mode.value = 'auto';
      break;
    case 2:
      mode.value = 'dark';
      break;
    case 3:
      mode.value = 'light';
      break;
  }
}

</script>

<template>
  <!--  <div style="position:absolute; top: 10px; right: 10px;" @click="AccessApi.removeToken()"> -->
  <!--    log -->
  <!--  </div> -->
  <router-view @changeTheme="toggleDark" @updateTheme="toggleCurrentTheme" />
</template>
