/**
 * zTree树形组件
 * 
 * @author
 * @module $.fn.extend
 * @class tree
 */
/* 
 * 使用工厂模式，是封装的ztree方法可以根据参数不同创建不同的对象，
 * 主要是为了解决同一个页面多次调用ztree时参数会互相覆盖的情况
 */
(function(factory) {
    // 启用严格模式
    "use strict";
    // 环境探测语句：如果采用了AMD异步加载模块的方式
    if (typeof define === 'function' && define.amd) {
        // 启用AMD模块化
        define(['jquery'], factory);
    } else if (typeof exports === 'object' && typeof require === 'function') {
        // 如果采用了CommonJS的模块加载方式，启用CommonJS模块化
        factory(require('jquery'));
    } else {
        // 原生JS调用工厂模式
        factory(jQuery);
    }
}(function($, undefined) {
    // 启用严格模式
    "use strict";

    /**
     * @title 创建下拉树所在的Div
     * @method createDivContainer
     * @return div 包裹zTree的div对象
     */

    function createDivContainer() {

        var div = document.createElement('div');

        div.className = 'menuContent';
        div.style.position = 'absolute';
        div.style.display = 'none';

        return div;
    }

    /**
     * @title 显示下拉菜单
     * @method showTree
     * @param divContainer 包裹下拉框的树容器
     * @param treeObj 树对象
     */

    function showTree(divContainer, treeObj) {

        // 以滑动方式显示隐藏的div容器
        divContainer.slideDown('fast');
        // 给当前页面绑定事件
        $("html").bind("mousedown", [divContainer, treeObj], onMouseDown);
    }

    /**
     * @title 隐藏下拉菜单
     * @method hideTree
     * @param divContainer
     *            包裹下拉框的树容器
     * @param treeObj
     *            树对象
     */

    function hideTree(divContainer, treeObj) {

        // 获取zTree的options
        var options = treeObj.setting;
        // 获取绑定ztree的input输入框的jQuery对象
        var inputObj = options.inputObj;
        // 获取绑定ztree的隐藏域的jQuery对象
        var hideObj = options.hideObj;

        // 获取默认选项的值
        var defaultOptionLabel = options.defaultOptionLabel || '';

        // 如果隐藏域的值为空，则清掉文本框中的值
        if (hideObj && hideObj.val() == '') {
            inputObj.val(defaultOptionLabel);
        }

        // 使用淡出效果来隐藏容器
        divContainer.fadeOut("fast");
        // 解绑鼠标按下事件
        $("html").unbind("mousedown", onMouseDown);
    }

    /**
     * @title 鼠标按下时绑定的事件 (鼠标按下时不在zTree所在下拉菜单范围内，则隐藏下拉菜单)
     * @method onMouseDown
     * @param event 对象
     */

    function onMouseDown(event) {

        // 在绑定鼠标按下事件时传递了两个参数，第一个参数为divContainer（包裹zTree下拉框的的div的jQuery对象）
        // 第二个参数为 treeObj（树对象）
        var param = event.data;
        var treeObj = param[1];
        var divContainer = param[0];
        // 获取输入框的jQuery对象
        var inputObj = treeObj.setting.inputObj;

        // event.target是指触发了鼠标按下事件的dom元素
        if (!($(event.target) == inputObj || $(event.target) == param || $(event.target).parents('.' + divContainer.attr('class')).length > 0)) {
            hideTree(divContainer, treeObj);
        }
    }

    /**
     * @title 得到ztree展开节点信息的cookie的数组
     * @method getCookieArray
     * @retrun z_tree 存放ztree展开节点信息的cookie数组
     */

    function getCookieArray() {

        // 获取名称为z_tree的cookie
        var cookie = $.cookie("z_tree");
        // 定义接收cookie的数组
        var z_tree = new Array();
        // 判断如果cookie存在，将cookie根据‘，’拆分并赋值给接收cookie的数组
        if (cookie) {
            z_tree = cookie.split(",");
        }
        return z_tree;
    }

    /**
     * @title 获取当前页面的actionName
     * @method getCurrentActionName
     * @retrun actionName 当前页面的actionname
     */

    function getCurrentActionName() {

        var currentUrl = window.location.href;
        // 截取最后一个'/'和'.do'之间的string，即为actionName，这么做是为了防止url过长
        var actionName = currentUrl.substring(0, currentUrl.lastIndexOf(".do"));
        actionName = actionName.substring(actionName.lastIndexOf("/") + 1, actionName.length - 1);
        return actionName;
    }

    /**
     * @title 展开节点事件 (展开节点时如果需要保持状态，则将节点信息拼接放入cookie中)
     * @method _onExpand
     * @param event 展开节点的事件
     * @param treeId ztree的ID
     * @param treeNode 当前节点对象
     */

    function _onExpand(event, treeId, treeNode) {

        // 获取树对象
        var treeObj = getTreeObj(treeId);
        // 获取树的参数
        var options = treeObj.setting;
        // 获取是否保持展开闭合状态
        var keepStatus = options.keepStatus;

        // 如果不需要保存展开闭合状态，阻断方法
        if (!keepStatus) {
            return;
        }
        // 得到cookie的数组
        var z_tree = getCookieArray();

        // 定义当前节点是否存在于cookie中的标识
        var isHave = false;

        // 获取当前页面的actionName
        var actionName = getCurrentActionName();
        // 为了防止页面之间cookie混乱，拼接当前页面actionName以及treeId
        var currentMsg = actionName + '@' + treeNode.id + '@' + treeId;
        // 遍历cookie所在的数组，判断
        for (var i = 0; i < z_tree.length; i++) {
            if (currentMsg == z_tree[i]) {
                isHave = true;
                break;
            }
        }
        // 如果当前节点不存在于cookie之中，则放至cookie
        if (!isHave) {
            z_tree.push(currentMsg);
        }

        // 把数组生成逗号分隔的字符串
        var z_tree_str = z_tree.join(',');
        // 将拼接好的字符串放至cookie
        $.cookie("z_tree", z_tree_str);
    }

    /**
     * @title 闭合某一节点，并把该节点和所有子节点从cookie中移除 （如果不移除子节点，当子节点处于展开状态，只闭合父节点不起作用）
     * @method _onCollapse
     * @param event 闭合节点的事件
     * @param treeId ztree的ID
     * @param treeNode 当前节点对象
     */

    function _onCollapse(event, treeId, treeNode) {

        // 获取树对象
        var treeObj = getTreeObj(treeId);
        // 获取树的参数
        var options = treeObj.setting;
        // 获取是否保持展开闭合状态
        var keepStatus = options.keepStatus;

        // 如果不需要保存展开闭合状态，阻断方法
        if (!keepStatus) {
            return;
        }

        // 得到cookie的数组
        var z_tree = getCookieArray();

        // 得到当前节点的所有子孙节点
        var nodeChildrens = getChildren(new Array(), treeNode);

        // 获取当前页面的actionName
        var actionName = getCurrentActionName();
        // 遍历当前节点及其所有的子节点
        for (var i = 0; i < nodeChildrens.length; i++) {
            var child_node_id = nodeChildrens[i];
            // 遍历ztree的cookie数组
            for (var j = 0; j < z_tree.length; j++) {
                // 如果actionName一致并且treeId一致，闭合时移除cookie
                if (actionName == z_tree[j].split('@')[0] && treeId == z_tree[j].split('@')[2]) {
                    if (child_node_id == z_tree[j].split('@')[1]) {
                        z_tree.splice(j, 1);
                        break;
                    }
                }
            }
        }

        // 把数组生成逗号分隔的字符串
        var z_tree_str = z_tree.join(',');
        // 将拼接好的字符串放至cookie
        $.cookie("z_tree", z_tree_str);
    }

    /**
     * @title 递归获取某一节点下所有子节点
     * @method getChildren
     * @param ids 数组
     * @param treeNode 需要递归的节点对象
     */

    function getChildren(ids, treeNode) {

        ids.push(treeNode.id);
        if (treeNode.isParent) {
            for (var obj in treeNode.children) {
                getChildren(ids, treeNode.children[obj]);
            }
        }

        return ids;
    }

    /**
     * @title 根据选中节点给页面绑定ztree的文本域和隐藏域赋值
     * @method setDefaultValue
     * @param nodes 选中的节点集合
     * @param $inputObj 需要赋值的input对象
     * @param $hideObj 需要赋值的隐藏域对象
     * @return boolean true 或者 false 是否需要隐藏下拉菜单
     */

    function setDefaultValue(nodes, $inputObj, $hideObj) {

        // 选中的节点的value
        var nodesValue = "";
        // 选中节点的id
        var nodesID = "";
        /* 
         * 如果是下拉菜单，则需要赋值操作，
         * 此处判断依据是左侧树不需要绑定到input，所以inputObj就是zTree所在的UL标签本身
         */
        if ($inputObj.get(0).tagName !== 'UL') {

            // 接收选中节点的长度
            var length = nodes.length;
            for (var i = 0; i < length; i++) {
                // input中的值显示拼接使用中文逗号
                nodesValue += nodes[i].name + "，";
                // 隐藏域中的值使用英文逗号拼接
                nodesID += nodes[i].id + ",";
            }
            // 如果回填至input的值的长度大于0，截取最后一个逗号
            if (nodesValue.length > 0) {
                nodesValue = nodesValue.substring(0, nodesValue.length - 1);
            }
            // 如果回填至隐藏域的值的长度大于0，截取最后一个逗号
            if (nodesID.length > 0) {
                nodesID = nodesID.substring(0, nodesID.length - 1);
            }
            // 将拼接好的值回填至input
            $inputObj.prop("value", nodesValue);
            // 将拼接好的值回填至隐藏域
            $hideObj.prop("value", nodesID);
            // 赋值结束返回true表示需要隐藏下拉菜单
            return true;
        } else {
            // 如果是左侧树返回false，不要隐藏下拉菜单
            return false;
        }
    }

    /**
     * @title 获取ztree对象
     * @param treeId ztree的Id
     * @retun zTreeObj ztree的对象
     */

    function getTreeObj(treeId) {
        return $.fn.zTree.getZTreeObj(treeId);
    }

    /**
     * @title 节点单击事件
     * @method _onClick
     * @param event 单击节点的事件
     * @param treeId ztree的ID
     * @param treeNode 当前节点
     */

    function _onClick(event, treeId, treeNode) {

        // zTree对象
        var zTreeObj = getTreeObj(treeId);
        // 选中的节点
        var nodes = zTreeObj.getSelectedNodes();
        // 包裹下拉框树的容器
        var divContainer = $("#" + treeId).parent();
        // zTree的参数数组
        var options = zTreeObj.setting;
        // input jQuery对象
        var $inputObj = $(options.inputObj);
        // 隐藏域对象
        var $hideObj = $(options.hideObj);
        // 自定义的选中回调函数
        var onSelectCallback = options.onSelect;

        // 给页面赋值，并根据返回值判断是否需要隐藏下拉菜单
        if (setDefaultValue(nodes, $inputObj, $hideObj)) {
            // 隐藏下拉框
            hideTree(divContainer, zTreeObj);
        }

        // 如果有自定义的回调，则执行此回调函数
        if ($.isFunction(onSelectCallback)) {
            onSelectCallback.call(zTreeObj, treeId, treeNode);
        }
    }

    /**
     * @title 复选框勾选事件
     * @method _onCheck
     * @param event 单击节点的事件
     * @param treeId ztree的ID
     * @param treeNode 当前节点
     */

    function _onCheck(event, treeId, treeNode) {

        // zTree对象
        var zTreeObj = getTreeObj(treeId);
        // 选中的节点
        var nodes = zTreeObj.getCheckedNodes();
        // zTree的参数数组
        var options = zTreeObj.setting;
        // input 对象
        var $inputObj = $(options.inputObj);
        // 隐藏域对象
        var $hideObj = $(options.hideObj);

        // 根据选中的节点给页面赋值
        setDefaultValue(nodes, $inputObj, $hideObj);

        // 自定义的选中回调函数
        var onCheckCallback = options.onCheck;

        // 如果有自定义的回调，则执行此回调函数
        if ($.isFunction(onCheckCallback)) {
            // call方法中，第一个参数为绑定回调的对象，后面依次为赋给该回调函数的参数，可为多个
            onCheckCallback.call(zTreeObj, treeId, nodes);
        }
    }

    /**
     * @title 节点选中之前的回调
     * @method _beforeClick
     * @param treeId ztree的ID
     * @param treeNode 当前节点
     */

    function _beforeClick(treeId, treeNode) {

        // 获取ztreeObj对象
        var treeObj = getTreeObj(treeId);
        // 获取当前树的参数
        var options = treeObj.setting;
        // 获取自定义的回调
        var beforeSelectCallback = options.beforeSelect;

        // 如果当前树为复选框，节点单击事件只用来选中以及取消选中而不是赋值操作
        if (options.checkEnable) {
            /* 
             * treeNode 表示当前节点；
             * !treeNode.checked 为boolean值，为true勾选，为false取消勾选；
             * 第三个参数表示是否依据chkboxType的关联关系，false表示不关联；
             * 第四个参数表示是否执行beforeCheck和onCheck回调
             */
            treeObj.checkNode(treeNode, !treeNode.checked, true, true);

            // 返回false时不会选中节点
            return false;
        } else {
            // 如果当前树为单选树，当前节点禁用,直接返回false
            if (treeNode.chkDisabled) {
                return false;
            }
        }

        // 如果存在选中之前的回调，则执行该回调
        if ($.isFunction(beforeSelectCallback)) {
            // 执行回调并取得回调函数的返回值
            var canSelect = beforeSelectCallback.call(treeObj, treeId, treeNode);
            // 返回是否可选中
            return canSelect;
        }
    }

    /**
     * @title 节点勾选之前的回调
     * @method _beforeCheck
     * @param treeId ztree的ID
     * @param treeNode 当前节点
     */

    function _beforeCheck(treeId, treeNode) {

        var treeObj = getTreeObj(treeId);
        var options = treeObj.setting;
        var beforeCheckCallback = options.beforeCheck;

        // 如果存在选中之前的回调，则执行该回调
        if ($.isFunction(beforeCheckCallback)) {
            // 获取回调函数的返回值
            var canCheck = beforeCheckCallback.call(treeObj, treeId, treeNode);
            // 返回是否可勾选
            return canCheck;
        }
    }

    // 是否强制异步默认为false
    var autoAsync = false;
    /**
     * @title 强制加载节点，为了初始化回选时能获取到节点
     * @method asyncNodes
     * @param treeObj ztree对象
     * @param nodes 需要强制异步加载其子节点的节点集合
     */

    function asyncNodes(treeObj, nodes) {

        // 如果需要强制异步加载的节点集合不存在，则阻断方法继续执行
        if (!nodes) {
            return;
        }

        // 获取需要强制异步的节点集合的长度
        var length = nodes.length;

        // 遍历需要强制异步的节点集合
        for (var i = 0; i < length; i++) {
            // 如果当前节点是父节点，并且已经进行过异步加载（避免当前节点重复异步加载）
            if (nodes[i].isParent && nodes[i].zAsync) {
                asyncNodes(treeObj, nodes[i].children);
            } else {
                // 如果执行了后台加载节点，则是否强制异步为true
                autoAsync = true;
                // 强行异步加载当前节点的子节点。
                /* 
                 * 参数说明：@param parentNode nodes[i] 指定的需要异步加载的父节点。
                 *          @parame reloadType "refresh" 表示清空后重新加载。其他值表示追加子节点
                 *          @parame isSilent true 表示是否展开父节点
                 */
                treeObj.reAsyncChildNodes(nodes[i], "refresh", true);
            }
        }
    }

    /**
     * @title 异步加载成功后的回调（异步加载默认选中必须在异步加载成功事件实现）
     * @method _onAsyncSuccess
     * @param event 异步加载的事件
     * @param treeId ztree的ID
     */

    function _onAsyncSuccess(event, treeId, treeNode) {

        // 获取树对象
        var treeObj = getTreeObj(treeId);

        // 如果treeNode为null说明是初始化需要选中，如果autoAsync为true说明是自动异步需要选中
        if (treeNode == null || autoAsync) {
            // 异步加载完成之后默认选中
            defaultSelect(treeObj, treeNode);
        }
    }

    /**
     * @title 默认选中(根据隐藏域的值默认选中节点)
     * @method defaultSelect
     * @param treeObj ztree对象
     * @param treeNode 当前点击的节点
     */

    function defaultSelect(treeObj, treeNode) {

        // 获取树的参数
        var options = treeObj.setting;
        // 获取当前树绑定的隐藏域对象
        var $hideObj = options.hideObj;
        // 获取是否保持展开闭合状态
        var keepStatus = options.keepStatus;
        // 获取是否是复选树
        var isCheck = options.checkEnable;
        // 获取初始化回调方法
        var initTreeCallback = options.initTree;
        // 获取默认的选项名称
        var defaultOptionLabel = options.defaultOptionLabel;
        // 如果隐藏域存在且隐藏域有值
        if ($hideObj && $hideObj.val() != '') {
            // 获取 zTree 的全部节点数据（对于异步加载模式下，尚未加载的子节点是无法通过此方法获取的）
            var nodes = treeObj.getNodes();
            // 当treeNode不为null时，需要强制加载当前treeNode的子节点
            if (treeNode) {
                nodes = treeNode.children;
            }
            // 如果是复选
            if (isCheck) {
                // 获取隐藏域的值并根据,拆分
                var hidIDArr = $hideObj.val().split(',');
                // 如果拆分后数组长度大于0
                if ($.isArray(hidIDArr) && hidIDArr.length > 0) {
                    var length = hidIDArr.length;
                    // 遍历数组
                    for (var i = 0; i < length; i++) {
                        // 根据id获取节点对象
                        var curNode = treeObj.getNodeByParam("id", hidIDArr[i]) || '';
                        // 如果当前节点已加载
                        if (curNode != '') {
                            // 勾选该节点对象 
                            /* 第三个参数为checkTypeFlagBoolean
                                checkTypeFlag = true 表示按照 setting.check.chkboxType 属性进行父子节点的勾选联动操作
                                checkTypeFlag = false 表示只修改此节点勾选状态，无任何勾选联动操作
                                checkTypeFlag = false 且 treeNode.checked = checked 时，不会触发回调函数，直接返回
                                treeNode.nochecked = true 的节点不受此参数影响。
                            */
                            // 第四个参数为是否触发回调函数，设置为false不触发，则不会在回选时修改隐藏域的值
                            treeObj.checkNode(curNode, true, false, false);
                            // 勾选不会展开，因此需要手动获取父节点并进行展开操作；
                            recursiveExpendNode(curNode, treeObj);
                        } else {
                            // 如果当前节点不存在，则强制异步加载
                            asyncNodes(treeObj, nodes);
                            // 勾选时隐藏域ID的排序是按照树的节点顺序的，所以跳出循环以优化速度
                            break;
                        }
                    }
                }
            } else { // 如果是单选
                var curNode = treeObj.getNodeByParam("id", $hideObj.val()) || '';
                // 如果当前节点已加载
                if (curNode != '') {
                    // 选中节点
                    treeObj.selectNode(curNode);
                } else {
                    // 如果当前节点不存在，则强制异步加载
                    asyncNodes(treeObj, nodes);
                }
            }
        }

        // 如果设置了默认选项并且当前下拉菜单为单选
        if (defaultOptionLabel != null && !isCheck) {
            setDefaultOption(treeObj, defaultOptionLabel);
        }

        // 如果需要保存展开合并状态
        if (keepStatus) {
            var treeId = options.treeId;
            // 获取cookie数组
            var z_tree = getCookieArray();
            // 获取当前页面的actionName
            var actionName = getCurrentActionName();

            for (var i = 0; i < z_tree.length; i++) {
                var currentMsgArray = z_tree[i].split('@');
                // 如果actionName和当前页面一致，判断展开
                if (actionName == currentMsgArray[0] && treeId == currentMsgArray[2]) {
                    // 根据节点id获取节点对象
                    var node = treeObj.getNodeByParam('id', currentMsgArray[1]);
                    // 展开节点对象
                    treeObj.expandNode(node, true, false, false);
                }
            }
        }

        // 如果存在初始化方法，则执行方法
        if ($.isFunction(initTreeCallback)) {
            var treeId = options.treeId;
            initTreeCallback.call(treeObj, treeObj, treeNode);
        }
    }

    /**
     * @title 设置单选下拉菜单默认选项
     * @method setDefaultOption
     * @param treeObj zTree对象
     * @param defaultOptionLabel 默认选项的值
     */

    function setDefaultOption(treeObj, defaultOptionLabel) {

        // 创建默认选项节点
        var newNode = {
            name: defaultOptionLabel,
            id: ''
        };
        // 将默认选项节点添加到zTreeObj并返回 返回值是 zTree 最终添加的节点数据集合
        newNode = treeObj.addNodes(null, 0, newNode);
        // 获取zTree已选中的节点
        var selectedNodes = treeObj.getSelectedNodes();

        // 如果没有选中任何节点 则应该选中 默认选项
        if (selectedNodes.length == 0) {
            treeObj.selectNode(newNode[0]);
        }
    }

    /**
     * @title 添加鼠标悬停事件
     * @method _addHoverDom
     * @param treeId ztree的ID
     * @param treeNode 当前节点
     */

    function _addHoverDom(treeId, treeNode) {

        var treeObj = getTreeObj(treeId);
        var options = treeObj.setting;
        var addHoverDomCallback = options.addHoverDom;

        // 如果存在选中之前的回调，则执行该回调
        if ($.isFunction(addHoverDomCallback)) {
            addHoverDomCallback.call(treeObj, treeId, treeNode);
        }
    }

    /**
     * @title 移除鼠标悬停事件
     * @method _removeHoverDom
     * @param treeId ztree的ID
     * @param treeNode 当前节点
     */

    function _removeHoverDom(treeId, treeNode) {

        var treeObj = getTreeObj(treeId);
        var options = treeObj.setting;
        var removeHoverDomCallback = options.removeHoverDom;

        // 如果存在选中之前的回调，则执行该回调
        if ($.isFunction(removeHoverDomCallback)) {
            removeHoverDomCallback.call(treeObj, treeId, treeNode);
        }
    }

    /**
     * @title 在显示节点时追加显示属性
     * @method _appendDom
     * @param treeId ztree的ID
     * @param treeNode 当前节点
     */

    function _appendDom(treeId, treeNode) {

        var treeObj = getTreeObj(treeId);
        var options = treeObj.setting;
        var addDiyDomCallback = options.appendDom;

        // 获取当前节点所在的span标签
        var aObj = $("#" + treeNode.tId + "_span");
        // 创建span
        var diySpan = document.createElement('span');

        // 如果存在选中之前的回调，则执行该回调
        if ($.isFunction(addDiyDomCallback)) {
            // 获取回调函数的返回值
            var viewItem = addDiyDomCallback.call(treeObj, treeId, treeNode) || '';
            // 将该返回值写入创建好的span
            $(diySpan).html(' ' + viewItem);
        }

        // 将创建的span追加到当前节点所在的span标签
        aObj.append($(diySpan));
    }

    /**
     * @title 获取节点的字体样式
     * @method getFont
     * @param treeId ztree的ID
     * @param treeNode 当前节点
     */

    function getFont(treeId, treeNode) {
        // 初始化样式
        var fontCss = {};
        // 如果当前节点禁用，则将字体设置为灰色斜体字
        if (treeNode.chkDisabled) {
            fontCss = {
                'color': 'gray',
                'font-style': 'italic'
            };
        }
        return fontCss;
    }

    /**
     * @title 手动递归展开当前节点及其父节点
     * @method recursiveExpendNode
     * @param node 需要手动展开的节点
     * @param treeObj 当前树对象
     */

    function recursiveExpendNode(node, treeObj) {
        // 获取当前节点的上级节点
        var rootNode = node.getParentNode();
        // 递归到当前节点的根节点
        while (rootNode) {
            treeObj.expandNode(rootNode, true);
            rootNode = rootNode.getParentNode();
        }
    }

    /**
     * @title 自定义zTree的构造函数
     * @method CustomZtree
     * @param element 绑定此函数的对象
     * @param opt 绑定此函数时传递的参数
     */
    var CustomZtree = function(element, opt) {

            var that = this;
            // 共享变量
            that.element = element;
            that.$el = $(element);
            that.isLocal = false;
            that.showContainer = true;
            that.divContainer = null;
            that.options = $.extend(true, {}, CustomZtree.defaults, opt);
            // 将当前树对象绑定的input对象设置到zTree的默认参数
            that.options.inputObj = that.$el;
            // 设置是否开启复选
            that.options.checkEnable = opt.checkEnable || false;
            that.options.check.enable = that.options.checkEnable;
            // 设置复选关联关系
            that.options.check.chkboxType = opt.chkboxType || that.options.check.chkboxType;
            that.setOptions(opt);
        };

    CustomZtree.defaults = {
        treeId: '',
        // zTree所在ul的Id
        hideObj: '',
        // 需要赋值的隐藏域
        inputObj: '',
        // zTree绑定的input对象
        checkEnable: false,
        // 是否复选
        chkboxType: '',
        // 宽度是否自定义
        width: 'auto',
        position: 'bottom',
        // 是否保存展开闭合状态
        keepStatus: false,
        // 数据源
        dataSource: null,
        beforeSelect: null,
        onSelect: null,
        defaultOptionLabel: null,
        view: {
            // 双击节点展开
            dblClickExpand: false,
            // 设置树展开的动画速度
            expandSpeed: 100,
            // 是否多选
            selectedMulti: false,
            // 是否显示图标
            showIcon: false,
            // 鼠标悬停事件
            addHoverDom: _addHoverDom,
            // 删除鼠标悬停事件
            removeHoverDom: _removeHoverDom,
            // 自定义Dom节点，
            addDiyDom: _appendDom,
            // 节点字体样式
            fontCss: getFont,
            nameIsHTML: true
        },
        async: {
            enable: false,
            type: 'get',
            url: '',
            autoParam: ["id", "level=treeNode_level"]
        },
        data: { // 必须使用data
            simpleData: {
                enable: true,
                idKey: "id",
                // id编号命名
                pIdKey: "pId",
                // 父id编号命名
                rootPId: ""
            },
            key: {
                name: "name",
                title: ""
            }
        },
        callback: { // 回调函数
            onExpand: _onExpand,
            onCollapse: _onCollapse,
            onCheck: _onCheck,
            onClick: _onClick,
            beforeClick: _beforeClick,
            beforeCheck: _beforeCheck,
            onAsyncSuccess: _onAsyncSuccess
        },
        check: {
            enable: false,
            chkStyle: "checkbox",
            chkboxType: {
                'Y': '',
                'N': ''
            }
        }
    };

    CustomZtree.prototype = {

        zSelect: function() {
            var that = this;
            // 接收参数
            var $self = that.$el;
            var options = that.options;
            // 创建包裹下拉框的div元素
            var divContainer = createDivContainer();
            // 将div转换成jQuery对象
            var $divContainer = $(divContainer);

            that.divContainer = $divContainer;
            // 将div插入到当前input的父级元素的最后
            $divContainer.appendTo('body');
            // 创建zTree所在的ul并给定样式
            var $ul = $("<ul>").addClass("ztree").addClass("ztree_select");

            // 给options设置treeId属性
            options.treeId = ($self.attr('id') || options.treeId) + "_zTree";

            // 将treeId赋给zTree的ul
            $ul.attr('id', options.treeId);
            // 将zTree所在的ul插入到包裹zTree的Div
            $divContainer.append($ul);
            var treeObj;
            // 给输入框绑定click事件，当zTree下拉框存在时，隐藏；不存在时显示
            $self.on('click.ztreeSelect', function(e) {
                that.onClick(e);
            });
/*$self.click(function() {
				// 初始化ztree
                var treeObj = that.initTree();
                // 如果showContainer为false，则阻断方法继续执行
                if(!that.showContainer){
                	return;
                }
				var containerWidth = '0px';
				if (options.width !== 'auto') {
					containerWidth = options.width;
				} else {
					containerWidth = $(this).outerWidth() + 'px';
				}
				// 给包裹zTree的div设定宽度以及显示优先级(之所以放到click中是因为初始化查询条件可能会隐藏)
				$divContainer.css({
					'width': containerWidth,
					// 宽度为当前input的宽度
					'z-index': '9999' // 显示优先级
				});
				// 定位
                that.fixPosition();
                // 窗口大小改变时 重新定位
                $(window).on('resize.ztreeSelect', that.fixPositionCapture);
                
				if ($divContainer.css('display') === 'none') {
					showTree($divContainer, treeObj);
				} else {
					hideTree($divContainer, treeObj);
				}
			});
*/
            // 如果是复选框，则不检索
            if (options.check.enable) {
                return that;
            }

            // 初始化需要隐藏的节点数组
            var hiddenNodes = [];

            // 给input绑定keyup事件用来模糊匹配显示结果
            $self.on('keyup.ztreeSelect', function() {
                var treeObj = $.fn.zTree.getZTreeObj(options.treeId);
                // 显示上次搜索后被隐藏的结点
                treeObj.showNodes(hiddenNodes);
                // 获取input的value
                var keywords = $(this).val();

                if (!keywords || !keywords.length) {
                    return false;
                }
                // 获取不符合条件的节点集合
                hiddenNodes = treeObj.getNodesByFilter(function(node) {
                    if (node.isParent || node.name.indexOf(keywords) != -1) {
                        // 递归展开当前节点的父节点
                        recursiveExpendNode(node, treeObj);
                        return false;
                    } else {
                        return true;
                    }
                });
                // 隐藏不符合条件的节点
                treeObj.hideNodes(hiddenNodes);
                $(this).focus();
                // 显示下拉菜单
                showTree($divContainer, treeObj);
            });

            return that;
        },
        /**
         * 给绑定ztree的文本框添加点击事件
         * @param e 点击事件对象
         */
        onClick: function(e) {
            var that = this;
            var options = that.options;
            // 初始化ztree
            var treeObj = that.initTree();
            // 如果showContainer为false，则阻断方法继续执行
            if (!that.showContainer) {
                return;
            }
            var containerWidth = '0px';
            if (options.width !== 'auto') {
                containerWidth = options.width;
            } else {
                containerWidth = that.$el.outerWidth() + 'px';
            }
            // 给包裹zTree的div设定宽度以及显示优先级(之所以放到click中是因为初始化查询条件可能会隐藏)
            that.divContainer.css({
                'width': containerWidth,
                // 宽度为当前input的宽度
                'z-index': '999' // 显示优先级
            });
            // 定位
            that.fixPosition();
            // 窗口大小改变时 重新定位
            $(window).on('resize.ztreeSelect', that.fixPositionCapture);

            if (that.divContainer.css('display') === 'none') {
                showTree(that.divContainer, treeObj);
            } else {
                hideTree(that.divContainer, treeObj);
            }
        },
        /**
         * 初始化树.
         * @rertun treeObj 树对象
         */
        initTree: function() {
            var that = this;
            var options = that.options;
            var treeObj;
            // 如果数据源为json数组，直接初始化
            if (that.isLocal) {
                // 初始化zTree
                treeObj = $.fn.zTree.init($('#' + options.treeId), options, options.dataSource);
                defaultSelect(treeObj);
            } else {
                // 如果数据源为url时，异步加载树
                treeObj = that.asyncTree(treeObj);
            }
            return treeObj;
        },
        /**
         * 异步加载树
         * @param treeObj 树对象
         * @rertun treeObj 树对象
         */
        asyncTree: function(treeObj) {
            var that = this;
            var options = that.options;
            // 数据源为url时，设置异步请求为true
            options.async.enable = true;
            if (typeof options.dataSource === 'string') {
                // 将数据源的url设置给zTree本身对应的参数
                options.async.url = options.dataSource;
            }
            // 如果数据源为function且返回值为string类型的url，初始化zTree，否则阻断
            else if ($.isFunction(options.dataSource)) {
                // 如果数据源的function的返回值为false或者空字符串或者直接return 阻断
                var callFlag = options.dataSource.call();
                if (!callFlag) {
                    that.showContainer = false;
                    return;
                } else {
                    that.showContainer = true;
                }

                // 将数据源的url设置给zTree本身对应的参数
                options.async.url = options.dataSource.call();
            }
            // 初始化树
            treeObj = $.fn.zTree.init($('#' + options.treeId), options);
            return treeObj;
        },

        fixPosition: function() {

            // 接收参数
            var that = this;
            // 获取包裹ztree的div
            var $container = $(that.divContainer);
            // 获取包裹ztree的父元素
            var containerParent = $container.parent().get(0);

            // 获取ztree下拉框的方向
            var position = that.options.position;
            // 获取ztree下拉框的高度
            var containerHeight = $container.outerHeight();
            // 获取绑定ztree的input的高度
            var height = that.$el.outerHeight();
            // 获取绑定ztree的input的offset
            var offset = that.$el.offset();
            // 创建样式
            var styles = {
                'top': offset.top,
                'left': offset.left
            };
            // 如果方向为自动，需要动态计算方向
            if (position === 'auto') {
                // 获取窗口高度
                var viewPortHeight = $(window).height();
                // 获取滚动条高度
                var scrollTop = $(window).scrollTop();
                // 计算 窗口顶部的距离
                var topOverflow = -scrollTop + offset.top - containerHeight;
                var bottomOverflow = scrollTop + viewPortHeight - (offset.top + height + containerHeight);

                position = (Math.max(topOverflow, bottomOverflow) === topOverflow) ? 'top' : 'bottom';
            }
            if (position === 'top') {
                styles.top += -containerHeight;
            } else {
                styles.top += height;
            }
            // If container is not positioned to body,
            // correct its position using offset parent offset
            if (containerParent !== document.body) {
                var opacity = $container.css('opacity'),
                    parentOffsetDiff;
                if (!that.visible) {
                    $container.css('opacity', 0).show();
                }

                parentOffsetDiff = $container.offsetParent().offset();
                styles.top -= parentOffsetDiff.top;
                styles.left -= parentOffsetDiff.left;

                if (!that.visible) {
                    $container.css('opacity', opacity).hide();
                }
            }

            $container.css(styles);
        },

        fixPositionCapture: function() {
            var that = this;

            if (that.visible) {
                that.fixPosition();
            }
        },

        setOptions: function(suppliedOptions) {
            var that = this;
            var options = that.options;
            // 调用者可以通过此方法修改参数
            this.options = $.extend({}, options, suppliedOptions);
            // 设置是否开启复选
            this.options.checkEnable = suppliedOptions.checkEnable || false;
            this.options.check.enable = this.options.checkEnable;
            // 设置复选关联关系
            this.options.check.chkboxType = suppliedOptions.chkboxType || this.options.check.chkboxType;
            // 根据数据源类型判断是否本地数据
            that.isLocal = $.isArray(options.dataSource);
        },

        zTreeLeftMenu: function() {
            var that = this;
            var self = that.$el;
            var options = that.options;

            // 给options设置treeId属性
            options.treeId = self.attr('id');

            // 初始化树
            that.initTree();

            return that;
        },

        dispose: function() {
            var that = this;
            that.$el.off('.ztreeSelect').removeData('ztreeSelect');
            $(window).off('resize.ztreeSelect', that.fixPositionCapture);
        }
    }

    // 暴露给外界调用的ztree下拉菜单方法
    $.fn.ztreeSelect = function(options, args) {
        var dataKey = 'ztreeSelect';
        // If function invoked without argument return
        // instance of the first matched element:
        if (!arguments.length) {
            return this.first().data(dataKey);
        }

        return this.each(function() {
            var inputElement = $(this),
                instance = inputElement.data(dataKey);

            if (typeof options === 'string') {
                if (instance && typeof instance[options] === 'function') {
                    instance[options](args);
                }
            } else {
                // If instance already exists, destroy it:
                if (instance && instance.dispose) {
                    instance.dispose();
                }
                instance = new CustomZtree(this, options).zSelect();
                inputElement.data(dataKey, instance);
            }
        });

        //		var customZtree = new CustomZtree(this, options);
        //		return customZtree.zSelect();
    }

    $.fn.ztreeLeftMenu = function(options) {
        var dataKey = 'ztreeLeftMenu';
        // If function invoked without argument return
        // instance of the first matched element:
        if (!arguments.length) {
            return this.first().data(dataKey);
        }

        return this.each(function() {
            var inputElement = $(this),
                instance = inputElement.data(dataKey);

            if (typeof options === 'string') {
                if (instance && typeof instance[options] === 'function') {
                    instance[options](args);
                }
            } else {
                // If instance already exists, destroy it:
                if (instance && instance.dispose) {
                    instance.dispose();
                }
                instance = new CustomZtree(this, options).zTreeLeftMenu();
                inputElement.data(dataKey, instance);
            }
        });
        //		var customZtree = new CustomZtree(this, options);
        //		return customZtree.zTreeLeftMenu();
    }
}));