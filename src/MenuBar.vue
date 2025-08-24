<template>
    <div class="menu-bar">
        <DropdownMenu id="menu-button-1" label="/icon/folder-line.svg" :items="[
            { label: '新建', handler: handleFileNew },
            { label: '打开', handler: handleFileOpen },
            { label: '保存', handler: handleFileSave }
        ]" alt="文件" />
        <DropdownMenu id="menu-button-2" :label="pinIcon" :items="[
            { label: '__NOTHING__', handler: setWindowAlwaysOnTop },
        ]" alt="置顶" />
        <DropdownMenu id="menu-button-3" label="/icon/arrow-go-back-line.svg" :items="[
            { label: '__NOTHING__', handler: handleReDo },
        ]" alt="上一步" />
        <DropdownMenu id="menu-button-4" label="/icon/arrow-go-forward-line.svg" :items="[
            { label: '__NOTHING__', handler: handleToDo },
        ]" alt="下一步" />
        <DropdownMenu id="menu-button-5" label="/icon/settings-3-line.svg" :items="[
            { label: '__NOTHING__', handler: handleSetUp },
        ]" alt="设置" />
    </div>
</template>
<script setup>
import DropdownMenu from './components/DropdownMenu.vue';
import { ref } from 'vue'  // 添加defineEmits引用
import { Window } from '@tauri-apps/api/window';

const isAlwaysOnTop = ref(false)
const pinIcon = ref('/icon/pushpin-line.svg')

// 添加事件发射器
const emit = defineEmits(['settings-click']);

const props = defineProps({
    sendNetArgs: {
        type: Function,
        required: true
    },
})
function handleSetUp() {
    console.log('设置');
    // 触发设置事件
    emit('settings-click');
}
async function setWindowAlwaysOnTop() {
    const currentWindow = Window.getCurrent();
    const isTop = !isAlwaysOnTop.value;
    isAlwaysOnTop.value = isTop;
    pinIcon.value = isTop ? '/icon/pushpin-2-line.svg' : '/icon/pushpin-line.svg';
    await currentWindow.setAlwaysOnTop(isTop);
}

function handleFileNew() {
    console.log('文件 - 新建');
}
function handleFileOpen() {
    console.log('文件 - 打开');
}
function handleFileSave() {
    console.log('文件 - 保存');
}

function handleReDo() {
    console.log('上一步');
    props.sendNetArgs({"--redo": 1})
}
function handleToDo() {
    console.log('下一步');
    props.sendNetArgs({"--todo": 1})

}
</script>

<style scoped>
.menu-bar {
    font-family: '宋体', 'Arial', sans-serif;
    background: linear-gradient(to right, #e85984, #e51050, #78082a);
    border-bottom-left-radius: 1vh;
    border-bottom-right-radius: 1vh;
    padding: 0.5vh;
    height: 5vh;
    justify-content: space-between;
    /* 居中 */
    align-items: center;
    transition: filter 0.3s;
    /* 添加过渡效果 */
}

.menu-bar:hover {
    filter:
        drop-shadow(0 0 0.5vh rgba(232, 89, 132, 0.1)) drop-shadow(0 0 1vh rgba(229, 16, 80, 0.2)) drop-shadow(0 0 1.5vh rgba(120, 8, 42, 0.3));
}

.menu-bar::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    /* 不影响鼠标事件 */
    transition: filter 0.3s;
    /* 添加过渡效果 */
}

.menu-bar::before:hover {
    filter: drop-shadow(0 0 10px rgba(229, 18, 81, 0.7));
    /* 更接近时的阴影效果 */
}
</style>