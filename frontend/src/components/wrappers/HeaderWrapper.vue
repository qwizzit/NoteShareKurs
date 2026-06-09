<template>
  <header class="header">
    <slot name="left-icons" />
    <slot />
    <slot name="right-icons" />
  </header>
</template>

<style lang="scss">
.header {
  display: flex;
  flex-shrink: 0;
  z-index: 4;
  padding: 0 var(--padding-left-notes-navigation);
  height: var(--height-header);
  width: 100%;
  align-items: center;
  justify-content: space-between;
  border-bottom: var(--border-side);
}
</style>
