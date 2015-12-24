// DaoliCloud GUI
;
(function (global, $) {
    var zoom, // 实现缩放功能
        gui, // 存放对外可见的参数和功能
        config, // 存放全局配置参数
        tool; // 实现拖曳创建Instance

    var prefix = "/dashboard/project/";
    var static_url = "/dashboard/static/";

    // 全局配置参数
    config = {
        timeout: 2000,  // 默认延迟 2 秒处理

        // 缩放的范围
        domain: [0.5, 5],

        // 图片宽高
        image: {
            width: 44,
            height: 44,
        },

        // 文字样式
        text: {
            "text-anchor": "middle",
        //    "font-family": "sans-serif",
            "font-family":"FangSong",
            "font-size": "large",
            "font-style":"normal"
        },

        // 图片显示名称映射
        typeMap: {
            vm: "VM",
            docker: "Docker",
            wordpress: "WordPress",
            container: "Container",
            apache: "Apache",
            java: "Java",
            lmap: "Lamp",
            mysql: "MySQL",
            ssh: "SSH",
            nginx: "Nginx",
            python: "Python",
            tomcat: "Tomcat",
            ruby: "Ruby",
            nodejs: "Nodejs",
            php: "PHP",
            perl: "Perl",
            mongodb: "MongoDB",
            go:"Go",
            postgresql:"Postgresql",
            redis:"Redis"
        },

        // 加载
        status: {
            BUILD: {
                image: static_url + "daoli/images/gui_loading.gif",
                text: "loading"
            },
            ERROR: {
                image: static_url + "daoli/images/gui_error.png",
                text: "error"
            }
        },

        // load窗口
        loadModel: {
            width: 400,
            height: 400
        }
    };

    // (1)通过鼠标左键拖曵——上下左右；（2）通过点击Slider控件上方的上下左右控件。
    zoom = {
        // 用于区别触发缩放功能的类型：（1）鼠标滚动缩放，（2）Slider缩放
        // 此标志为了防止缩放两次。
        roll_click: true,

        // 点击roll button按钮，实现上下左右移动
        rollButton: function() {
            var roll_buttons = $("#roll_button div");
            var position = ["0px", "0px"].join(" ");
            var translate = [0, 0];
            var d = 80; // 每次幅度80

            // 为上下左右添加事件（mouseover，mouseout，click）和参数
            for (var i = 0, n = roll_buttons.length; i < n; i++) {
                switch (roll_buttons[i].id) {
                    case "roll_buttonN":
                        position = ["0px", "-44px"].join(" ");
                        translate = [0, -d];
                        zoom.rollMouseEvent("#roll_buttonN", position, translate);
                        break;
                    case "roll_buttonS":
                        position = ["0px", "-132px"].join(" ");
                        translate = [0, d];
                        zoom.rollMouseEvent("#roll_buttonS", position, translate);
                        break;
                    case "roll_buttonE":
                        position = ["0px", "-88px"].join(" ");
                        translate = [d, 0];
                        zoom.rollMouseEvent("#roll_buttonE", position, translate);
                        break;
                    case "roll_buttonW":
                        position = ["0px", "-176px"].join(" ");
                        translate = [-d, 0];
                        zoom.rollMouseEvent("#roll_buttonW", position, translate);
                        break;
                }
            }
        },

        // 上下左右事件
        // 鼠标移到id上面，背景图片position偏移位置
        // 鼠标点击id，位置发生translate移动
        rollMouseEvent: function(id, position, translate) {
            $(id).mouseover(function() {
                $("#roll_button").css('background-position', position);
            });

            $(id).mouseout(function() {
                $("#roll_button").css('background-position', "0px 0px");
            });

            $(id).click(function() {
                var trans = zoom.coordinate(gui.share.g1.attr("transform"));
                var s = zoom.scale(gui.share.g1.attr('transform'));
                gui.share.g1.attr("transform", "translate(" + zoom.coordinateAdd(trans, translate) + ")scale(" + s + ")");
            });
        },

        // 提取整个画布的偏移量
        coordinate: function(translate) {
            if (translate) {
                var m;

                if (translate.indexOf(",") == -1) {
                    // ie问题
                    m = translate.split(' ');
                } else {
                    m = translate.split(',');
                }

                var x = m[0].split('(');
                var t = m[1].split(')');
                return [x[1], t[0]];
            } else {
                return [0, 0];
            }
        },

        // 偏移量相加，放回新的偏移量
        coordinateAdd: function(trans1, trans2) {
            x = parseInt(trans1[0]) + parseInt(trans2[0]);
            y = parseInt(trans1[1]) + parseInt(trans2[1]);
            return [x, y].join(',');
        },

        // 鼠标滚轮缩放
        roll_zoom: function() {
            gui.share.g1.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
            zoom.roll_click = false;
            var value = (zoom.scale(gui.share.g1.attr('transform')) - config.domain[0]) / (config.domain[1] - config.domain[0]) * 100;
            $("#slider").slider('value', value);
        },

        // 初始化 Slider 的 Range
        roll_zoom_init: function() {
            $("#slider").slider({
                orientation: "vertical",
                range: "min"
            });
            var value = (zoom.scale(gui.share.g1.attr('transform')) - config.domain[0]) / config.domain[1] * 100;
            $("#slider").slider('value', value);
        },

        // 获取缩放的比例，默认为1
        scale: function(scales) {
            if (scales) {
                return scales.split("scale(")[1].split(')')[0];
            } else {
                return 1;
            }
        },

        // roll中slider值改变，缩放画布
        roll_move: function() {
            var value1 = $('#slider').slider('value');
            $('#slider').bind('slidechange', function(event, ui) {
                if (zoom.roll_click) {
                    var value2 = $('#slider').slider('value');
                    zoom.roll_action(value1, value2);
                    value1 = value2;
                }
            });
        },

        // 根据roll中slider值，缩放画布
        roll_action: function(value1, value2) {
            if (value1 != value2) {
                var tran_d_x = (value2 - value1) / 100 * (config.domain[1] - config.domain[0]) * (-500),
                    tran_d_y = (value2 - value1) / 100 * (config.domain[1] - config.domain[0]) * (-250);
                var trans = zoom.coordinate(gui.share.g1.attr("transform"));
                var s = value2 / 100 * (config.domain[1] - config.domain[0]) + config.domain[0];
                gui.share.g1.attr("transform", "translate(" + zoom.coordinateAdd(trans, [tran_d_x, tran_d_y]) + ")scale(" + s + ")");
            }
        },

        // 初始化画布大小，缩放
        init: function(svg, width, height) {
            gui.share.g1.append("rect")
                .classed('overlay', false)
                .attr("width", width)
                .attr("height", height)
                .attr('opacity', 0);

            // 给svg绑定缩放事件
            svg.call(d3.behavior.zoom().scaleExtent(config.domain).on("zoom", zoom.roll_zoom))
                .on('dblclick.zoom', null);

            this.rollButton(); // 为roll button绑定上下左右等移动事件
            this.roll_zoom_init(); // 初始化Slider的Range
            this.roll_move(); // 为Slider绑定事件——当Slider值发生改变时，缩放画布

            // 当鼠标放到Slider缩放控件上时，如果发生缩放事件，则认为缩放类型为Slider缩放，并由Slider进行缩放；
            // 否则，认为缩放类型是鼠标缩放
            $("#slider").mouseover(function(e) {
                zoom.roll_click = true;
            });

            // 为 Slider 中的 + 控件绑定缩放事件——点击此控件，可以放大画布
            $("#slider_plus").bind({
                mouseover: function(e) {
                    $(this).css('background-position', "0px -243px");
                },

                mouseout: function(e) {
                    $(this).css('background-position', "0px -221px");
                },

                click: function(e) {
                    e.stopPropagation();
                    svg.call(d3.behavior.zoom().scaleExtent(config.domain).on("zoom", zoom.roll_zoom));
                    var value = $("#slider").slider("value");
                    var value2;
                    zoom.roll_click = false;

                    if ((value + 20) <= 100) {
                        value2 = value + 20;
                    } else {
                        value2 = 100;
                    }

                    zoom.roll_action(value, value2);
                    $("#slider").slider("value", value2);
                }
            });

            // 为 Slider 中的 - 控件绑定缩放事件——点击此控件，可以缩放画布
            $("#slider_minus").bind({
                mouseover: function(e) {
                    $(this).css('background-position', "0px -287px");
                },

                mouseout: function(e) {
                    $(this).css('background-position', "0px -265px");
                },

                click: function(e) {
                    e.stopPropagation();
                    var value = $("#slider").slider("value");
                    var value2;
                    zoom.roll_click = false;

                    if ((value - 20) >= 1) {
                        value2 = value - 20;
                    } else {
                        value2 = 1;
                    }

                    zoom.roll_action(value, value2);
                    $("#slider").slider("value", value2);
                }
            });
        },
    };

    // 主要存放供其它组件共享的参数和功能，此对象会被导出到全局空间，供外部查看
    gui = {
        // 各组件间的共享变量
        share: {
            // 是否点击了图标
            select_node: null,
            // 是否点击剪刀
            select_scissor: false,
            // 是否点击划线
            select_drawline: false,
            // 设置tip停留
            interval: null,
            // 用于控制links中id值
            links_length: 0,
        },

        // 初始化GUI
        init: function() {
            var width = document.getElementById("play").offsetWidth,
                height = document.getElementById("play").offsetHeight;
            gui.share.width = width;
            gui.share.height = height;

            var svg = d3.select("#play").append("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("pointer-events", 'all')
                .style('overflow', 'hidden')
                .append('g');
            var g1 = svg.append("g").attr('id', 'g1');
            gui.share.g1 = g1;

            // 初始化缩放功能
            zoom.init(svg, width, height);

            gui.share.g_links = g1.append("g");
            gui.share.g_nodes = g1.append("g");

            // tool拖拽创建虚拟机
            tool.init();

            // 加载Instances数据
            this.load_data(width, height);
        },

        // 格式化数据，保留唯一关系，即消重（比如links={"A":"B","B":"A"}格式化成links=[{"A","B"}]）
        formatData: function(links) {
            var linknew = [];

            for (var i in links) {
                for (var j in links[i]) {
                    linknew.push({
                        source: i,
                        target: links[i][j]
                    });
                }
            }

            for (var i in linknew) {
                for (var j in linknew) {
                    if (linknew[j].source == linknew[i].target && linknew[j].target == linknew[i].source) {
                        linknew.splice(j, 1);
                    }
                }
            }
            return linknew;
        },

        // 根据links中的uuid找到虚拟机信息，此时links就是各个虚拟机之间的关系
        linkFormate: function(links, nodes) {
            function finduuid(nodes, id) {
                var i = 0;
                for (i = 0; i < nodes.length; i++) {
                    if (nodes[i].id == id) {
                        return nodes[i];
                    }
                }
                return null;
            }
            var newlinks = [];
            var num = 0;
            for (var i = 0; i < links.length; i++) {
                if (finduuid(nodes, links[i].source) && finduuid(nodes, links[i].target)) {
                    links[i].source = finduuid(nodes, links[i].source);
                    links[i].target = finduuid(nodes, links[i].target);
                    links[i].id = num;
                    num++;
                    newlinks.push(links[i]);
                } else {
                    console.log("[links]", "not find", links[i]);
                }
            }
            return newlinks;
        },

        // 通过 ID 找到相应的 Node 信息
        getNode: function (node_id, nodes) {
            if (!nodes) {
                nodes = gui.share.nodes;
            }
            for (var i = 0; i < nodes.length; i++) {
                if (nodes[i].id == node_id) {
                    return nodes[i];
                }
            }
            return null;
        },

        // 通过 ID 移除某个 Node 节点信息
        removeNode: function (node_id, nodes) {
            if (!nodes) {
                nodes = gui.share.nodes;
            }
            for (var i = 0; i < nodes.length; i++) {
                if (nodes[i].id == id) {
                    nodes.splice(i, 1);
                    break;
                }
            }
        },

        // 请求Instances数据，并根据数据动态显示到页面上
        load_data: function(width, height) {

            tool.renderLoad(50, $(".draw").width(), $(".draw").height(), $(".draw").offset());
            tool.loading(1);

            // 求线段的中点
            function middle(point1, point2) {
                var x = (point2[0] - point1[0]) / 2 + point1[0];
                var y = (point2[1] - point1[1]) / 2 + point1[1];
                return [x, y];
            }

            // AJAX 成功时的回调函数
            function _success(o) {
                tool.loading(0);
                var nodes = o.servers,
                    links = o.groups;
                gui.share.nodes = nodes;
                gui.share.links = links;
                console.log("nodes", nodes, "links", links);
                gui.share.links = gui.formatData(gui.share.links);
                gui.share.links = gui.linkFormate(gui.share.links, gui.share.nodes);
                gui.share.links_length = gui.share.links.length;

                // First: Draw all lines（logical relation）.
                var force = d3.layout.force()
                    .nodes(gui.share.nodes)
                    .links(gui.share.links)
                    .linkDistance([200])
                    .alpha(0.1)
                    .size([width, height])
                    .gravity(0.01)
                    .charge(-150)
                    //.chargeDistance(-350)
                    .start();
                gui.share.force = force;

                // Second: To listen the drag event on the lines.
                var drag = d3.behavior.drag()
                    .origin(function(d) {
                    return {
                        x: d.x,
                        y: d.y
                    };
                })
                    .on('drag', function dragmove(d) {
                    d.x = d3.event.x;
                    d.y = d3.event.y;
                    d3.select(this).attr('transform', "translate(" + d3.event.x + "" + ',' + "" + d3.event.y + ")");
                    force.start();
                })
                    .on('dragstart', function(d) {
                    d3.event.sourceEvent.stopPropagation();
                });

                gui.share.drag = drag;
                // Fourth: Add the event listener.
                force.on('tick', function() {
                    gui.share.g_nodes.selectAll('g').attr('transform', function(d) {
                        return "translate(" + d.x + "," + d.y + ")"
                    });
                    gui.share.g_links.selectAll('line').attr('x1', function(d) {
                        return d.source.x;
                    })
                        .attr('y1', function(d) {
                        return d.source.y + 22;
                    })
                        .attr('x2', function(d) {
                        return d.target.x;
                    })
                        .attr('y2', function(d) {
                        return d.target.y + 22;
                    });

                    gui.share.g_links.selectAll('path').attr("d", function(d) {
                        var x1 = d.source.x,
                            y1 = d.source.y + 22,
                            x3 = d.target.x,
                            y3 = d.target.y + 22;

                        var p1 = [x1, y1],
                            p3 = [x3, y3],
                            p2 = [(x1 + x3 + y3 - y1) / 2, (y1 + y3 + x1 - x3) / 2],
                            p4 = [(x1 + x3 - y3 + y1) / 2, (y1 + y3 - x1 + x3) / 2];

                        var p5 = middle(p1, p3);
                        var p6 = middle(p2, p5);
                        var p7 = middle(p4, p5);

                        return "M" + p1 + " Q" + p6 + " " + p3 + "M" + p3 + " Q" + p7 + " " + p1;
                    });
                });

                gui.share.force = force;

                $('#scissor').click(gui._events.scissor.click);
                $('#cursor').click(gui._events.cursor.click);
                $('#line').click(gui._events.line_ico.click);

                // Used to add the new relationship
                var drag_line = gui.share.g1.insert("svg:line", ":nth-child(2)")
                    .style('stroke', "black")
                    .style('stroke-width', 4)
                    .attr("x1", 0)
                    .attr("y1", 0)
                    .attr("x2", 0)
                    .attr("y2", 0);
                gui.share.drag_line = drag_line;

                gui.share.g1.on('mousemove', gui._events.g1.mousemove)
                    .on('click', gui._events.g1.click);
                gui.render(gui.share.nodes, gui.share.links);
                gui.timer();
            }

            function requestData() {
                // 通过AJAX请求数据
                $.ajax({
                    type: "get",
                    url: prefix + "show",
                    async: true,
                    success: _success,
                    error: function(o) {
                        gui.handleJSError(o, function (o) {
                            console.log("error", o);
                            tool.loading(0);
                        });
                    }
                });

                //if ($.cookie("reloaded")) {
                //    $.cookie("reloaded", "");
                //}
            }

            requestData();
            //if (!$.cookie("reloaded")) {
            //    $.cookie("reloaded", true);
            //    setTimeout(function(){
            //        location.reload();
            //    }, 2000);
            //} else {
            //    requestData();
            //}
        },

        // 辅助功能函数——查找已有的links，返回其 index
        findLink: function(link, links) {
            for (var i in links) {
                if (links[i].source == link.source && links[i].target == link.target) {
                    return i;
                } else if (links[i].source == link.target && links[i].target == link.source) {
                    return i;
                }
            }
            return -1;
        },

        // 辅助功能函数——从现在的Links中删除指定的link，即删除两Instances之间的连线关系
        deleteLink: function(link, links) {
            for (var i in links) {
                if (links[i] == link) {
                    links.splice(i, 1);
                }
            }
        },

        // 辅助功能函数——发送创建或删除Instances间的连线信息给服务器后端，使服务器清除数据库中的记录
        sendLinks: function(url, link) {
            var success = false;
            $.ajax({
                type: "get",
                //url: url + "?src=" + link.src + "&dst=" + link.dst,
                url: url + "?suid=" + link.suid + "&spid=" + link.spid + "&duid=" + link.duid + "&dpid=" + link.dpid,
                async: false,
                //data:link,
                success: function(o) {
                    success = true;
                },
                error: function(o) {
                    gui.handleJSError(o, function (o) {
                        success = false;
                    });
                }
            });
            return success;
        },

        // 辅助功能函数--通过虚拟机的id，向服务器查询虚拟机的状态
        getServers: function(ids, successfunc, errorfunc) {
            var csrftoken = $.cookie('csrftoken');

            function csrfSafeMethod(method) {
                // these HTTP methods do not require CSRF protection
                return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
            };

            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $.ajax({
                type: "post",
                url: prefix + "/get_servers/",
                async: true,
                data: {
                    "ids": ids,
                },
                dataType: "json",
                success: function(o) {
                    if (successfunc)
                        successfunc(o);
                },
                error: function(o) {
                    gui.handleJSError(o, errorfunc);
                }
            });
        },

        // 辅助功能函数--创建虚拟机完成后，更新虚拟机信息
        updateNodes: function(nodes) {
            for (var i = 0; i < nodes.length; i++) {
                if (nodes[i].status == "building") {
                    nodes[i].status = "BUILD";
                }

                if (nodes[i].status == "BUILD") {
                    //console.log(nodes[i].id, "BUILD");
                    //gui.getServers(nodes[i].id,gui.updateNodes,gui.updateNodes);
                    gui.delayGetServer(nodes[i].id);
                    //gui.timer();
                    return;
                } else {
                    for (var j = 0; j < gui.share.nodes.length; j++) {
                        if (gui.share.nodes[j].id == nodes[i].id) {
                            gui.share.nodes[j].status = nodes[i].status;
                            gui.share.nodes[j].gip = nodes[i].gip;
                            gui.share.nodes[j].ip = nodes[i].ip;
                            gui.share.nodes[j].port = nodes[i].port;
                            gui.share.nodes[j].type = nodes[i].type;
                            gui.share.nodes[j].dc = nodes[i].dc;
                            if (nodes[i].disk_name){
                                gui.share.nodes[j].disk_name = nodes[i].disk_name;
                                gui.share.nodes[j].disk_size = nodes[i].disk_size;
                              }

                            d3.select("#node_status").text(nodes[i].status);

                            gui.render(gui.share.nodes, gui.share.links);
                            horizon.clearAllMessages();
                            //horizon.alert("success", gettext('Success to create the instance'), ' ');
                            horizon.autoDismissAlerts();
                            return;
                        }
                    }
                }
            }
        },

        // 通用JS请求错误处理
        handleJSError: function (o, errorfunc) {
            if (o.status == 401) {
                //gui.alert("error", gettext("Page timeout. Please re-authorize by login again!"));
                //var tmp = location.href.split("?")[0].split("/").splice(3);
                //tmp.unshift("/dashboard/login/?next=");
                //location.replace(tmp.join("/"));
                location.replace("/dashboard/auth/login/");
                return;
            } else if (o.status == 423) {
                gui.alert("warning", gettext("The operation is too frequent, and please wait a moment!"));
                return;
            }

            if (errorfunc) {
                errorfunc(o);
            }
        },

        // 辅助功能函数--定时器，延迟一次getServer请求
        timer: function() {
            function judge() {
                var buildNum = 0;
                for (var i = 0; i < gui.share.nodes.length; i++) {
                    if (gui.share.nodes[i].status == "BUILD") {
                        buildNum++;
                        gui.getServers(gui.share.nodes[i].id, gui.updateNodes, gui.updateNodes);
                    }
                }
                if (!buildNum) {
                    gui.render(gui.share.nodes, gui.share.links);
                }
            };
            setTimeout(judge, 2000);
        },

        // 辅助功能函数--在getSever请求后，有些虚拟还未创建完成，在回调函数中使用
        delayGetServer: function(id, timeout) {
            function handle() {
                gui.getServers(id, gui.updateNodes, gui.updateNodes);
            };
            if (timeout === undefined) {
                timeout = config.timeout;
            }
            setTimeout(handle, timeout);
        },

        // 根据nodes,links绘制图
        render: function(nodes, links) {
            //if (!nodes) {
            //  nodes = gui.share.nodes;
            //}
            //if (!likes) {
            //  likes = gui.share.links;
            //}

            // links
            var gLinks = gui.share.g_links.selectAll("g")
                .data(links, function(d) {
                return d.id;
            })
                .enter()
                .append("g")
                .on("click", gui._events.g_links.click)
                .on("mouseover", gui._events.g_links.mouseover)
                .on("mouseout", gui._events.g_links.mouseout);
            var gLines = gLinks.append("line")
                .classed("link", true);
            var gPaths = gLinks.append("path")
                .attr("opacity", 0);
            gui.share.g_links.selectAll("g")
                .data(links, function(d) {
                return d.id;
            })
                .exit()
                .remove();

            var image_get = function(value) {
              if (value == null || value == "") {
                value = "container";
              }
              return static_url + "daoli/images/gui_" + value + ".png";
            };

            // nodes
            var gNodes = gui.share.g_nodes.selectAll("g")
                .data(nodes)
                .enter()
                .append("g")
                .call(gui.share.drag)
                .on("click", gui._events.g_nodes.click)
                .on("mouseover", gui._events.g_nodes.mouseover)
                .on("mouseout", gui._events.g_nodes.mouseout);
            gNodes.append("image")
                .attr(config.image)
                .attr("id", function(d) {
                  return "vpc_details_" + d.id;
                })
                .attr('xlink:href', function(d) {
                if (config.status[d.status]) {
                    return config.status[d.status]["image"];
                } else {
                    return image_get(d.type);
                }
            });
            gNodes.append("text")
                .text(function(d) {
                if (config.status[d.status]) {
                    return config.status[d.status]["text"];
                } else {
                    return d.ip;
                }
            })
                .attr('y', config.image.height + 7)
                .attr(config.text);

            var gNodeUpdate = gui.share.g_nodes.selectAll("g")
                .data(nodes);
            gNodeUpdate.selectAll("image")
                .attr(config.image)
                .attr('x', -config.image.width / 2)
                .attr('xlink:href', function(d) {
                if (config.status[d.status]) {
                    return config.status[d.status]["image"];
                } else {
                    return image_get(d.type);
                }
            });
            gNodeUpdate.selectAll("text")
                .text(function(d) {
                if (config.status[d.status]) {
                    return config.status[d.status]["text"];
                } else {
                    return d.ip;
                }
            })
                .attr('y', config.image.height + 15)
                .attr(config.text);
            gui.share.g_nodes.selectAll("g")
                .data(nodes)
                .exit()
                .remove();

            gui.share.force.start();
        },

        // 更新画布
        _reDraw: function() {
            gui.share.g_edges = this.share.g_edges.data(gui.share.links, function(d) {
                return d.id
            });
            var g = gui.share.g_edges.enter().insert('g', ":nth-child(3)")
                .on('click', gui._events.g_edges.click)
                .on('mouseover', gui._events.g_edges.mouseover)
                .on('mouseout', gui._events.g_edges.mouseout);
            g.append("line").classed("link", true);
            g.append("path").attr("opacity", "0");

            gui.share.edges = gui.share.g_edges.selectAll("line");
            gui.share.g_path = gui.share.g_edges.selectAll("path");

            gui.share.g_edges.exit().remove();
            gui.share.force.start();
        },

        // 重新加载页面
        reload: function () {
            location.replace(document.referrer);
        },

        alert: function (_type, message, timeout) {
            horizon.clearAllMessages();
            //horizon.alert("success", gettext('Success to create the instance'), ' ');
            if (_type !== undefined) {
                horizon.alert(_type, message);
            }
            //horizon.autoDismissAlerts();

            if (timeout === undefined) {
                horizon.autoDismissAlerts();
                return;
            }
            setTimeout(function(){horizon.autoDismissAlerts();}, timeout);
        },

        // 事件集合 click，mouseover，mouseout，mousemove
        // 由于要绑定到DOM上的事件太多，因此我们把这些事件的回调函数集成起来管理。
        // _events 的属性名（如：scissor）是在绑定的DOM名，其值是个事件集，其中，属性名是事件名，值是相应的回调函数。
        _events: {
            scissor: {
                click: function() {
                    $("#play").hover(function() {
                        $(this).css({
                            cursor: "url(" + static_url + "daoli/images/gui_scissors.ico),auto"
                        });
                    });
                    gui.share.g_links.selectAll('line').classed('linkscissor', true);
                    gui.share.select_scissor = true;
                    gui.share.select_node = null;
                    gui.share.select_drawline = false;
                    $("#vpc_details_tip").popover('hide');
                },
            },

            cursor: {
                click: function() {
                    $('#play').hover(function() {
                        $(this).css({
                            cursor: "pointer"
                        });

                    });
                    gui.share.g_links.selectAll('line').classed('linkscissor', false);
                    gui.share.select_node = null;
                    gui.share.select_scissor = false;
                    gui.share.select_drawline = false;
                },
            },

            line_ico: {
                click: function() {
                    $('#play').hover(function() {
                        $(this).css({
                            cursor: "url(" + static_url + "daoli/images/gui_wired_top.cur),auto"
                        });

                    });
                    gui.share.g_links.selectAll('line').classed('linkscissor', false);
                    gui.share.select_drawline = true;
                    gui.share.select_scissor = false;
                    $("#vpc_details_tip").popover('hide');
                },
            },

            g1: {
                mousemove: function() {
                    d3.event.preventDefault();

                    if (!gui.share.select_node) {
                        if (gui.share.select_drawline) {
                            $('#play').css({
                                cursor: "url(" + static_url + "daoli/images/gui_wired_top.cur),auto"
                            });
                        }
                        return;
                    }

                    $('#play').css({
                        cursor: "url(" + static_url + "daoli/images/gui_wired_bottom.cur),auto"
                    });

                    gui.share.drag_line
                        .attr("x1", gui.share.select_node.x)
                        .attr("y1", gui.share.select_node.y + 22)
                        .attr("x2", d3.mouse(this)[0])
                        .attr("y2", d3.mouse(this)[1]);
                },
                click: function() {
                    d3.event.preventDefault();

                    if (gui.share.select_node) {
                        $('#play').css({
                            cursor: "url(" + static_url + "daoli/images/gui_wired_top.cur),auto"
                        });

                        gui.share.drag_line
                            .attr("x1", 0)
                            .attr("y1", 0)
                            .attr("x2", 0)
                            .attr("y2", 0);
                        gui.share.select_node = null;
                    }
                },
            },

            template: null,
            g_nodes: {
                mouseover: function(d) {
                  if (gui.template == null)
                    gui.template =  Hogan.compile($("#tip_template").html());
                  if (!gui.share.select_scissor && !gui.share.select_drawline) {
                  var offset = $(this).offset();
                  $("#vpc_details_tip").css({
                    left: offset.left - $("#sidebar").width() + 2 * config.image.width,
                    top: offset.top, display: 'block'})
                  .attr("data-original-title", "Details: " + d.name)
                  .attr("data-content", gui.template.render({
                        id: d.id,
                        name: d.name,
                        address: d.ip,
                        gateway: d.gip,
                        gport: d.port,
                        zone: d.zone_name,
                        status: d.status,
                        _start: d.status == 'SHUTOFF',
                        _stop: d.status == 'ACTIVE',
                        }))
                  .popover({html: true})
                  .popover('show');
                  }
                },
                mouseout: function(d) {
                  $("#vpc_details_tip").siblings('.popover').mouseleave(function() {
                    $(this).popover('hide');
                    //$("#vpc_details_tip").popover('hide');
                  });
                  $("#vpc_details_tip").siblings('.popover').mouseleave(function() {
                    $(this).popover('hide');
                  });
                },
                click: function(d) {
                    //console.log("g_nodesclick",d);
                    var e = d3.event || window.event;
                    if (e.stopPropagation) {
                        e.stopPropagation();
                    } else {
                        e.cancelBubble = true;
                    }
                    e.preventDefault();
                    d3.event.preventDefault();

                    if (gui.share.select_drawline) {
                        console.log(gui.share.select_node);
                        if (gui.share.select_node && gui.share.select_node != d) {
                            var add_link = {
                                source: gui.share.select_node,
                                target: d
                            };
                            // var create_link = {
                            //  src: gui.share.select_node.id,
                            //  dst: d.id
                            // };
                            var create_link = {
                                suid: gui.share.select_node.id,
                                spid: gui.share.select_node.pid,
                                duid: d.id,
                                dpid: d.pid
                            };
                            if (gui.findLink(add_link, gui.share.links) == -1) {
                                // 如果状态不是ACTIVE，不允许连线
                                //if (add_link.source.status != "ACTIVE" || add_link.target.status != "ACTIVE") {
                                //    horizon.clearAllMessages();
                                //    horizon.alert("error", gettext("Failed to connect two instances, because one may not be active"));
                                //    return;
                                //}
                                //如果状态是unknow，不允许连线
                                if (add_link.source.status == "UNKNOWN" || add_link.target.status == "UNKNOWN") {
                                    horizon.clearAllMessages();
                                    horizon.alert("error", gettext("Failed to connect two instances ,One server may be down"));
                                    return;
                                }
                                if (add_link.source.status == "ERROR" || add_link.target.status == "ERROR") {
                                    horizon.clearAllMessages();
                                    horizon.alert("error", gettext("Failed to connect two instances, because one may not be ERROR"));
                                    return;
                                }
                                if (gui.sendLinks(prefix + "create", create_link)) {
                                    gui.share.links.push({
                                        id: gui.share.links_length,
                                        source: gui.share.select_node,
                                        target: d
                                    });
                                    gui.share.links_length++;
                                    gui.render(gui.share.nodes, gui.share.links);
                                } else {
                                    //horizon.clearAllMessages();
                                    //horizon.alert("error", gettext('Failed to connect two instances'));
                                }
                            }
                            gui.share.select_node = null;
                            gui.share.drag_line
                                .attr("x1", 0)
                                .attr("y1", 0)
                                .attr("x2", 0)
                                .attr("y2", 0);
                        } else {
                            gui.share.select_node = d;
                            gui.share.drag_line
                                .attr("x1", gui.share.select_node.x)
                                .attr("y1", gui.share.select_node.y + 22)
                                .attr("x2", gui.share.select_node.x)
                                .attr("y2", gui.share.select_node.y + 22);
                        }
                    }
                },
            },

            g_links: {
                click: function(d) {
                    var e = d3.event || window.event;
                    if (e.stopPropagation) {
                        e.stopPropagation();
                    } else {
                        e.cancelBubble = true;
                    }
                    e.preventDefault();
                    d3.event.preventDefault();

                    if (gui.share.select_scissor) {
                        console.log(d.source)
                        var delete_link = {
                            suid: d.source.id,
                            spid: d.source.pid, 
                            duid: d.target.id,
                            dpid: d.target.pid
                            
                        };
                        if (d.source.status == "UNKNOWN" || d.target.status == "UNKNOWN") {
                            horizon.clearAllMessages();
                            horizon.alert("error", gettext("One server may be down"));
                            return;
                        }

                        if (gui.sendLinks(prefix + "delete", delete_link)) {
                            gui.deleteLink(d, gui.share.links);
                            gui.render(gui.share.nodes, gui.share.links);
                        } else {
                            //horizon.clearAllMessages();
                            //horizon.alert("error", gettext("Failed to cut off the connection"));
                        }
                    }
                },
                mouseover: function(d) {
                    var e = d3.event || window.event;
                    if (e.stopPropagation) {
                        e.stopPropagation();
                    } else {
                        e.cancelBubble = true;
                    }
                    e.preventDefault();
                    d3.event.preventDefault();

                    if (gui.share.select_scissor) {
                        d3.select(this).select('line')
                            .classed('link', false)
                            .classed('linkscissor', false)
                            .attr('stroke', "red")
                            .attr('stroke-width', 4);
                    }
                },
                mouseout: function(d) {
                    var e = d3.event || window.event;
                    if (e.stopPropagation) {
                        e.stopPropagation();
                    } else {
                        e.cancelBubble = true;
                    }
                    e.preventDefault();

                    if (gui.share.select_scissor) {
                        d3.select(this).select('line')
                            .classed('link', true)
                            .classed('linkscissor', false);
                    }
                },
            },
        },
    };

    tool = {
        // 箭头&提示
        toolAceTip: function() {
            var is = $("#tool .separate_line ~ i");
            for (var i = 0; i < is.length; i++) {
                if (!$(is[i]).attr("id")) {
                    $(is[i]).mouseover(function(e) {
                        e.preventDefault();
                        var offset = $(this).offset();
                        $("#toolAce").css("visibility", "visible");
                        $("#toolAce").offset(function() {
                            var newPos = new Object();
                            newPos.left = offset.left;
                            newPos.top = offset.top + 20;
                            return newPos;
                        });
                        $("#toolTip").css("visibility", "visible");
                        $("#toolTip").css("font-style", "normal");
                        $("#toolTip").css("font-weight", "normal");
                        $("#toolTip").offset(function() {
                            var newPos = new Object();
                            newPos.left = offset.left;
                            newPos.top = offset.top - 35;
                            return newPos;
                        }).html(config.typeMap[$(this).children("div").attr("image_type")]);
                    }).mouseout(function() {
                        $("#toolAce").css("visibility", "hidden");
                        $("#toolTip").css("visibility", "hidden");
                    })
                }
            }
        },
        // 辅助功能函数--控制load开始与结束
        loading: function(start) {
            gui.share.deg = 0;

            function rotate() {
                if (gui.share.deg < 360) {
                    gui.share.deg += 1;
                } else {
                    gui.share.deg = 0;
                }
                d3.select("#gui_load").attr("transform", "rotate(" + gui.share.deg + ",200,200)");
                if (start) {
                    $("#gui_loading").show();
                    $("#gui_model").show();
                    gui.share.intervalLoad = setTimeout(rotate, 1);
                } else {
                    clearTimeout(gui.share.intervalLoad);
                    $("#gui_loading").hide();
                    $("#gui_model").hide();
                }
            };
            rotate();

        },
        // 辅助功能函数--渲染load（包括图层，以及中间那个圆）
        renderLoad: function(innerRadius, modelWidth, modelHeight, value) {
            $("#gui_loading").show();
            $("#gui_model").show();
            d3.select("#gui_loading").select("svg").remove();
            var svg = d3.select("#gui_loading")
                .append("svg")
                .attr("width", config.loadModel.width)
                .attr("height", config.loadModel.height);
            svg.append("defs")
                .append("filter")
                .attr("id", "inner-glow")
                .append("feGaussianBlur")
                .attr("in", "SourceGraphic")
                .attr("stdDeviation", "7 7");

            function resizeRelation() {
                var lefts = value.left + modelWidth / 2 - config.loadModel.width / 2;
                var tops = value.top + modelHeight / 2 - config.loadModel.height / 2;
                if (tops < 0) {
                    tops = 0;
                }
                $("#gui_loading").offset({
                    left: lefts,
                    top: tops,
                });
                //console.log($("#gui_loading").offset());
            }
            resizeRelation();
            $("#gui_model")
                .css("width", modelWidth)
                .css("height", modelHeight)
                .offset({
                left: value.left,
                top: value.top,
            });
            var fullAngle = 2 * Math.PI;
            var endAngle = fullAngle;
            var data = [{
                    startAngle: 0,
                    endAngle: 0.3 * endAngle
                }, {
                    startAngle: 0.33 * endAngle,
                    endAngle: 0.63 * endAngle
                }, {
                    startAngle: 0.66 * endAngle,
                    endAngle: 0.96 * endAngle
                },

            ];
            var arc = d3.svg.arc().outerRadius(62)
                .innerRadius(innerRadius);
            svg.select("g").remove();
            var inner = svg.append("g")
                .append("g")
                .attr("id", "inner");
            inner.append("path")
                .attr("id", "inner-glowing-arc")
                .attr("transform", "translate(200,200)")
                .attr("d", d3.svg.arc()
                .innerRadius(50)
                .outerRadius(65)
                .startAngle(0)
                .endAngle(fullAngle))
                .style("fill", "rgba(13,215,247, .9)")
                .attr("filter", "url(#inner-glow)");

            inner.append("circle")
                .attr("id", "#inner-circle")
                .attr("cx", 200)
                .attr("cy", 200)
                .attr("r", 40)
                .style("fill", "white")
                .style("stroke", "white")
                .style("stroke-width", "0");

            inner.append("use")
                .attr("xlink:href", "#inner-circle")
                .attr("filter", "url(#inner-glow)");

            inner.append("g")
                .attr('transform', "translate(200,200)")
                .attr("id", "gui_load")
                .selectAll("path.arc")
                .data(data)
                .enter()
                .append("path")
                .attr("class", "arc")
                .attr("fill", "rgb(13,215,247)")
                .attr("d", function(d, i) {
                return arc(d, i);
            })
                .attr("transform", "translate(200,200)");
            $("#gui_loading").hide();
            $("#gui_model").hide();
        },

        // 可拖的参数
        draggable: {
            helper: "clone",
            revert: false,
            opacity: 0.8,
            cursor: "move",
        },

        // 可拖放的参数
        droppable: {
            activeClass: "dragPlay",
            hoverClass: "dragPlay",
            revert: "valid", //revert target when quotas exceeded
            drop: function(e, ui) {
                tool.drop(ui);
            }
        },
        drop: function(obj) {
          if (typeof obj != "undefined")
            obj.draggable.click();
        },

        // 拖的过程中共享的变量
        drag: function(event) {
            var image = $(event.target).attr("image_id").split(" ");
            var imageIdc = [];
            for (var i = 0; i < image.length; i++) {
                var t = image[i].split(":");
                var m = {};
                m.image_id = t[0];
                m.image_dc = t[1];
                imageIdc.push(m);
            }
            gui.share.imageIdc = imageIdc;
        },
        init: function() {
            // 执行箭头提示
            tool.toolAceTip();

            $("#play").droppable(tool.droppable);

            // 点击
            $("#tool .gui_drag").click(function(e) {
                e = window.event || e;
                tool.drag(e);
                tool.drop();
            }).dblclick(function(e) {
                e = window.event || e;
                tool.drag(e);
                tool.drop();
            });

            // 拖拽
            $("#tool .gui_drag").draggable(tool.draggable);
            $("#tool .gui_drag").bind("drag", tool.drag);
            $("#tool .gui_drag").draggable(function() {
                $("#tool .gui_drag").trigger("drag");
            });
        },
    };

    global.gui = gui;
    $(function() {
        gui.init();
    });
})(window, jQuery);
