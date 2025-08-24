<template>
  <LeftDrawer v-show="!showSettings" :themeState="themeState">
    <!-- 在左拉框中放置自定义内容 -->
  </LeftDrawer>
  <UpDrawer v-model:modelValue="settingsIsOpen" v-model:setting="showSettings" v-model:configDictionary="mainConfig"
    :themeState="themeState" @update:configDictionary="handleConfigUpdate">
    <!-- 在上拉框中放置自定义内容 -->
  </UpDrawer>
  <div :class="['app-container', {
    dark: themeState.is_dark_mode_theme,
    light: themeState.is_light_mode_theme,
  }]">
    <div class="menu-bar">
      <!-- 添加toggleSettings事件监听 -->
      <MenuBar @settings-click="toggleSettings" :sendNetArgs="sendMessage" />
    </div>

    <main class="content">
      <!-- 页面的主要内容 -->
      <Transition name="fade" mode="out-in">
        <OptionDiagram v-if="netType !== null && netType !== 'start'" class="option-diagram" :mainConfig="mainConfig"
          :originPosition="originPosition" :dataDrawingType="drawingType" v-model:dataNetType="netType"
          :themeState="themeState" :sendNetArgs="sendMessage" @sendStatueInfo="togglestatusInfo" />
        <span class="option-diagram warning-span" v-else-if="netType === null">
          <h3>已放弃本次绘画，请重新选择拖网类型</h3>
        </span>
        <div class="warning-span" v-else>
          <h1>✨️欢迎✨️</h1>
          <div class="start-diagram"><a href="#"
              @click.prevent="openInBrowser('https://github.com/cha-hai-ji-lan?tab=repositories')">❇︎源码已存放在上传远程仓库（点击前往）</a>
          </div>
          <div class="start-diagram"><a
              href="mailto:shi2760992374@outlook.com?subject=BUG反馈&body=请发送反馈内容">❇︎Bug反馈：shi2760992374@outlook.com（点击反馈）</a>
          </div>
        </div>
      </Transition>
      <Actionbar class="actionbar" v-model="originPosition" @sendOriPos="toggleSendOriPos"
        @sendNetTypes="toggleNetTypes" @sendDrawTypes="toggleDrawTypes" :themeState="themeState" />

    </main>

    <div class="status-bar">
      <StatusBar :statusInfo="statusInfo" />
    </div>
  </div>
</template>

<script setup>
import MenuBar from './MenuBar.vue';  // 导入菜单栏组件
import StatusBar from './StatusBar.vue';  // 导入状态栏组件
import OptionDiagram from './OptionDiagram.vue';  // 导入选项框组件
import Actionbar from './Actionbar.vue';  // 导入右侧操作栏组件
import LeftDrawer from './components/LeftDrawer.vue';  // 导入左侧抽屉组件
import UpDrawer from './components/UpDrawer.vue';  // 导入上方抽屉组件 用于打开设置界面
import { invoke } from "@tauri-apps/api/core";  // 引入tauri的api
import { resolveResource } from '@tauri-apps/api/path';  // 引入tauri的资源解析器
import { readTextFile, writeFile, writeTextFile } from '@tauri-apps/plugin-fs';  // 引入tauri的文本文件读写插件
import { open } from '@tauri-apps/plugin-shell'; // 确保已导入 execute 函数
import { platform } from '@tauri-apps/plugin-os';
import { ref, onMounted, watch } from 'vue';
import { useWebSocket } from "./webSocketUsing"

const platformName = platform()  // 获取当前平台名称
const showSettings = ref(false);  // 创建一个ref对象，用于控制设置面板的显示
const settingsIsOpen = ref(false);  // 创建一个ref对象，用于控制设置面板的打开状态
const drawingType = ref('');  // 创建一个ref对象，用于保存绘图类型
const netType = ref('start');  // 创建一个ref对象，用于保存网络类型
const mainConfig = ref({});  // 创建一个ref对象，用于保存主配置
const isDarkModeSystem = ref(false);  // 创建一个ref对象，用于保存是否为深色模式系统
const originPosition = ref("");  //  获取右侧原点输入框绘制起始位置字符串存储变量
const statusInfo = ref("就绪");  // 创建一个ref对象，用于保存状态栏显示信息

