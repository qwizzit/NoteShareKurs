<script lang="ts" setup>
import api from "@src/Api/AccessApi.js";
import pinIcon from '@src/assets/icons/pin.svg'
import ellipsis from '@src/assets/icons/ellipsis.svg'
import BtnWrapper from "@src/components/wrappers/BtnWrapper.vue";
import { MOBILE_BREAKPOINT } from "@src/composition/constants.js";
import type { InterfaceNoteDto } from "@src/models/InterfaceNoteDto.js";
import { computed, type CSSProperties, inject, nextTick, ref, unref, watch } from "vue";
import { useDebounceFn, useWindowSize } from "@vueuse/core";

const emit = defineEmits<{
  (e: 'triggerMenu'): void
  (e: 'updateColor', value: { noteId: typeof props.note.id, color: typeof color.value }): void;
  (e: 'deleteNote', id: number): void;
}>()
const props = defineProps<{
  note: InterfaceNoteDto,
  menuOpen: boolean,
  displayNoteName?: number,
  selectedNoteId: number | null
  isShortStyle: boolean;
}>()

const { width } = useWindowSize();

const inputRef = ref<HTMLInputElement>();

const noteName = ref(props.note.title)
const isNoteRename = ref(false);
const editName = ref('');

const noteShortName = computed(() => {
  const plainText = props.note?.content.replace(/<[^>]*>/g, '') || '';

  const letters = plainText
    .trim()
    .split(/\s+/)
    .slice(0, 3)
    .filter(word => word.length > 0)
    .map(word => word[0])
    .join('') || '';

  if (letters === "<" || letters.length === 0) {
    return 'N/A'
  }
  return letters;
});
const triggerRef = ref<HTMLElement>();
const color = computed(() => props.note.color);
const menuRef = ref<HTMLDivElement>();

const styleAdditionalNoteName = computed(() => ({
  display: props.displayNoteName === 2 ? "inline-block" : "none",
  fontSize: '12px'
}))
const styleMenu = computed(() => {
  const el = unref(triggerRef);

  if (el && props.menuOpen) {
    const rect = el.getBoundingClientRect();

    if (unref(width) > MOBILE_BREAKPOINT) {
      return {
        position: 'absolute',
        left: `${ rect.left + 45 }px`,
        right: 'unset',
        top: `${ rect.top - 10 }px`,
        display: 'flex'
      };
    }

    return {
      position: 'absolute',
      left: `unset`,
      right: `35px`,
      top: `${ rect.top - 15 }px`,
      display: 'flex'
    };
  }
  return { display: 'none' };
});
const styleBorderLeft = computed(() => ({
  borderLeft: props.isShortStyle ? 'unset' : `8px solid ${ color.value }`,
}))
const styleBoxShadow = computed(() => ({
  boxShadow: props.isShortStyle ? `0 0 4px ${ unref(color) }` : 'unset',
}))

function startRename() {
  isNoteRename.value = true
  editName.value = noteName.value

  nextTick(() => {
    unref(inputRef)?.focus()
    unref(inputRef)?.select()
  })
}

async function commitRename() {
  const newName = unref(editName).trim();

  if (newName) {
    noteName.value = newName

    // move to some api file
    await api.patch(`/notes/${ props.note.id }`, { title: newName })
      .then(res => {
        inject('updateNote', res.data);
      })
  }
  isNoteRename.value = false;
}

const handleClickOutside = (event: MouseEvent) => {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
    emit('triggerMenu')
  }
};

// usetoggle
function cancelRename() {
  isNoteRename.value = false
}

function openMenu() {
  emit('triggerMenu')
}

function updateColor(color: string) {
  emit('updateColor', {
    color,
    noteId: props.note.id,
  })
}

watch(() => props.menuOpen, () => {
  if (props.menuOpen) {
    window.addEventListener('click', handleClickOutside);
  } else {
    window.removeEventListener('click', handleClickOutside);
  }
})

watch(() => isNoteRename.value, () => {
  if (unref(isNoteRename)) {
    unref(inputRef)?.focus()
  }
});

// watch(() => props.note.title, (newTitle) => {
//   noteName.value = newTitle;
// });
//
// watch(() => props.note.color, (newColor) => {
//   color.value = newColor;
// });
watch(color, useDebounceFn(() => {
  emit('updateColor', { noteId: props.note.id, color: color.value })
}, 500))
</script>

