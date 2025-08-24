<template>
    <div :class="['option-diagram', {
        dark: themeState.is_dark_mode_theme,
        light: themeState.is_light_mode_theme,
    }]">
        <Transition name="fade" mode="out-in">
            <div v-if="dataNetType === 'two-slices-type'">
                <Transition name="fade" mode="out-in">
                    <div v-if="dataDrawingType === 'wing-left'">
                        <!-- 绘制网翼 -->
                        <div class="option-diagram-title-1">
                            <p v-if="segments === 1">上网翼: 第{{ segments }}段(网口段)</p>
                            <p v-else>上网翼: 第{{ segments }}段</p>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网 翼 目 大 :</span>
                            <span><input v-model="value_1" type="text" :placeholder="text_metric_parameters"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>网翼纵向目数:</span>
                            <span><input v-model="value_2" type="text" :placeholder="text_vertical_mesh"></span>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网翼横向目数:</span>
                            <span><input v-model="value_3" type="text" :placeholder="text_horizontal_mesh"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>边旁剪裁斜率 :</span>
                            <span><input v-model="value_4" type="text" :placeholder="text_cutting_slope"></span>
                        </div>
                        <div  v-if="segments !== 1" class="option-diagram-title-2">
                            <span>宕眼剪裁斜率 :</span>
                            <span><input v-model="value_5" type="text" :placeholder="text_eye_cutting_slope"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>对称绘制网翼:</span>
                            <span><ToggleSwitch v-model="symmetry_switch" left-label="左侧" right-label="右侧" /></span>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>标注该段剪裁斜率（比率）:</span>
                            <span><ToggleSwitch v-model="mark_switch" left-label="左侧" right-label="右侧" /></span>
                            <span>标注该段剪裁斜率:</span>
                            <span><ToggleSwitch v-model="mark_slope_switch" left-label="左侧" right-label="右侧" /></span>
                        </div>

                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="NextSegments">下一段</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="give-up-segments" @click="GiveUpSegments">放弃绘制</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="CleanLineInput">清空</button>
                            <button class="next-segments-warning" @click="CleanInput">全部重置</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="ReDoSteps" title="上一步"><img class="image-icon"
                                    src="/icon/arrow-go-back-line.svg" alt="上一步"></button>
                            <button class="next-segments-warning" @click="ToDoSteps" title="下一步"><img class="image-icon"
                                    src="/icon/arrow-go-forward-line.svg" alt="下一步"></button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="FinishDrawing">完成</button>
                        </div>
                    </div>


                    <div v-else-if="dataDrawingType === 'wing-right'">
                        <!-- 绘制网翼 -->
                        <div class="option-diagram-title-1">
                            <p>下网翼: 第{{ segments }}段</p>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网 翼 目 大 :</span>
                            <span><input v-model="value_1" type="text" :placeholder="text_metric_parameters"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>网翼纵向目数:</span>
                            <span><input v-model="value_2" type="text" :placeholder="text_vertical_mesh"></span>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网翼横向目数:</span>
                            <span><input v-model="value_3" type="text" :placeholder="text_horizontal_mesh"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>边旁剪裁斜率 :</span>
                            <span><input v-model="value_4" type="text" :placeholder="text_cutting_slope"></span>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>宕眼剪裁斜率 :</span>
                            <span><input v-model="value_5" type="text" :placeholder="text_eye_cutting_slope"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>对称绘制网翼:</span>
                            <span><ToggleSwitch v-model="symmetry_switch" left-label="左侧" right-label="右侧" /></span>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>标注该段剪裁斜率（比率）:</span>
                            <span><ToggleSwitch v-model="mark_switch" left-label="左侧" right-label="右侧" /></span>
                            <span>标注该段剪裁斜率:</span>
                            <span><ToggleSwitch v-model="mark_slope_switch" left-label="左侧" right-label="右侧" /></span>
                        </div>

                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="NextSegments">下一段</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="give-up-segments" @click="GiveUpSegments">放弃绘制</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="CleanLineInput">清空</button>
                            <button class="next-segments-warning" @click="CleanInput">全部重置</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="ReDoSteps" title="上一步"><img class="image-icon"
                                    src="/icon/arrow-go-back-line.svg" alt="上一步"></button>
                            <button class="next-segments-warning" @click="ToDoSteps" title="下一步"><img class="image-icon"
                                    src="/icon/arrow-go-forward-line.svg" alt="下一步"></button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="FinishDrawing">完成</button>
                        </div>
                    </div>

                    <div v-else-if="dataDrawingType === 'wing-body'">
                        <!-- 绘制网翼 -->
                        <div class="option-diagram-title-1">
                            <p>网身: 第{{ segments }}段</p>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网 身 目 大 :</span>
                            <span><input v-model="value_1" type="text" :placeholder="text_metric_parameters"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>网身纵向目数:</span>
                            <span><input v-model="value_2" type="text" :placeholder="text_vertical_mesh"></span>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网身横向目数:</span>
                            <span><input v-model="value_3" type="text" :placeholder="text_horizontal_mesh"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>边旁剪裁斜率 :</span>
                            <span><input v-model="value_4" type="text" :placeholder="text_cutting_slope"></span>
                        </div>

                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="NextSegments">下一段</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="give-up-segments" @click="GiveUpSegments">放弃绘制</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="CleanLineInput">清空</button>
                            <button class="next-segments-warning" @click="CleanInput">全部重置</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="ReDoSteps" title="上一步"><img class="image-icon"
                                    src="/icon/arrow-go-back-line.svg" alt="上一步"></button>
                            <button class="next-segments-warning" @click="ToDoSteps" title="下一步"><img class="image-icon"
                                    src="/icon/arrow-go-forward-line.svg" alt="下一步"></button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="FinishDrawing">完成</button>
                        </div>

                    </div>
                </Transition>

            </div>
            <div v-else-if="dataNetType === 'four-slices-type'">
                <Transition name="fade" mode="out-in">
                    <div v-if="dataDrawingType === 'wing-left'">
                        <!-- 绘制网翼 -->
                        <div class="option-diagram-title-1">
                            <p v-if="segments === 1">上网翼: 第{{ segments }}段(网口段)</p>
                            <p v-else>上网翼: 第{{ segments }}段</p>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网 翼 目 大 :</span>
                            <span><input v-model="value_1" type="text" :placeholder="text_metric_parameters"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>网翼纵向目数:</span>
                            <span><input v-model="value_2" type="text" :placeholder="text_vertical_mesh"></span>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网翼横向目数:</span>
                            <span><input v-model="value_3" type="text" :placeholder="text_horizontal_mesh"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>边旁剪裁斜率 :</span>
                            <span><input v-model="value_4" type="text" :placeholder="text_cutting_slope"></span>
                        </div>

                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="NextSegments">下一段</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="give-up-segments" @click="GiveUpSegments">放弃绘制</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="CleanLineInput">清空</button>
                            <button class="next-segments-warning" @click="CleanInput">全部重置</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="ReDoSteps" title="上一步"><img class="image-icon"
                                    src="/icon/arrow-go-back-line.svg" alt="上一步"></button>
                            <button class="next-segments-warning" @click="ToDoSteps" title="下一步"><img class="image-icon"
                                    src="/icon/arrow-go-forward-line.svg" alt="下一步"></button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="FinishDrawing">完成</button>
                        </div>
                    </div>
                    <div v-else-if="dataDrawingType === 'wing-right'">
                        <!-- 绘制网翼 -->
                        <div class="option-diagram-title-1">
                            <p>下网翼: 第{{ segments }}段</p>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网 翼 目 大 :</span>
                            <span><input v-model="value_1" type="text" :placeholder="text_metric_parameters"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>网翼纵向目数:</span>
                            <span><input v-model="value_2" type="text" :placeholder="text_vertical_mesh"></span>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网翼横向目数:</span>
                            <span><input v-model="value_3" type="text" :placeholder="text_horizontal_mesh"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>边旁剪裁斜率 :</span>
                            <span><input v-model="value_4" type="text" :placeholder="text_cutting_slope"></span>
                        </div>

                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="NextSegments">下一段</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="give-up-segments" @click="GiveUpSegments">放弃绘制</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="CleanLineInput">清空</button>
                            <button class="next-segments-warning" @click="CleanInput">全部重置</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="ReDoSteps" title="上一步"><img class="image-icon"
                                    src="/icon/arrow-go-back-line.svg" alt="上一步"></button>
                            <button class="next-segments-warning" @click="ToDoSteps" title="下一步"><img class="image-icon"
                                    src="/icon/arrow-go-forward-line.svg" alt="下一步"></button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="FinishDrawing">完成</button>
                        </div>
                    </div>
                    <div v-else-if="dataDrawingType === 'wing-side'">
                        <!-- 绘制网翼 -->
                        <div class="option-diagram-title-1">
                            <p>侧边网翼: 第{{ segments }}段</p>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网 翼 目 大 :</span>
                            <span><input v-model="value_1" type="text" :placeholder="text_metric_parameters"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>网翼纵向目数:</span>
                            <span><input v-model="value_2" type="text" :placeholder="text_vertical_mesh"></span>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网翼横向目数:</span>
                            <span><input v-model="value_3" type="text" :placeholder="text_horizontal_mesh"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>边旁剪裁斜率 :</span>
                            <span><input v-model="value_4" type="text" :placeholder="text_cutting_slope"></span>
                        </div>

                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="NextSegments">下一段</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="give-up-segments" @click="GiveUpSegments">放弃绘制</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="CleanLineInput">清空</button>
                            <button class="next-segments-warning" @click="CleanInput">全部重置</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="ReDoSteps" title="上一步"><img class="image-icon"
                                    src="/icon/arrow-go-back-line.svg" alt="上一步"></button>
                            <button class="next-segments-warning" @click="ToDoSteps" title="下一步"><img class="image-icon"
                                    src="/icon/arrow-go-forward-line.svg" alt="下一步"></button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="FinishDrawing">完成</button>
                        </div>
                    </div>
                    <div v-else-if="dataDrawingType === 'wing-body-side'">
                        <!-- 绘制网翼 -->
                        <div class="option-diagram-title-1">
                            <p>侧边网身: 第{{ segments }}段</p>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网 身 目 大 :</span>
                            <span><input v-model="value_1" type="text" :placeholder="text_metric_parameters"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>网身纵向目数:</span>
                            <span><input v-model="value_2" type="text" :placeholder="text_vertical_mesh"></span>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网身横向目数:</span>
                            <span><input v-model="value_3" type="text" :placeholder="text_horizontal_mesh"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>边旁剪裁斜率 :</span>
                            <span><input v-model="value_4" type="text" :placeholder="text_cutting_slope"></span>
                        </div>

                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="NextSegments">下一段</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="give-up-segments" @click="GiveUpSegments">放弃绘制</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="CleanLineInput">清空</button>
                            <button class="next-segments-warning" @click="CleanInput">全部重置</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="ReDoSteps" title="上一步"><img class="image-icon"
                                    src="/icon/arrow-go-back-line.svg" alt="上一步"></button>
                            <button class="next-segments-warning" @click="ToDoSteps" title="下一步"><img class="image-icon"
                                    src="/icon/arrow-go-forward-line.svg" alt="下一步"></button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="FinishDrawing">完成</button>
                        </div>

                    </div>
                    <div v-else-if="dataDrawingType === 'wing-body'">
                        <!-- 绘制网翼 -->
                        <div class="option-diagram-title-1">
                            <p>网身: 第{{ segments }}段</p>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网 身 目 大 :</span>
                            <span><input v-model="value_1" type="text" :placeholder="text_metric_parameters"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>网身纵向目数:</span>
                            <span><input v-model="value_2" type="text" :placeholder="text_vertical_mesh"></span>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网身横向目数:</span>
                            <span><input v-model="value_3" type="text" :placeholder="text_horizontal_mesh"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>边旁剪裁斜率 :</span>
                            <span><input v-model="value_4" type="text" :placeholder="text_cutting_slope"></span>
                        </div>

                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="NextSegments">下一段</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="give-up-segments" @click="GiveUpSegments">放弃绘制</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="CleanLineInput">清空</button>
                            <button class="next-segments-warning" @click="CleanInput">全部重置</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="ReDoSteps" title="上一步"><img class="image-icon"
                                    src="/icon/arrow-go-back-line.svg" alt="上一步"></button>
                            <button class="next-segments-warning" @click="ToDoSteps" title="下一步"><img class="image-icon"
                                    src="/icon/arrow-go-forward-line.svg" alt="下一步"></button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="FinishDrawing">完成</button>
                        </div>

                    </div>
                </Transition>

            </div>


            <div v-else-if="dataNetType === 'six-slices-type' && false">
                <Transition name="fade" mode="out-in">
                    <div v-if="dataDrawingType === 'wing-left'">
                        <!-- 绘制网翼 -->
                        <div class="option-diagram-title-1">
                            <p v-if="segments === 1">上网翼: 第{{ segments }}段(网口段)</p>
                            <p v-else>上网翼: 第{{ segments }}段</p>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网 翼 目 大 :</span>
                            <span><input v-model="value_1" type="text" :placeholder="text_metric_parameters"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>网翼纵向目数:</span>
                            <span><input v-model="value_2" type="text" :placeholder="text_vertical_mesh"></span>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网翼横向目数:</span>
                            <span><input v-model="value_3" type="text" :placeholder="text_horizontal_mesh"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>边旁剪裁斜率 :</span>
                            <span><input v-model="value_4" type="text" :placeholder="text_cutting_slope"></span>
                        </div>

                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="NextSegments">下一段</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="give-up-segments" @click="GiveUpSegments">放弃绘制</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="CleanLineInput">清空</button>
                            <button class="next-segments-warning" @click="CleanInput">全部重置</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="ReDoSteps" title="上一步"><img class="image-icon"
                                    src="/icon/arrow-go-back-line.svg" alt="上一步"></button>
                            <button class="next-segments-warning" @click="ToDoSteps" title="下一步"><img class="image-icon"
                                    src="/icon/arrow-go-forward-line.svg" alt="下一步"></button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="FinishDrawing">完成</button>
                        </div>
                    </div>
                    <div v-else-if="dataDrawingType === 'wing-right'">
                        <!-- 绘制网翼 -->
                        <div class="option-diagram-title-1">
                            <p>下网翼: 第{{ segments }}段</p>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网 翼 目 大 :</span>
                            <span><input v-model="value_1" type="text" :placeholder="text_metric_parameters"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>网翼纵向目数:</span>
                            <span><input v-model="value_2" type="text" :placeholder="text_vertical_mesh"></span>
                        </div>
                        <div class="option-diagram-title-2">
                            <span>网翼横向目数:</span>
                            <span><input v-model="value_3" type="text" :placeholder="text_horizontal_mesh"></span>
                        </div>
                        <div class="option-diagram-title-1">
                            <span>边旁剪裁斜率 :</span>
                            <span><input v-model="value_4" type="text" :placeholder="text_cutting_slope"></span>
                        </div>

                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="NextSegments">下一段</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="give-up-segments" @click="GiveUpSegments">放弃绘制</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="CleanLineInput">清空</button>
                            <button class="next-segments-warning" @click="CleanInput">全部重置</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="ReDoSteps" title="上一步"><img class="image-icon"
                                    src="/icon/arrow-go-back-line.svg" alt="上一步"></button>
                            <button class="next-segments-warning" @click="ToDoSteps" title="下一步"><img class="image-icon"
                                    src="/icon/arrow-go-forward-line.svg" alt="下一步"></button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="FinishDrawing">完成</button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments-warning" @click="ReDoSteps" title="上一步"><img class="image-icon"
                                    src="/icon/arrow-go-back-line.svg" alt="上一步"></button>
                            <button class="next-segments-warning" @click="ToDoSteps" title="下一步"><img class="image-icon"
                                    src="/icon/arrow-go-forward-line.svg" alt="下一步"></button>
                        </div>
                        <div class="option-diagram-title-3">
                            <button class="next-segments" @click="FinishDrawing">完成</button>
                        </div>
                    </div>
                </Transition>
            </div>
            <div v-else-if="dataDrawingType === 'wing-body'">
                <!-- 绘制网翼 -->
                <div class="option-diagram-title-1">
                    <p>网身: 第{{ segments }}段</p>
                </div>
                <div class="option-diagram-title-2">
                    <span>网 身 目 大 :</span>
                    <span><input v-model="value_1" type="text" :placeholder="text_metric_parameters"></span>
                </div>
                <div class="option-diagram-title-1">
                    <span>网身纵向目数:</span>
                    <span><input v-model="value_2" type="text" :placeholder="text_vertical_mesh"></span>
                </div>
                <div class="option-diagram-title-2">
                    <span>网身横向目数:</span>
                    <span><input v-model="value_3" type="text" :placeholder="text_horizontal_mesh"></span>
                </div>
                <div class="option-diagram-title-1">
                    <span>边旁剪裁斜率 :</span>
                    <span><input v-model="value_4" type="text" :placeholder="text_cutting_slope"></span>
                </div>

                <div class="option-diagram-title-3">
                    <button class="next-segments" @click="NextSegments">下一段</button>
                </div>
                <div class="option-diagram-title-3">
                    <button class="give-up-segments" @click="GiveUpSegments">放弃绘制</button>
                </div>
                <div class="option-diagram-title-3">
                    <button class="next-segments-warning" @click="CleanLineInput">清空</button>
                    <button class="next-segments-warning" @click="CleanInput">全部重置</button>
                </div>
                <div class="option-diagram-title-3">
                    <button class="next-segments-warning" @click="ReDoSteps" title="上一步"><img class="image-icon"
                            src="/icon/arrow-go-back-line.svg" alt="上一步"></button>
                    <button class="next-segments-warning" @click="ToDoSteps" title="下一步"><img class="image-icon"
                            src="/icon/arrow-go-forward-line.svg" alt="下一步"></button>
                </div>
                <div class="option-diagram-title-3">
                    <button class="next-segments" @click="FinishDrawing">完成</button>
                </div>

            </div>
        </Transition>
    </div>

