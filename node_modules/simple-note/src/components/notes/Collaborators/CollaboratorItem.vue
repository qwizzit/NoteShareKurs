<script lang="ts" setup>
import { MOBILE_BREAKPOINT } from "@src/composition/constants.ts";
import type { InterfaceShortUserDto } from "@src/models/InterfaceUserDto.ts";
import ellipsis from '@src/assets/icons/ellipsis.svg'
import { useWindowSize } from "@vueuse/core";
import { computed, type CSSProperties, ref, unref, watch } from "vue";

const emit = defineEmits<{
  (e: 'triggerMenu'): void;
  (e: 'deleteCollaborator', value: typeof props.user.id): void;
}>()
const props = defineProps<{
  isCurrentUser: boolean,
  isOwner?: boolean,
  menuOpen: boolean,
  isLast: boolean,
  user: InterfaceShortUserDto,
}>()
const triggerRef = ref<HTMLElement>();
const menuRef = ref<HTMLDivElement>();
const { width } = useWindowSize();

function openMenu() {
  emit('triggerMenu')
}

const handleClickOutside = (event: MouseEvent) => {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
    emit('triggerMenu')
  }
};
const styleMenu = computed((): CSSProperties => {
  const el = unref(triggerRef);

  if (el && props.menuOpen) {
    const rect = el.getBoundingClientRect();

    if (unref(width) > MOBILE_BREAKPOINT) {
      return {
        position: 'absolute',
        left: `${ rect.left - 150 }px`,
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

watch(() => props.menuOpen, () => {
  if (props.menuOpen) {
    window.addEventListener('click', handleClickOutside);
  } else {
    window.removeEventListener('click', handleClickOutside);
  }
})
</script>

<template>
  <div
    class="collaborator-item"
    :class="{'isBorderBottom' : isLast, 'current-user': isCurrentUser}"
    :title="isCurrentUser ? 'You' : 'Collaber'"
  >
    <div class="collaborator-name-container">
      {{ user.email }}
    </div>
    <details
      class="collab-menu"
      :style="{ visibility: isOwner ? 'hidden' : 'visible'}"
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
          <li class="menu-item" @click="emit('deleteCollaborator', user.id)">
            Delete
          </li>
          <li class="menu-item">
            Change role
          </li>
        </ul>
      </teleport>
    </details>
  </div>
</template>

<style lang="scss">
.current-user {
  background: rgb(var(--color-active-item));
}

.collaborator-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: var(--border-side);
  padding: var(--padding-left-notes-navigation) 10px;
  gap: 5px;

  .svg-icon {
    width: 20px;
    height: 20px;
    cursor: pointer;
  }

  .collaborator-name-container {
    background: none;
    padding: 0 10px;
    border: none;
    width: 100%;
    max-width: 300px;
  }

  .collab-menu {

  }

  summary::marker {
    content: ''
  }

  li {
    cursor: pointer;
  }
}

.isBorderBottom {
  border-bottom: none;
}
</style>