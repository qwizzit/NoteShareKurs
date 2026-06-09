<script lang="ts" setup>
import BtnWrapper from "@src/components/wrappers/BtnWrapper.vue";
import closeWindow from '@src/assets/icons/close.svg'
import ModalWrapper from "@src/components/wrappers/ModalWrapper.vue";
import type { Note } from "@src/models/Note.ts";
import { ref } from "vue";

const emit = defineEmits<{
  (e: 'close'): void;
}>();
const props = defineProps<{
  note: Note
}>()
const countWords = ref(props.note.content.trim().split(/\s+/).length);
const countSymbols = ref(props.note.content.trim().length);
</script>

<template>
  <ModalWrapper @close="emit('close')">
    <div class="modal-note-info">
      <header class="modal-header">
        <span class="text">{{ note.title }}</span>
        <BtnWrapper class="modal-btn" @click="emit('close')">
          <closeWindow class="svg-icon icon-stroke" />
        </BtnWrapper>
      </header>
      <main class="note-info">
        <span class="text">Updated at: {{ note.updated_at }}</span>
        <span class="text">Created at: {{ note.created_at }}</span>
        <span class="text">Words: {{ countWords }}</span>
        <span class="text">Symbols: {{ countSymbols }}</span>
      </main>
    </div>
  </ModalWrapper>
</template>

<style lang="scss">
.modal-note-info {
  display: flex;
  flex-direction: column;
  padding: 15px;
  background: rgb(var(--color-bg-secondary));
  gap: 10px;
  border-radius: 10px;

  .svg-icon {
    width: 15px;
    height: 15px;
  }

  .text {
    padding: 3px;
  }

  .modal-header {
    border-bottom: var(--border-side);
    height: 40px;
    display: flex;
    justify-content: space-between;

    .modal-btn{
      width: auto;
    }
  }

  .note-info {
    display: flex;
    flex-direction: column;
  }
}
</style>