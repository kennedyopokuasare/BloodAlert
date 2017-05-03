$(function () {
    //highlight Donate menu
    $("#myProfileMenu").css({'background':'white', 'color':'black'});
    $("#myHistoryMenu").css({'background':'white', 'color':'black'});
    $("#donateMenu").css({'background':'darkred', 'color':'white'});

    $('[id^=detail-]').hide();
    $('.toggle').click(function() {
        $input = $( this );
        $target = $('#'+$input.attr('data-toggle'));
        $target.slideToggle();
    });
});
