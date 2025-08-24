<template>
    <div class="settings-container" :class="['kid-overlay', {
                dark: themeState.is_dark_mode_theme,
                light: themeState.is_light_mode_theme,
            }]">
        <h3>全局设置</h3>
        <div class="setting-item">
            <label>主题模式</label>
            <select v-model="selectedTheme">
                <option value="" disabled selected style="display: none;">{{ currentTheme }}
                </option>
                <option value="auto">默认</option>
                <option value="light">浅色主题</option>
                <option value="dark">深色主题</option>
            </select>
        </div>
        <div class="setting-item">
            <label>是否恢复默认约束参数</label>
            <div class="control-group">
                <Switch  v-model="restore_default_constraint_parameters"/>
            </div>
        </div>
        <button class="save-btn" @click="saveSettings">保存设置</button>
    </div>
</template>

<script setup>
import { ref, onMounted, watch} from 'vue';
import Switch from './tool/switch.vue';


const emit = defineEmits(['update:mainConfig']); // 添加 emit 声明
const selectedTheme = ref('auto');  // 默认跟随系统
const gridSize = ref(20);
const fontSize = ref('16px');
const currentTheme = ref(localStorage.getItem('theme'));
const restore_default_constraint_parameters = ref(false)
const props = defineProps({
    mainConfig: {
        type: Object,
        required: true
    },
    themeState: { // 标准 v-model 属性名
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
const updateGridSize = () => {
    document.documentElement.style.setProperty('--grid-size', `${gridSize.value}px`);
};

const updateFontSize = () => {
    document.documentElement.style.fontSize = fontSize.value;
};

const saveSettings = () => {
    localMainConfig.value = props.mainConfig;
    if (restore_default_constraint_parameters.value === true) {
        localMainConfig.value['core-config'] = localMainConfig.value['__default__.core-config'];
    }
    localMainConfig.value.theme["current-theme"] = selectedTheme.value
    localStorage.setItem('theme', localMainConfig.value.theme["target-theme"][selectedTheme.value]);
    emit('update:mainConfig', localMainConfig.value);
    // 这里可以添加保存到本地存储的逻辑
    restore_default_constraint_parameters.value = false;
};

onMounted(() => {
    // 初始化时应用设置
    updateGridSize();
    updateFontSize();
});

const updateOpacity = () => {
    let pass = null;
}


</script>

<style scoped>
.settings-container {
    float: right;
    width: 80%;
    height: 100%;
    box-sizing: border-box;
    border-radius: 5vh;
    padding: 1.5vh;
    color: var(--text-color);
}

.setting-item {
    height: 7.5vh;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
}

.setting-item label {
    width: 300px;
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