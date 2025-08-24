// 创建WebSocket工具函数
import { ref, onUnmounted } from 'vue';
export function useWebSocket(url) {
    const socket = ref(null);
    const messages = ref([]);
    const isConnected = ref(false);
    const error = ref(null);
    const connect = () => {
        try {
            socket.value = new WebSocket(url);

            socket.value.onopen = () => {
                isConnected.value = true;
                console.log('WebSocket 已连接');
            };

            socket.value.onmessage = (event) => {
                try {
                    // 尝试将消息解析为 JSON 对象
                    const parsedData = JSON.parse(event.data)
                    console.log('收到消息:', parsedData);
                    messages.value.push(parsedData);
                } catch (e) {
                    // 如果解析失败，将原始字符串存储
                    messages.value.push(event.data);
                }
            };

            socket.value.onerror = (err) => {
                error.value = err;
                console.error('Websocket错误:', err);
            };

            socket.value.onclose = () => {
                isConnected.value = false;
                console.log('Websocket断开连接');
            };
        } catch (err) {
            error.value = err;
            console.error('Websocket初始化错误:', err);
        }
    };

    const send = (data) => {

        if (isConnected.value && socket.value) {
            socket.value.send(JSON.stringify(data));
        }
    };

    const disconnect = () => {
        if (socket.value) {
            socket.value.close();
        }
    };

    // 组件卸载时自动断开连接
    onUnmounted(() => {
        disconnect();
    });

    return {
        socket,
        messages,
        isConnected,
        error,
        connect,
        send,
        disconnect
    };
}