</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { getCurrentWindow } from '@tauri-apps/api/window';

import ToggleSwitch from './components/tool/switch.vue';

const value_1 = ref("");  //  目大参数 Metric parameters
const value_2 = ref("");  //  纵向目数 Vertical mesh
const value_3 = ref("");  //  横向目数 Horizontal mesh
const value_4 = ref("");  //  剪裁斜率 Cutting slope
const value_5 = ref("");  //  宕眼剪裁斜率 Down eye slope
const value_1_copy = ref("");  //  继承参数：目大参数 Metric parameters
const value_2_copy = ref("");  //  继承参数：纵向目数 Vertical mesh
const value_3_copy = ref("");  //  继承参数：横向目数 Horizontal mesh
const value_4_copy = ref("");  //  继承参数：剪裁斜率 Cutting slopse
const value_5_copy = ref("");  //  继承参数：宕眼剪裁斜率 Down eye slope

const text_metric_parameters = ref("请输入目大");
const text_vertical_mesh = ref("请输入纵向目数");
const text_horizontal_mesh = ref("请输入横向目数");
const text_cutting_slope = ref("请输入剪裁斜率 默认:1-1");
const text_eye_cutting_slope =  ref("请输入宕眼剪裁斜率 默认:1-1");
const symmetry_switch = ref(false);  // 确认对称画图
const mark_switch = ref(false);  // 确认标注剪裁斜率
const mark_slope_switch = ref(false);  // 确认标注剪裁斜率