const currentTheme = ref(["auto", "跟随系统主题"])
const themeState = ref({  // 主题状态
  is_dark_mode_theme: false,
  is_light_mode_theme: false,
})
const {
  messages,
  isConnected,
  connect,
  send,
  disconnect
} = useWebSocket('ws://127.0.0.1:8080');

// 异步函数读取字符文件
async function readJsonFile(path) {
  if (!(path && path.length > 0)) {
    throw new Error("路径无效");
  }
  const resourcePath = await resolveResource(path);
  return await readTextFile(resourcePath);
}
// 异步函数写入字符文件
async function saveJsonFile(filePath) {
  try {
    // 将对象转换为 JSON 字符串并写入文件
    const resourcePath = await resolveResource(filePath);
    await writeTextFile(resourcePath, JSON.stringify(mainConfig.value, null, 2));
    console.log('数据已成功写入 config.json');
  } catch (error) {
    console.error('写入文件时出错:', error);
  }

}

readJsonFile("resources/config.json").then(data => {
  mainConfig.value = JSON.parse(data);  // json对象赋值给 mainConfig
  console.log("载入成功", mainConfig.value);

  // 在配置加载完成后设置主题
  if (mainConfig.value.theme && mainConfig.value.theme["current-theme"] === 'auto') {
    isDarkModeSystem.value = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;  // 获取系统主题
    currentTheme.value = ["auto", "跟随系统主题"];
    toggleTheme()
  } else if (mainConfig.value.theme) {
    currentTheme.value[0] = mainConfig.value.theme["current-theme"];
    currentTheme.value[1] = mainConfig.value.theme["target-theme"][currentTheme.value[0]];
    toggleTheme()
  }
}).catch(error => {
  console.log(error);
});



// 挂载组件时执行
onMounted(() => {
  setTimeout(() => {
    runExe("resources/core.exe");
  }, 100); // 延迟 100ms 启动
});

watch(
  () => mainConfig.value,
  (newConfig, oldConfig) => {
    sendMessage({ "--core-cfg": mainConfig.value["core-config"] })
  },
  { deep: true }
);


watch(
  () => messages.value.length,
  (newLength, oldLength) => {
    if (newLength === oldLength + 1) {
      const server_data = messages.value.at(-1);
      // 如果 server_data 是字符串，则尝试解析为 JSON 对象
      if (typeof server_data === 'string') {
        try {
          server_data = JSON.parse(server_data);
        } catch (e) {
          // 如果解析失败，保持原样
          console.error('无法将Server_data解析为JSON:', e);
        }
      }
      // 确保 server_data 是一个对象再使用 in 操作符
      if (typeof server_data === 'object' && server_data !== null) {
        console.log(typeof server_data);
        if ("operation-error" in server_data) {
          switch (server_data["operation-error"]) {
            case 1:
              togglestatusInfo(mainConfig.value["err-msg"]["no-redo-part-step"]);
              break;
            case 2:
              togglestatusInfo(mainConfig.value["err-msg"]["no-redo-step"]);
              break;
            default:
              togglestatusInfo(mainConfig.value["err-msg"]["err-operation"]);
              break;
          }
        } else if ("type-error" in server_data) {
          switch (server_data["type-error"]) {
            case 1:
              togglestatusInfo(mainConfig.value["err-msg"]["no-cur-net-type"]);
              break;
            default:
              togglestatusInfo(mainConfig.value["err-msg"]["err-net-type"]);
              break;
          }
        } else if ("clean-error" in server_data) {
          switch (server_data["clean-error"]) {
            case 1:
              togglestatusInfo(mainConfig.value["err-msg"]["err-clean-msp"]);
              break;
            default:
              togglestatusInfo(mainConfig.value["err-msg"]["err-clean-operation"]);
              break;
          }
        }
      }
    }
  }
);


// 启用服务程序
async function runExe(path) {
  try {
    if (!(path && path.length > 0)) {
      throw new Error("路径无效");
    }
    const resourcePath = await resolveResource(path);
    // 调用后端的 run_exe 命令，并传递 EXE 文件路径
    await invoke('run_exe', { path: resourcePath });
    console.log('EXE 文件已成功运行');
  } catch (error) {
    console.error('运行 EXE 文件时出错:', error);
  }
}

// 示例：发送消息
const sendMessage = (data) => {
  send(data);
};

