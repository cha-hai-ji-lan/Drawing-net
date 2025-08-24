<!-- 左侧抽屉组件用于定位当前操作步骤 -->
<template>
    <div>
        <!-- 触发按钮 -->
        <button class="toggle-button" @click="toggleDrawer">
            <img class="jump-out-icon" :src="jumpIcon" alt="菜单">
        </button>

        <!-- 遮罩层 -->
        <div v-if="isOpen" class="drawer-backdrop" @click="closeDrawer">
        </div>

        <!-- 左拉框主体 -->
        <transition name="slide">
            <div v-show="isOpen" :class="['drawer', {
                dark: themeState.is_dark_mode_theme,
                light: themeState.is_light_mode_theme,
            }]">
                <div class="drawer-content">
                    <div :class="['drawer-header', {
                        dark: themeState.is_dark_mode_theme,
                        light: themeState.is_light_mode_theme,
                    }]">
                        <p>{{ label }}</p>
                    </div>
                    <div class="drawer-body">
                    </div>
                    <!-- 这里放置内容 -->
                </div>
            </div>
        </transition>
    </div>
</template>

<script setup>
import { watch, ref } from 'vue';

const isOpen = ref(false);
const jumpIcon = ref("/icon/arrow-right-wide-line.svg");
const label = ref("绘图节点");

watch(() => jumpIcon, (newVal, oldVal) => {
    console.log('jumpIcon changed from', oldVal, 'to', newVal);
});

const props = defineProps({
    themeState: { // 标准 v-model 属性名
        type: Object,
        required: true
    }

});
const toggleDrawer = () => {
    isOpen.value = !isOpen.value;
    jumpIcon.value = isOpen.value ? "/icon/arrow-left-wide-line.svg" : "/icon/arrow-right-wide-line.svg";
}

const closeDrawer = () => {
    isOpen.value = false;
};
</script>

<style scoped>
.drawer {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 35vw;
    background-color: white;
    z-index: 999;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.drawer-header {
    top: 0;
    font-size: 3vw;
    font-weight: 900;
    text-align: center;
    border-bottom-right-radius: 1rem;
    border-bottom-left-radius: 1rem;
    height: 15vh;
    width: 100%;
    padding: 0.25vw 0;

}

.drawer.dark {
    background-color: var(--dark-background-color--left-drawer);
    color: var(--dark-font-color);

}

.drawer.light {
    background-color: var(--light-background-color--left-drawer);
    color: var(--light-font-color);
}




.drawer.dark .drawer-header {
    background-color: var(--dark-background-color-head--left-drawer);

}

.drawer.light .drawer-header {
    background-color: var(--light-background-color-head--left-drawer);
}

.drawer-body {
    font-size: 0.5rem;
    align-items: center;
    text-align: center;
    border-radius: 0.5rem;
    height: 80vh;
    width: 100%;
}

.jump-out-icon {
    width: 5vh;
    height: 5vh;
}

.toggle-button {
    position: fixed;
    top: 50vh;
    left: -2.5vh;
    transform: translateY(-50%);
    z-index: 1000;
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 10px;
}

.drawer-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: var(--drawer-width, 35vw);
    height: 100vh;
    background-color: --dark-background-color--left-drawer;
    z-index: 998;
}



.drawer-content {
    height: 100%;
    overflow-y: auto;
}

/* 滑入动画 */
.slide-enter-active,
.slide-leave-active {
    transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
    transform: translateX(-100%);
}

.slide-enter-to,
.slide-leave-from {
    transform: translateX(0);
}
</style>