const value_send_obj = ref({});  //  socket 序列化待传递参数
const segments = ref(1);
const stepStack = ref({});
const result_origin_pos_list = ref([]);
const step = ref(1);
const currentStep = ref(1);
const have_ori_step = ref(false);
const emit = defineEmits(['sendStatueInfo', 'update:dataNetType'])
const props = defineProps({
    mainConfig: {  //  主配置项
        type: Object,
        required: true
    },
    dataDrawingType: {  //  绘制部位类型
        type: String,
        required: true
    },
    dataNetType: {  //  拖网类型
        type: [String, null],
        required: true
    },
    themeState: { // 标准 v-model 属性名
        type: Object,
        required: true
    },
    sendNetArgs: {
        type: Function,
        required: true
    },
    originPosition: {
        type: String,
        required: true
    }
})

watch(
    () => props.dataDrawingType,
    (newVal, oldVal) => {
        if (newVal !== oldVal) {
            CleanInLineInput()
        }
    }
);

const ToDoSteps = () => {
    if (currentStep.value < steps.value.length) {
        currentStep.value += 1;
        props.sendNetArgs({ "--todo-step": 1 })
    }
    else {
        emit("sendStatueInfo", props.mainConfig["err-msg"]["set-default-ori-pos"])
    }

};
const ReDoSteps = () => {
    currentStep.value -= 1;
    props.sendNetArgs({ "--redo-step": 1 })

};

