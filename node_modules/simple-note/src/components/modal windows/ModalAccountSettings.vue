<script lang="ts" setup>
import { UsersApi } from "@src/Api/AccessApi.ts";
import SectionsSettings from "@src/components/modal windows/userSettings/SectionsSettings.vue";
import BtnWrapper from "@src/components/wrappers/BtnWrapper.vue";
import ModalWrapper from "@src/components/wrappers/ModalWrapper.vue";
import closeWindow from '@src/assets/icons/close.svg'
import type { InterfaceSettingsDto } from "@src/models/InterfaceSettingsDto.ts";
import type { InterfaceUserDto } from "@src/models/InterfaceUserDto.ts";
import { onMounted, ref } from "vue";

const emit = defineEmits<{
  (e: 'updateUserSettings', value: InterfaceSettingsDto): void,
  (e: 'close'): void;
}>();

const user = ref<InterfaceUserDto>();
const selectedSection = ref(1);

function changeSection(section: number) {
  selectedSection.value = section;
}

function updateUserSettings(settings: InterfaceSettingsDto) {
  if (user.value) {
    user.value.settings = { ...settings };
  }
  emit("updateUserSettings", settings);
}

onMounted(() => {
  const userId = localStorage.getItem('token');

  if (userId) {
    UsersApi.getUser(parseInt(userId))
      .then(res => {
        if (res) {
          user.value = { ...res }
        }
      })
  }
})
</script>

<template>
  <ModalWrapper @close="emit('close')">
    <div class="modal-account-settings">
      <header class="modal-header">
        <span class="text">Settings</span>
        <BtnWrapper class="modal-btn" @click="emit('close')">
          <closeWindow class="svg-icon icon-stroke" />
        </BtnWrapper>
      </header>
      <nav class="modal-nav">
        <BtnWrapper class="navigation" @click="changeSection(1)">
          Account
        </BtnWrapper>
        <BtnWrapper class="navigation" @click="changeSection(2)">
          Display
        </BtnWrapper>
        <BtnWrapper class="navigation" @click="changeSection(3)">
          Tools
        </BtnWrapper>
      </nav>
      <main class="account-settings">
        <SectionsSettings
          v-if="user"
          :selectedSection="selectedSection"
          :user="user"
          @updateUserSettings="updateUserSettings"
        />
      </main>
    </div>
  </ModalWrapper>
</template>

<style lang="scss">
.modal-account-settings {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  background: rgb(var(--color-bg-secondary));
  padding: 15px;
  gap: 10px;
  border-radius: 10px;
  width: 100%;
  height: 100%;
  max-width: 650px;
  max-height: 650px;

  .svg-icon {
    width: 15px;
    height: 15px;
  }

  .text {
    padding: 3px;
  }

  .modal-header {
    border-bottom: var(--border-side);
    width: 100%;
    height: 40px;
    display: flex;
    justify-content: space-between;
  }

  .modal-nav {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    border-bottom: var(--border-side);
    height: 50px;

    .navigation {
      width: 100%;
      border-radius: unset;
      height: 50px;
      border-bottom: calc(var(--size-divider) + 1px) solid rgba(255, 255, 255, 0);
      transition: border .35s;
    }

    .navigation:hover {
      border-bottom: var(--border-side-btn);
    }
  }

  .account-settings {
    width: 100%;
    height: 100%;
  }
}
</style>