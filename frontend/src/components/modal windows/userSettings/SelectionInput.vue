<script lang="ts" setup>

const emit = defineEmits<{
  (e: 'update:modelValue', value: number): void,
  (e: 'click'): void
}>()
const props = defineProps<{
  section: number;
  modelValue: number;
  type: string;
  name: string;
}>()

const onChange = () => {
  emit('update:modelValue', props.section);
  emit('click');
}
</script>

<template>
  <div class="select-setting">
    <label :for="`${props.type}-${props.section}`">
      <slot />
    </label>
    <input
      :id="`${props.type}-${props.section}`"
      type="radio"
      :checked="modelValue === props.section"
      :name="`${name}`"
      :value="props.section"
      @change="onChange"
    >
  </div>
</template>

<style lang="scss">
.select-setting {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 20px;
  border: var(--border-side);
  padding: 5px;
}
</style>