const NextSegments = () => {  // 下一段
    if (props.dataDrawingType === "wing-body") {
        have_ori_step.value = true;  // 绘图界面已完成初始绘画块后续参数可以允许继承
    }
    if (have_ori_step.value) {
        copyArgs()
        if (value_1.value === "") {
            emit("sendStatueInfo", props.mainConfig["err-msg"]["no-v1-value"]);
            return 0;
        }
        if (value_2.value === "") {
            emit("sendStatueInfo", props.mainConfig["err-msg"]["no-v2-value"]);
            return 0;
        }
        if (value_3.value === "") {
            emit("sendStatueInfo", props.mainConfig["err-msg"]["no-v3-value"]);
            return 0;
        }
        changePlaceholderText()
        if (result_origin_pos_list.value.length === 0) {
            console.log(props.originPosition);
            emit("sendStatueInfo", props.mainConfig["err-msg"]["set-default-ori-pos"])
            const matches = props.originPosition.match(/-?\d+(\.\d+)?/g);
            result_origin_pos_list.value = matches ? matches.map(Number) : [0, 0];
            console.log(result_origin_pos_list.value); // 输出: [0, 0]
        }
        if (value_4.value.length === 0) {
            value_4.value = "1-1";
        }
        if (value_5.value.length === 0) {
            value_5.value = "1-1";
        }
        value_send_obj.value = {
            "node": step.value,  // 节点编号
            "netType": props.dataNetType,  // 拖网类型
            "partType": props.dataDrawingType,  // 绘制部位类型
            "originPosition": result_origin_pos_list.value,  // 原点位置
            "CurrentNumberOfSegments": segments.value,  // 当前段数
            "MetricParameters": value_1.value,  // 目大参数
            "VerticalMesh": value_2.value,  // 纵向目数
            "HorizontalMesh": value_3.value,  // 横向目数
            "CuttingSlope": value_4.value,  // 剪裁斜率
            "EyeCuttingSlope": value_5.value,  // 宕眼剪裁斜率
            "SymmetrySwitch": symmetry_switch.value,  //  确认是否对称画图
            "MarkSwitch": mark_switch.value,  //   确认是否标注本次剪裁斜率（比率）
            "MarkSlopeSwitch": mark_slope_switch.value,  //   确认是否标注本次剪裁斜率
        }
        props.sendNetArgs(value_send_obj.value)
        stepStack.value[step.value] = value_send_obj.value;
        segments.value += 1;
        step.value += 1;
        currentStep.value = step.value;
        CleanLineInput()
    } else {
        emit("sendStatueInfo", props.mainConfig["err-msg"]["no-first-step"]);

    }

}

