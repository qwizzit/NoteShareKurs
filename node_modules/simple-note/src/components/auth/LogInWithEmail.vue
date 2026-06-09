<script lang="ts" setup>
import api, { AccessApi } from "@src/Api/AccessApi.ts";
import AuthWrapper from "@src/components/wrappers/AuthWrapper.vue";
import axios from "axios";
import { inject, ref } from "vue";

const getCaptchaToken = inject<(action: string) => Promise<string | null>>('getCaptchaToken')

const email = ref('');
const inputCode = ref('');
const isCodeSent = ref(false);

const submitEmailCode = async() => {
  if (!getCaptchaToken) {
    return;
  }

  const token = await getCaptchaToken('send_otp');
  if (!token) {
    alert('Captcha error');
    return;
  }

  try {
    await api.post('/send-email-code', {
      email: email.value,
      captchaToken: token
    })
      .then(() => isCodeSent.value = true);
  } catch (e) {
    console.error('Ошибка при отправке кода:', e);
  }
}

async function verifyAndLogin() {
  await api.post('/verify-otp', {
    email: email.value,
    code: inputCode.value
  })
    .then(res => {
      if (res.data.user_id) {
        AccessApi.setToken(res.data.user_id);
      }
    })
    .catch(() => {
      alert('Неверный код или срок его действия истек');
    });
}
</script>

<template>
  <div class="log-with-email">
    <AuthWrapper>
      <template #welcome>
        <span class="text">Log In</span>
      </template>
      <template #inputs>
        <input
          v-if="!isCodeSent"
          v-model="email"
          class="field"
          placeholder="Email"
          type="email"
          required
        >
        <input
          v-else
          v-model="inputCode"
          class="field"
          placeholder="000000"
          type="tel"
          required
        >
      </template>
      <template #btn>
        <button
          v-if="!isCodeSent"
          class="field but-color"
          type="button"
          :disabled="!email"
          @click="submitEmailCode"
        >
          Log In with Email
        </button>
        <button
          v-else
          class="field but-color"
          type="button"
          :disabled="inputCode.length !== 6"
          @click="verifyAndLogin"
        >
          Log In
        </button>
      </template>
      <template #footer>
        <span class="footer-text">We’ll email you a code to log in, or you can <router-link :to="{name: 'LogWithPass'}">log in manually</router-link>.</span>
        <hr>
        <span class="footer-text">or <router-link :to="{name: 'SignUp'}">Sign up</router-link></span>
      </template>
    </AuthWrapper>
  </div>
</template>

<style lang="scss">
.log-with-email {

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
  .log-with-email {

    .field {
      max-width: 300px;
    }
  }
}
</style>
