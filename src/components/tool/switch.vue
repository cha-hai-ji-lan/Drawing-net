<template>
  <div class="toggle-switch" :class="{ 'active': modelValue }" @click="toggle">
    <div class="toggle-switch-slider">
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  leftLabel: {
    type: String,
    default: '关'
  },
  rightLabel: {
    type: String,
    default: '开'
  }
});

const emit = defineEmits(['update:modelValue']);

const toggle = () => {
  emit('update:modelValue', !props.modelValue);
};
</script>

<style scoped>
.toggle-switch {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  user-select: none;
  cursor: pointer;
}

.toggle-switch-slider {
  text-align: center;
  position: relative;
  width: 4vw;
  height: 2vw;
  background-color: rgba(195, 193, 193, 0.75);
  border-radius: 2.5vw;
  transition: background-color 0.3s ease;
  /* margin-bottom: 0.8vw; */
  margin: auto 0;
}

.toggle-switch-slider::before {
  content: '';
  position: absolute;
  width: 1.6vw;
  height: 1.6vw;
  border-radius: 50%;
  background-color: white;
  top: 0.2vw;
  left: 0.2vw;
  transition: transform 0.3s ease;
  box-shadow: 0 0.2vw 0.4vw rgba(0, 0, 0, 0.2);
  margin: auto 0;
}

.toggle-switch.active .toggle-switch-slider {
  background-color: #42b983;
}

.toggle-switch.active .toggle-switch-slider::before {
  transform: translateX(2vw);
}

.toggle-switch-labels {
  display: flex;
  justify-content: space-between;
  width: 100%;
  font-size: 1vw;
}
.toggle-switch-thumb {
  margin: 0 auto;
}

.toggle-switch-label {
  font-size: 1vw;
  color: #999;
  transition: color 0.3s ease;
  padding: 0 0.4vw;
}

.toggle-switch-label.active {
  color: #333;
  font-weight: bold;
}

.toggle-switch-label.left {
  text-align: left;
}

.toggle-switch-label.right {
  text-align: right;
}
</style>