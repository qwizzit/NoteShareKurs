<script lang="ts" setup>
import { onMounted, provide, ref, unref } from 'vue'
import { load, ReCaptchaInstance } from 'recaptcha-v3'

const recaptchaInstance = ref<ReCaptchaInstance | null>(null)

const getCaptchaToken = async(action: string): Promise<string | null> => {
  const instance = unref(recaptchaInstance);
  if (!instance) {
    return null
  }
  return await instance.execute(action)
}

onMounted(async() => {
  try {
    recaptchaInstance.value = await load('6LcDVLMsAAAAAHRHMPw20O44QsbAlxhVPmdkSWOZ')
  } catch (e) {
    console.error(e)
  }
})
provide('getCaptchaToken', getCaptchaToken)
</script>

<template>
  <form class="sign-page">
    <router-view />
  </form>
</template>

<style lang="scss">
.sign-page {
  display: flex;
  gap: 20px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100svw;
  height: 100svh;
  padding: 15px;
}
</style>
