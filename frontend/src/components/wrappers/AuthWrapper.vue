

<template>
  <div class="wrapper">
    <div class="welcome-block">
      <slot name="welcome" />
    </div>
    <div class="fields">
      <div class="log-in-container">
        <slot name="inputs" />
      </div>
      <slot name="btn" />
    </div>
    <div class="text-container">
      <slot name="footer" />
    </div>
  </div>
</template>

<style lang="scss">
.wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100svw;
  height: 100svh;
  gap: 30px;

  .welcome-block {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;

  }

  .fields {
    display: flex;
    gap: 15px;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 100%;

    .log-in-container {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      gap: 10px;
      width: 100%;
      height: 100%;
      max-height: 300px;
    }
  }

  .text-container {
    display: flex;
    padding: 0 20px;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 15px;
  }
}
</style>