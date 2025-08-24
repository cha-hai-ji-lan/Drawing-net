<template>
    <div class="dropdown" @click.stop="toggle">
        <div class="tooltip-container">
            <button @click="items[0].label === '__NOTHING__' ? items[0].handler() : null" class="dropdown-trigger"
                :id="id"><img :src="label" alt="icon"></button>
            <span class="tooltip">{{ alt }}</span>
        </div>
        <ul v-if="items[0].label !== '__NOTHING__'" v-show="isOpen" class="dropdown-menu">
            <li v-for="(item, index) in items" :key="index" @click.stop="handleItemClick(item)">
                {{ item.label }}
            </li>
        </ul>
    </div>
</template>

<script setup>
import { ref } from 'vue';
defineProps({
    id: {
        type: String,
        required: true
    },
    label: {
        type: String,
        required: true
    },
    items: {
        type: Array,
        required: true,
        default: () => []
    },
    alt: {
        type: String,
        default: '',
        required: false
    }

});

const emit = defineEmits(['item-click']);

const isOpen = ref(false);

const toggle = () => {
    isOpen.value = !isOpen.value;
};

const handleItemClick = (item) => {
    if (item.handler) {
        item.handler();
    }
    emit('item-click', item);
};
</script>

<style scoped>
.tooltip {
    visibility: hidden;
    position: absolute;
    top: 5vh;
    /* 显示在按钮上方 */
    left: 4.5vh;
    transform: translateX(-50%);
    white-space: nowrap;
    /* 折行 文本 */
    padding: 0.1vh 0.8vh;
    border-radius: 0.5vh;
    font-size: 1.2vh;
    opacity: 0;
    transition: opacity 0.3s, visibility 0.3s;
    z-index: 20;
    /* 确保在按钮下方 */
    pointer-events: none;
    border: 0.3vh solid black;
    /* 添加黑边框 */
    background-color: #fff;
    /* 默认背景颜色 */
    color: #333;
    box-shadow: 0 0.3vh 1vh rgba(0, 0, 0, 0.1);
    /* 调整阴影效果 */
}

.tooltip::after {
    content: '';
    position: absolute;
    bottom: 100%;
    /* 箭头位于提示框下方 */
    left: 50%;
    margin-left: -1vh;
    /* 水平居中 */
    border-width: 1vh;
    border-style: solid;
    border-color: black transparent transparent transparent;
    /* 创建黑色箭头 */
}

.tooltip-container:hover .tooltip {
    visibility: visible;
    opacity: 1;
}

.dropdown {
    position: relative;
    display: inline-block;
    cursor: pointer;
}

img {
    width: 3vh;
    height: 3vh;
}

button {
    position: relative;
}

@media (prefers-color-scheme: dark) {
    .dropdown-trigger {
        font-weight: 800;
        width: 8vh;
        height: 4vh;
        line-height: 100%;
        align-items: center;
        border-radius: 0.5vh;
        border: none;
        color: rgb(204, 204, 204);
        font-size: 1.5vh;
        padding: 0.2vh;
        margin: 0 0.5vh;
        font-family: '宋体', 'Arial',serif;
        filter: drop-shadow(0 0 0.5vh rgba(68, 71, 72, 0.1)) drop-shadow(0 0 1vh rgba(189, 189, 189, 0.2)) drop-shadow(0 0 1.5vh rgba(240, 240, 240, 0.3));
        background-color: transparent;
    }

    button:hover {
        filter:
            drop-shadow(0 0 0.5vh rgba(68, 71, 72, 0.1)) drop-shadow(0 0 1vh rgba(189, 189, 189, 0.2)) drop-shadow(0 0 1.5vh rgba(240, 240, 240, 0.3));
    }

    .dropdown-menu li:hover {
        border-radius: 0.4vh;
        background-color: rgba(59, 177, 245, 0.5);
    }

    .tooltip {
        background-color: #333;
        color: #fff;
        border: 0.4vh solid #cdcdcd;
        box-shadow: 0 0.3vh 1vh rgba(0, 0, 0, 0.3);
    }

    .tooltip::after {
        border-color: #333 transparent transparent transparent;
        /* 暗色模式下的箭头颜色 */
    }

}

@media (prefers-color-scheme: light) {
    .dropdown-trigger {
        font-weight: 900;
        width: 8vh;
        height: 4vh;
        line-height: 100%;
        align-items: center;
        border-radius: 0.5vh;
        border: none;
        color: rgb(43, 43, 43);
        font-size: 1.5vh;
        padding: 0.2vh;
        margin: 0 0.5vh;
        font-family: '宋体', 'Arial',serif;
        filter: drop-shadow(0 0 0.5vh rgba(68, 71, 72, 0.1)) drop-shadow(0 0 1vh rgba(189, 189, 189, 0.2)) drop-shadow(0 0 1.5vh rgba(240, 240, 240, 0.3));
        background-color: transparent;
    }

    button:hover {
        filter:
            drop-shadow(0 0 0.5vh rgba(255, 255, 255, 0.1)) drop-shadow(0 0 1vh rgba(62, 64, 65, 0.2)) drop-shadow(0 0 1.5vh rgba(17, 17, 17, 0.3));
    }

    .dropdown-menu li:hover {
        border-radius: 0.4vh;
        background-color: rgb(34, 166, 242, 0.5);
    }

    .tooltip {
        background-color: #edebeb;
        color: #333;
        border: 0.4vh solid #3d3d3d;
        box-shadow: 0 0.3vh 1vh rgba(0, 0, 0, 0.1);
    }

    .tooltip::after {
        border-color: #ddd transparent transparent transparent;

        /* 亮色模式下的箭头颜色 */
    }


}



.dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    list-style: none;
    margin: 0;
    padding: 0;
    background: linear-gradient(to right, rgb(218, 218, 218) 0%, rgb(255, 255, 255) 100%);
    border-radius: 0.5vh;
    border: rgb(68, 71, 72) solid 0.1vh;
    box-shadow: 0 0.3vh 1vh rgba(0, 0, 0, 0.1);
    z-index: 10;
    min-width: 22vh;
    color: #333;
}

.dropdown-menu li {
    height: 4vh;

    font-weight: 700;
    font-size: 2vh;
    padding: 1vh 2vh;
    cursor: pointer;
}
</style>