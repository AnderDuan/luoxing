/*
* table_name 后端执行操作访问数据库的表明
* item 从后端查出来数据之后用vue添加遍历时候的每一次的data列表json
* skip 后端查找数据访问数据库时跳过的条数
* limit 后端查找数据访问数据库时要查几条数据    (limit kip,limit)
* btn_name 前端元素的id(input标签的id名)
* */

// 批量删除
function deletes(table_name) {
    var del_data = [];
    $('.deletes:checked').each(function () {
        del_data.push($(this).text());
    })
    console.log(del_data);
    if (del_data.length == 0) {
        return
    }
    del = JSON.stringify(del_data);
    console.log(del);
    console.log(del_data);
    axios.get("/restful/api/" + table_name + "/?do=deletes&data=" + del)
        .then(function (res) {
            $(".deletes").attr("checked", false)
            console.log(res.data);
            del = null;
            app.loadData()
        });
}

// 单条删除
function delete_item(item, table_name) {

    console.log(item);
    axios.get("/restful/api/" + table_name + "/?do=delete&data=" + JSON.stringify(item))
        .then(function (res) {
            console.log(res.data);
            alert("删除成功！")
            app.loadData();
        });
}

// 更新之后单条保存
function save(item, table_name) {
    console.log(item);

    axios.get("/restful/api/" + table_name + "/?do=update&data=" + JSON.stringify(item))
        .then(function (res) {
            console.log(res.data);
            alert("修改成功！")
            app.loadData();
        });
}

// 初始化页面的数据查找
function loadData(skip, limit, table_name) {
    if (skip == null || limit == null) {
        skip = 0, limit = 10
    }
    var _this = this;
    axios.get("/restful/api/" + table_name + "/?do=select&skip=" + skip + "&limit=" + limit).then(function (res) {
        app.tables = res.data;
        console.log(res.data);
    });
}

// 分页
function limit(table_name) {
    $.ajax({
        url: "/restful/paging/" + table_name + "/?do=count_num",
        type: "get",
        success: function (result) {

            layui.use(['laypage', 'layer'], function () {
                var laypage = layui.laypage
                    , layer = layui.layer;
                //调用分页
                laypage.render({
                    elem: 'demo20'
                    , count: result
                    , layout: ['count', 'prev', 'page', 'next', 'limit', 'skip']
                    , jump: function (obj) {
                        skip = 10 * $("em").text() - 10;
                        limit = 10;
                        app.loadData(skip, limit)
                    }
                });
            });
        }
    })
}

// layui弹窗
function new_table(btn_name, add_table) {
    layui.use('layer', function () {
        var layer = layui.layer;
    });
    $("#" + btn_name).click(function () {
        layer.open({
            type: 1,
            title: "添加新的表",
            area: ['23%', '70%'],
            content: $("#" + add_table).html()
        })
    });
}

// lay弹窗的from表单提交
function from(table_name) {
    layui.use('form', function () {
        var form = layui.form;
        //监听提交
        form.on('submit(formDemo)', function (data) {

            var _this = this;
            console.log(data);
            axios.get("/restful/api/" + table_name + "/?do=insert&data=" + JSON.stringify(data.field))
                .then(function (res) {
                    console.log(res.data);
                    alert("添加成功！")
                    app.loadData();
                });
            return false;
        });
    });
}

// 批量插入数据，上传文件
function upload(btn_name) {
    layui.use('upload', function () {
        var upload = layui.upload;

        //执行上传
        var uploadInst = upload.render({
            elem: '#' + btn_name //绑定元素
            , url: '/restful/upload/dasset_tables/' //上传接口
            , method: 'POST'
            , accept: 'file'
            , size: 1024 * 20
            , before: function (obj) {
                layer.load();
            }
            , done: function (res) {//上传完毕回调
                layer.closeAll('loading');
                if (res == "401") {
                    layer.msg('文件不能为空！');
                } else if (res == "402") {
                    layer.msg('文件不符合规格！')
                } else {
                    layer.msg('上传操作成功了' + res + '条')
                }

            }
            , error: function () {//请求异常回调
                layer.closeAll('loading');
                alert('上传失败请联系管理员！');
            }
        });
    });
}