const GiveUpSegments = async () => {
    // 使用 Tauri 的确认对话框
    const confirmed = await confirm('确定要放弃当前绘制吗？所有进度将丢失。', {
        title: '确认放弃绘制',
        type: 'warning'
    });

    // 如果用户点击"确定"，则执行放弃操作
    if (confirmed) {
        CleanInLineInput();
        step.value = 1
        props.sendNetArgs({ "--give-up-drawing": 1 })
        emit('update:dataNetType', null)
    }
    // 如果用户点击"取消"，则什么也不做
}

const CleanLineInput = () => {  // 清空
    value_1.value = "";
    value_2.value = "";
    value_3.value = "";
    value_4.value = "";
    value_5.value = "";
    value_send_obj.value = "";
    symmetry_switch.value = false;
    mark_switch.value = false;
    mark_slope_switch.value = false;
}
const CleanInLineInput = () => {  // 清空当前输入行
    segments.value = 1;
    value_1.value = "";
    value_2.value = "";
    value_3.value = "";
    value_4.value = "";
    value_5.value = "";
    value_send_obj.value = "";
    symmetry_switch.value = false;
    mark_switch.value = false;
    mark_slope_switch.value = false;
}

const CleanInput = () => {  // 全部重置
    segments.value = 1;
    value_1.value = "";
    value_2.value = "";
    value_3.value = "";
    value_4.value = "";
    value_5.value = "";
    value_send_obj.value = "";
    symmetry_switch.value = false;
    mark_switch.value = false;
    mark_slope_switch.value = false;
}

