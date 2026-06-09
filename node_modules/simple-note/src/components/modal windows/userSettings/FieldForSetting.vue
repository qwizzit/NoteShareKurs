<script lang="ts" setup>
import SelectionInput from "@src/components/modal windows/userSettings/SelectionInput.vue";

const model = defineModel<number | boolean>();

const emit = defineEmits<{
  (e: 'update'): void
}>()

const props = defineProps<{
  options: {
    id: number,
    label: string
  }[],
  title: string,
  type: string
  isCheckBox: boolean,
}>()
</script>

<template>
  <div class="field">
    <span>{{ title }}</span>
    <div class="selection-fields">
      <div v-if="isCheckBox" class="select-setting">
        <label :for="type">{{ options[0]?.label }}</label>
        <input
          :id="type"
          v-model="model"
          type="checkbox"
          @change="emit('update')"
        >
      </div>

      <template v-else>
        <SelectionInput
          v-for="item in options"
          :key="item.id"
          v-model="model"
          :name="type"
          :section="item.id"
          :type="type"
          @click="emit('update')"
        >
          {{ item.label }}
        </SelectionInput>
      </template>
    </div>
  </div>
</template>

