<script lang="ts" setup>
import api, { NotesApi, UsersApi } from "@src/Api/AccessApi.ts";
import ModalNewCollab from "@src/components/modal windows/ModalNewCollab.vue";
import AppMenu from "@src/components/navigation/AppMenu.vue";
import NoteCollaborators from "@src/components/notes/Collaborators/NoteCollaborators.vue";
import ActiveNote from "@src/components/notes/DefaultNotes/ActiveNote.vue";
import AllNotes from "@src/components/notes/DefaultNotes/AllNotes.vue";
import { MOBILE_BREAKPOINT } from "@src/composition/constants.ts";
import { findArrayIndexById } from "@src/composition/methods.ts"
import type { InterfaceColaborators } from "@src/models/InterfaceColaborators.ts";
import type { InterfaceNoteDto } from "@src/models/InterfaceNoteDto.ts";
import type { InterfaceSettingsDto } from "@src/models/InterfaceSettingsDto.ts";
import type { InterfaceUserTags } from "@src/models/InterfaceTagDto.ts";
import { Note } from "@src/models/Note.ts";
import type { Tag } from "@src/models/Tag.ts";
import { useToggle, useWindowSize } from "@vueuse/core";
import { instanceToInstance } from "class-transformer";
import { computed, onMounted, provide, ref, unref, watch } from "vue";

const emit = defineEmits<{
  (e: 'changeTheme'): void,
  (e: 'updateTheme', value: number): void,
}>()

provide('createNote', createNote);

const { width } = useWindowSize();
const [ isModalNewCollab, toggleModalNewCollab ] = useToggle(false)
const [ value, toggle ] = useToggle();

const notes = ref<Note[]>([])
const tags = ref<InterfaceUserTags[]>([])
const collaboratorsNote = ref<InterfaceColaborators>()

const selectedNoteId = ref<number | null>(null);
const selectedTag = ref<InterfaceUserTags | null>(null);

const isNotesListShort = ref(false);
const isCollaboratorsList = ref(false);
const isNoteContentLoading = ref(false);
const isMobileCollabMenu = ref(false)
const userSettings = ref<InterfaceSettingsDto>();

const isMobile = computed(() => unref(width) < MOBILE_BREAKPOINT);

const selectedNote = computed({
  get: () => {
    if (unref(selectedNoteId) === null) {
      return null;
    }
    return notes.value.find(note => note.id === unref(selectedNoteId)) as Note || null;
  },
  set: val => {
    if (val == null) {
      return;
    }
    notes.value = unref(notes)
      .map(v => {
        if (v.id == val.id) {
          return val
        }
        return v
      })
  }
});

const selectNote = async(id: number) => {
  selectedNoteId.value = id;
  await loadCurrentNoteContent()
    .then(async() => collaboratorsNote.value = await NotesApi.getCollaborators(id))
    .then(() => {
      if (collaboratorsNote.value && collaboratorsNote.value.collaborators.length > 0) {
        isCollaboratorsList.value = true
      }
    })
}
const selectTag = (tag: InterfaceUserTags): void => {
  selectedTag.value = { ...tag };
}
const closeNote = () => {
  selectedNoteId.value = null;
}

async function loadCurrentNoteContent() {
  const noteId = unref(selectedNoteId);
  const index = findArrayIndexById(unref(notes), noteId);
  if (!noteId || notes.value.length === 0 || notes.value[index]?.content) {
    return;
  }

  isNoteContentLoading.value = false;

  await NotesApi.getNoteData(noteId).then((res) => {
    notes.value[index]!.content = res.content;
    notes.value[index]!.tags = res.tags;

  });

  isNoteContentLoading.value = true;
}

async function updateNoteContent(shortNote: { id: number, content: string }, isNoteClosed: boolean) {
  if (isNoteClosed) {
    const index = findArrayIndexById(unref(notes), shortNote.id);

    notes.value[index]!.content = shortNote.content;
  }
  await api.patch(`/notes/${ shortNote.id }`, { content: shortNote.content })
    .then((res) => {
      updateNoteArray(res.data);
    });
}

/**
 * @param {{id: number, tag: string}} shortNoteTag
 * @returns {Promise<void>}
 * @deprecated
 */
