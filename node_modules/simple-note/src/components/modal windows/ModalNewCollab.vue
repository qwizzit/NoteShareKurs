<script lang="ts" setup>
import closeWindow from '@src/assets/icons/close.svg'
import BtnWrapper from "@src/components/wrappers/BtnWrapper.vue";
import ModalWrapper from "@src/components/wrappers/ModalWrapper.vue";
import { ref } from "vue";

const emit = defineEmits<{
  (e: 'addCollaborator', email: string): void
  (e: 'close'): void
}>()
const email = ref('')

function addCollaborator() {
  emit("addCollaborator", email.value);
}

function closeModal() {
  emit('close')
}
</script>

<template>
  <ModalWrapper @close="closeModal">
    <div class="modal-collab">
      <div class="modal-header">
        <span class="text">
          New collab
        </span>
        <closeWindow class="svg-icon icon-stroke" @click="closeModal" />
      </div>
      <div class="add-collaborator">
        <span>
          Write email of new collaborator
        </span>
        <input
          v-model="email"
          class="email-input"
          type="email"
          @keyup.enter="addCollaborator"
        >
        <BtnWrapper @click="addCollaborator">
          Submit
        </BtnWrapper>
      </div>
    </div>
  </ModalWrapper>
</template>

<style>
.modal-collab {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  background: rgb(var(--color-bg-secondary));
  padding: 15px;
  gap: 10px;
  border-radius: 10px;
  width: 100%;
  max-width: 450px;

  .svg-icon {
    width: 15px;
    height: 15px;
  }

  .icon-stroke {
    cursor: pointer;
  }

  .text {
    padding: 3px;
  }

  .modal-header {
    border-bottom: var(--border-side);
    width: 100%;
    height: 30px;

    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .add-collaborator {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 0 10px;

    .email-input {
      background: rgba(var(--color-bg-main));
      border-radius: 12px;
      width: 100%;
      padding: 5px var(--padding-left-notes-navigation);
      border: unset;
      height: 50px;
      outline: unset;
    }
  }
}
</style>