const toggleSendOriPos = (origin_position) => {
  originPosition.value = origin_position;
};
const toggleSettings = () => {
  // 添加切换设置面板的逻辑
  showSettings.value = !showSettings.value;
  settingsIsOpen.value = !settingsIsOpen.value;
};

const toggleNetTypes = (net_type) => {
  // 添加切换网络类型面板的逻辑
  netType.value = net_type;

};
const togglestatusInfo = (status_info) => {
  statusInfo.value = status_info;
};

const toggleDrawTypes = (draw_type) => {
  // 添加切换绘图类型面板的逻辑
  drawingType.value = draw_type;
  if (!(isConnected.value)) {
    connect();
    setTimeout(() => {
      sendMessage({ "--core-cfg": mainConfig.value["core-config"] })
    }, 1000); // 延迟 1000ms 发送config
  }

};

// 中心控制切换主题函数
const toggleTheme = () => {
  Object.keys(themeState.value).forEach(key => {
    themeState.value[key] = false;
  });
  currentTheme.value[0] = mainConfig.value.theme["current-theme"];
  currentTheme.value[1] = mainConfig.value.theme["target-theme"][currentTheme.value[0]];
  switch (currentTheme.value[0]) {
    case "light":
      themeState.value.is_light_mode_theme = true;
      mainConfig.value.theme["current-theme"] = "light";
      break;
    case "dark":
      themeState.value.is_dark_mode_theme = true;
      mainConfig.value.theme["current-theme"] = "dark";
      break;
    case "auto":
      if (isDarkModeSystem.value) {
        themeState.value.is_dark_mode_theme = true;
      } else {
        themeState.value.is_light_mode_theme = true;

      }
      mainConfig.value.theme["current-theme"] = "auto";
      break;
    default:
      mainConfig.value.theme["current-theme"] = "auto";
      break;
  }
  saveJsonFile("resources/config.json")

}

const handleConfigUpdate = (newConfig) => {
  mainConfig.value = newConfig;
  console.log('更新配置:', mainConfig.value);
  toggleTheme();
  saveJsonFile("resources/config.json")

}


const openInBrowser = async (url) => {
  try {
    await invoke('open_url', { url });
  } catch (err) {
    console.error('无法打开链接:', err);
  }
};


</script>

<style scoped>
.warning-span {
  font-family: '宋体', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  text-align: center;
  float: left;
  /* 默认左浮动 */
  width: 60%;
  box-sizing: border-box;
  display: block;
  margin: 0;
  padding: 35vh 0 0 0;
  background-attachment: fixed;
  overflow: hidden;
  position: fixed;
  left: 0;
  transition: background-color 0.5s ease, color 0.5s ease;
}

.app-container {
  display: flex;
  /* 水平布局 */
  flex-direction: column;
  /* 垂直布局 */
  height: 100vh;
  /* 100%高度 */
  transition: background-color 0.5s ease, color 0.5s ease;
  /* 渐变过渡效果 */
}

/* 暗色模式主题 */
.app-container.dark {
  color: rgba(246, 246, 246, 1);
  background-color: rgba(33, 40, 48, 1);
  /* 淡灰色底色 */
  background-image:
    linear-gradient(to right, rgba(45, 51, 65, 0.5) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(45, 51, 65, 0.5) 1px, transparent 1px);
  /* 创建虚线网格 */
  background-size: 2vh 2vh;
  /* 网格大小为 20x20 像素 */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);

}

/* 亮色模式主题 */
.app-container.light {
  color: rgba(33, 40, 48, 1);
  background-color: rgb(232, 232, 232, 1);
  background-image:
    linear-gradient(to right, rgba(162, 165, 172, 0.5) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(162, 165, 172, 0.5) 1px, transparent 1px);
  background-size: 2vh 2vh;
  box-shadow: 0 0.4vh 0.7vh rgba(0, 0, 0, 0.2);

}

.app-container.dark .actionbar {
  border: 0.5vw solid rgba(49, 51, 53, 0.85);
  border-bottom-left-radius: 2vh;
  border-bottom-right-radius: 2vh;
}

.app-container.dark .option-diagram {
  border: 0.5vw solid rgba(49, 51, 53, 0.85);
  border-bottom-left-radius: 2vh;
  border-bottom-right-radius: 2vh;
}

