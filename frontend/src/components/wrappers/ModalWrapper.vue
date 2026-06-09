<script lang="ts" setup>
const emit = defineEmits<{
  (e: 'close'): void;
}>()
</script>

<template>
  <div class="modal-wrapper" @click.self="emit('close')">
    <div class="modal-content" @click.self="emit('close')">
      <slot />
    </div>
  </div>
</template>

<style lang="scss">
.modal-wrapper {
  position: absolute;
  z-index: 10;
  top: 0;
  left: 0;
  background: rgba(var(--color-bg-main), .5);

  .modal-content {
    width: 100svw;
    height: 100svh;
    padding: 10px;
    display: flex;
    justify-content: center;
    align-items: center;
  }
}
</style>