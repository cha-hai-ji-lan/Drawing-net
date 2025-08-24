<!-- 主界面右侧操作界面用于拖网选型以及，原点坐标规划 -->
<template>
    <div :class="['actionbar', {
        dark: themeState.is_dark_mode_theme,
        light: themeState.is_light_mode_theme,
    }]">
        <div class="net-type">
            <label>选择拖网类型</label> <br />
            <select v-model="selectedTheme" @change="sendNetTypes(selectedTheme)">
                <option value="two-slices-type">两片式</option>
                <option value="four-slices-type">四片式</option>
                <option value="six-slices-type">六片式</option>
            </select>
            <input v-model="posValue" type="text" placeholder="请输入原点坐标默认 0, 0" />
        </div>
        <Transition name="fade" mode="out-in">
            <div v-if="selectedTheme === 'two-slices-type'">
                <div class="net-2">
                    <span id="net-2-wing-left" @click="sendDrawTypes('wing-left')">
                        <svg width="40" height="170" xmlns="http://www.w3.org/2000/svg">
                            <polygon points="7,163 37,163 7,3" fill="rgba(255, 201, 14, 0.4)"
                                stroke="rgba(255, 201, 14, 0.9)" stroke-width="3" />
                        </svg>
                    </span>
                    <span @click="sendDrawTypes('wing-right')">
                        <svg width="40" height="170" xmlns="http://www.w3.org/2000/svg">
                            <polygon points="33,163 7,163 37,3" fill="rgba(255, 201, 14, 0.4)"
                                stroke="rgba(255, 201, 14, 0.9)" stroke-width="3" />
                        </svg>
                    </span>
                </div>
                <div class="net-2" @click="sendDrawTypes('wing-body')">
                    <svg width="200" height="210" xmlns="http://www.w3.org/2000/svg">
                        <polygon points="69,207 129,207 179,7 19,7" stroke="rgba(255, 201, 14, 0.9)"
                            fill="rgba(255, 201, 14, 0.4)" stroke-width="3" />
                    </svg>
                </div>

            </div>
            <div v-else-if="selectedTheme === 'four-slices-type'">
                <div class="net-2">
                    <span @click="sendDrawTypes('wing-side')">
                        <svg width="50" height="170" xmlns="http://www.w3.org/2000/svg">
                            <polygon points="45,163 7,163 45,3" fill="rgba(255, 201, 14, 0.4)"
                                stroke="rgba(255, 201, 14, 0.9)" stroke-width="3" />
                        </svg>
                    </span>
                    <span id="net-4-wing-left" @click="sendDrawTypes('wing-left')">
                        <svg width="40" height="170" xmlns="http://www.w3.org/2000/svg">
                            <polygon points="7,163 37,163 7,3" fill="rgba(255, 201, 14, 0.4)"
                                stroke="rgba(255, 201, 14, 0.9)" stroke-width="3" />
                        </svg>
                    </span>
                    <span @click="sendDrawTypes('wing-right')">
                        <svg width="40" height="170" xmlns="http://www.w3.org/2000/svg">
                            <polygon points="33,163 7,163 37,3" fill="rgba(255, 201, 14, 0.4)"
                                stroke="rgba(255, 201, 14, 0.9)" stroke-width="3" />
                        </svg>
                    </span>
                </div>
                <div class="net-2">
                    <span @click="sendDrawTypes('wing-body-side')"><svg width="55" height="210"
                            xmlns="http://www.w3.org/2000/svg">
                            <polygon points="15,207 37,207 45,7 5,7" stroke="rgba(255, 201, 14, 0.9)"
                                fill="rgba(255, 201, 14, 0.4)" stroke-width="3" />
                        </svg></span>
                    <span @click="sendDrawTypes('wing-body')">
                        <svg width="85" height="210" xmlns="http://www.w3.org/2000/svg">
                            <polygon points="22, 207 62, 207 82, 7 2, 7" stroke="rgba(255, 201, 14, 0.9)"
                                fill="rgba(255, 201, 14, 0.4)" stroke-width="3" />
                        </svg>
                    </span>

                </div>
            </div>

            <div v-else-if="selectedTheme === 'six-slices-type'">

            </div>
        </Transition>

    </div>

