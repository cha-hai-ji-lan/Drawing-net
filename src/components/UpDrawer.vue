<!-- 设置界面的父级组件， 作为上抽屉组件 -->
<template>
    <div>
        <!-- 全屏覆盖层 -->
        <transition name="slide-up">
            <div v-show="modelValue" :class="['overlay', {
                dark: themeState.is_dark_mode_theme,
                light: themeState.is_light_mode_theme,
            }]">
                <div class="overlay-content">
                    <div class="setting-title">
                        <button class="close-button" @click="closeOverlay"> <img src="/icon/arrow-down-double-line.svg"
                                alt="返回界面" title="返回界面"></button>
                    </div>
                    <div class="setting-page-container">
                        <div class="setting-page-choose">
                            <div>
                                <button class="setting-page-choose-button" @click="interface_setting_switch">界面设置</button>
                            </div>
                            <div>
                                <button class="setting-page-choose-button"  @click="constraint_setting_switch">约束设置</button>
                            </div>

                        </div>
                        <InterfaceSettings v-if="switch_list[0] === true" :themeState="props.themeState" :mainConfig="localConfig"
                            @update:mainConfig="handleConfigUpdate">
                        </InterfaceSettings>
                        <ConstraintSettings v-else-if="switch_list[1] === true" :themeState="props.themeState" :mainConfig="localConfig"
                            @update:mainConfig="handleConfigUpdate">
                        </ConstraintSettings>
                    </div>
                </div>
            </div>
        </transition>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import InterfaceSettings from './InterfaceSettings.vue';
import ConstraintSettings from './ConstraintSettings.vue';
const props = defineProps({
    modelValue: { // 标准 v-model 属性名
        type: Boolean,
        required: true
    },
    setting: {
        type: Boolean,
        required: true
    },
    configDictionary: { // 配置字典
        type: Object,
        required: true
    },
    themeState: { // 标准 v-model 属性名
        type: Object,
        required: true
    }
});
const emit = defineEmits(['update:modelValue', 'update:setting', 'update:configDictionary']); // 添加 emit 声明
const localConfig = ref(JSON.parse(JSON.stringify(props.configDictionary)));
const switch_list = ref([false, false])

// 监听props.configDictionary的变化，同步更新本地副本
watch(() => props.configDictionary, (newVal) => {
    localConfig.value = JSON.parse(JSON.stringify(newVal));
}, { deep: true });

// 添加方法用于更新状态
const closeOverlay = () => {
    emit('update:modelValue', false);
    emit('update:setting', false);
}

const handleConfigUpdate = (newConfig) => {
    console.log('Received updated config:', newConfig);
    localConfig.value = JSON.parse(JSON.stringify(newConfig));
    emit('update:configDictionary', localConfig.value);
}

const interface_setting_switch = () => {
    for (let index = 0; index < switch_list.value.length; index++) {
        switch_list.value[index] = false;
    };
    switch_list.value[0] = true;

}

const constraint_setting_switch = () => {
    for (let index = 0; index < switch_list.value.length; index++) {
        switch_list.value[index] = false;
    };
    switch_list.value[1] = true;

}
</script>

<style scoped>
.close-button {
    background: transparent;
    width: 7vh;
    height: 7vh;
    border: none;
    border-radius: 3vh;
    cursor: pointer;
}

.setting-page-container {
    padding: 0 0 0 2vh;
    height: calc(100vh - 8vh);
    overflow-y: auto;
}

.setting-page-choose {
    padding: 1vh 0;
    float: left;
    width: 20%;
    height: 90%;
    box-sizing: border-box;
    border-top-right-radius: 5vh;
    border-bottom-right-radius: 5vh;
    padding: 0.5rem;
    position: absolute;
    text-align: center;
    z-index: 999;

}

.setting-title {
    height: 8vh;
    font-family: '宋体';
    background: linear-gradient(to right, #e85984, #e51050, #78082a);
    border-bottom-left-radius: 1vh;
    border-bottom-right-radius: 1vh;
    padding: 0.1vh 2vh;
}

.overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1000;
    transition: background-color 0.5s ease, color 0.5s ease;
}

.setting-page-choose-button {
    margin-bottom: 2.5vh;
    font-family: '宋体', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-weight: 700;
    font-size: 2vw;
    width: 100%;
    height: 8vh;
    border-radius: 3vh;
}

.overlay.dark {
    background-color: var(--dark-background-color--settingbar);
    color: var(--dark-font-color);
}

.overlay.dark .close-button:checked {
    border: #4f4f4f 0.3vh solid;
}

.overlay.dark .setting-page-choose-button {
    color: rgb(231, 230, 228);
    background-color: rgba(83, 85, 86, 0.8);
    border: rgba(162, 163, 164, 0.9) 0.4vh solid;
}

.overlay.dark .setting-page-choose {
    background-color: var(--dark-background-color-head--left-settingbar);
}

.overlay.dark .setting-page-choose-button:active {
    background-color: rgba(240, 240, 240, 0.8);
    border: rgba(206, 205, 205, 0.8) 0.3vh solid;
}

.overlay.light .overlay-content {
    color: #333333;
    padding: 0;
    height: 100%;
    display: flex;
    flex-direction: column;

}
.overlay.dark .overlay-content {
    color: rgb(231, 230, 228);
    padding: 0;
    height: 100%;
    display: flex;
    flex-direction: column;

}

.overlay.light {
    background-color: var(--light-background-color--settingbar);
    color: var(--light-font-color);
}

.overlay.light .close-button:checked {
    border: #333333 0.3vh solid;
}

.overlay.light .setting-page-choose-button {
    color: #333333;
    background-color: #e1e1e1;
    border: #434343 0.3vh solid;
}

.overlay.light .setting-page-choose {
    background-color: var(--light-background-color-head--left-settingbar);
}

.overlay.light .setting-page-choose-button:active {
    background-color: #cbcaca;
    border: #4f4f4f 0.3vh solid;
}

.overlay-content {
    height: 100%;
    display: flex;
    flex-direction: column;
}

/* 上滑动画 */
.slide-up-enter-active,
.slide-up-leave-active {
    transition: transform 0.5s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
    transform: translateY(100%);
}

.slide-up-enter-to,
.slide-up-leave-from {
    transform: translateY(0);
}
</style>