.app-container.light .actionbar {
  border: 0.5vw solid rgba(188, 186, 186, 0.85);
  border-bottom-left-radius: 2vh;
  border-bottom-right-radius: 2vh;
}

.app-container.light .option-diagram {
  border: 0.5vw solid rgba(188, 186, 186, 0.85);
  border-bottom-left-radius: 2vh;
  border-bottom-right-radius: 2vh;
}

.app-container .status-bar {
  height: 4vh;
  /* 设置状态栏高度为视口高度的 2% */
  flex-shrink: 0;
  /* 防止被压缩 */
}

/* 
添加激活状态样式
.settings-container.active {
  height: 400px;
 根据实际需求调整高度
} */

.content {
  flex: 1;
  /* 填充剩余空间 */
  overflow-y: auto;
  /* 允许垂直滚动 */
}

.option-diagram {
  border: 0vw solid rgb(176, 137, 137);
}

.start-diagram {
  text-align: left;
  padding: 1vh 0 0 12.5vw;
}

a {
  font-size: 2.5vh;
  color: rgba(29, 144, 215, 0.85);
  text-decoration: solid;
  font-weight: 700;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
<style>
body {
  font-family: '宋体';
  display: block;
  margin: 0;
  padding: 0;
  background-attachment: fixed;
  overflow: hidden;
}

:root {
  /* 文本颜色
  --text-color: #0f0f0f; */
  /*  网格大小 */
  --grid-size: 20px;
  /*暗色变量*/
  --dark-font-color: rgba(246, 246, 246, 1);
  /*亮色变量*/
  --light-font-color: rgba(33, 40, 48, 1);
  /* 左侧抽屉组件 变量 暗色 */
  --dark-background-color--left-drawer: rgba(60, 63, 65, 0.8);
  --dark-background-color-head--left-drawer: rgba(23, 23, 23, 0.8);
  --dark-background-color-body--left-drawer: rgba(33, 40, 48, 0.8);
  /* 浅色 */
  --light-background-color--left-drawer: rgba(232, 232, 232, 0.8);
  --light-background-color-head--left-drawer: rgba(182, 182, 182, 0.8);
  --dark-background-color-body--left-drawer: rgba(33, 40, 48, 0.8);

  /* 右侧操作栏 变量 暗色 */
  --dark-background-color--right-actionbar: rgba(90, 93, 95, 0.3);
  --dark-background-color-head--right-actionbar: rgba(90, 93, 95, 0.8);
  /* 浅色 */
  --light-background-color--right-actionbar: rgba(242, 242, 242, 0.6);
  --light-background-color-head--right-actionbar: rgba(200, 203, 196, 0.8);
  /* 左侧操作栏 变量 暗色 */
  --dark-background-color--left-actionbar: rgba(90, 93, 95, 0.15);
  --dark-background-color-head--left-actionbar: rgba(90, 93, 95, 0.8);
  /* 浅色 */
  --light-background-color--left-actionbar: rgba(242, 242, 242, 0.3);
  --light-background-color-head--left-actionbar: rgba(200, 203, 196, 0.8);
  /* 设置栏 变量 暗色 */
  --dark-background-color--settingbar: rgba(90, 93, 95, 0.99);
  --dark-background-color-head--left-settingbar: rgba(60, 63, 65, 0.8);
  /* 浅色 */
  --light-background-color--settingbar: rgba(242, 242, 242, 0.95);
  --light-background-color-head--left-settingbar: rgba(200, 203, 196, 0.8);




  font-family: '宋体', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 24px;
  font-weight: 400;

  color: #0f0f0f;
  background-color: #f6f6f6;

  font-synthesis: none;
  /* 禁用系统字体kerning */
  text-rendering: optimizeLegibility;
  /* 优化中文字体 */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: 100%;
}

.dark-theme {
  --text-color: #f6f6f6;
  background-color: #212830;
  background-image:
    linear-gradient(to right, rgba(45, 51, 65, 0.5) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(45, 51, 65, 0.5) 1px, transparent 1px);
  background-size: var(--grid-size) var(--grid-size);
}

.light-theme {
  --text-color: #212830;
  background-color: rgb(232, 232, 232);
  background-image:
    linear-gradient(to right, rgba(162, 165, 172, 0.5) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(162, 165, 172, 0.5) 1px, transparent 1px);
  background-size: var(--grid-size) var(--grid-size);
}
</style>