<template>
  <div
    class="note-item"
    :class="{'note-item-short': isShortStyle, 'active-note': selectedNoteId === note.id}"
    :style="styleBorderLeft"
    @click.middle="emit('deleteNote', note.id)"
  >
    <BtnWrapper v-if="!isShortStyle" class="pin-btn">
      <pinIcon class="svg-icon icon-stroke" />
    </BtnWrapper>
    <div
      class="note-name-container"
      :class="{'note-name-short': isShortStyle}"
      :style="styleBoxShadow"
    >
      <div v-if="!isNoteRename && !isShortStyle" class="note-name">
        <span>{{ noteName }}</span>
        <span :style="styleAdditionalNoteName">{{
          note.content.replace(/<[^>]*>/g, '')
            .slice(0, 10)
        }}</span>
      </div>

      <input
        v-else-if="isNoteRename && !isShortStyle"
        ref="inputRef"
        v-model="editName"
        class="note-name-input"
        maxlength="30"
        @blur="cancelRename"
        @click.stop
        @keyup.enter="commitRename"
        @keyup.esc="cancelRename"
      >
      <span v-else>
        {{ noteShortName }}
      </span>
    </div>
    <details
      v-if="!isShortStyle"
      class="note-menu"
      @click.stop
    >
      <summary class="menu-trigger">
        <span ref="triggerRef" @click="openMenu">
          <ellipsis
            class="svg-icon icon-stroke"
          />
        </span>
      </summary>
      <teleport to="body">
        <ul
          v-if="menuOpen"
          ref="menuRef"
          class="menu-list"
          :style="styleMenu"
        >
          <li class="menu-item" @click="startRename">
            Rename
          </li>
          <li class="menu-item" @click="emit('deleteNote', note.id)">
            Delete
          </li>
          <li class="menu-item">
            <label for="colorPicker">Change color: </label>
            <input
              id="colorPicker"
              name="colorPicker"
              type="color"
              :value="color"
              @input="updateColor($event.target!.value)"
            >
          </li>
          <li class="menu-item">
            In the archive
          </li>
        </ul>
      </teleport>
    </details>
  </div>
</template>


<style lang="scss">
.pin-btn {
  width: auto;
}

.menu-list {
  display: flex;
  flex-direction: column;
  position: absolute;
  background: rgb(var(--color-bg-main));
  padding: var(--padding-left-notes-navigation);
  gap: 30px;
  z-index: 2;
  list-style-type: none;
  border-radius: 6px;

  .menu-item {
    cursor: pointer;
  }
}

.active-note {
  background: rgb(var(--color-active-item));
}

.note-item {
  display: flex;
  justify-content: center;
  align-items: center;
  border-bottom: var(--border-side);
  padding: var(--padding-left-notes-navigation) 10px;
  gap: 5px;
  cursor: pointer;

  .svg-icon {
    width: 20px;
    height: 20px;
  }

  .note-name-container {
    background: none;
    padding: 0 10px;
    border: none;
    width: 100%;

    .note-name {
      display: flex;
      max-width: 200px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex-direction: column;
    }

    .note-name-input {
      background: none;
      font-size: medium;
      border: none;
      outline: none;
    }
  }

  summary::marker {
    content: ''
  }

  li {
    cursor: pointer;
  }
}

.note-item-short {
  border-bottom: none;
  width: 100%;
  padding: calc(var(--padding-left-notes-navigation) / 2);

  .note-name-short {
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background-color: rgb(var(--color-short-style-notes));
    width: calc(var(--short-size-grid-columns) - var(--padding-left-notes-navigation));
    height: calc(var(--short-size-grid-columns) - var(--padding-left-notes-navigation));

  }
}

@media (max-width: 1200px) {
  .note-item {
    .note-name-container {
      .note-name {
        max-width: 120px;
        overflow-x: auto;
      }

      .note-name-input {
        max-width: 120px;
      }
    }
  }
}

@media (max-width: 700px) {
  .note-item {
    .note-name-container {
      .note-name {
        max-width: 250px;
        overflow-x: auto;
      }


    }
  }
}
</style>
