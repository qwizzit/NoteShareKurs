<script lang="ts" setup>
import BtnWrapper from "@src/components/wrappers/BtnWrapper.vue";
import chevronRight from "@src/assets/icons/chevron-right.svg";
import ModalWrapper from "@src/components/wrappers/ModalWrapper.vue";
import closeWindow from '@src/assets/icons/close.svg'
import JSZip from "jszip";
import { inject, ref } from "vue";

const createNote = inject<(title?: string, content?: string) => Promise<void>>("createNote");

const isImportModal = ref(false);

const toggle = () => {
  isImportModal.value = !isImportModal.value;
}

async function reviewFile(event: Event) {
  const target = event.target as HTMLInputElement;
  if (!target || !target.files || target.files.length === 0) {
    return;
  }

  const file = target.files[0]!;

  if (file.name.endsWith('.txt')) {

    const text = await file.text();
    await createNote(file.name.slice(0, file.name.indexOf('.txt')), text);
    return;
  }

  if (file.name.endsWith('.zip')) {
    const buffer = await file.arrayBuffer();
    const zip = new JSZip();
    const loadedZip = await zip.loadAsync(buffer);

    for (const relativePath in loadedZip.files) {
      const zipObject = loadedZip.files[relativePath];

      if (!zipObject.dir && zipObject.name.endsWith('.txt')) {
        const txtContent = await zipObject.async("string");
        createNote(zipObject.name, txtContent);
      }
    }
  }
}
</script>

<template>
  <BtnWrapper>
    <div id="select-tool" @click="toggle">
      <span>Import Notes</span>
      <chevronRight class="svg-icon icon-stroke" />
    </div>
  </BtnWrapper>

  <teleport v-if="isImportModal" to="body">
    <ModalWrapper>
      <div class="import-notes">
        <header class="modal-header">
          <span>Import</span>
          <BtnWrapper class="modal-btn" @click="toggle">
            <closeWindow class="svg-icon icon-stroke" />
          </BtnWrapper>
        </header>
        <main class="import-files">
          <span>Select notes you'd like to import.<br>Formats: TXT, ZIP<br></span>
          <input
            id="file-upload"
            accept=".txt, .zip"
            type="file"
            @change="reviewFile"
          >
          <label
            id="file-label"
            class="file-upload"
            for="file-upload"
          >
            Choose file
          </label>
        </main>
      </div>
    </ModalWrapper>
  </teleport>
</template>

<style lang="scss">
#file-upload {
  display: none;
}

.modal-btn {
  width: auto;
}

.svg-icon {
  width: 15px;
  height: 15px;
}

#select-tool {
  display: flex;
  align-items: center;
  cursor: pointer;
  justify-content: space-between;
  width: 100%;
  gap: 20px;
  border: var(--border-side);
  padding: 5px;

  .svg-icon {
    width: 40px;
    height: 40px;
  }
}

.import-notes {
  display: flex;
  border-radius: 10px;
  padding: 15px;
  flex-direction: column;
  background-color: rgb(var(--color-bg-secondary));
  gap: 10px;

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: var(--border-side);
    padding-bottom: 5px;


  }

  .import-files {
    display: flex;
    flex-direction: column;
    gap: 10px;

    .file-upload {
      width: 100%;
      height: 100%;
      padding: 24px 12px;
      border: 2px dashed rgb(var(--color-border));
      border-radius: 10px;
      text-align: center;
    }

    //.input-file:: {
    //  display: none;
    //}
  }


}
</style>