const copyArgs = () => {
    if (value_1.value !== "") {
        value_1_copy.value = value_1.value;
    } else {
        value_1.value = value_1_copy.value;
    }
    if (value_2.value !== "") {
        value_2_copy.value = value_2.value;
    } else {
        value_2.value = value_2_copy.value;
    }
    if (value_3.value !== "") {
        value_3_copy.value = value_3.value;
    } else {
        value_3.value = value_3_copy.value;
    }
    value_4_copy.value = value_4.value;
    value_5_copy.value = value_5.value;

}
const changePlaceholderText = () => {
    if (value_1_copy.value !== "") {
        text_metric_parameters.value = `请输入目大 默认：${value_1_copy.value}`;
        text_vertical_mesh.value = `请输入纵向目数 默认：${value_2_copy.value}`;
        text_horizontal_mesh.value = `请输入横向目数 默认：${value_3_copy.value}`;
    }
}

const FinishDrawing = async () => {
    // 使用 Tauri 的确认对话框
    const confirmed = await confirm('确认已完成该拖网的绘制？\n完成后无法回退修改。', {
        title: '确认放弃绘制',
        type: 'warning'
    });

    // 如果用户点击"确定"，则执行放弃操作
    if (confirmed) {
        value_send_obj.value = {
            "--exit": 0
        }
        props.sendNetArgs(value_send_obj.value)
    }
    // 如果用户点击"取消"，则什么也不做
}

