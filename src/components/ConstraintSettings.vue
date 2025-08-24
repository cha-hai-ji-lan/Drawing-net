<template>
    <div class="settings-container" :class="['kid-overlay', {
                dark: themeState.is_dark_mode_theme,
                light: themeState.is_light_mode_theme,
            }]">
        <h3>约束设置</h3>
        <div class="setting-item">
            <label>全局缩放比</label>  
            <div class="control-group">
                <input  v-model="localMainConfig['core-config']['SCALE_RATIO']" type="number" :placeholder="localMainConfig['core-config']['SCALE_RATIO']">
            </div>
        </div>
        <div class="setting-item">
            <label>表格偏移量</label>
            <div class="control-group">
                <input  v-model="localMainConfig['core-config']['TABLE_OFFSET']" type="number" :placeholder="localMainConfig['core-config']['TABLE_OFFSET']">
            </div>
        </div>

        <div class="setting-item">
            <label>水平比例尺</label>
            <div class="control-group">
                <input  v-model="localMainConfig['core-config']['HORIZONTAL_SCALE_BAR']" type="number" :placeholder="localMainConfig['core-config']['HORIZONTAL_SCALE_BAR']">
            </div>
        </div>
        <div class="setting-item">
            <label>垂直比例尺</label>
            <div class="control-group">
                <input  v-model="localMainConfig['core-config']['VERTICAL_SCALE_BAR']" type="number" :placeholder="localMainConfig['core-config']['VERTICAL_SCALE_BAR']">
            </div>
        </div>
        <div class="setting-item">
            <label>字  高</label>
            <div class="control-group">
                <input  v-model="localMainConfig['core-config']['WORD_HEIGHT']" type="number" :placeholder="localMainConfig['core-config']['WORD_HEIGHT']">
            </div>
        </div>
        <div class="setting-item">
            <label>表 格 字 高</label>
            <div class="control-group">
                <input  v-model="localMainConfig['core-config']['FORM_WORD_HEIGHT']" type="number" :placeholder="localMainConfig['core-config']['FORM_WORD_HEIGHT']">
            </div>
        </div>
        <div class="setting-item">
            <label>注释的偏移量</label>
            <div class="control-group">
                <input  v-model="localMainConfig['core-config']['ANNOTATED_OFFSETS']" type="number" :placeholder="localMainConfig['core-config']['ANNOTATED_OFFSETS']">
            </div>
        </div>
        <div class="setting-item">
            <label>制 网 材 料</label>
            <div class="control-group">
                <input  v-model="localMainConfig['core-config']['MATERIAL']" type="text" :placeholder="localMainConfig['core-config']['MATERIAL']">
            </div>
        </div>
        <div class="setting-item">
            <label>表格偏移量</label>
            <div class="control-group">
                <input  v-model="localMainConfig['core-config']['TABLE_OFFSET']" type="number" :placeholder="localMainConfig['core-config']['TABLE_OFFSET']">
            </div>
        </div>
        <div class="setting-item">
            <label>表格偏移量</label>
            <div class="control-group">
                <input  v-model="localMainConfig['core-config']['TABLE_OFFSET']" type="number" :placeholder="localMainConfig['core-config']['TABLE_OFFSET']">
            </div>
        </div>
        <button class="save-btn" @click="saveSettings">保存设置</button>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const emit = defineEmits(['update:mainConfig']);
const props = defineProps({
    mainConfig: {
        type: Object,
        required: true
    },
    themeState: {
        type: Object,
        required: true
    }
});

// 创建本地副本以避免直接修改props
const localMainConfig = ref(JSON.parse(JSON.stringify(props.mainConfig)));

// 监听props.mainConfig的变化，同步更新本地副本
watch(() => props.mainConfig, (newVal) => {
    localMainConfig.value = JSON.parse(JSON.stringify(newVal));
}, { deep: true });

const saveSettings = () => {
    // 发送本地配置的更改到父组件
    emit('update:mainConfig', localMainConfig.value);
};
</script>

<style scoped>
input {
    border-radius: 5vw;
    width: 45vw;
    margin: auto 0px;
}

.settings-container {
    float: right;
    width: 80%;
    min-height: 100vh;
    box-sizing: border-box;
    border-radius: 5vh;
    padding: 1.5vh;
    color: var(--text-color);
}

.setting-item {
    margin-bottom: 20px;
    display: flex;
    align-items: center;
}

.setting-item label {
    width: 120px;
    font-weight: bold;
}

.setting-item select,
.setting-item input[type="range"] {
    flex: 1;
    margin: 0 10px;
}

.save-btn {
    background-color: #4a6fa5;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 10px;
}

.save-btn:hover {
    background-color: #3a5a80;
}

.kid-overlay.dark .setting-item {
    background-color: rgba(67, 66, 66, 0.8);
    border-radius: 1rem;
    padding: 0.5rem;
    border: rgba(186, 186, 186, 0.8) 0.1rem solid;
}

.kid-overlay.light .setting-item {
    background-color: rgba(207, 206, 206, 0.8);
    border-radius: 1rem;
    padding: 0.5rem;
    border: rgba(151, 150, 150, 0.8) 0.1rem solid;
}

.control-group {
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.slider {
  width: 300px;
  height: 10px;
}
</style>