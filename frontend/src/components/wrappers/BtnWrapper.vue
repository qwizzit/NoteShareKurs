<template>
  <button class="btn">
    <slot />
  </button>
</template>

<style lang="scss">
.btn {
  background: unset;
  border: none;
  cursor: pointer;
  width: 100%;
  border-radius: 12px;
  min-height: 30px;
}
</style>