onMounted(async () => {
    // 监听窗口关闭事件
    await getCurrentWindow().onCloseRequested(async () => {
        try {
            // 调用你希望在关闭前执行的函数
            // await invoke('on_before_close');
            props.sendNetArgs({ "--exit": -1 })

        } catch (error) {
            console.error('执行关闭前逻辑时出错:', error);
        }
    });
});
</script>

<style scoped>
.option-diagram {
    font-family: '宋体', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    float: left;
    /* 默认左浮动 */
    width: 60%;
    box-sizing: border-box;
    display: block;
    margin: 0;
    padding: 0;
    background-attachment: fixed;
    /* overflow: hidden; */
    /* position: fixed; */
    left: 0;
    transition: background-color 0.5s ease, color 0.5s ease;
}

.option-diagram.dark {
    background-color: var(--dark-background-color--left-actionbar);
}

.option-diagram.light {
    background-color: var(--light-background-color--left-actionbar);
}

.option-diagram p {
    font-size: 3vw;
    font-weight: 900;
    display: inline;
}


.option-diagram.dark .option-diagram-title-1 {
    background-color: rgba(43, 43, 43, 0.6);

}

.option-diagram.dark .option-diagram-title-2 {

    background-color: rgba(60, 63, 65, 0.6);

}

.option-diagram.dark .option-diagram-title-3 {
    background-color: rgba(60, 63, 65, 0.6);

}

.option-diagram.dark .next-segments {
    background-color: rgba(31, 147, 207, 0.5);
    border-color: rgba(0, 102, 157, 0.6);

}

.option-diagram.dark .next-segments-warning {
    background-color: rgba(221, 179, 64, 0.5);
    border-color: rgba(194, 83, 43, 0.6);

}

.option-diagram.dark .give-up-segments {
    background-color: rgba(207, 16, 32, 0.5);
    border-color: rgba(232, 17, 35, 0.6);

}




.option-diagram.light .option-diagram-title-1 {
    background-color: rgba(172, 172, 172, 0.8);
}

.option-diagram.light .option-diagram-title-2 {
    background-color: rgba(195, 195, 195, 0.8);
}

