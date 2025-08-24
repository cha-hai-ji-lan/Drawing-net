<template>
    <div class="status-bar">
        <p>{{ statusInfo }}</p>
    </div>

</template>
<script setup>
const props = defineProps({
    statusInfo :{
        type: String,
        required: true
    }
   
})

</script>

<style scoped>
@media (prefers-color-scheme: dark) {

    .status-bar {
        font-family: '宋体',serif;
        background-color: rgb(123, 8, 43);
        border-top: 0.5vh solid rgb(41, 47, 60);
        padding: 0.1vh 1vh;
    }
}

@media (prefers-color-scheme: light) {

    .status-bar {
        font-family: '宋体' ,serif;
        background-color: rgb(123, 8, 43);
        border-top: 0.5vh solid rgb(179, 181, 187);
        padding: 0.1vh 1vh;
    }
}

p {
    margin: 0;
    font-size: 1.2vh;
    color: white;
}
</style>