<script lang="ts" setup>
import api, { AccessApi } from "@src/Api/AccessApi.ts";
import AuthWrapper from "@src/components/wrappers/AuthWrapper.vue";
import { inject, ref } from "vue";

const getCaptchaToken = inject<(action: string) => Promise<string | null>>('getCaptchaToken')

const inputCode = ref('');
const email = ref('');
const pass = ref('');
const isCodeSent = ref(false);

const submitRegisterRequest = async() => {
  if (!getCaptchaToken) {
    return;
  }

  const token = await getCaptchaToken('signup');
  if (!token) {
    alert('Captcha error');
    return;
  }

  await api.post('/register-request', {
    email: email.value,
    password: pass.value,
    captchaToken: token
  })
    .then(() => isCodeSent.value = true)
    .catch((e) => {
      console.error('Ошибка при регистрации:', e);
      alert(e.response?.data?.detail || 'Ошибка отправки кода');
    });
}

async function verifyAndRegister() {
  await api.post('/confirm-registration', {
    email: email.value,
    code: inputCode.value
  })
    .then(res => AccessApi.setToken(res.data.id))
    .catch(e => alert(e.response?.data?.detail || 'Неверный код или срок его действия истек'));
}

</script>

<template>
  <div class="sign-up">
    <AuthWrapper>
      <template #welcome>
        <span class="text">Sign Up</span>
      </template>
      <template #inputs>
        <input
          v-if="!isCodeSent"
          v-model="email"
          class="field"
          placeholder="Email"
          type="email"
        >
        <input
          v-if="!isCodeSent"
          v-model="pass"
          class="field"
          placeholder="Password"
          type="password"
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
          :disabled="!email || !pass"
          @click="submitRegisterRequest"
        >
          Get Code
        </button>
        <button
          v-else
          class="field but-color"
          type="button"
          :disabled="inputCode.length !== 6"
          @click="verifyAndRegister"
        >
          Sign Up
        </button>
      </template>
      <template #footer>
        <span class="footer-text">Already have an account? <router-link
          :to="{name: 'LogWithEmail'}"
        >Log in</router-link>.</span>
      </template>
    </AuthWrapper>
  </div>
</template>

<style lang="scss">
.sign-up {

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

  .field {
    border: none;
    padding: 5px 12px;
    background: rgb(var(--color-bg-secondary));
    border-radius: 10px;
    max-width: 350px;
    min-height: 50px;
    width: 100%;
  }
}

@media (max-width: 600px) {
  .sign-up {

    .field {
      max-width: 300px;
    }
  }
}
</style>