.option-diagram.light .option-diagram-title-3 {
    background-color: rgba(195, 195, 195, 0.8);
}

.option-diagram.light .next-segments {
    background-color: rgba(43, 170, 163, 0.5);
    border-color: rgba(41, 184, 219, 0.6);

}

.option-diagram.light .give-up-segments {
    background-color: rgba(201, 32, 46, 0.5);
    border-color: rgba(232, 17, 35, 0.6);

}

.option-diagram.light .next-segments-warning {
    background-color: rgba(3232, 191, 98, 0.5);
    border-color: rgba(232, 149, 42, 0.6);

}

input {
    width: 25vw;
    height: 3vh;
    border-radius: 1rem;
    border: 0px solid rgb(255, 255, 255);

    display: inline-block;

}

input:hover {
    filter:
        drop-shadow(0 0 0.1rem rgba(250, 236, 191, 0.1)) drop-shadow(0 0 0.2rem rgba(254, 203, 28, 0.2)) drop-shadow(0 0 0.5rem rgba(72, 204, 252, 0.9));
}

input::before:hover {
    filter:
        drop-shadow(0 0 0.5rem rgba(250, 236, 191, 0.1)) drop-shadow(0 0 1rem rgba(255, 221, 110, 0.2)) drop-shadow(0 0 1.5rem rgba(72, 204, 252, 0.9));
    /* 更接近时的阴影效果 */
}

input:active {
    filter:
        drop-shadow(0 0 0.2rem rgba(250, 236, 191, 0.1)) drop-shadow(0 0 0.3rem rgba(254, 203, 28, 0.2)) drop-shadow(0 0 0.5rem rgba(1, 121, 212, 0.9));

}



.option-diagram-title-1,
.option-diagram-title-2 {
    text-align: center;
    padding: 0.1vh 0;
    width: 100%;
    line-height: 8vh;
    margin: auto 0;


}

.option-diagram-title-3 {
    width: 100%;
    /* flex: 1; */
    height: 6.8vh;
    /* 自动撑满剩余空间 */
    line-height: 8.5vh;
    text-align: center;
}

span {
    font-size: 1.5vw;
    margin: 2vw;
}

.image-icon {
    width: 2vw;
    height: 2vw;
}

.next-segments {
    font-size: 1.5vw;
    height: 3.5vh;
    width: 35vw;
    margin: auto 2em;
    border: 0px solid rgb(255, 255, 255);
    border-radius: 0.5rem;

}

.give-up-segments {
    font-size: 1.5vw;
    height: 3.5vh;
    width: 35vw;
    margin: auto 2em;
    border: 0px solid rgb(255, 255, 255);
    border-radius: 0.5rem;

}

.next-segments-warning {
    font-size: 1.5vw;
    height: 3.5vh;
    width: 16vw;
    margin: auto 1em;
    border: 0px solid rgb(255, 255, 255);
    border-radius: 0.5rem;

}

.next-segments:hover {
    filter:
        drop-shadow(0 0 0.1rem rgba(101, 235, 114, 0.1)) drop-shadow(0 0 0.2rem rgba(76, 200, 177, 0.2)) drop-shadow(0 0 0.5rem rgba(70, 200, 221, 0.9));
}

.next-segments:active {
    filter:
        drop-shadow(0 0 0.2rem rgba(18, 115, 168, 0.1)) drop-shadow(0 0 0.3rem rgba(7, 108, 180, 0.2)) drop-shadow(0 0 0.5rem rgba(0, 111, 195, 0.9));

}

.next-segments-warning:hover {
    filter:
        drop-shadow(0 0 0.1rem rgba(226, 192, 124, 0.1)) drop-shadow(0 0 0.2rem rgba(213, 175, 192, 0.2)) drop-shadow(0 0 0.5rem rgba(233, 184, 49, 0.9));
}

.next-segments-warning:active {
    filter:
        drop-shadow(0 0 0.1rem rgba(226, 192, 124, 0.3)) drop-shadow(0 0 0.2rem rgba(213, 175, 192, 0.5)) drop-shadow(0 0 0.6rem rgba(241, 183, 26, 0.9));

}


@media (prefers-color-scheme: light) {}

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