<script lang="ts" setup>
import menuIcon from '@src/assets/icons/menu.svg'
import newNoteIcon from '@src/assets/icons/new-note.svg'
import search from '@src/assets/icons/search.svg'
import BtnWrapper from "@src/components/wrappers/BtnWrapper.vue";
import HeaderWrapper from "@src/components/wrappers/HeaderWrapper.vue";
import NoteItem from "@src/components/notes/DefaultNotes/NoteItem.vue";
import type { InterfaceNoteDto } from "@src/models/InterfaceNoteDto.js";
import type { InterfaceSettingsDto } from "@src/models/InterfaceSettingsDto.js";
import type { InterfaceUserTags } from "@src/models/InterfaceTagDto.js";
import { computed, ref } from "vue";

const emit = defineEmits<{
  (e: 'selectNote', id: number): void,
  (e: 'changeNote', id: number): void,
  (e: 'deleteNote', id: number): void,
  (e: 'updateColor', value: { noteId: number, color: string }): void,
  (e: 'openMenu'): void,
  (e: 'createNote'): void,
  (e: 'clearFilterNote'): void
}>()
const props = defineProps<{
  notes: InterfaceNoteDto[],
  selectedNoteId: number | null,
  selectedTag: InterfaceUserTags | null,
  userSettings: InterfaceSettingsDto | undefined,
  isNotesListShort: boolean
}>()

const openedMenuId = ref<number | null>(null);
const searchFilter = ref('')

const filteredNotes = computed(() => {
  if (!searchFilter.value && props.userSettings) {
    let neededNotes = [ ...props.notes ];
    if (props.selectedTag) {
      neededNotes = neededNotes.filter(note => props.selectedTag?.note_ids?.has(note.id));
    }
    switch (props.userSettings.note_sort) {
      case 1:
        return [ ...neededNotes ].sort((a, b) => a.title.localeCompare(b.title));
      case 2:
        return [ ...neededNotes ].sort((a, b) => b.title.localeCompare(a.title))
      case 3:
        return [ ...neededNotes ].sort((a, b) => b.created_at.localeCompare(a.created_at));
      case 4:
        return [ ...neededNotes ].sort((a, b) => a.created_at.localeCompare(b.created_at));
      case 5:
        return [ ...neededNotes ].sort((a, b) => b.updated_at.localeCompare(a.updated_at));
      case 6:
        return [ ...neededNotes ].sort((a, b) => a.updated_at.localeCompare(b.updated_at));
    }
  }
  return props.notes.filter(note => note.title.includes(searchFilter.value))
})

function onScrollContainer() {
  openedMenuId.value = null;
}

function deleteNote(id: number) {
  openedMenuId.value = null;
  emit("deleteNote", id);
}

function updateColor({ noteId, color }: { noteId: number, color: string }) {
  emit('updateColor', { noteId, color })
}
</script>

<template>
  <aside class="notes-page divider-right" :class="{ 'short-notes-pages': isNotesListShort}">
    <HeaderWrapper>
      <template #left-icons>
        <BtnWrapper class="header-btn" @click="emit('openMenu')">
          <menuIcon class="svg-icon icon-stroke" />
        </BtnWrapper>
      </template>
      <template #default>
        <span
          class="text"
          :style="{cursor: selectedTag ? 'pointer' : 'default'}"
          @click="emit('clearFilterNote')"
        >{{ selectedTag?.name || 'All notes' }}</span>
      </template>
      <template #right-icons>
        <BtnWrapper class="header-btn">
          <newNoteIcon
            v-if="!isNotesListShort"
            class="svg-icon icon-stroke"
            @click="emit('createNote')"
          />
        </BtnWrapper>
      </template>
    </HeaderWrapper>
    <nav class="notes" :class="{ 'short-notes': isNotesListShort}">
      <BtnWrapper v-if="isNotesListShort" class="add-note-btn">
        <newNoteIcon class="svg-icon icon-stroke" @click="emit('createNote')" />
      </BtnWrapper>
      <div v-if="!isNotesListShort" class="searching-notes">
        <search class="svg-icon icon-stroke" />
        <input
          v-model="searchFilter"
          class="search-note"
          placeholder="Search all notes..."
          type="search"
        >
      </div>
      <div class="notes-container" @scroll.prevent="onScrollContainer">
        <NoteItem
          v-for="note in filteredNotes"
          :id="note.id"
          :key="note.id"
          :displayNoteName="userSettings?.note_display"
          :isShortStyle="isNotesListShort"
          :menuOpen="openedMenuId === note.id"
          :note="note"
          :selectedNoteId="selectedNoteId"
          @click="emit('selectNote', note.id)"
          @deleteNote="deleteNote"
          @triggerMenu="openedMenuId = (openedMenuId === note.id) ? null : note.id"
          @updateColor="updateColor"
        />
      </div>
    </nav>
  </aside>
</template>

<style lang="scss">
.header-btn {
  width: auto;
}

.add-note-btn {
  border: none;
  cursor: pointer;
  border-radius: 50%;
  background-color: rgb(var(--color-short-style-notes));
  box-shadow: 0 0 4px rgb(var(--color-short-style-notes));
  width: calc(var(--short-size-grid-columns) - var(--padding-left-notes-navigation));
  height: calc(var(--short-size-grid-columns) - var(--padding-left-notes-navigation));
}

.svg-icon {
  width: 25px;
  height: 25px;
}

.notes-page {
  display: flex;
  flex-direction: column;
  background: rgb(var(--color-bg-secondary));
  width: 100%;
  height: 100svh;

  .header {

    .text {
      cursor: pointer;
      white-space: nowrap;
    }

    .svg-icon {
      width: 30px;
      height: 30px;
    }
  }

  .notes {
    height: 100%;

    .searching-notes {
      display: flex;
      align-items: center;
      justify-content: center;
      height: var(--height-searching-notes);
      gap: 5px;
      padding: 0 var(--padding-left-notes-navigation);
      border-bottom: var(--border-side);


      .search-note {
        width: 100%;
        height: 25px;
        background: none;
        border: none;
        outline: none;
      }
    }

    .notes-container {
      display: flex;
      flex-direction: column;
      overflow-y: auto;
      height: calc(100svh - (var(--height-searching-notes) + var(--height-header)));
      margin-bottom: calc(var(--height-searching-notes) + var(--height-header))
    }
  }
}

.short-notes-pages {
  width: var(--short-size-grid-columns) !important;

  .header {

    .text {
      display: none;
    }
  }

  .short-notes {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding-top: 10px;
    gap: 5px;
  }
}


</style>
