$(function () {
    //highlight Donate menu
    $("#myProfileMenu").css({'background':'white', 'color':'black'});
    $("#myHistoryMenu").css({'background':'white', 'color':'black'});
    $("#donateMenu").css({'background':'darkred', 'color':'white'});

    var map = new Array();
    var bbLocation = new Array();
    var bbanksCount;
    //get blood banks list
    $.ajax({
        url: "/bloodalert/bloodbanks",
        dataType: "json"
    }).done(function (data, textStatus, jqXHR) {
        //create a list of blood banks
        bbanksCount = data.items.length;
        for (bbankIndex=0; bbankIndex < bbanksCount; bbankIndex++){
            $(
            '<li class="list-group-item">'+
                '<div class="row toggle" id="dropdown-bbank-' + bbankIndex + '" data-toggle="bbank-' +  bbankIndex + '">'+
                    '<div class="col-xs-10">'+
                        data.items[bbankIndex].name +
                    '</div>'+
                    '<div class="col-xs-1"><i class="glyphicon glyphicon-chevron-down" style="right: -45px" ></i></div>'+
                '</div>'+
                '<div id="bbank-'+ bbankIndex + '">'+
                    '<hr></hr>'+
                    '<div class="container">'+
                        '<div class="fluid-row">'+
                            '<center>'+
                                '<p><b style="font-size:150% ; margin-bottom:10px">' + data.items[bbankIndex].name + '</b></p>'+
                                '<div style="margin-bottom:5px"><i class="glyphicon glyphicon-map-marker"></i> ' + data.items[bbankIndex].address +', ' + data.items[bbankIndex].city + '</div>'+
                                '<div style="margin-bottom:20px">'+
                                    '<span><i class="glyphicon glyphicon-envelope"></i> ' + data.items[bbankIndex].email +' &nbsp&nbsp&nbsp</span>'+
                                    '<span><i class="glyphicon glyphicon-earphone"></i> ' + data.items[bbankIndex].telephone +'</span><br />'+
                                '</div>'+
                                '<div id="map-' +  bbankIndex + '" style="width:100%; height:100%; min-width:300px; min-height:300px; margin-top:10px; margin-bottom:10px">'+
                            '</center>'+
                        '</div>'+
                    '</div>'+
                '</div>'+
            '</li>'
            ).appendTo("#bbanksList");
    
            //locate blood banks on the maps
            bbLocation[bbankIndex] = new google.maps.LatLng(data.items[bbankIndex].latitude, data.items[bbankIndex].longitude);
            var mapOptions = {
                center: bbLocation,
                zoom: 15
            };
            var marker = new google.maps.Marker({
                position: bbLocation[bbankIndex],
                title: "Property Location"
            });
            map[bbankIndex] = new google.maps.Map(document.getElementById("map-"+bbankIndex), mapOptions);
            marker.setMap(map[bbankIndex]);
        
        }

        //make the list intractive
        $('[id^=bbank-]').hide();
        $('.toggle').click(function() {
            $input = $( this );
            $target = $('#'+$input.attr('data-toggle'));
            $target.slideToggle();
            for (bbankIndex=0; bbankIndex < bbanksCount; bbankIndex++){
                google.maps.event.trigger(map[bbankIndex], 'resize');
                map[bbankIndex].setCenter(bbLocation[bbankIndex]);
            }
        });

    });

});
