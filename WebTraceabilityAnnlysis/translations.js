// 垃圾类别中英文翻译
const CLASS_TRANSLATIONS = {
    'beer bottle': '啤酒瓶',
    'tire': '轮胎',
    'plastic shell': '塑料壳',
    'gunny sack': '麻袋',
    'plastic bottle': '塑料瓶',
    'can': '罐子',
    'fishing gear': '渔具',
    'ointment': '药膏',
    'plastic bag': '塑料袋',
    'plastic packaging bag': '塑料包装袋',
    'glove': '手套',
    'ground cage': '地笼',
    'fishing net': '渔网'
};

function translateClassName(className) {
    return CLASS_TRANSLATIONS[className] || className;
}