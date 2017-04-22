var validCheck = {
    keyDown : function (e) {
        var key;
        if(window.event)
            key = window.event.keyCode; //IE
        else
            key = e.which; //firefox
        var event;
        if (key == 0 || key == 8 || key == 46 || key == 9){
            event = e || window.event;
            if (typeof event.stopPropagation != "undefined") {
                event.stopPropagation();
            } else {
                event.cancelBubble = true;
            }
            return;
        }
        if (key < 48 || (key > 57 && key < 96) || key > 105 || e.shiftKey) {
            e.preventDefault ? e.preventDefault() : e.returnValue = false;
        }
    },
    keyUp : function (e) {
        var key;
        if(window.event)
            key = window.event.keyCode; //IE
        else
            key = e.which; //firefox
        var event;
        event = e || window.event;
        if ( key == 8 || key == 46 || key == 37 || key == 39 )
            return;
        else
            event.target.value = event.target.value.replace(/[^0-9]/g, "");
    },
    focusOut : function (ele) {
        ele.val(ele.val().replace(/[^0-9]/g, ""));
    }
};

$('#phone').css("ime-mode", "disabled").keydown( function(e) {
    validCheck.keyDown(e);
}).keyup( function(e){
    validCheck.keyUp(e);
}).focusout( function(e){
    validCheck.focusOut($(this));
});