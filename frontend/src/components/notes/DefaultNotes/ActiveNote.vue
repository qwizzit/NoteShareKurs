<script lang="ts" setup>
import api from "@src/Api/AccessApi.ts";
import sidebar from '@src/assets/icons/sidebar-left.svg'
import checklist from '@src/assets/icons/checklist.svg'
import info from '@src/assets/icons/info.svg'
import newCollab from '@src/assets/icons/user-plus.svg'
import leftArrow from '@src/assets/icons/left-arrow.svg'
import ModalNoteInfo from "@src/components/modal windows/ModalNoteInfo.vue";
import BtnWrapper from "@src/components/wrappers/BtnWrapper.vue";
import HeaderWrapper from "@src/components/wrappers/HeaderWrapper.vue";
import { MOBILE_BREAKPOINT } from "@src/composition/constants.js";
import type { InterfaceColaborators } from "@src/models/InterfaceColaborators.ts";
import type { Note } from "@src/models/Note.js";
import type { Tag } from "@src/models/Tag.ts";
import { useDebounceFn, useWindowSize } from "@vueuse/core";
import { instanceToInstance } from "class-transformer";
import { computed, nextTick, onBeforeUnmount, onMounted, ref, unref, watch } from "vue";
import DOMPurify from "dompurify";

const emit = defineEmits<{
  (e: 'updateNoteContent', value: {
    id: typeof props.note.id,
    content: typeof props.note.content
  }, isNoteClosed: boolean): void
  (e: 'update:note', v: typeof props.note): void
  (e: 'add:tag', v: typeof props.note.tags[number]): void
  // (e: 'updateNoteTags', value: { id: typeof props.note.id, tag: string }): void
  (e: 'syncCollabList', noteId: number): void
  // (e: 'syncNoteColor', note: { id: number, color: string }): void
  // (e: 'syncTags', note: { id: number, tags: Tag[] }): void
  // (e: 'syncNoteName', note: { id: number, name: string }): void
  (e: 'deleteNoteFromList', noteId: number): void
  (e: 'deleteNoteTag', tagId: number, noteId: number): void
  (e: 'addCollaborator'): void,
  (e: 'closeNote'): void
  (e: 'changeListStyle'): void
  (e: 'openCollabMenu'): void
}>()

const props = defineProps<{
  note: Note;
  isMobile: boolean;
  isNoteSelected: boolean;
  loading: boolean;
  collaboratorsNote?: InterfaceColaborators
}>()
const contentRef = ref<HTMLDivElement | null>(null);

const tagInput = ref('');
const { width } = useWindowSize()
const isModalNoteInfo = ref(false)

const socket = ref<WebSocket>();

const toggleModalNoteInfo = () => {
  isModalNoteInfo.value = !isModalNoteInfo.value;

  if (contentRef.value) {
    const content = DOMPurify.sanitize(contentRef.value.innerHTML);
    emit('updateNoteContent', { id: props.note.id, content: content }, true);
  }

  if (!isModalNoteInfo.value && contentRef.value) {
    placeCaretAtEnd(contentRef.value);
  }
}

const debouncedEmitUpdate = useDebounceFn((content: string) => {
  emit('updateNoteContent', { id: props.note.id, content }, false);
}, 500);

const onInput = () => {
  if (!contentRef.value) {
    return;
  }

  const content = DOMPurify.sanitize(contentRef.value.innerHTML);

  debouncedEmitUpdate(content);

  if (socket.value && socket.value.readyState === WebSocket.OPEN) {
    socket.value.send(JSON.stringify({ type: 'text_update', content: content }));
  }
};

function connectWebSocket(noteId: number) {
  if (socket.value) {
    socket.value.close();
  }
  socket.value = new WebSocket(`${ api.defaults.baseURL?.replace(/^http/, 'ws') }/ws/notes/${ noteId }`);

  socket.value.onmessage = (event) => {
    if (!contentRef.value) {
      return;
    }
    const data = JSON.parse(event.data);

    if (data.type === 'collaborators_update') {
      emit('syncCollabList', props.note.id);
      return;
    }

    if (data.type === 'text_update') {
      if (contentRef.value.innerHTML !== data.content) {
        contentRef.value.innerHTML = data.content;
        placeCaretAtEnd(contentRef.value);
        return;
      }
    }

    if (data.type === 'color_update') {
      emit('syncNoteColor', { id: props.note.id, color: data.color });
      return;
    }

    if (data.type === 'rename_update') {
      emit('syncNoteName', { id: props.note.id, name: data.name });
      return;
    }

    if (data.type == 'tags_update') {
      emit('syncTags', { id: props.note.id, tags: data.tags });
      return;
    }
  };
}

const placeCaretAtEnd = (el: HTMLDivElement) => {
  el.focus();

  if (typeof window.getSelection != "undefined"
    && typeof document.createRange != "undefined") {
    const range = document.createRange();
    range.selectNodeContents(el);
    range.collapse(false);
    const sel = window.getSelection();
    if (sel !== null) {
      sel.removeAllRanges();
      sel.addRange(range);
    }
  }
};

function isCanBeTag() {
  const tag = unref(tagInput).replace(" ", "")
  if (tag.length == 0) {
    return
  }
  if (props.note.tags.some(t => t.name === tag)) {
    return;
  }
  api.patch(`/notes/${ props.note.id }`, { tag })
    .then(({ data }: { data: typeof props.note }) => {
      const newInstance = instanceToInstance(props.note)
      newInstance.updated_at = data.updated_at;
      newInstance.tags = [ ...new Set(data.tags) ];
      emit('update:note', newInstance);
      emit('add:tag', [ ...data.tags ].pop() as Tag)
    })
    .finally(() => {
      tagInput.value = "";
    })
}

