<script lang="ts" setup>
import allNotesIcon from '@src/assets/icons/all-notes.svg'
import trashIcon from '@src/assets/icons/trash.svg'
import settingsIcon from '@src/assets/icons/settings.svg'
import themeIcon from '@src/assets/icons/theme.svg'
import ModalAccountSettings from "@src/components/modal windows/ModalAccountSettings.vue";
import BtnWrapper from "@src/components/wrappers/BtnWrapper.vue";
import type { InterfaceSettingsDto } from "@src/models/InterfaceSettingsDto.ts";
import type { InterfaceUserTags } from "@src/models/InterfaceTagDto.ts";
import { ref } from "vue";

const emit = defineEmits<{
  // (e: 'changeTheme', value: InterfaceSettingsDto): void
  (e: 'changeTheme'): void
  (e: 'updateUserSettings', value: InterfaceSettingsDto): void
  (e: 'closeMenu'): void
  (e: 'chooseNotesByTag', value: InterfaceUserTags): void
}>()
const props = defineProps<{
  tags: InterfaceUserTags[],
  userSettings: InterfaceSettingsDto
}>()
const isModal = ref(false)

const toggleModal = () => {
  isModal.value = !isModal.value;

  if (!isModal.value) {
    emit('closeMenu')
  }
}

function updateUserSettings(settings: InterfaceSettingsDto): void {
  emit("updateUserSettings", settings);
}

function selectTag(tag: InterfaceUserTags) {
  emit('chooseNotesByTag', tag);
  emit('closeMenu')
}

function changeTheme() {
  // const newTheme = props.userSettings.theme === 2 ? 3 : 2;
  // if(props.userSettings.theme)
  // emit('changeTheme', { ...props.userSettings, theme: props.userSettings.theme });
  emit('changeTheme');
}
</script>


<template>
  <div
    v-show="!isModal"
    class="menu-page"
    @click.self="emit('closeMenu') "
  >
    <div class="menu-bar">
      <nav class="nav-group first-group">
        <div class="nav-item">
          <BtnWrapper class="header-btn">
            <allNotesIcon class="svg-icon icon-stroke" />
            <span class="text">
              All notes
            </span>
          </BtnWrapper>
        </div>
        <div class="nav-item">
          <BtnWrapper class="header-btn">
            <trashIcon class="svg-icon icon-stroke" />
            <span class="text">
              Trash
            </span>
          </BtnWrapper>
        </div>
        <div class="nav-item">
          <BtnWrapper class="header-btn" @click="changeTheme">
            <themeIcon class="svg-icon icon-stroke" />
            <span class="text">
              Theme
            </span>
          </BtnWrapper>
        </div>

        <div class="nav-item">
          <BtnWrapper class="header-btn" @click="toggleModal">
            <settingsIcon class="svg-icon icon-stroke" />
            <span class="text">
              Settings
            </span>
          </BtnWrapper>
        </div>
      </nav>
      <nav class="nav-group middle-group">
        <span class="nav-item">Tags</span>
        <div
          v-for="tag in tags"
          :key="tag.id"
          class="tag"
          @click="selectTag(tag)"
        >
          {{ tag.name }}
        </div>
      </nav>
      <nav class="nav-group last-group">
        <div class="nav-item">
          Keyboard Shortcuts
        </div>
        <a class="nav-item" href="https://github.com/qwizzit/NoteShare">
          About
        </a>
      </nav>
    </div>
    <teleport to="body">
      <ModalAccountSettings
        v-if="isModal"
        @close="toggleModal"
        @updateUserSettings="updateUserSettings"
      />
    </teleport>
  </div>
</template>


<style lang="scss">
.header-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  background: unset;
  border: none;
  cursor: pointer;
  width: auto;
  height: auto;
}

.menu-page {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 7;
  background: rgba(var(--color-bg-main), 0.5);
  width: 100svw;
  height: 100svh;

  .text {
    font-size: 15px;
  }


  .svg-icon {
    width: 25px;
    height: 25px;
  }

  hr {
    margin: unset;
    width: 100%;
    border-bottom: var(--border-side);
  }

  .menu-bar {
    background: rgb(var(--color-bg-secondary));
    display: flex;
    flex-direction: column;
    width: 330px;
    height: 100svh;


    .nav-group {
      display: flex;
      flex-direction: column;
      width: 100%;

      .tag {
        margin-left: 16px;
        padding: 12px 8px;
        display: flex;
        cursor: pointer;
        align-items: center;
        border-bottom: var(--border-side);
      }

      .nav-item {
        display: flex;
        align-items: center;
        padding: 15px;
        width: 100%;
        border-top: var(--border-side);
        border-bottom: var(--border-side);
        margin-top: -1px;
      }

      .nav-item:first-child {
        margin-top: 0;
      }
    }

    .first-group {
      margin-top: 40px;
    }

    .middle-group {
      height: 100%;
      overflow-x: hidden;
      overflow-y: auto;
    }
  }
}
</style>