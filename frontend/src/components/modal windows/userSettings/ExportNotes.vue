<script lang="ts" setup>
import { NotesApi } from "@src/Api/AccessApi.ts";
import BtnWrapper from "@src/components/wrappers/BtnWrapper.vue";
import type { InterfaceNoteDto } from "@src/models/InterfaceNoteDto.ts";
import type { InterfaceUserDto } from "@src/models/InterfaceUserDto.ts";
import JSZip from "jszip";
import chevronRight from "@src/assets/icons/chevron-right.svg";

const props = defineProps<{
  user: InterfaceUserDto;
}>()

async function exportNotes() {
  const zip = new JSZip();
  const notes = await NotesApi.getUserFullNotes(props.user.id);

  if (!notes) {
    return;
  }
  const filteredFullNotesInfo: Omit<InterfaceNoteDto, 'userId'>[] = notes.map(({ userId, ...note }) => note);
  const filteredShortNotesInfo = notes.map(({ userId, tags, content, ...note }) => note)
  filteredFullNotesInfo.forEach(note => {
    zip.file(`${ note.title }.txt`, note.content, { binary: false });
  })
  zip.file('info.json', JSON.stringify(filteredShortNotesInfo, null, 2), { binary: false });

  const content = await zip.generateAsync({ type: "blob" });

  const url = URL.createObjectURL(content);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'project-archive.zip';

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  URL.revokeObjectURL(url);
}

</script>

<template>
  <BtnWrapper @click="exportNotes">
    <div id="select-tool">
      <span>Export Notes</span>
      <chevronRight class="svg-icon icon-stroke" />
    </div>
  </BtnWrapper>
</template>

<style lang="scss">
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
</style>