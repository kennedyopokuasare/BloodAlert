function loadDonorHistory(){
    historyUrl=window.loggedInUser["@controls"].self.href+"history/"
    return $.ajax({
        url: historyUrl,
        dataType: "json"
    }).done(function (data, textStatus, jqXHR) {
        history=data.items
        $listGroup=$("list-group");

        //todo: build list-group-item here and append to list-group
    });
}

$(function () {
    //highlight My history menu
    $("#myProfileMenu").css({'background':'white', 'color':'black'});
    $("#myHistoryMenu").css({'background':'darkred', 'color':'white'});
    $("#donateMenu").css({'background':'white', 'color':'black'});

    $('[id^=detail-]').hide();
    $('.toggle').click(function() {
        $input = $( this );
        $target = $('#'+$input.attr('data-toggle'));
        $target.slideToggle();
    });
    loadDonorHistory();
});