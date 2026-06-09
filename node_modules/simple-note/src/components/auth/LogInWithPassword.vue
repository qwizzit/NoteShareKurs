<script lang="ts" setup>
import api, { AccessApi } from "@src/Api/AccessApi.ts";
import AuthWrapper from "@src/components/wrappers/AuthWrapper.vue";
import axios from "axios";
import { inject, ref } from 'vue'

const getCaptchaToken = inject<(action: string) => Promise<string | null>>('getCaptchaToken')

const email = ref('')
const password = ref('')

const handleLogin = async() => {
  if (!getCaptchaToken) {
    console.error('captchaToken not found')
    return
  }

  const token = await getCaptchaToken('login')

  if (!token) {
    alert('Captcha error')
    return
  }

  try {
    await api.post('/login', {
      email: email.value,
      password: password.value,
      captchaToken: token
    })
      .then((res) => {
        AccessApi.setToken(res.data.user_id)
      })

  } catch (e) {
    console.error('Ошибка при входе:', e)
  }
}
</script>

<template>
  <div class="log-with-pass">
    <AuthWrapper>
      <template #welcome>
        <span class="text">Log In</span>
      </template>
      <template #inputs>
        <input
          v-model="email"
          class="field"
          placeholder="Email"
          type="email"
        >
        <input
          v-model="password"
          class="field"
          placeholder="Password"
          type="password"
        >
      </template>
      <template #btn>
        <button
          class="field but-color"
          type="button"
          :disabled="!email || !password"
          @click="handleLogin"
        >
          Log In with Password
        </button>
      </template>
      <template #footer>
        <span class="footer-text">You can log in manually, or we will send you a  <router-link
          :to="{name: 'LogWithEmail'}"
        >log in code via email</router-link>.</span>
        <hr>
        <span class="footer-text">or <router-link :to="{name: 'SignUp'}">Sign up</router-link></span>
      </template>
    </AuthWrapper>
  </div>
</template>

<style lang="scss">
.log-with-pass {

  .field {
    border: none;
    padding: 5px 12px;
    background: rgb(var(--color-bg-secondary));
    border-radius: 10px;
    max-width: 350px;
    min-height: 50px;
    width: 100%;
  }

  .text {
    font-size: 40px;
  }

  .but-color:disabled {
    cursor: not-allowed;
    background: rgb(var(--color-disabled-btn));
  }

  .but-color {
    cursor: pointer;
    background: rgb(var(--color-btn));
    transition: background .5s;
  }

  .footer-text {
    text-align: center;
  }
}

@media (max-width: 600px) {
  .log-with-pass {

    .field {
      max-width: 300px;
    }
  }
}
</style>