async function updateNoteTags(shortNoteTag: { id: number, tag: string }) {
  await api.patch(`/notes/${ shortNoteTag.id }`, { tag: shortNoteTag.tag })
    .then((res) => {
      updateNoteArray(res.data);
      const index = findArrayIndexById(unref(notes), shortNoteTag.id)
      const lastIndex = res.data.tags.length - 1;
      if (notes.value[index]!.tags.find(tag => tag.id === res.data.tags[lastIndex].id)?.id === -1) {
        notes.value[index]!.addTag({ id: res.data.tags[lastIndex].id, name: res.data.tags[lastIndex].name });
      }

      const tagIndex = tags.value.findIndex((tag) => tag.id === res.data.tags[lastIndex].id);
      if (tagIndex !== -1) {
        tags.value[tagIndex]!.note_ids.add(shortNoteTag.id);
      } else {
        tags.value = [ ...tags.value, {
          id: res.data.tags[lastIndex].id,
          name: res.data.tags[lastIndex].name,
          note_ids: new Set([ shortNoteTag.id ])
        } ];
      }
    })
}

function syncTagsFromWebSocket(noteTags: { id: number, tags: Tag[] }) {
  const noteIndex = notes.value.findIndex(n => n.id === noteTags.id);

  if (noteIndex !== -1) {
    notes.value[noteIndex]!.tags = [ ...noteTags.tags ];
  }

  tags.value.forEach(tag => {
    tag.note_ids.delete(noteTags.id);
  });

  noteTags.tags.forEach(incomingTag => {
    const globalTagIndex = tags.value.findIndex(t => t.id === incomingTag.id);

    if (globalTagIndex !== -1) {
      tags.value[globalTagIndex]!.note_ids.add(noteTags.id);
    } else {
      tags.value.push({
        id: incomingTag.id,
        name: incomingTag.name,
        note_ids: new Set([ noteTags.id ])
      });
    }
  });

  tags.value = tags.value.filter(tag => tag.note_ids.size > 0);

  if (selectedTag.value && !tags.value.some(t => t.id === selectedTag.value?.id)) {
    selectedTag.value = null;
  }
}

function syncNoteColorFromWebSocket({ id, color }: { id: number, color: string }) {
  const newVal = instanceToInstance(unref(notes))
  const index = newVal.findIndex(v => v.id === id);

  if (index !== -1) {
    newVal[index]!.color = color;
    notes.value = newVal
  }
}

function syncNoteNameFromWebSocket({ id, name }: { id: number, name: string }) {
  const newVal = [ ...unref(notes.value) ]
  const index = newVal.findIndex(v => v.id === id);
  newVal[index]!.title = name;
  notes.value = newVal
}

async function deleteNote(noteId: number) {
  const arrIndex = notes.value.findIndex(note => note.id === noteId);
  if (arrIndex === -1) {
    return;
  }
  if (selectedNoteId.value === noteId) {
    selectedNoteId.value = null;
  }
  const noteTags = notes.value[arrIndex]!.tags;
  notes.value.splice(arrIndex, 1);
  collaboratorsNote.value = undefined;

  await api.delete(`/notes/${ noteId }`)
    .then(() => {
      let newTags = unref(tags);
      noteTags.forEach(tag => {
        newTags.forEach((t, index) => {
          if (t.id === tag.id) {
            newTags[index]!.note_ids.delete(noteId);
            if (newTags[index]!.note_ids.size === 0) {
              newTags.splice(index, 1);
            }
          }
        });

      });
      tags.value = newTags
    })
    .catch(error => {
      console.error('Ошибка при удалении заметки:', error);
    });

}

/**
 * Need for socket
 */
const {
  deleteNoteFromList
} = (() => {
  function deleteNoteFromList(noteId: number) {
    const newNotes = unref(notes);
    const index = findArrayIndexById(unref(notes), noteId);
    if (index !== -1) {
      newNotes.splice(index, 1);
    }
    notes.value = newNotes;
  }

  return {
    deleteNoteFromList
  }
})()

async function deleteNoteTag(tagId: number, noteId: number) {
  const noteIndex = findArrayIndexById(unref(notes), noteId);
  const tagsIndex = findArrayIndexById(unref(tags), tagId);

  notes.value[noteIndex]!.removeTag(tagId);

  if (tags.value[tagsIndex]) {
    tags.value[tagsIndex].note_ids.delete(noteId);
    if (tags.value[tagsIndex].note_ids.size === 0) {
      tags.value.splice(tagsIndex, 1);
      selectedTag.value = null;
    }
  }

  await api.delete(`/notes/${ noteId }/tags/${ tagId }`)
}

