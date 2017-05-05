$(function () {
    //highlight Donate menu
    $("#myProfileMenu").css({'background':'white', 'color':'black'});
    $("#myHistoryMenu").css({'background':'white', 'color':'black'});
    $("#donateMenu").css({'background':'darkred', 'color':'white'});

    //get blood banks list
    $.ajax({
        url: "/bloodalert/bloodbanks",
        dataType: "json"
    }).done(function (data, textStatus, jqXHR) {
        //create a list of blood banks
        for (bbankIndex=0; bbankIndex < data.items.length; bbankIndex++){
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
                                '<div style="margin-bottom:5px">'+
                                    '<span><i class="glyphicon glyphicon-envelope"></i> ' + data.items[bbankIndex].email +' &nbsp&nbsp&nbsp</span>'+
                                    '<span><i class="glyphicon glyphicon-earphone"></i> ' + data.items[bbankIndex].telephone +'</span><br />'+
                                '</div>'+
                                '<div style="width:100%; height:400px; min-width: 300px; min-height: 300px" id="map-' +  bbankIndex + '">'+
                            '</center>'+
                        '</div>'+
                    '</div>'+
                '</div>'+
            '</li>'
            ).appendTo("#bbanksList");
        }
    
            //locate blood banks on the maps
            var myLocation = new google.maps.LatLng(38.885516, -77.09327200000001);
            var mapOptions = {
                center: myLocation,
                zoom: 16
            };
            var marker = new google.maps.Marker({
                position: myLocation,
                title: "Property Location"
            });
            var map = new google.maps.Map(document.getElementById("map-0"),
                mapOptions);
            marker.setMap(map);
        
        

        //make the list intractive
        $('[id^=bbank-]').hide();
        $('.toggle').click(function() {
            $input = $( this );
            $target = $('#'+$input.attr('data-toggle'));
            $target.slideToggle();
        });

    });

});
