<script lang="ts" setup>
import CollaboratorItem from "@src/components/notes/Collaborators/CollaboratorItem.vue";
import BtnWrapper from "@src/components/wrappers/BtnWrapper.vue";
import HeaderWrapper from "@src/components/wrappers/HeaderWrapper.vue";
import sidebar from '@src/assets/icons/sidebar-right.svg'
import search from '@src/assets/icons/search.svg'
import newCollaboratorIcon from '@src/assets/icons/new-note.svg'
import { MOBILE_BREAKPOINT } from "@src/composition/constants.ts";
import type { InterfaceColaborators } from "@src/models/InterfaceColaborators.ts";
import leftArrow from '@src/assets/icons/left-arrow.svg'
import { provideSSRWidth, useWindowSize } from "@vueuse/core";
import { computed, onMounted, ref, unref, watch } from "vue";

const emit = defineEmits<{
  (e: 'hideMenu'): void;
  (e: 'addCollaborator'): void;
  (e: 'closeCollabMenu'): void;
  (e: 'deleteCollaborator', noteId: number): void;
}>()
const props = defineProps<{
  collaboratorsNote: InterfaceColaborators,
  isMobile: boolean,
  isCollaboratorsList: boolean,
}>()
const { width } = useWindowSize()

const currentUserId = ref<number>();
const searchFilter = ref('');
const openedMenuId = ref<number | null>(null);
const collabPage = ref<HTMLDivElement | null>(null);
const maxWidth = ref<number>(250);

const filteredCollabers = computed(() => {
  return props.collaboratorsNote.collaborators.filter(user => user.email.includes(searchFilter.value))
})
const styleCollabSidebar = computed(() => ({
  // maxWidth: p
  minWidth: props.isCollaboratorsList ? 'auto' : `${ maxWidth.value }px`,
}))
const arrowStyle = computed(() => ({
  display: unref(width) > MOBILE_BREAKPOINT ? "none" : "block",
}))

function addCollaborator() {
  emit('addCollaborator');
}

function deleteCollaborator(userId: number) {
  emit('deleteCollaborator', userId);
}

watch(() => collabPage.value, () => {
  if (collabPage.value) {
    maxWidth.value = Math.max(maxWidth.value, collabPage.value.offsetWidth);
  }
})
onMounted(() => {
  const id = localStorage.getItem('token');
  if (id) {
    currentUserId.value = parseInt(id);
  }
})
</script>

<template>
  <aside
    ref="collabPage"
    class="collaborators-page"
    :class="{'mobile-page-collabers' : isMobile}"
    :style="styleCollabSidebar"
  >
    <HeaderWrapper>
      <template #left-icons>
        <BtnWrapper
          v-if="!isCollaboratorsList && isMobile"
          class="header-btn"
          :style="arrowStyle"
        >
          <leftArrow
            class="svg-icon icon-stroke"
            @click="emit('closeCollabMenu')"
          />
        </BtnWrapper>
        <BtnWrapper
          v-else-if="!isMobile"
          class="header-btn"
          @click="emit('hideMenu')"
        >
          <sidebar class="svg-icon icon-stroke" />
        </BtnWrapper>
      </template>
      <template v-if="!isCollaboratorsList" #default>
        <span class="text">Collaborators</span>
      </template>
      <template v-if="!isCollaboratorsList" #right-icons>
        <BtnWrapper class="header-btn">
          <newCollaboratorIcon
            class="svg-icon icon-stroke"
            @click="addCollaborator"
          />
        </BtnWrapper>
      </template>
    </HeaderWrapper>
    <nav v-if="!isCollaboratorsList" class="collaborators">
      <div class="searching-user">
        <search class="svg-icon icon-stroke" />
        <input
          v-model="searchFilter"
          class="search-user"
          placeholder="Search all users..."
          type="search"
        >
      </div>
      <div class="collaborators-container">
        <div class="collab-role">
          <span class="role">Owner</span>
          <div class="collab">
            <CollaboratorItem
              :isCurrentUser="currentUserId === collaboratorsNote.owner.id"
              :isLast="true"
              :isOwner="true"
              :menuOpen="openedMenuId === collaboratorsNote.owner.id"
              :user="collaboratorsNote.owner"
              @deleteCollaborator="deleteCollaborator"
              @triggerMenu="openedMenuId = (openedMenuId === collaboratorsNote.owner.id) ? null : collaboratorsNote.owner.id"
            />
          </div>
        </div>
        <div class="collab-role">
          <span class="role">Collabers</span>
          <div class="collab">
            <CollaboratorItem
              v-for="(user, index) in filteredCollabers"
              :key="user.id"
              :isCurrentUser="currentUserId === user.id"
              :isLast="index === collaboratorsNote.collaborators.length - 1"
              :menuOpen="openedMenuId === user.id"
              :user="user"
              @deleteCollaborator="deleteCollaborator"
              @triggerMenu="openedMenuId = (openedMenuId === user.id) ? null : user.id"
            />
          </div>
        </div>
      </div>
    </nav>
  </aside>
</template>

<style lang="scss">
.header-btn {
  width: auto;
}

.text {
  cursor: pointer;
}


.collaborators-page {
  border-left: var(--border-side);
  transition: .1s;

  .svg-icon {
    width: 30px;
    height: 30px;
  }

  .collaborators {

    .searching-user {
      display: flex;
      padding: 0 10px;
      height: var(--height-searching-notes);
      align-items: center;
      gap: 5px;
      border-bottom: var(--border-side);

      .svg-icon {
        width: 25px;
        height: 25px;
      }

      .search-user {
        width: 100%;
        height: 25px;
        background: none;
        border: none;
        outline: none;
      }
    }

    .collaborators-container {

      .collab-role {
        display: flex;
        border-bottom: var(--border-side);

        .role {
          padding: 15px 5px;
          text-align: center;
          min-width: 100px;
          border-right: var(--border-side);
        }

        .collab {
          width: 100%;
        }
      }
    }
  }
}

.mobile-page-collabers {
  width: 100%;
  max-width: none !important;
}

@media (max-width: 1200px) {
  .collaborators-page {
    max-width: 150px;
    word-break: break-all;
  }
}
</style>