function updateNoteArray(updatedNote: Note) {
  const index = findArrayIndexById(unref(notes), updatedNote.id);

  notes.value[index]!.updated_at = updatedNote.updated_at;
  notes.value[index]!.title = updatedNote.title;
}

function updateUserSettings(settings: InterfaceSettingsDto): void {
  userSettings.value = { ...settings };
}

function updateCollaboratorsList(noteId: number) {
  const id = localStorage.getItem('token');

  NotesApi.getCollaborators(noteId)
    .then((collaboratorsData) => {
      collaboratorsNote.value = collaboratorsData;

      if (!collaboratorsData) {
        removeNoteFromLocalList();
        return;
      }

      if (id && parseInt(id) !== collaboratorsData.owner.id) {
        const currentUser = collaboratorsData.collaborators.find(
          collaborator => collaborator.id === parseInt(id)
        );

        if (!currentUser) {
          removeNoteFromLocalList();
        }
      }
    })
    .catch((error) => {
      console.log("Заметка удалена или доступ закрыт:", error);
      removeNoteFromLocalList();
    });

  function removeNoteFromLocalList() {
    collaboratorsNote.value = undefined;

    if (tags.value) {
      tags.value = tags.value.filter(tag => {
        if (tag.note_ids) {
          tag.note_ids.delete(noteId);
          return tag.note_ids.size > 0;
        }
        return false;
      });
    }

    const noteIndex = findArrayIndexById(unref(notes), noteId);
    if (noteIndex !== -1) {
      notes.value.splice(noteIndex, 1);
    }

    if (selectedNote.value?.id === noteId) {
      selectedNote.value = null;
    }
  }
}

async function createNote(title: string = 'New note', content: string = '') {
  const userId = localStorage.getItem('token');
  await api.post(`/notes?user_id=${ userId }&note_title=${ title }&note_content=${ content }`)
    .then(res => {
      const newNote: InterfaceNoteDto = res.data;
      notes.value = [
        ...notes.value,
        new Note(
          newNote.id,
          newNote.userId,
          newNote.title,
          newNote.color,
          newNote.created_at,
          newNote.updated_at,
          newNote.content
        )
      ];
    });
}

async function addCollaborator(email: string) {
  await api.post(`/notes/${ selectedNote.value?.id }/share?email=${ email }`)
    .then(res => {
      if (collaboratorsNote.value) {
        collaboratorsNote.value.collaborators = [ ...collaboratorsNote.value.collaborators, res.data.user ];
      }
    })
    .catch(err => console.log(err));
}

async function deleteCollaborator(userId: number) {
  await api.delete(`/notes/${ selectedNote.value?.id }/share/${ userId }`)
    .then(() => {
      if (collaboratorsNote.value) {
        const id = localStorage.getItem('token');

        if (id && parseInt(id) === userId) {
          collaboratorsNote.value = undefined;
          if (selectedNote.value) {
            const noteIndex = findArrayIndexById(unref(notes), selectedNote.value.id);
            if (noteIndex !== -1) {
              notes.value.splice(noteIndex, 1);
            }
          }
        } else {
          collaboratorsNote.value.collaborators = collaboratorsNote.value.collaborators.filter(collaborator => collaborator.id !== userId);
        }

      }
    })
    .catch(err => console.error(err));
}

function openCollabMenu() {
  isMobileCollabMenu.value = !isMobileCollabMenu.value;
  isCollaboratorsList.value = !isCollaboratorsList.value;
}

async function updateColor({ noteId, color }: { noteId: number, color: string }) {
  await api.patch(`/notes/${ noteId }`, { color })
  const newNotes = unref(notes);
  const index = newNotes.findIndex(note => note.id === noteId);
  newNotes[index]!.color = color;
  notes.value = newNotes;
}

watch(() => userSettings.value, () => {
  if (userSettings.value) {
    emit('updateTheme', userSettings.value.theme)
  }
})
onMounted(() => {
  const token = localStorage.getItem('token');

  if (token !== null) {
    const userId = parseInt(token);

    NotesApi.getUserNotes(userId)
      .then((res) => {
        notes.value = res.map(note => new Note(
          note.id,
          note.userId,
          note.title,
          note.color,
          note.created_at,
          note.updated_at
        ));
      })
      .catch(err => {
        console.error("Ошибка при загрузке заметок:", err);
      });
    NotesApi.getTags(userId)
      .then(res => {
        tags.value = res.map(tag => ({
          ...tag,
          note_ids: new Set(tag.note_ids)
        }));

      })
    UsersApi.getUserSettings(userId)
      .then(res => userSettings.value = { ...res })
  }

})

