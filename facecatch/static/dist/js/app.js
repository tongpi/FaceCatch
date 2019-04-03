/*!
 * Copyright (c) 2018 gdsgui
 */

var userAgent = navigator.userAgent; //取得浏览器的userAgent字符串
// document.getElementById("version").innerHTML = userAgent;

var isOpera = userAgent.indexOf("Opera") > -1 || userAgent.indexOf("OPR/") > -1; //判断是否Opera浏览器
var isIE = userAgent.indexOf("compatible") > -1 && userAgent.indexOf("MSIE") > -1 && !isOpera; //判断是否IE浏览器
var isEdge = userAgent.indexOf("Edge") > -1 || userAgent.indexOf(") like Gecko") > -1; //判断是否IE的Edge浏览器
var isFF = userAgent.indexOf("Firefox") > -1; //判断是否Firefox浏览器
var isSafari = userAgent.indexOf("Safari") > -1 && userAgent.indexOf("Chrome") == -1; //判断是否Safari浏览器
var isChrome = userAgent.indexOf("Chrome") > -1 && userAgent.indexOf("Safari") > -1 && userAgent.indexOf("OPR/") == -1 && userAgent.indexOf("Edge") == -1; //判断Chrome浏览器

//获取IE版本号
if (isIE) {
  var reIE = new RegExp("MSIE (\\d+\\.\\d+);");
  reIE.test(userAgent);
  var fIEVersion = parseFloat(RegExp["$1"]); //IE版本号
  IE55 = fIEVersion == 5.5;
  IE6 = fIEVersion == 6.0;
  IE7 = fIEVersion == 7.0;
  IE8 = fIEVersion == 8.0;
  // console.log(fIEVersion);
  var bodyDom = document.querySelector("body");
  var browseDom = document.createElement("div");
  browseDom.innerHTML += '<div style="position:fixed;top:0;left:0;right:0;bottom:0;z-index:1040;filter:alpha(opacity=50);background:#000;"></div><div class="position-fixed w-100 alert alert-warning m-0 fade show browser-alert" role="alert" style="z-index: 1050;"><h5 class="m-0 d-inline-block"><i class="anticon icon-warning"></i> 对不起，您的浏览器已经过时！<small>请点击右边列出的浏览器下载并使用。</small></h5><div class="d-inline-block ml-3"><a href="http://gui.hqzh.mtn/image/browser/IE11.exe" title="IE11"><img src="http://gui.hqzh.mtn/image/browser/IE11.png" height="24" hspace="10"></a><a href="http://gui.hqzh.mtn/image/browser/Chrome.exe" title="chrome"><img src="http://gui.hqzh.mtn/image/browser/Chrome.png" height="24" hspace="10"></a><a href="http://gui.hqzh.mtn/image/browser/Firefox.exe" title="firefox"><img src="http://gui.hqzh.mtn/image/browser/Firefox.png" height="24" hspace="10"></a><a href="http://gui.hqzh.mtn/image/browser/360se.exe" title="360浏览器"><img src="http://gui.hqzh.mtn/image/browser/360se.png" height="24" hspace="10"></a></div></div>';
  bodyDom.appendChild(browseDom);
} else {
  console.log(userAgent);
}

// popover class=".pop"
function initPop() {
  $('.pop').popover({
    trigger: 'manual',
    html: true,
    template: '<div class="popover" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'
  })
  //给Body加一个Click监听事件
  $('body').click(function (event) {
    var popTarget = $(event.target); // 判断自己当前点击的内容
    if (!popTarget.hasClass('popover') &&
    !popTarget.parents('.popover').hasClass('popover') &&
    !popTarget.hasClass('pop') &&
    !popTarget.parents('[data-toggle="popover"]').hasClass('pop')) {
      $('.pop').popover('hide'); // 当点击body的非弹出框相关的内容的时候，关闭所有popover
    }
  });
  $(".pop").on("click",function (event) {
    _thisP = $(this);
    $('.pop').not(_thisP).popover('hide'); // 当点击一个按钮的时候把其他的所有内容先关闭。
    _thisP.popover('toggle'); // 然后只把自己打开。
    return false;
  });
}

// app-sidebar-toggle
function sidebarToggle() {
  
  $(".sidebar-toggle-icon").click(function (e) {
    e.preventDefault();
    $(".app-sidebar").toggleClass("sidebar-toggle");
    $(this).children('.anticon').toggleClass("icon-menuunfold");
    if ($('.sidebar-toggle').length > 0) {
      $('.sidebar-menu ul').slideUp('fast');
      $.cookie("sidebarToggle", "sidebarToggleON", {expires: 1000});
      pScrollbar.destroy();
    }else{
      $('.sidebar-menu').find('.active').parents('ul').slideDown('fast');
      $('.sidebar-menu').find('.active').parents('li').addClass('open active');
      $.cookie("sidebarToggle", "sidebarToggleOFF", {expires: 1000});
      pScrollbar.update();
    }
  });
}

// sidebar-menu ul toggle visible
function initMenu() {

  $('.sidebar-menu ul.sub-menu').hide();
  $('.sidebar-menu').find('#' + $('body').attr('data-menu')).addClass('active');
  $('.sidebar-menu').find('.active').parents('ul').show();
  $('.sidebar-menu').find('.active').parents('li').addClass('open active');
  //$('#menu ul:first').show();

  // sidebar scroll
  if ($('.sidebar-scroll').length > 0) {
    var pScrollbar = new PerfectScrollbar('.sidebar-scroll');
  }
  
  var cookie_sidebarToggle = $.cookie("sidebarToggle");
  if (cookie_sidebarToggle == "sidebarToggleON") {
    $(".app-sidebar").addClass("sidebar-toggle");
    $(".sidebar-toggle-icon").children('.anticon').toggleClass("icon-menuunfold");
    pScrollbar.destroy();
  }

  $('.sidebar-menu li.parent > a').click(
    function () {
      var checkElement = $(this).next();
      if ((checkElement.is('ul.sub-menu')) && (checkElement.is(':visible'))) {
        checkElement.slideUp('normal', function () {
          pScrollbar.update();
        });
        checkElement.parent('li').toggleClass('open');
        return false;
      }
      if ((checkElement.is('ul.sub-menu')) && (!checkElement.is(':visible'))) {
        checkElement.slideDown('normal', function () {
          pScrollbar.update();
        });
        checkElement.parent('li').toggleClass('open');
        checkElement.parent().siblings('li:not(.active)').find('ul:visible').slideUp('normal');
        checkElement.parent().siblings('li:not(.active)').find('li.open:not(.active)').toggleClass('open');
        checkElement.parent().siblings('li.open:not(.active)').toggleClass('open');
        return false;
      }
    }
  );
}

// header notice
function initNotice() {

}

$(document).ready(function () {
  if ($('.app-sidebar').length > 0) {
    initMenu();
  }
  if ($('.pop').length > 0) {
    initPop();
  }
});