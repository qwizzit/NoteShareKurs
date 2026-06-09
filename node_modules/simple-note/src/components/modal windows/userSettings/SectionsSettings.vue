<script lang="ts" setup>
import api, { AccessApi } from "@src/Api/AccessApi.ts";
import ExportNotes from "@src/components/modal windows/userSettings/ExportNotes.vue";
import FieldForSetting from "@src/components/modal windows/userSettings/FieldForSetting.vue";
import ImportNotes from "@src/components/modal windows/userSettings/ImportNotes.vue";
import BtnWrapper from "@src/components/wrappers/BtnWrapper.vue";
import type { InterfaceSettingsDto } from "@src/models/InterfaceSettingsDto.ts";
import type { InterfaceUserDto } from "@src/models/InterfaceUserDto.ts";
import { useDebounceFn } from "@vueuse/core";
import axios from "axios";
import { ref } from "vue";

const emit = defineEmits<{
  (e: 'updateUserSettings', value: InterfaceSettingsDto): void,
}>();
const props = defineProps<{
  selectedSection: number;
  user: InterfaceUserDto
}>();
const settingGroups = [
  {
    name: 'note_display',
    label: 'Note display',
    type: 'display',
    isCheckBox: false,
    options: [
      { id: 1, label: 'Compfy' },
      { id: 2, label: 'Condensed' },
    ]
  },
  {
    name: 'note_sort',
    label: 'Sort by',
    type: 'note-sort',
    isCheckBox: false,
    options: [
      { id: 1, label: 'Name: A-Z' },
      { id: 2, label: 'Name: Z-A' },
      { id: 3, label: 'Creation date descending' },
      { id: 4, label: 'Creation date ascending' },
      { id: 5, label: 'Update date descending' },
      { id: 6, label: 'Update date ascending' }
    ]
  },
  {
    name: 'tags_sort',
    label: 'Tags',
    type: 'tags-sort',
    isCheckBox: true,
    options: [
      { id: 1, label: 'Alphabetically sort' },
    ]
  },
  {
    name: 'theme',
    label: 'Theme',
    type: 'theme',
    isCheckBox: false,
    options: [
      { id: 1, label: 'System' },
      { id: 2, label: 'Dark' },
      { id: 3, label: 'White' }
    ]
  }
]

const userSettings = ref<InterfaceSettingsDto>({
  note_display: props.user.settings.note_display,
  note_sort: props.user.settings.note_sort,
  tags_sort: props.user.settings.tags_sort,
  theme: props.user.settings.theme
})
const updateSettingsDebounced = useDebounceFn(async() => {
  await updateSettings();
}, 1000);

const onInputClick = () => {
  updateSettingsDebounced();
}

async function updateSettings() {
  if (JSON.stringify(userSettings.value) !== JSON.stringify(props.user.settings)) {
    await api.patch(`/users/${ props.user.id }/settings`, userSettings.value)
      .then(res => {

        // fix this. Use Pina https://pinia.vuejs.org/
        emit("updateUserSettings", res.data)
      })
  }
}


</script>

<template>
  <div v-if="selectedSection === 1" class="account">
    <div class="field">
      <span class="text-in-field">Email</span>
      <input
        class="user-setting-input"
        placeholder="Change email..."
        type="email"
        :disabled="true"
        :value="user.email"
      >
    </div>
    <div class="field">
      <router-link :to="{name: 'Settings'}">
        Edit account
      </router-link>
    </div>
    <div class="field">
      <BtnWrapper class="btn-color" @click="AccessApi.removeToken()">
        LogOut
      </BtnWrapper>
    </div>
  </div>
  <div v-else-if="selectedSection === 2" class="account">
    <FieldForSetting
      v-for="group in settingGroups"
      :key="group.name"
      v-model="userSettings[group.name as keyof InterfaceSettingsDto]"
      :isCheckBox="group.isCheckBox"
      :options="group.options"
      :title="group.label"
      :type="group.type"
      @update="onInputClick"
    />
  </div>
  <div v-else-if="selectedSection === 3" class="account">
    <span class="text-before-field">Tools</span>
    <div class="field">
      <ImportNotes />
      <ExportNotes :user="user" />
    </div>
  </div>
</template>

<style lang="scss">
.btn-color {
  background: rgb(var(--color-btn));
}

.account {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 15px;
  gap: 20px;
  width: 100%;
  height: 100%;
  max-height: 500px;
  overflow-y: auto;

  .text-before-field {
    max-width: var(--max-width-setting);
    width: 100%;
  }

  .field {
    display: flex;
    flex-direction: column;
    max-width: var(--max-width-setting);
    gap: 5px;
    width: 100%;


    .user-setting-input {
      background: rgb(var(--color-bg-main));
      border: none;
      padding: 10px;
      border-radius: 8px;
    }

    .selection-fields {
      display: flex;
      flex-direction: column;
    }

    //.btn {
    //  width: 100%;
    //  height: 40px;
    //  border-radius: 8px;
    //  background: rgb(var(--color-btn));
    //}
  }
}
</style>