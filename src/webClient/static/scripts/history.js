function loadDonorHistory(){
    historyUrl=window.loggedInUser["@controls"].self.href+"history/"
    return $.ajax({
        url: historyUrl,
        dataType: "json"
    }).done(function (data, textStatus, jqXHR) {
        history=data.items
        // $listGroup=$("list-group");
        console.log(data);

        //todo: build list-group-item here and append to list-group
        historyCount = data.items.length;
        for (historyIndex=0; historyIndex < historyCount; historyIndex++){
            //Todo: use the blood bank Id to get and display the blood bank information 
            $(
            '<li class="list-group-item">'+
                '<div class="row toggle" id="dropdown-history-' + historyIndex + '" data-toggle="history-' +  historyIndex + '">'+
                    '<div class="col-xs-10">'+
                        data.items[historyIndex].timeStamp.slice(0 , 10) +
                    '</div>'+
                    '<div class="col-xs-1"><i class="glyphicon glyphicon-chevron-down" style="right: -45px" ></i></div>'+
                '</div>'+
                '<div id="history-'+ historyIndex + '">'+
                    '<hr></hr>'+
                    '<div class="container">'+
                        '<div class="fluid-row" style="margin-bottom:10px">'+
                            '<div style="margin-bottom:5px ; margin-left: 30px;"><i class="glyphicon glyphicon-time"></i> ' + data.items[historyIndex].timeStamp.slice(11 , 19) + '</div>'+
                            '<div style="margin-bottom:5px ; margin-left: 30px;"><i class="glyphicon glyphicon-tint"></i> ' + data.items[historyIndex].amount + ' ml</div>'+
                            '<div style="margin-bottom:5px ; margin-left: 30px;"><i class="glyphicon glyphicon-home"></i> ' + data.items[historyIndex].bloodBankId + '</div>'+
                        '</div>'+
                    '</div>'+
                '</div>'+
            '</li>'
            ).appendTo("#historyList");
        }

        //make the list intractive
        $('[id^=history-]').hide();
        $('.toggle').click(function() {
            $input = $( this );
            $target = $('#'+$input.attr('data-toggle'));
            $target.slideToggle();
        });


    });
}

$(function () {
    //highlight My history menu
    $("#myProfileMenu").css({'background':'white', 'color':'black'});
    $("#myHistoryMenu").css({'background':'darkred', 'color':'white'});
    $("#donateMenu").css({'background':'white', 'color':'black'});
    
    loadDonorHistory();

});