watch(isMobile, () => {
  if (unref(isMobile)) {
    isNotesListShort.value = false;
  }
})

</script>

<template>
  <div
    class="page"
    :class="{
      'mobile-page': isMobile,
      'grid-with-collaborators': collaboratorsNote && collaboratorsNote.collaborators.length > 0,
      'short-page': isNotesListShort
    }"
  >
    <AppMenu
      v-if="value"
      :tags="tags"
      @changeTheme="emit('changeTheme')"
      @chooseNotesByTag="selectTag"
      @closeMenu="toggle"
      @updateUserSettings="updateUserSettings"
    />

    <AllNotes
      v-show="!isMobile || selectedNoteId === null"
      :isNotesListShort="isNotesListShort"
      :notes="notes"
      :selectedNoteId="selectedNoteId"
      :selectedTag="selectedTag"
      :userSettings="userSettings"
      @clearFilterNote="selectedTag = null"
      @createNote="createNote"
      @deleteNote="deleteNote"
      @openMenu="toggle"
      @selectNote="selectNote"
      @updateColor="updateColor"
    />

    <ActiveNote
      v-if="(!isMobile || selectedNoteId !== null) && !isMobileCollabMenu && selectedNote"
      :key="selectedNoteId || 'none' "
      v-model:note="selectedNote"
      :collaboratorsNote="collaboratorsNote"
      :isMobile="isMobile"
      :isNoteSelected="selectedNoteId !== null"
      :loading="isNoteContentLoading"
      @addCollaborator="toggleModalNewCollab"
      @changeListStyle="isNotesListShort = !isNotesListShort"
      @closeNote="closeNote"
      @deleteNoteFromList="deleteNoteFromList"
      @deleteNoteTag="deleteNoteTag"
      @openCollabMenu="openCollabMenu"
      @syncCollabList="updateCollaboratorsList"
      @syncNoteColor="syncNoteColorFromWebSocket"
      @syncNoteName="syncNoteNameFromWebSocket"
      @syncTags="syncTagsFromWebSocket"
      @updateCollabNoteContent="updateNoteContent"
      @updateNoteContent="updateNoteContent"
      @updateNoteTags="updateNoteTags"
    />
    <div v-else-if="!isMobile" class="note-placeholder">
      <span>Choose any note</span>
    </div>
    <NoteCollaborators
      v-if="(!isMobile || isMobileCollabMenu) && collaboratorsNote && collaboratorsNote.collaborators.length > 0"
      :collaboratorsNote="collaboratorsNote"
      :isCollaboratorsList="isCollaboratorsList"
      :isMobile="isMobile"
      @addCollaborator="toggleModalNewCollab"
      @closeCollabMenu="openCollabMenu"
      @deleteCollaborator="deleteCollaborator"
      @hideMenu="isCollaboratorsList = !isCollaboratorsList"
    />
  </div>
  <teleport to="body">
    <ModalNewCollab
      v-if="isModalNewCollab"
      @addCollaborator="addCollaborator"
      @close="toggleModalNewCollab"
    />
  </teleport>
</template>

<style lang="scss">


.page {
  display: grid;
  width: 100svw;
  height: 100svh;
  grid-template-columns: var(--size-grid-columns) 1fr;
  background-color: rgb(var(--color-bg-secondary));
  transition: .2s;

  .note-placeholder {
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 30px;
  }
}

.grid-with-collaborators {
  //grid-template-columns: var(--size-grid-columns) 1fr var(--size-grid-columns-collaborators-page);
  grid-template-columns: var(--size-grid-columns) 1fr auto;
}

.short-page {
  grid-template-columns: var(--short-size-grid-columns) 1fr auto;
  transition: .2s;
}

.mobile-page {
  display: flex;
}

.divider-right {
  border-right: var(--border-side);
}

.icon-stroke {
  path {
    stroke: rgb(var(--color-svg));
  }
}

@media (max-width: 1200px) {
  .page {
    grid-template-columns: calc(var(--size-grid-columns) / 1.5) 1fr auto;
  }
}

@media (max-width: 700px) {
  .page {
    display: flex;
  }
}
</style>