</template>

<script setup>
import { ref } from 'vue'
import { getCurrentWindow } from '@tauri-apps/api/window';
const selectedTheme = ref('nothing')
const emit = defineEmits(['sendDrawTypes', 'sendNetTypes',])
const window = ref(null)
const posValue = ref("")

const props = defineProps({
    themeState: {
        type: Object,
        required: true
    },
})

const getWindowSize = () => {
    window.value = getCurrentWindow();
    window.value.innerSize().then(size => {
        console.log("当前窗口大小信息", size.width, size.height);
    }).catch(error => {
        console.error('获取窗口大小失败:', error);
    });
};

getWindowSize()

const sendOriPos = (pos_args) => {
    emit('sendOriPos', pos_args);
};
const sendNetTypes = (net_type) => {
    emit('sendNetTypes', net_type);
    emit('sendDrawTypes', null);
}
const sendDrawTypes = (part_type) => {
    console.log(part_type)
    emit('sendDrawTypes', part_type);
    console.log("原点坐标", posValue.value)
    sendOriPos(posValue.value)
}


</script>

<style scoped>
.actionbar {
    float: right;
    font-size: 2.5vw;
    width: 40%;
    height: 100%;
    box-sizing: border-box;
    align-items: center;
    text-align: center;
    transition: background-color 0.5s ease, color 0.5s ease;
}

.actionbar.dark {
    background-color: var(--dark-background-color--right-actionbar);
    color: var(--dark-font-color);
}

.actionbar.light {
    background-color: var(--light-background-color--right-actionbar);
    color: var(--light-font-color);
}

.net-type {
    background-color: rgb(230, 230, 230);
    padding: 1vh 1vw;
    border-bottom-left-radius: 1.5rem;
    border-bottom-right-radius: 1.5rem;
}

.actionbar.dark .net-type {
    background-color: var(--dark-background-color-head--right-actionbar);
}

.actionbar.light .net-type {
    background-color: var(--light-background-color-head--right-actionbar);
}



.net-type:hover {
    filter:
        drop-shadow(0 0 0.5vh rgba(205, 234, 243, 0.1)) drop-shadow(0 0 1vh rgba(124, 215, 243, 0.2)) drop-shadow(0 0 1.5vh rgba(41, 198, 245, 0.3));
}

.net-type::before:hover {
    filter:
        drop-shadow(0 0 0.5vh rgba(205, 234, 243, 0.1)) drop-shadow(0 0 1vh rgba(124, 215, 243, 0.2)) drop-shadow(0 0 1.5vh rgba(41, 198, 245, 0.3));
    /* 更接近时的阴影效果 */
}

input,
select {
    border-radius: 5rem;
    width: 25vw;
    border: 0.25vw solid rgba(255, 201, 14, 0.9);
}


svg:hover {
    filter:
        drop-shadow(0 0 0.5rem rgba(250, 236, 191, 0.1)) drop-shadow(0 0 1rem rgba(254, 203, 28, 0.2)) drop-shadow(0 0 1.5rem rgba(72, 204, 252, 0.9));
}

svg::before:hover {
    filter:
        drop-shadow(0 0 0.5rem rgba(250, 236, 191, 0.1)) drop-shadow(0 0 1rem rgba(255, 221, 110, 0.2)) drop-shadow(0 0 1.5rem rgba(72, 204, 252, 0.9));
    /* 更接近时的阴影效果 */
}

svg:active {
    filter:
        drop-shadow(0 0 0.5rem rgba(250, 236, 191, 0.1)) drop-shadow(0 0 1rem rgba(254, 203, 28, 0.2)) drop-shadow(0 0 1.5rem rgba(1, 121, 212, 0.9));

}




.net-2 {
    align-items: center;
}

span {
    justify-content: center;
    align-items: center;
}

#net-2-wing-left {
    margin-right: 5.85rem;

}

#net-4-wing-left {
    margin-right: 0.85rem;
}

.fade-enter-active {
    transition: opacity 0.5s ease;
}

.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>