function addCollaborator() {
  emit("addCollaborator");
}

const arrowStyle = computed(() => ({
  display: unref(width) > MOBILE_BREAKPOINT ? "none" : "block",
}))
const sideBarStyle = computed(() => ({
  display: unref(width) < MOBILE_BREAKPOINT ? "none" : "block",
}))

watch(() => props.note.id, (newNoteId) => {
  if (newNoteId) {
    connectWebSocket(newNoteId);
  }
}, { immediate: true });
// watch(() => props.collaboratorsNote, () => {
//   console.log(1)
//   const id = localStorage.getItem("token");
//   if (props.collaboratorsNote) {
//     console.log(2)
//     if (id && socket.value && parseInt(id) !== props.collaboratorsNote.owner.id) {
//       console.log(3)
//       const isCollaborator = props.collaboratorsNote.collaborators.find(collaber => collaber.id === parseInt(id));
//       if (!isCollaborator?.id && props.collaboratorsNote) {
//         console.log(4)
//         socket.value.close();
//         emit('deleteNoteFromList', props.note.id);
//         emit('closeNote');
//         alert("Доступ к этой заметке был ограничен");
//       }
//     }
//   }
// }, { deep: true })
onMounted(async() => {
  await nextTick();
  if (contentRef.value) {
    placeCaretAtEnd(contentRef.value);
  }
});

onBeforeUnmount(() => {
  if (socket.value) {
    socket.value.close();
  }
  // if (contentRef.value && props.note && props.isNoteSelected) {
  //   const content = DOMPurify.sanitize(contentRef.value.innerHTML);
  //   emit('updateNoteContent', { id: props.note.id, content: content }, true);
  // }
});
</script>

<template>
  <main class="note">
    <HeaderWrapper v-if="props.loading && isNoteSelected">
      <template #left-icons>
        <div class="note-bar">
          <BtnWrapper :style="arrowStyle">
            <leftArrow
              class="svg-icon icon-stroke"
              @click="emit('closeNote')"
            />
          </BtnWrapper>
          <BtnWrapper :style="sideBarStyle">
            <sidebar
              class="svg-icon icon-stroke"
              @click="emit('changeListStyle')"
            />
          </BtnWrapper>
        </div>
      </template>
      <template #right-icons>
        <div class="note-bar">
          <BtnWrapper>
            <checklist class="svg-icon icon-stroke" />
          </BtnWrapper>
          <BtnWrapper>
            <info class="svg-icon icon-stroke" @click="toggleModalNoteInfo" />
          </BtnWrapper>
          <BtnWrapper v-if="collaboratorsNote?.collaborators.length === 0">
            <newCollab
              class="svg-icon icon-stroke"
              @click="addCollaborator"
            />
          </BtnWrapper>
          <BtnWrapper v-else-if="isMobile">
            <newCollab
              class="svg-icon icon-stroke"
              @click="emit('openCollabMenu')"
            />
          </BtnWrapper>
        </div>
      </template>
    </HeaderWrapper>
    <div v-if="props.loading && isNoteSelected" class="note-info">
      <div
        ref="contentRef"
        class="info"
        contenteditable="true"
        @input="onInput"
        v-html="note?.content"
      />
      <div class="note-tags">
        <div class="tags-container">
          <div
            v-for="tag in note?.tags"
            :key="tag.id"
            class="tag"
            @click="emit('deleteNoteTag', tag.id, props.note.id)"
          >
            {{ tag.name }}
          </div>
        </div>
        <input
          v-model="tagInput"
          class="add-new-tag"
          maxlength="50"
          placeholder="Add new tags..."
          type="text"
          @keyup.enter="isCanBeTag"
          @keyup.space="isCanBeTag"
        >
      </div>
    </div>
    <teleport to="body">
      <ModalNoteInfo
        v-if="isModalNoteInfo"
        :note="note"
        @close="toggleModalNoteInfo"
      />
    </teleport>
  </main>
</template>


<style lang="scss">
.note {
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: rgb(var(--color-bg-secondary));
  width: 100%;
  overflow: hidden;


  .note-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;

    .svg-icon {
      width: 30px;
      height: 30px;
    }
  }

  .note-info {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    overflow: hidden;

    .info {
      width: 100%;
      height: 100%;
      padding: 30px;
      background: unset;
      border: unset;
      outline: unset;
      background: unset;
      overflow-y: auto;
      word-break: break-word;
      white-space: pre-wrap;
      overflow-wrap: break-word;
    }


    .note-tags {
      display: flex;
      align-items: center;
      width: 100%;
      border-top: var(--border-side);

      .tags-container {
        display: flex;
        gap: 10px;
        padding: 10px;
        max-height: 70px;
        min-height: 50px;
        flex-wrap: wrap;
        overflow: auto;
        max-width: 800px;

        .tag {
          background: rgb(var(--color-bg-main));
          border: unset;
          border-radius: 12px;
          cursor: pointer;
          padding: 0 5px;
        }
      }

      .add-new-tag {
        background: none;
        width: 100%;
        padding: 5px var(--padding-left-notes-navigation);
        border: unset;
        outline: unset;
      }
    }
  }
}

@media (max-width: 800px) {
  .note {
    .note-info {
      .note-tags {
        .tags-container {
          max-width: 200px;
        }
      }
    }
  }

}
</style>